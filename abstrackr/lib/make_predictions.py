import sqlalchemy
from sqlalchemy import *
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_
import os, pdb, pickle

import datetime
import sys

sys.path.append("/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/curious_snake")
# for libsvm
sys.path.append("/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/curious_snake/learners/libsvm/python")

import curious_snake # magic!

engine = create_engine("mysql://abstrackr-user:5xl.z=Uy6d@127.0.0.1:3306/abstrackrDBP01?unix_socket=/var/mysql/mysql.sock")

conn = engine.connect()
metadata = MetaData(bind=engine)

encoded_status = Table("EncodedStatuses", metadata, autoload=True)
prediction_status = Table("PredictionStatuses", metadata, autoload=True)
predictions_table = Table("Predictions", metadata, autoload=True)

#base_dir="/home/byron/abstrackr-web/curious_snake/data"
#base_dir="C:/dev/abstrackr_web/encode_test"
base_dir = "/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/curious_snake/data"
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
    predictions, train_size, num_pos = pred_results 
    # 5/4/12 -- predictions now include probability estimates!
    # just need to add these to the database.


    ####
    # update the database
    ####

    # first, delete all prediction entries associated with this
    # review (these are presumably 'stale' now)
    conn.execute(predictions_table.delete().where(predictions_table.c.project_id == review_id))

    # map -1's to 0's; this is because the ORM (sql-alchemy)
    # expects boolean fields to be either 0 or 1, which is apparently
    # a new thing in later releases (oh, well).
    neg_one_to_0 = lambda x : 0 if x < 0 else x

    # now re-insert them, reflecting the new prediction
    for study_id, pred_d in predictions.items():
        conn.execute(predictions_table.insert().values(study_id=study_id, project_id=review_id, \
                    prediction=neg_one_to_0(pred_d["prediction"]), num_yes_votes=pred_d["num_yes_votes"]),

                    predicted_probability=pred_d["pred_prob"])
    
    # delete any existing prediction status entries, should they exist
    conn.execute(prediction_status.delete().where(prediction_status.c.project_id == review_id))

    # finally, update the prediction status
    conn.execute(prediction_status.insert().values(project_id=review_id, predictions_exist=True,\
         predictions_last_made=datetime.datetime.now(), train_set_size=train_size,\
         num_pos_train=num_pos))



