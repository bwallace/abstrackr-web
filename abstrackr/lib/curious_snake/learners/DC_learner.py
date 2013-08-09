'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	DC_learner.py
	---
	
    Donmez & Carbonell (DC) model

'''

import pdb
import random
import base_svm_learner
from base_svm_learner import BaseSVMLearner
from base_svm_learner import *

class DCSVMLearner(BaseSVMLearner):
    
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
        
    def DC(self, k):
        '''
        Implements the decision-theoretic strategy proposed by Donmez & Carbonel
        '''
        pass
        
    def density_weighted_uncertainty_score(self, x_id):
        pass