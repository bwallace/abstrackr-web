'''    
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
    base_learner.py
    --
    This module contains the BaseLearner class, which you can subclass  to implement your own 
    (pool-based) active learning strategy. BaseLearner itself can not be used directly.
'''

import pdb
import os
import sys
import random
import math
import dataset 
import numpy

class BaseLearner(object):
    '''
    Base learner class. Sub-class this object to implement your own learning strategy. 
    
    Reiterating the comment in curious_snake.py, Curious Snake was originally written for a scenario in which multiple feature spaces
    were being exploited, thus pluralizing may of the attributes in this class. For example, 
    *lists* of unlabeled_datasets and models are kept. If you only have one feature space that you're interested
     in, as is often the case, simply pass around unary lists.  
    ''' 
    
    def __init__(self, unlabeled_datasets = None, models = None, undersample_before_eval = False):
        '''
        unlabeled_datasets should be either (1) a string pointing to a single data file (e.g., "mydata.txt") or (2) a list of strings
        pointing to multiple data files that represent the same data with different feature spaces. For more on the data format,
        consult the doc or see the samples.        
        '''
        if isinstance(unlabeled_datasets, str):
            # then a string, presumably pointing to a single data file, was passed in
            unlabeled_datasets  = [unlabeled_datasets]
            
        self.unlabeled_datasets = unlabeled_datasets or []
        # initialize empty labeled datasets (i.e., all data is unlabeled to begin with)
        # note that we give the labeled dataset the same name as the corresponding
        # unlabeled dataset
        if unlabeled_datasets is not None:
            self.labeled_datasets = [dataset.dataset(name=d.name) for d in unlabeled_datasets]

        self.models = models
        self.undersample_before_eval = undersample_before_eval 
        self.undersample_function = self.undersample_labeled_datasets if undersample_before_eval else None
        
        self.query_function = self.base_q_function # throws exception if not overridden 
        self.name = "Base"
        self.description = ""
        self.longer_name = ""
        
        # default prediction function; only important if you're aggregating multiple feature spaces (see 
        # cautious_predict function documentation)
        self.predict_func = self.at_least
        print "using prediction function: %s" % self.predict_func.__name__
        
        # if this is false, the models will not be rebuilt after each round of active learning
        self.rebuild_models_at_each_iter = True 
        

    
    def active_learn(self, num_examples_to_label, batch_size=5):
        ''''
        Core active learning routine. Here the learner uses its query function to select a number of examples 
        (num_to_label_at_each_iteration) to label at each step, until the total number of examples requested 
        (num_examples_to_label) has been labeled. The models will be updated at each iteration.
        '''
        labeled_ids = []
        labeled_so_far = 0
        while labeled_so_far < num_examples_to_label:
            example_ids_to_label = self.query_function(batch_size)
            # now remove the selected examples from the unlabeled sets and put them in the labeled sets.
            # if not ids are returned -- ie., if a void query_function is used --
            # it is assumed the query function took care of labeling the examples selected. 
            if example_ids_to_label:
                self.label_instances_in_all_datasets(example_ids_to_label)
                labeled_ids.extend(example_ids_to_label)
                
            if self.rebuild_models_at_each_iter:
                self.rebuild_models(for_eval=False)   

            labeled_so_far += batch_size
            
        self.rebuild_models()
        return labeled_ids # in case you want to know which instances were selected.
    
    def predict(self, x_id=None, n=1, X=None):
        ''' 
        This defines how we will predict labels for new examples. We first 
        check to make sure we have sufficient representation for
        X, e.g., if there is no abstract we're probably not confident. If there is,
        we return whatever the current aggregation function is for X.
        If X
        '''
        if X is None and x_id is None:
            raise Exception, "Neither an id nor a vector for X was provided!"
        elif X is None:
            X = self.points_for_x(x_id)
            
        if len([x for x in X if len(x.keys())==0]) > n:
            print "[predict] insufficient representation of x! returning +"
            return 1

        return self.predict_func(X)
        
        
    def at_least(self, X, n=1):
        '''
        Predict 1 if at least n views predict 1.
        '''
        votes = self._votes_for_X(X)
        if votes.count(1) >= n:
            return 1
        return -1        

    def unanimous(self, X):
        votes = self._votes_for_X(X)
        if min(votes) == 1.0:
            return 1
        return -1
        
    def at_least_noisy(self, X, id, n=1):
        votes = self._noisy_votes_for_X(X, 250, id)
        if votes.count(1) >= n:
            return 1
        return -1    
        

    def noisy_predict(self, X, id):
        if self.models and len(self.models) > 0:
            votes = self._noisy_votes_for_X(X, 250, id)
            # the sort ensures that tie goes to the + class
            vote_set = sorted(list(set(votes)), reverse=True)
            count_in_list = lambda x: votes.count(x)
            
            majority_vote = vote_set[_arg_max(vote_set, count_in_list)]
            return majority_vote
        else:
            raise Exception, "No models have been initialized."       
        
    def _noisy_votes_for_X(self, X, i, id):
        votes = []
        f_i= 0
        for m,x in zip(self.models, X):
            if id==4179:
                pdb.set_trace()
            votes.append(m.predict(x))
            f_i+=1
        return votes
        
        
    def majority_predict(self, X):
        '''
        If there are multiple models built over different feature spaces, this predicts a label for an instance based on the
        majority vote of these classifiers -- otherwise this is simply "predict"
        '''
        if self.models and len(self.models) > 0:
            votes = self._votes_for_X(X)
            # the sort ensures that tie goes to the + class
            vote_set = sorted(list(set(votes)), reverse=True)
            count_in_list = lambda x: votes.count(x)
            
            majority_vote = vote_set[_arg_max(vote_set, count_in_list)]
            #print "majority vote: %s" % majority_vote
            return majority_vote
        else:
            raise Exception, "No models have been initialized."

    def _votes_for_X(self, X):
        votes = []
        for m,x in zip(self.models, X):
            votes.append(m.predict(x))
        return votes
        
    def points_for_x(self, x_id):
        return [d.get_point_for_id(x_id) for d in self.unlabeled_datasets]
        
    def cautious_predict(self, X):
        '''
        A naive way of combining different models (built over different feature-spaces); if any othe models vote yes, then vote yes.
        When there is only on feature space, this reduces to simply "predict".
        '''            
        if self.models and len(self.models):
            return max([m.predict(x) for m,x in zip(self.models, X)])
        else:
            raise Exception, "No models have been initialized."
                
    def base_q_function(self, k):
        ''' overwite this method with query function of choice (e.g., SIMPLE) '''
        raise Exception, "no query function provided!"

                                 
    def label_all_data(self):
        '''
        Labels all the examples in the training set
        '''
        inst_ids = [inst.id for inst in self.unlabeled_datasets[0].instances.values()]
        self.label_instances_in_all_datasets(inst_ids)
        
        
    def label_instances(self, inst_ids):
        self.label_instances_in_all_datasets(inst_ids)
        
    def label_instances_in_all_datasets(self, inst_ids):
        '''
        Removes the instances in inst_ids (a list of instance numbers to 'label') from the unlabeled dataset(s) and places
        them in the labeled dataset(s). These will subsequently be used in training models, thus this simulates 'labeling'
        the instances.
        '''
        for unlabeled_dataset, labeled_dataset in zip(self.unlabeled_datasets, self.labeled_datasets):
            labeled_dataset.add_instances(unlabeled_dataset.remove_instances(inst_ids))  
    

    def pick_balanced_initial_training_set(self, k):
        '''
        Picks k + and k - examples at random for bootstrap set.
        '''
        minority_ids_to_label = self.unlabeled_datasets[0].pick_random_minority_instances(k)
        majority_ids_to_label = self.unlabeled_datasets[0].pick_random_majority_instances(k)
        all_ids_to_label = [inst.id for inst in minority_ids_to_label + majority_ids_to_label]
        #self.label_instances_in_all_datasets(all_ids_to_label)
        return all_ids_to_label
        
        
    def undersample_labeled_datasets(self, k=None, undersample_these=None):
        '''
        Returns undersampled copies of the current labeled datasets, i.e., copies in which
        the two classes have equal size. Note that this methods returns a *copy* of the 
        undersampled datasets. Thus it *does not mutate the labeled datasets*.
        
        TODO probably it would be advantagous to undersample different instances
                from different views. this would require undersample_these to be a list
                of lists; one per view, indicating which instances should be undersampled
                in each view.
        '''
        if self.labeled_datasets and len(self.labeled_datasets) and (len(self.labeled_datasets[0].instances) > 0):
            if undersample_these is not None:
               k = len(undersample_these)
               print "undersampling %s examples, which were passed in"  % k
            elif not k:
                print "undersampling majority class to equal that of the minority examples"
                # we have to include 'false' minorities -- i.e., instances we've assumed are positives -- because otherwise we'd be cheating
                k = self.labeled_datasets[0].number_of_majority_examples() - self.labeled_datasets[0].number_of_minority_examples()
                
            # we copy the datasets rather than mutate the class members.
            copied_datasets = [d.copy() for d in self.labeled_datasets]
            if k < self.labeled_datasets[0].number_of_majority_examples() and k > 0:
                # make sure we have enough majority examples...
                print "removing %s majority instances. there are %s total majority examples in the dataset." % \
                        (k, self.labeled_datasets[0].number_of_majority_examples())
                
                removed_instance_ids = undersample_these
                start_at = 0
                if undersample_these is None:
                    removed_instance_ids = copied_datasets[0].undersample(k)
                    start_at = 1 # we've already undersampled from the 0th dataset, in this case
                
                # if there is more than one feature-space, remove the same instances from the remaining spaces (sets)
                for labeled_dataset in copied_datasets[start_at:]:
                    # now remove them from the corresponding sets
                    labeled_dataset.remove_instances(removed_instance_ids)
        else:
            raise Exception, "No labeled data has been provided!"   
        return copied_datasets
    

    def get_random_unlabeled_ids(self, k):
        ''' Returns a random set of k instance ids ''' 
        return random.sample(self.unlabeled_datasets[0].get_instance_ids(), k)

    def get_unlabeled_ids(self):
        return self.unlabeled_datasets[0].get_instance_ids()
        
    def rebuild_models(self, for_eval=False):
        raise Exception, "No models provided! (BaseLearner)"

    def write_out_labeled_data(self, path, dindex=0):
        outf = open(path, 'w')
        outf.write(self.labeled_datasets[dindex].get_points_str())
        outf.close()

    def unlabel_instances(self, inst_ids):
        # remove the instances and place them into the unlabeled set
        for unlabeled_dataset, labeled_dataset in zip(self.unlabeled_datasets, self.labeled_datasets):
            unlabeled_dataset.add_instances(labeled_dataset.remove_instances(inst_ids))

def _arg_max(ls, f):
    ''' Returns the index for x in ls for which f(x) is maximal w.r.t. the rest of the list '''
    return_index = 0
    max_val = f(ls[0])
    for i in range(len(ls)-1):
        adjusted_i = i+1
        if f(ls[adjusted_i]) > max_val:
            return_index = adjusted_i
            max_val = f(ls[adjusted_i])
    return return_index

        