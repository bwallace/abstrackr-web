'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	stacked_svm_learner.py
	
	Gettin' meta with it. Stacking creates a classifier by using the outputs of
	base classifiers as feature vectors. See Wolpert "Stacked Generalization" 
	in Neural Networks (1992).
'''
import pdb
import base_svm_learner
from base_svm_learner import BaseSVMLearner
from base_svm_learner import *

class StackedSVMLearner(BaseSVMLearner):
    
    def __init__(self, learners, unlabeled_datasets=None, undersample_before_eval = False, kernel_type=RBF, 
                    weights=[1,100], use_raw=False, name="STACKED"):
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets,
                                                undersample_before_eval = undersample_before_eval)

        self.learners = learners
        self.labeled_datasets = None# stacked dataset
        self.unlabeled_datasets = None
        self.kernel_type = kernel_type
        self.weights = weights

        # If use_raw is true, the meta features will be the raw (signed) distances of
        # points from the hyperplanes, rather than the binary 1/-1 predictions.
        self.use_raw = use_raw
        self.name = name

        
    def predict(self, x_id):
        '''
        This overrides the base predict function. We generate a prediction
        for the *stacked* point.
        '''
        points = [learner.unlabeled_datasets[0].get_point_for_id(x_id) for learner in self.learners]
        X = self.get_pred_vector(points)
        return self.models[0].predict(X)
        
    def rebuild_models(self, for_eval=False, undersample_these=None, 
                                    do_grid_search=True, beta=2, verbose=True):
        '''
        Trains the global 'stacked' model, which is an SVM trained on a 
        stacked representation of the data. This representation maps
        each point x to the k distances from the respective (k) hyperplanes.
        '''
        # rebuild the models that compose the stacked model
        for learner in self.learners:
            learner.rebuild_models(for_eval=for_eval, do_grid_search=do_grid_search, undersample_these = undersample_these)

            
        self.labeled_datasets = [self.get_stacked_dataset(True)]
        self.unlabeled_datasets = [self.get_stacked_dataset(False)]
        if self.undersample_before_eval and for_eval:
            if verbose:
                print "%s: undersampling (using %s) before building models.." % (self.name, self.undersample_function.func_name)
            
            #
            # @experimental 9/23 
            # Here we're assuming the undersample function accepts an 'undersample_these'
            # parameter. We should implement a different strategy that doesn't make any
            # assumptions about the undersample function. Alternatively, if we want to force
            # the undersample fucntion to allow for an optional 'undersample_these' argument, 
            # we need to document this explicitly.
            #
            print ">> warning -- we're making assumptions about the undersample function being used here"
            datasets = self.undersample_function(undersample_these=undersample_these)
            undersampled_ids = list(set(self.labeled_datasets[0].instances.keys()) - set(datasets[0].instances.keys()))
        else:
            datasets = self.labeled_datasets
          
        # now train
        samples, labels = datasets[0].get_samples_and_labels()
        problem = svm_problem(labels, samples)
        param = svm_parameter(kernel_type = self.kernel_type, weight = self.weights)
        if do_grid_search:
            print "running grid search..."
            C, gamma = grid_search(problem, param, linear_kernel=(self.kernel_type==LINEAR), beta=beta)
            print "done. best C, gamma: %s, %s" % (C, gamma)
            param = svm_parameter(kernel_type = self.kernel_type, weight = self.weights, 
                                                    C=C, gamma=gamma)
       
        self.models = [svm_model(problem, param)]

    def get_stacked_dataset(self, labeled_data):
        instances = {}
        if labeled_data:
            for x_id in self.learners[0].labeled_datasets[0].get_instance_ids():
                # it doesn't matter which learner we pull the label from
                lbl = self.learners[0].labeled_datasets[0].get_label_for_id(x_id) 
                # note that we assume the following:
                #   1) the learners have the same instances in the first dataset
                #   2) each learner has only one dataset (we ignore any others)
                
                points = [learner.labeled_datasets[0].get_point_for_id(x_id) for learner in self.learners]
                stacked_point = self.get_pred_vector(points)
                # one point per learner
                dict_point = dict(zip(range(len(self.learners)), stacked_point))
                # not dealing with level-2 labels here (yet)
                instances[x_id] = dataset.instance(x_id, dict_point, level_1_label=lbl)        
        else:
            for x_id in self.learners[0].unlabeled_datasets[0].get_instance_ids():
                # it doesn't matter which learner we pull the label from
                lbl = self.learners[0].unlabeled_datasets[0].get_label_for_id(x_id) 
                # note that we assume the following:
                #   1) the learners have the same instances in the first dataset
                #   2) each learner has only one dataset (we ignore any others)
                points = [learner.unlabeled_datasets[0].get_point_for_id(x_id) for learner in self.learners]
                stacked_point = self.get_pred_vector(points)

                # one point per learner
                dict_point = dict(zip(range(len(self.learners)), stacked_point))
                # not dealing with level-2 labels here (yet)
                instances[x_id] = dataset.instance(x_id, dict_point, level_1_label=lbl)                        

        return dataset.dataset(instances)

    def label_instances_in_all_datasets(self, inst_ids):
        #
        # In fact we label the examples in the 'base' classifiers
        # composing the stacked classifier.
        #
        for learner in self.learners:
            learner.label_instances_in_all_datasets(inst_ids)
        
    
    def get_pred_vector(self, X):
        preds = []
        for model, x in zip(self.learners, X):
            if self.use_raw:
                preds.append(model.models[0].distance_to_hyperplane(x, signed=True))
            else:
                preds.append(model.models[0].predict(x))
        return preds
               
    def get_distance_vector(self, X):
        ''' Raw distance vector '''
        distances = []
        for model, x in zip(self.learners, X):
            distances.append(model.models[0].distance_to_hyperplane(x, signed=True))
        return distances
        
        