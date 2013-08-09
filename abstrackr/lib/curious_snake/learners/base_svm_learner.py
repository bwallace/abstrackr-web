'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	base_svm_learner.py
	---

	A base class for active learners using Support Vector Machines (SVMs). Uses (a modified version of) the
	libsvm library, Copyright (c) 2000-2008 Chih-Chung Chang and Chih-Jen Lin.

	Subclass this if you want to implement a different active learning strategy with SVMs (see the random_svm_learner and
	simple_svm_learner modules).
'''
#
# Here we explicitly append the path to libsvm; is there a better way to do this?
#
import os
import sys
import pdb
path_to_libsvm = os.path.join(os.getcwd(), "learners", "libsvm", "python")
sys.path.append(path_to_libsvm)
import svm
from svm import *
import base_learner
from base_learner import BaseLearner
from base_learner import dataset

class BaseSVMLearner(BaseLearner):

    def __init__(self, unlabeled_datasets = None, models = None, undersample_before_eval = False,
                        weights=[1,100], kernel_type=LINEAR, svm_params=None):
        BaseLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                        undersample_before_eval = undersample_before_eval)

        self.unlabeled_datasets = unlabeled_datasets or []
        # params correspond to each of the respective models (one if we're in a single feature space)
        # these specify things like what kind of kernel to use. here we just use the default, but
        # *you'll probably want to overwrite this* in your subclass. see the libsvm doc for more information
        # (in particular, svm_test.py is helpful).

        print "%s: using kernel type: %s" % (self.name, kernel_type)
        self.weights = weights
        self.kernel_type = kernel_type
        self.params = None
        if svm_params is None:
          self.params = [svm_parameter(weight=self.weights, kernel_type=self.kernel_type)  for d in self.unlabeled_datasets]
        else:
          self.params = [svm_params for d in self.unlabeled_datasets]

        self.div_hash = {}


    def rebuild_models(self, for_eval=False, verbose=True, undersample_these=None,
                                    do_grid_search=False, beta=2):
        '''
        Rebuilds all models over the current labeled datasets. If for_eval is true,
        we undersample if this learner is set to undersample before evaluation.
        Returns a list of the undersampled ids (if any).
        '''
        dataset = None
        undersampled_ids  = []
        if self.undersample_before_eval and for_eval:
            if verbose:
                print "%s: undersampling (using %s) before building models.." % (self.name, self.undersample_function.func_name)

            #
            # @experimental 9/23
            # Here we're assuming the undersample function accepts an 'undersample_these'
            # parameter. You should implement a diffferent, more flexible strategy to allow this
            #
            if self.undersample_function.__name__ == "undersample_labeled_datasets":
                # print ">> warning -- we're making assumptions about the undersample function being used here"
                datasets = self.undersample_function(undersample_these=undersample_these)
            else:
                datasets = self.undersample_function()
            undersampled_ids = list(set(self.labeled_datasets[0].instances.keys()) - set(datasets[0].instances.keys()))
        else:
            datasets = self.labeled_datasets

        if verbose:
            print "training model(s) on %s instances" % datasets[0].size()

        self.models = []
        for dataset, param in zip(datasets, self.params):
            samples, labels = dataset.get_samples_and_labels()
            try:
                problem = svm_problem(labels, samples)
            except:
                pdb.set_trace()

      
            #param = svm_parameter(kernel_type = self.kernel_type, weight = self.weights,\
            #                         weight_label=[1], nr_weight=1)#len(self.weights))
            
            if do_grid_search:
                if verbose:
                    print "running grid search..."
                    print "number of labels: %s" % len(labels)
                C, gamma = grid_search(problem, param, linear_kernel=(self.kernel_type==LINEAR), \
                                        beta=beta, verbose=verbose)
                if verbose:
                    print "done. best C, gamma: %s, %s" % (C, gamma)
                param = svm_parameter(kernel_type = self.kernel_type, weight = self.weights,
                                                        C=C, gamma=gamma)
            else:
                if verbose:
                    print "not doing grid search."
            model = svm_model(problem, param)
            self.models.append(svm_model(problem, param))


        #
        # Return the ids of the instances that were undersampled,
        # i.e., thrown away. This is in case you want to undersample
        # the same examples in every learner (you undersample for one
        # learner then throw the same majority examples away for the
        # others.
        return undersampled_ids


    def get_raw_predictions(self):
        '''
        Returns (summed) raw predictions for unlabeled instances. These can
        be used, for example, to generate ROC curves. In particular,
        for each unlabeled instance in the unlabeled dataset corresponding
        to the view_index parameter, the following is returned:

            #id  true_label  prediction  raw_distance
            true_label  prediction
        '''
        sign = lambda x: 1 if x > 0 else -1
        preds_and_true = []
        for inst_id, inst in self.unlabeled_datasets[0].instances.items():
            raw_prediction = 0.0
            for model, dataset in zip(self.models, self.unlabeled_datasets):
                raw_prediction += model.distance_to_hyperplane(dataset.get_point_for_id(inst_id), signed=True)
            #preds_and_true.append([inst.id, inst.label, sign(raw_prediction), raw_prediction])
            preds_and_true.append([inst.id, inst.label, raw_prediction])
        return preds_and_true


    def _get_dist_from_l(self, model, data, x):
        min_dist = None
        for y in data.instances.values():
            if not (x.id, y.id) in self.dist_hash:
                self.dist_hash[(x.id, y.id)] = model.compute_dist_between_examples(x.point, y.point)
            if not min_dist or self.dist_hash[(x.id, y.id)] < min_dist:
                min_dist = self.dist_hash[(x.id, y.id)]
        return min_dist

    def _max_dists_to_hyperplanes(self):
        '''
        Returns the maximum distance from each hyperplane in the respective views.
        This can be used to normalize these distances, for example.
        '''
        max_dists = [0.0 for m in self.models]
        for inst_id in self.unlabeled_datasets[0].get_instance_ids():
            for view_index, model in enumerate(self.models):
                # note that we get the unsigned distance because we're only
                # concerned with magnitude here
                cur_dist =  model.distance_to_hyperplane(self.unlabeled_datasets[view_index].get_point_for_id(inst_id))
                if cur_dist > max_dists[view_index]:
                    max_dists[view_index] = cur_dist
        return max_dists


    def _compute_div(self, model, data, x):
        sum = 0.0
        for y in data.instances.values():
            # have we already computed this?
            if not (x.id, y.id) in self.div_hash:
                # if not, compute the function and add to the hash
                self.div_hash[(x.id, y.id)] = model.compute_cos_between_examples(x.point, y.point)
            sum+= self.div_hash[(x.id, y.id)]
        return sum


    def _compute_cos(self, model_index, x, y):
        '''
        computes the cosine between two instances, x and y. note that this memoizes
        (caches) the cosine, to avoid redundant computation.
        '''
        if not (model_index, x.id, y.id) in self.div_hash:
            model = self.models[model_index]
            self.div_hash[(model_index, x.id, y.id)] = model.compute_cos_between_examples(x.point, y.point)
        return self.div_hash[(model_index, x.id, y.id)]



    def most_pos(self, k):
        model = self.models[0]
        unlabeled_dataset = self.unlabeled_datasets[0]

        k_ids_to_distances = {}
        for x in unlabeled_dataset.instances.values()[:k]:
            k_ids_to_distances[x.id] = model.distance_to_hyperplane(x.point, signed=True)

       # now iterate over the rest
        for x in unlabeled_dataset.instances.values()[k:]:
            cur_min_id, cur_min_dist = self._get_min_val_key_tuple(k_ids_to_distances)
            x_dist = model.distance_to_hyperplane(x.point, signed=True)
            if x_dist > cur_min_dist:
                # then x is closer to the hyperplane than the farthest currently observed
                # remove current max entry from the dictionary
                k_ids_to_distances.pop(cur_min_id)
                k_ids_to_distances[x.id] = x_dist
                print "better dist: %s" % x_dist

        return k_ids_to_distances.keys()


    def _SIMPLE(self, model, unlabeled_dataset, k, do_not_pick=None):
        '''
        Implementation of SIMPLE; takes model and dataset to use parametrically.
        Returns selected instance identifiers, as provided by their id fields.
        '''
        # initially assume k first examples are closest
        k_ids_to_distances = {}

        if do_not_pick is None:
            do_not_pick = []

        picked = 0
        start_at = 0
        # pick first k examples not on the do_not_pick list
        while picked < k:
            for x in unlabeled_dataset.instances.values():
                start_at += 1
                if not x.id in do_not_pick:
                    k_ids_to_distances[x.id] = model.distance_to_hyperplane(x.point)
                    picked+=1
                    if picked == k:
                        print "ok!"
                        break

        # now iterate over the rest
        for x in unlabeled_dataset.instances.values()[start_at:]:
            cur_max_id, cur_max_dist = self._get_max_val_key_tuple(k_ids_to_distances)
            x_dist = model.distance_to_hyperplane(x.point)
            if not x.id in do_not_pick and x_dist < cur_max_dist:
                # then x is closer to the hyperplane than the farthest currently observed
                # remove current max entry from the dictionary
                k_ids_to_distances.pop(cur_max_id)
                k_ids_to_distances[x.id] = x_dist

        return k_ids_to_distances.keys()


    def _get_max_val_key_tuple(self, d):
        keys, values = d.keys(), d.values()
        max_key, max_val = keys[0], values[0]
        for key, value in zip(keys[1:], values[1:]):
            if value > max_val:
                max_key, max_val = key, value
        return (max_key, max_val)


    def _get_min_val_key_tuple(self, d):
        keys, values = d.keys(), d.values()
        min_key, min_val = keys[0], values[0]
        for key, value in zip(keys[1:], values[1:]):
            if value < min_val:
                min_key, min_val = key, value
        return (min_key, min_val)

    def find_outliers(self, instances, k, model_index=0):
        #
        # @deprecated
        #
        if len(instances) == 0:
            return None

        if len(instances) == 1:
            # only one instance
            return instances[0].id

        insts_to_scores = {}
        for instance_1 in instances:
            cur_score = 0.0
            for instance_2 in [inst for inst in instances if inst.id != instance_1.id]:
                cur_score+=self._compute_cos(model_index, instance_1, instance_2)

            insts_to_scores[instance_1.id] = cur_score

        top_scores = insts_to_scores.values()[:k]
        top_scores.sort(reverse=True)
        return [top_id for top_id in insts_to_scores.keys() if insts_to_scores[top_id]  in top_scores[:k]]


    def aggressive_undersample_labeled_datasets(self, k=None):
        '''
        Aggressively undersamples the current labeled datasets; returns a *copy* of the undersampled datasets.
        *Does not mutate the labeled datasets*.
        '''
        feature_space_index = 0
        if self.labeled_datasets and len(self.labeled_datasets) and (len(self.labeled_datasets[0].instances) > 0):
            if not k:
                print "(aggressively) undersampling majority class to equal that of the minority examples"
                # we have to include 'false' minorities -- i.e., instances we've assumed are positives -- because otherwise we'd be cheating
                k = self.labeled_datasets[feature_space_index].number_of_majority_examples() - self.labeled_datasets[0].number_of_minority_examples()
            # we copy the datasets rather than mutate the class members.
            copied_datasets = [d.copy() for d in self.labeled_datasets]
            if k < self.labeled_datasets[0].number_of_majority_examples() and k > 0:
                print "removing %s majority instances. there are %s total majority examples in the dataset." % \
                                    (k, self.labeled_datasets[0].number_of_majority_examples())

                # get the majority examples; find those closeset to the hyperplane (via the SIMPLE method)
                # and return them.
                majority_examples = list(self.labeled_datasets[feature_space_index].get_majority_examples())
                majority_ids = [inst.id for inst in majority_examples]
                majority_dataset = dataset.dataset(instances=dict(zip(majority_ids, majority_examples)))
                removed_these = self._SIMPLE(self.models[feature_space_index], majority_dataset, int(k))
                # if there is more than one feature-space, remove the same instances from the remaining spaces (sets)
                for labeled_dataset in copied_datasets:
                    # now remove them from the corresponding sets
                    labeled_dataset.remove_instances(removed_these)
        else:
            raise Exception, "No labeled data has been provided!"
        return copied_datasets
