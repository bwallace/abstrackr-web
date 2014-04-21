'''
This should replace extract_from_sql!
'''

import os, pdb, pickle, random
from operator import itemgetter
import datetime

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_

import make_predictions_sklearn

engine = create_engine("mysql://root@127.0.0.1:3306/abstrackr?unix_socket=/var/mysql/mysql.sock")
#engine = create_engine("mysql://abstrackr-user:5xl.z=Uy6d@127.0.0.1:3306/abstrackrDBP01?unix_socket=/var/mysql/mysql.sock")
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

def get_ids_from_names(review_names):
    s = reviews.select(reviews.c.name.in_(review_names))
    return [review.id for review in s.execute()]

def _all_review_ids():
    return [review.id for review in reviews.select().execute()]

def _get_citations_for_review(review_id):
    citation_ids = list(select([citations.c.id], 
                                    citations.c.project_id == review_id).execute())
    return citation_ids

def _predictions_last_updated(review_id):
    if not _do_predictions_exist_for_review(review_id):
        return False

    pred_last = list(select(
                    [prediction_status.c.predictions_last_made], 
                        prediction_status.c.project_id == review_id).execute().fetchone())[0]
    return pred_last
                    
def _do_predictions_exist_for_review(review_id):
    pred_status = select(
                    [prediction_status.c.project_id, prediction_status.c.predictions_exist],
                     prediction_status.c.project_id == review_id).execute().fetchone()
              
    if pred_status is None or not pred_status.predictions_exist:
        return False
    return True

def _get_predictions_for_review(review_id):
    '''
    map citation ids to predictions 
    '''
    preds = list(select([predictions.c.study_id, predictions.c.predicted_probability],
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
    priority_ids_for_review = list(select([priorities.c.id, priorities.c.citation_id], 
                                    priorities.c.project_id == review_id).execute())
    for priority_id, citation_id in priority_ids_for_review:
        if citation_id in cit_id_to_new_priority:
            priority_update = priorities.update(priorities.c.id == priority_id)
            priority_update.execute(priority = cit_id_to_new_priority[citation_id])
        
def _priority_q_is_empty(review_id):
    return len(select([priorities.c.id], priorities.c.project_id == review_id).execute().fetchall()) == 0

if __name__ == "__main__":
    all_reviews = _all_review_ids()
    reviews_to_update = [r for r in all_reviews if not _priority_q_is_empty(r)]
    #pdb.set_trace()
    for review_id in reviews_to_update:
        predictions_last_updated = _predictions_last_updated(review_id)
        sort_by_str = select([reviews.c.sort_by], reviews.c.id == review_id).execute()
        # uh-oh
        if sort_by_str.rowcount == 0:
            print "I can't do anything for review %s -- it doesn't appear to have an entry" % review_id
        else:
            sort_by_str = sort_by_str.fetchone().sort_by
            labels_for_review = select([labels.c.label_last_updated], 
			         labels.c.project_id==review_id).order_by(labels.c.label_last_updated.desc()).execute()
            if labels_for_review.rowcount > 0:
                print "checking review %s..." % review_id
                most_recent_label = labels_for_review.fetchone().label_last_updated
                #pdb.set_trace()
                print "the most recent label for review %s is dated: %s" % (review_id, most_recent_label)
                if not _do_predictions_exist_for_review(review_id) or most_recent_label > predictions_last_updated:
                    # now make predictions for updated reviews.
                    print "making predictions for %s" % review_id
                    make_predictions_sklearn.make_predictions(review_id)

                    # now re-prioritize
                    print "re-prioritizing..."
                    _re_prioritize(review_id, sort_by_str)
                else:
                    # initial set of predictions
                    print "not updating predictions for %s" % review_id

    print "done."
