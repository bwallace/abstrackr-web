'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	simple_svm_learner.py
	---
	
	Implements the SIMPLE active learning strategy (Tong and Koller). 
	
	Uses (a modified version of) the libsvm library, Copyright (c) 2000-2008 
	Chih-Chung Chang and Chih-Jen Lin. 

'''

import pdb
import random
import base_svm_learner
from base_svm_learner import BaseSVMLearner
from base_svm_learner import *

class SimpleLearner(BaseSVMLearner):
    
    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False, kernel_type=LINEAR, svm_params=None):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval, kernel_type=kernel_type,
                                                svm_params=svm_params)


        #
        # most importantly we change the query function to SIMPLE here
        #
        print "switching query function to SIMPLE!"
        self.query_function = self.SIMPLE
        self.name = "SIMPLE"
        
        
    def SIMPLE(self, k):
        '''
        Returns the instance numbers for the k unlabeled instances closest the hyperplane.
        '''
        # randomly flip an m-sided coin (m being the number of feature spaces)
        # and pick from this space
        
        feature_space_index = random.randint(0, len(self.models)-1)
        model = self.models[feature_space_index] 
        dataset = self.unlabeled_datasets[feature_space_index]
        return self._SIMPLE(model, dataset, k)
          
        
