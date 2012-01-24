import sqlalchemy
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_
import os, pdb, pickle
from make_predictions import make_predictions
import tfidf2
import datetime

engine = create_engine("mysql://root:xxxxx@127.0.0.1:3306/abstrackr")
metadata = MetaData(bind=engine)

####
# bind the tables
citations = Table("Citations", metadata, autoload=True)
labels = Table("Labels", metadata, autoload=True)
reviews = Table("Reviews", metadata, autoload=True)
users = Table("user", metadata, autoload=True)
labeled_features = Table("LabelFeatures", metadata, autoload=True)
encoded_status = Table("EncodedStatuses", metadata, autoload=True)

def get_labels_from_names(review_names):
    r_ids = get_ids_from_names(review_names)
    if len(r_ids) == 0:
        pdb.set_trace()
    return labels_for_review_ids(r_ids)

def get_ids_from_names(review_names):
    s = reviews.select(reviews.c.name.in_(review_names))
    return [review.review_id for review in s.execute()]

def labels_for_review_ids(review_ids):
    #s = labels.select(labels.c.review_id.in_(review_ids))
    #  this selects labels and information about the corresponding
    # labelers.
    s = select([labels, users, citations.c.abstract], \
                        and_(labels.c.reviewer_id == users.c.id,
                             labels.c.review_id.in_(review_ids),
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

    s = citations.select(citations.c.review_id==review_id)
    citations_for_review = [x for x in s.execute()]

    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    for field in fields:
        print "(citations_to_disk) on field: %s" % field
        field_path = os.path.join(base_dir, field)
        if not os.path.exists(field_path):
            os.mkdir(field_path)

    for citation in citations_for_review:
        citation_id = citation['citation_id']
        
        for field in fields:
            fout = open(os.path.join(base_dir, field, "%s" % citation_id), 'w')
            fout.write(none_to_text(citation[field]))
            fout.close()


def get_lbl_d_for_review(review_id):
    lbl_d = {}
    s = labels.select(labels.c.review_id==review_id)
    for lbl in s.execute():
        lbl_d[lbl["study_id"]]=lbl["label"]  
    return lbl_d

def lbls_to_disk(review_ids, base_dir):
    lbl_d = {}
    s = labels.select(labels.c.review_id.in_(review_ids))
    for lbl in s.execute():
        lbl_d[lbl["study_id"]]=lbl["label"]
    
    fout = open(os.path.join(base_dir, "labels.pickle"), 'w')
    pickle.dump(lbl_d, fout)                     
    fout.close()
    
    # also get labeled features
    lbl_feature_d = {}

    s =  labeled_features.select(labeled_features.c.review_id.in_(review_ids))   
    for lbld_feature in s.execute():
        lbl_feature_d[lbld_feature["term"]] = lbld_feature["label"]
    
    fout = open(os.path.join(base_dir, "labeled_features_d.pickle"), 'w')
    pickle.dump(lbl_feature_d, fout)                     
    fout.close()

def encode_review(review_id, base_dir="/home/byron/abstrackr-web/curious_snake/data"):
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
                    min_word_count=3, bi_grams_too=True)

    # fetch the encoded status entry for this review, 
    # ***which we assume exists!***
    return base_dir

def update_labels(review_id, base_dir="/home/byron/abstrackr-web/curious_snake/data"):
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
    update = encoded_status.update(encoded_status.c.review_id==review_id)
    update.execute(labels_last_updated = datetime.datetime.now())

def check_encoded_status_table():
    '''
    look at all the entries in the EncodedStatus table; for any reviews
    that are present but not yet encoded, encode them.
    '''

    unencoded_review_ids = list(select([encoded_status.c.review_id], encoded_status.c.is_encoded==False).execute())
    for unencoded_id in unencoded_review_ids:
        unencoded_id = unencoded_id.review_id
        print "encoding review %s.." % unencoded_id
        base_dir = encode_review(unencoded_id)#, base_dir="C:/dev/abstrackr_web/encode_test")
        print "done!"
        # update the record
        update = encoded_status.update(encoded_status.c.review_id==unencoded_id)
        update.execute(is_encoded = True)
        update.execute(labels_last_updated = datetime.datetime.now())
        update.execute(base_path = base_dir)


if __name__ == "__main__":
    print "checking the EncodedStatus table for new reviews..."
    check_encoded_status_table()
    print "done."

    print "now checking to see if I should update labels..."
    # for each review, get newest label; check this against
    # the last_updated_field

    encoded_reviews = list(select([encoded_status.c.review_id, encoded_status.c.labels_last_updated],\
                                 encoded_status.c.is_encoded==True).execute())
   
    for encoded_review in encoded_reviews:
        review_id, labels_last_updated = encoded_review
        labels_for_review = select([labels.c.label_last_updated], \
                    labels.c.review_id==review_id).order_by(labels.c.label_last_updated.desc()).execute()
        if labels_for_review.rowcount > 0:
            most_recent_label = labels_for_review.fetchone().label_last_updated
            print "checking review %s.." % review_id
            if most_recent_label > labels_last_updated:
                # then there's been at least one new label, update encoded files!
                print "updating labels for review %s..." % review_id
                update_labels(review_id)#, base_dir="C:/dev/abstrackr_web/encode_test")

                # now make predictions for updated reviews.
                print "making predictions"
                make_predictions(review_id)
                
    print "done."

