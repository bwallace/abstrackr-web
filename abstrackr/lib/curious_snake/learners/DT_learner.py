'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	DC_learner.py
	---
	
    Our DT learning strategy 
    
'''

import pdb
import random
import base_svm_learner
from base_svm_learner import BaseSVMLearner
from base_svm_learner import *


class DTSVMLearner(BaseSVMLearner):
    
    def __init__(self, unlabeled_datasets = [], experts=None,
                         models=None, undersample_before_eval = False, request_path=None):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)


        #
        # most importantly we change the query function to SIMPLE here
        #
        self.query_function = self.DT

        
    def DT(self, k):
        '''
        Implements our decision-theoretic approach
        '''
        pass
        
