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

class FakeSVMLearner(BaseSVMLearner):
    
    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False, request_path=None):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)


        #
        # most importantly we change the query function to SIMPLE here
        #
        self.query_function = self.faker
        self.name ="FAKER"
        self.get_these = eval(open(request_path, 'r').readline())
        #pdb.set_trace()
        
    def faker(self, k):
        '''
        Returns the instance numbers for the k unlabeled instances closest the hyperplane.
        '''
        # randomly flip an m-sided coin (m being the number of feature spaces)
        # and pick from this space
        ask_for = self.get_these[:k]
        for x_id in ask_for:
            self.get_these.remove(x_id)
            
        #pdb.set_trace()
        #if 1647 in ask_for:
        #    pdb.set_trace()
        return ask_for