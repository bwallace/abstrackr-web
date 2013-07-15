import os, pdb, pickle, random
from operator import itemgetter
import datetime

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_

from make_predictions import make_predictions
import tfidf2

engine = create_engine("mysql://abstrackr-user:5xl.z=Uy6d@127.0.0.1:3306/abstrackrDBP01?unix_socket=/var/mysql/mysql.sock")
metadata = MetaData(bind=engine)

####
# bind the tables
citations = Table("Citations", metadata, autoload=True)
labels = Table("Labels", metadata, autoload=True)
reviews = Table("Projects", metadata, autoload=True)
users = Table("user", metadata, autoload=True)
labeled_features = Table("labeledfeatures", metadata, autoload=True)
encoded_status = Table("encodedstatuses", metadata, autoload=True)
prediction_status = Table("predictionstatuses", metadata, autoload=True)
predictions = Table("predictions", metadata, autoload=True)
priorities = Table("priorities", metadata, autoload=True)

def get_labels_from_names(review_names):
    r_ids = get_ids_from_names(review_names)
    if len(r_ids) == 0:
        pdb.set_trace()
    return labels_for_review_ids(r_ids)

def get_ids_from_names(review_names):
    s = reviews.select(reviews.c.name.in_(review_names))
    return [review.id for review in s.execute()]

def labels_for_review_ids(review_ids):
    # this selects labels and information about the corresponding
    # labelers.
    s = select([labels, users, citations.c.abstract], \
                        and_(labels.c.reviewer_id == users.c.id,
                             labels.c.project_id.in_(review_ids),
                             citations.c.citation_id == labels.c.study_id),
                        use_labels=True)

    # unroll the result
    return [x for x in s.execute()]


def write_out_labels_for_reviews(review_sets, out_path):  
    # review_sets is a list of lists; each list therein comprises
    # n reviews corresponding to one single review
    # e.g,. [[my_review_1, my_review_2], [a diff review A, a diff review B]]
    abstract_length = lambda x: 0 if x is None else len(x.split(" "))
    all_results = []
    for reviews in review_sets:
        # first fetch the results
        result = get_labels_from_names(reviews)  
        all_results.append(result)

    # first write out the headers
    out_str = ["\t".join(["meta_review_id", "comprising"]+\
                    all_results[0][0].keys()[:-1] + ["abstract_length"])]

    for i, names in enumerate(review_sets):
        for result in all_results[i]:
            cur_str = "\t".join(["%s" % i, "%s" % "-".join(names)]+\
                                [str(x) for x in result.values()[:-1]]+\
                                [str(abstract_length(result['citations_abstract']))])
            out_str.append(cur_str)
    
    # ok, let's dump the result to file
    out_stream = open(out_path, 'w')
    out_stream.write("\n".join(out_str))
    out_stream.close()

def to_disk(base_dir, review_names=None, review_ids=None, fields=None):
    ''' 
    writes the citations (titles, abstracts, etc) and labels
    (both feature and instance) over the given reviews to disk; 
    base_dir tells the routine where to save the files.
    '''
    if not (review_ids or review_names):
        raise Exception, "you need to provide either the names or the ids of the reviews you want, dummy."
    elif review_ids is None:
        # get the ids from the names
        review_ids = get_ids_from_names(review_names)

    for review_id in review_ids:
        citations_to_disk(review_id, base_dir, fields=fields)
    
    lbls_to_disk(review_ids, base_dir)


def citations_to_disk(review_id, base_dir, fields=None):
    fields = fields or ["title", "abstract", "keywords", "authors", "journal"]
    none_to_text= lambda x: "none" if x is None else x

    s = citations.select(citations.c.project_id==review_id)
    citations_for_review = [x for x in s.execute()]

    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    for field in fields:
        print "(citations_to_disk) on field: %s" % field
        field_path = os.path.join(base_dir, field)
        if not os.path.exists(field_path):
            os.mkdir(field_path)

    for citation in citations_for_review:
        citation_id = citation['id']
        
        for field in fields:
            fout = open(os.path.join(base_dir, field, "%s" % citation_id), 'w')
            fout.write(none_to_text(citation[field]))
            fout.close()


def get_lbl_d_for_review(review_id):
    lbl_d = {}
    s = labels.select(labels.c.project_id==review_id)
    for lbl in s.execute():
        lbl_d[lbl["study_id"]]=lbl["label"]  
    return lbl_d

def lbls_to_disk(review_ids, base_dir):
    lbl_d = {}
    s = labels.select(labels.c.project_id.in_(review_ids))
    for lbl in s.execute():
        lbl_d[lbl["study_id"]]=lbl["label"]
    
    fout = open(os.path.join(base_dir, "labels.pickle"), 'w')
    pickle.dump(lbl_d, fout)                     
    fout.close()
    
    # also get labeled features
    lbl_feature_d = {}

    s =  labeled_features.select(labeled_features.c.project_id.in_(review_ids))   
    for lbld_feature in s.execute():
        lbl_feature_d[lbld_feature["term"]] = lbld_feature["label"]
    
    fout = open(os.path.join(base_dir, "labeled_features_d.pickle"), 'w')
    pickle.dump(lbl_feature_d, fout)                     
    fout.close()

def encode_review(review_id, base_dir="/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/curious_snake/data"):
    fields=["title", "abstract", "keywords"]
    
    base_dir = os.path.join(base_dir, str(review_id))
    
    # write the abstracts to disk
    to_disk(base_dir, review_ids=[review_id], fields=fields)

    # now encode them
    lbl_d = pickle.load(open(os.path.join(base_dir, "labels.pickle")))

    # we encode the three main fields in separate spaces (multi-view)
    for field in fields:
        print "\n\n\n(write_review_to_disk) on field: %s..." % field
        
        dir_path = os.path.join(base_dir, field)
        out_path = os.path.join(dir_path, "encoded")
        out_f_name = "%s_encoded" % field
        tfidf2.encode_docs(dir_path, out_path, out_f_name, \
                    lbl_dict=lbl_d, clean_first=True, binary=True, \
                    min_word_count=3, bi_grams_too=True, delete_files_after=True)

    # fetch the encoded status entry for this review, 
    # ***which we assume exists!***
    return base_dir

def update_labels(review_id, base_dir="/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/curious_snake/data"):
    new_lbls = get_lbl_d_for_review(review_id)
    fields = ["title", "abstract", "keywords"]
    for field in fields:
        # relying on conventions here
        dir_path = os.path.join(base_dir, str(review_id), field)
        f_path = os.path.join(dir_path, "encoded")
        out_f_name = "%s_encoded" % field
        f_path = os.path.join(f_path, out_f_name)
        print "updating file at %s" % f_path
        # just overwrite the old file
        tfidf2.update_labels(f_path, f_path, new_lbls)
        print "done"
    print "ok, all updated."
    # update the database
    update = encoded_status.update(encoded_status.c.project_id==review_id)
    update.execute(labels_last_updated = datetime.datetime.now())

def check_encoded_status_table():
    '''
    look at all the entries in the EncodedStatus table; for any reviews
    that are present but not yet encoded, encode them.
    '''

    unencoded_review_ids = list(select([encoded_status.c.project_id], \
                                    encoded_status.c.is_encoded == False).execute())
    for unencoded_id in unencoded_review_ids:
        unencoded_id = unencoded_id.project_id
        print "encoding review %s.." % unencoded_id
        base_dir = encode_review(unencoded_id)#, base_dir="C:/dev/abstrackr_web/encode_test")
        print "done!"
        # update the record
        update = encoded_status.update(encoded_status.c.project_id == unencoded_id)
        update.execute(is_encoded = True)
        update.execute(labels_last_updated = datetime.datetime.now())
        update.execute(base_path = base_dir)


def _get_citations_for_review(review_id):
    citation_ids = list(select([citations.c.id], \
                                    citations.c.project_id == review_id).execute())
    return citation_ids

def _do_predictions_exist_for_review(review_id):
    pred_status = \
            select([prediction_status.c.project_id, prediction_status.c.predictions_exist],\
                     prediction_status.c.project_id == review_id).execute().fetchone()
              
    if pred_status is None or not pred_status.predictions_exist:
        return False
    return True

def _get_predictions_for_review(review_id):
    '''
    map citation ids to predictions (num_yes_votes)
    '''
    #preds = list(select([predictions.c.study_id, predictions.c.num_yes_votes],\
    #                predictions.c.project_id == review_id).execute())
    preds = list(select([predictions.c.study_id, predictions.c.predicted_probability],\
                    predictions.c.project_id == review_id).execute())

    preds_d = {}              
    for study_id, prob in preds:
        preds_d[study_id] = prob
    return preds_d


###
# @TODO this is redundant with the corresponding method in review.py, but
#       we need to be able to invoke this statically, hence its re-implementation
###
def _re_prioritize(review_id, sort_by_str):
    citation_ids = [cit.id for cit in _get_citations_for_review(review_id)]
    predictions_for_review = None
    if _do_predictions_exist_for_review(review_id):
        # this will be a dictionary mapping citation ids to
        # the number of yes votes for them
        predictions_for_review = _get_predictions_for_review(review_id)
    else:
        # then we have to sort randomly, since we haven't any predictions
        sort_by_str = "Random"

    # we'll map citation ids to the newly decided priorities;
    # these will depend on the sort_by_str
    cit_id_to_new_priority = {}
    if sort_by_str == "Random":
        ordering = range(len(citation_ids))
        # shuffle
        random.shuffle(ordering)
        cit_id_to_new_priority = dict(zip(citation_ids, ordering))
    elif sort_by_str == "Most likely to be relevant":
        # sort the citations by ascending likelihood of relevance
        cits_to_preds = {}
        # first insert entries for *all* citations, set this to 11
        # to prioritize newly added citations (don't want to accidently
        # de-prioritize highly relevant citations). this will take care 
        # of any citations without predictions -- 
        # e.g., a review may have been merged (?) -- citations for which
        # we have predictions will simply be overwritten, below
        for citation_id in citation_ids:
            #cits_to_preds[citation_id] = 11
            cits_to_preds[citation_id] = 1.0

        for study_id, prob in predictions_for_review.items():
            cits_to_preds[study_id] = prob
        
        # now we will sort by *descending* order; those with the most yes-votes first
        sorted_cit_ids = sorted(cits_to_preds.iteritems(), key=itemgetter(1), reverse=True)

        # now just assign priorities that reflect the ordering w.r.t. the predictions
        for i, cit in enumerate(sorted_cit_ids):
            cit_id_to_new_priority[cit[0]] = i

    #####
    #   TODO -- ambiguous case (i.e., uncertainty sampling)
    ###

    ####
    # now update the priority table for the entries
    # corresponding to this review to reflect
    # the new priorities (above)
    priority_ids_for_review = list(select([priorities.c.id, priorities.c.citation_id], \
                                    priorities.c.project_id == review_id).execute())
    for priority_id, citation_id in priority_ids_for_review:
        if citation_id in cit_id_to_new_priority:
            priority_update = \
                priorities.update(priorities.c.id == priority_id)

            priority_update.execute(priority = cit_id_to_new_priority[citation_id])
        

if __name__ == "__main__":
    print "checking the EncodedStatus table for new reviews..."
    check_encoded_status_table()
    print "done."

    print "now checking to see if I should update labels..."
    # for each review, get newest label; check this against
    # the last_updated_field

    encoded_reviews = list(select([encoded_status.c.project_id, encoded_status.c.labels_last_updated],\
                                 encoded_status.c.is_encoded==True).execute())
   
    for encoded_review in encoded_reviews:
        review_id, labels_last_updated = encoded_review

        sort_by_str = \
            select([reviews.c.sort_by], reviews.c.id == review_id).execute()
        # uh-oh
        if sort_by_str.rowcount == 0:
            print "I can't do anything for review %s -- it doesn't appear to have an entry" % review_id
        else:
            sort_by_str = sort_by_str.fetchone().sort_by
            labels_for_review = select([labels.c.label_last_updated], \
			labels.c.project_id==review_id).order_by(labels.c.label_last_updated.desc()).execute()
            if labels_for_review.rowcount > 0:
                print "checking review %s..." % review_id
                most_recent_label = labels_for_review.fetchone().label_last_updated
                print "the most recent label for review %s is dated: %s" % (review_id, most_recent_label)
                if most_recent_label > labels_last_updated:
                    # then there's been at least one new label, update encoded files!
                    print "updating labels for review %s..." % review_id
                    update_labels(review_id)
            
                    # now make predictions for updated reviews.
                    print "making predictions"
                    make_predictions(review_id)

                    # now re-prioritize
                    print "re-prioritizing..."
                    _re_prioritize(review_id, sort_by_str)
                else:
                    # initial set of predictions
                    if not _do_predictions_exist_for_review(review_id):
                        make_predictions(review_id)
                        print "ok, now re-prioritizing..."
                        _re_prioritize(review_id, sort_by_str)

    print "done."
