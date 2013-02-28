import sqlalchemy
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_
import os, pdb, pickle

import datetime
import sys

sys.path.append("/home/byron/abstrackr-web/abstrackr/lib/curious_snake")
# for libsvm
sys.path.append("/home/byron/abstrackr-web/abstrackr/lib/curious_snake/learners/libsvm/python")

import curious_snake # magic!

engine = create_engine("mysql://root:homer@127.0.0.1:3306/abstrackr")
conn = engine.connect()
metadata = MetaData(bind=engine)

encoded_status = Table("EncodedStatuses", metadata, autoload=True)
prediction_status = Table("PredictionStatuses", metadata, autoload=True)
predictions_table = Table("Predictions", metadata, autoload=True)

base_dir="/home/byron/abstrackr-web/abstrackr/lib/curious_snake/data"
#base_dir="C:/dev/abstrackr_web/encode_test"
fields=["title", "abstract", "keywords"]


def make_predictions(review_id):
    # we're assuming the review is encoded!
    review_base_dir = os.path.join(base_dir, str(review_id))
    data_paths = []
    for field in fields:
        data_paths.append(os.path.join(review_base_dir, field, "encoded", "%s_encoded" % field))
    
    pred_results = None
    try:
        pred_results = curious_snake.abstrackr_predict(data_paths)
    except:
        print "!!!! failed to predict results for " + review_base_dir

    if pred_results is None:
        return None # fail

    # otherwise unpack the results
    predictions, train_size, num_pos = pred_results #curious_snake.abstrackr_predict(data_paths)
    # 5/4/12 -- predictions now include probability estimates!
    # just need to add these to the database.
    #pdb.set_trace()

    ####
    # update the database
    ####

    # first, delete all prediction entries associated with this
    # review (these are presumably 'stale' now)
    conn.execute(predictions_table.delete().where(predictions_table.c.review_id == review_id))

   
    # now re-insert them, reflecting the new prediction
    for study_id, pred_d in predictions.items():
        conn.execute(predictions_table.insert().values(study_id=study_id, review_id=review_id, \
                    prediction=pred_d["prediction"], num_yes_votes=pred_d["num_yes_votes"]),
                    predicted_probability=pred_d["pred_prob"])
    
    # delete any existing prediction status entries, should they exist
    conn.execute(prediction_status.delete().where(prediction_status.c.review_id == review_id))

    # finally, update the prediction status
    conn.execute(prediction_status.insert().values(review_id=review_id, predictions_exist=True,\
         predictions_last_made=datetime.datetime.now(), train_set_size=train_size,\
         num_pos_train=num_pos))



