'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	co_test_svm_learner.py
	
	This module implements 'co-testing', an active learning strategy for
	multiple views. See Muslea et al. in Journal of AI Research (2006).
'''


import random
from base_svm_learner import BaseSVMLearner


class CoTestLearner(BaseSVMLearner):
    def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)


        #
        # most importantly we change the query function to max_contention here
        #
        print "switching query function to max contention!"
        self.query_function = self.max_contention
        self.name = "CoTester_max_contention" 
        
    def naive_co_test(self, k):
        '''
        Picks for labeling k points about whose labels the views disagree. If there 
        are not enough such points, returns points at random.
        '''
        contention_points = self.get_contention_points()
        label_these = []
        if len(contention_points) < k:
            print "naive co-test -- not enough contention points (only %s, you wanted %s); \
                        augmenting with random instance ids." % (len(contention_points), k)
            difference = k- len(contention_points) 
            label_these = random.sample(self.unlabeled_datasets[0].get_instance_ids(), difference)
            label_these.extend(contention_points)
        else:
            label_these = random.sample(contention_points, k)
        return label_these
     
    def max_contention(self, k):
        # first, get the maximum distances to the hyperplanes over
        # all unlabeled examples in the respective spaces. we'll use
        # these to normalize.
        norms = self._max_dists_to_hyperplanes()
        ids_to_distance_vars = {}
        
        unlabeled_ids = self.unlabeled_datasets[0].get_instance_ids()
        for x_id in unlabeled_ids:
            # build a vector with x's representation in each view/space
            X = [d.get_point_for_id(x_id) for d in self.unlabeled_datasets]
            distances = self._get_distance_vector(X)
            # normalize
            normed_distances = [d/max_d for d, max_d in zip(distances, norms)]
            # compute the variance over the distances; we'll use this as 
            # a proxy for disagreement
            N = float(len(normed_distances))
            #print normed_distances
            avg_dist = sum(normed_distances) / N
            var_dist = (sum([(distance - avg_dist)**2 for distance in normed_distances]))/N
            ids_to_distance_vars[x_id] = var_dist
            #print var_dist

        # now return the ids for the k examples with the highest
        # variances
        top_k = []
        while len(top_k) < k:
            max_id, max_val = self._get_max_val_key_tuple(ids_to_distance_vars)
            ids_to_distance_vars.pop(max_id)
            top_k.append(max_id)
        
        return top_k
                

    def get_contention_points(self):
        # return all instances about whose class the feature spaces, or views, disagree
        contention_points = []
        for instance_id in self.unlabeled_datasets[0].get_instance_ids():
            predictions = []
            for view_index, h in enumerate(self.models):
                predictions.append(h.predict(self.unlabeled_datasets[view_index].\
                                                                                    get_point_for_id(instance_id)))
            if min(predictions) != max(predictions):
                contention_points.append(instance_id)
        return contention_points