import pdb
from collections import defaultdict

import sklearn
from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.grid_search import GridSearchCV
# sklearn.svm.LinearSVC
import numpy as np

class MetaClf:

    def __init__(self, clf_ti, clf_ab, clf_mh=None):
        self.clf_ti = clf_ti
        self.clf_ab = clf_ab
        self.clf_mh = clf_mh

    def predict(self, X_ti, X_ab, X_mh=None):
        preds_ti = self.clf_ti.predict(X_ti)
        preds_ab = self.clf_ab.predict(X_ab)
        if self.clf_mh is None or X_mh is None:
            preds_mh = [1]*X_ti.shape[0]
        else:
            preds_mh = self.clf_mh.predict(X_mh)
        # at least one is -1 here; not sure if you want that 
        # or 0
        return preds_ti + preds_ab + preds_mh >= -1

    def predict_probabilities(self, X_ti, X_ab, X_mh):
        probs_ti = self.clf_ti.predict_proba(X_ti)[:,1]
        probs_ab = self.clf_ab.predict_proba(X_ab)[:,1]
        if self.clf_mh is None or X_mh is None:
            probs_mh = np.asarray([.5]*X_ti.shape[0])
        else:
            probs_mh = self.clf_mh.predict_proba(X_mh)[:,1]
        # @TODO should probably do something clever here
        # (e.g., calibrate the weightings apportioned to 
        #  each view)
        return (probs_ti + probs_ab + probs_mh) / 3.0

class BaggedUSLearner:
    """ bagged & undersampled learner. """
    def __init__(self, dataset, ensemble_size=11):
        self.dataset = dataset
        self.ensemble_size = ensemble_size

    def train(self):
        X_titles, X_abstracts, X_mesh, y = self.dataset.get_train_X_y()
        if max(y) < 0:
            raise Exception, "no positive examples!"

        print "training on %s labeled instances" % len(y)

        self.ensemble = []

        param_grid = [{'C': [.001, .01, 1, 10, 100]}]
        
        ###
        # undersampling
        pos_indices = np.where(y==1)[0]
        n_pos = len(pos_indices)
        neg_indices = np.where(y==-1)[0]
        for l_i in xrange(self.ensemble_size):
            neg_indices_i = np.random.choice(neg_indices, n_pos)
            indices_i = np.hstack((pos_indices, neg_indices_i))
        
            X_i_ti, X_i_ab = X_titles[indices_i], X_abstracts[indices_i]
            if X_mesh is not None:
                X_i_mh = X_mesh[indices_i]

            y_i = y[indices_i]

            ###
            # might want to swap in a different scoring function here,
            # but on the other hand, this is balanced accuracy, so probably
            # what we want (i guess?). could also try recall..
            self.clf_ti = GridSearchCV(svm.SVC(probability=True, kernel="linear"), param_grid)
            self.clf_ti.fit(X_i_ti, y_i)

            self.clf_ab = GridSearchCV(svm.SVC(probability=True, kernel="linear"), param_grid)
            self.clf_ab.fit(X_i_ab, y_i)

            self.clf_mh = None
            if X_mesh is not None:
                self.clf_mh = GridSearchCV(svm.SVC(probability=True, kernel="linear"), param_grid)
                self.clf_mh.fit(X_i_mh, y_i)

            self.ensemble.append(MetaClf(self.clf_ti, self.clf_ab, self.clf_mh))

        print "ok -- all trained (ensemble built)"
        
    #### TODO this needs to be a dictionary with study id's
    # as keys and values should themselves be dictionaries
    # with 
    def predict_remaining(self, return_true_labels=False):
        #test_X, test_y = self.dataset.get_test_X_y()
        X_titles, X_abstracts, X_mesh, y = self.dataset.get_test_X_y()
        ids = self.dataset.get_test_ids()

        predictions = []
        predicted_probabilities = []
        for ensemble in self.ensemble:
            predictions.append(ensemble.predict(X_titles, X_abstracts, X_mesh).tolist())
            predicted_probabilities.append(ensemble.predict_probabilities(X_titles, X_abstracts, X_mesh).tolist())

        final_preds_d = defaultdict(dict)
        k = float(self.ensemble_size)/2
        num_pos = 0
        for i in xrange(X_titles.shape[0]):
            id_ = ids[i]
            ensemble_preds_i = [preds[i] for preds in predictions]
            pos_count = ensemble_preds_i.count(True)
            final_prediction_i = pos_count >= k
            if final_prediction_i:
                num_pos += 1
            #final_predictions.append(final_prediction_i)
            final_preds_d[id_]["prediction"] = final_prediction_i
            final_preds_d[id_]["num_yes_votes"] = pos_count
            ### 
            # @TODO reimplement our ICDM stuff!
            # these are really awful.
            predicted_probs_i = [pred_probs[i] for pred_probs in predicted_probabilities]
            final_predicted_prob_i = sum(predicted_probs_i) / float(self.ensemble_size)

            final_preds_d[id_]["pred_prob"] = final_predicted_prob_i

        train_size = self.dataset.N - len(ids)
        return final_preds_d, train_size, num_pos