#!/usr/bin/env python
# encoding: utf-8
'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis (tuftscaes.org)
	pooling multinomials
	---
    
	Pooling multionomials model, from Melville et al., 2009
'''


import pdb
import random
import base_nb_learner
from base_nb_learner import *
import math
import os
from operator import itemgetter

class PMLearner(BaseNBLearner):
        def __init__(self, pos_f_ids_file, neg_f_ids_file, m, unlabeled_datasets = None, \
                           undersample_before_eval = False, r=100, pc=.5):
            #
            # call the SimpleLearner constructor to initialize various globals
            BaseNBLearner.__init__(self, unlabeled_datasets=unlabeled_datasets)
            self.undersample_before_eval = undersample_before_eval
            self.name = "pooling"
            print "assuming pc is %s!!!" % pc
            self.pc = pc

            # read
            print "we are assuming that we are given *indices* of pos/neg features!"
            self.pos_feature_ids = eval(open(pos_f_ids_file, 'r').readline())#[:100]
            self.neg_feature_ids = eval(open(neg_f_ids_file, 'r').readline())#[:100]
            
            # this will be a vector with two entries weighting
            # the `feature' and `standard' models -- will need to 
            # sum to 1. see Section 3.1.
            self.alphas = [.5, .5]
            
            
            # for memoization
            self.texts = {}
            self.feature_votes={}
            self.feature_scores={}
            
            self.m = m # vocab (feature-space) size
            self.np= None
            self.pp= None
            
            self.r = r
           
            
        def rebuild_models(self, for_eval=True, compute_ps=True, recompute_alphas=True):
            ''' Rebuilds all models over the current labeled datasets. '''
            datasets = self.labeled_datasets
            if self.undersample_before_eval and for_eval:
                print "undersampling before building models.."
                datasets = self.undersample_labeled_datasets()
                
            all_train_sets, labels = self._datasets_to_matrices(datasets)
            self.models = [NB_Model(naive_bayes.train(training_set, labels)) for training_set in all_train_sets]
            
            ## also recompute_ps! 
            if compute_ps:
                self.compute_ps()
            
            if recompute_alphas:
                self.compute_alphas()

        def compute_ps(self):
            ''' Melville et al., 2009, Section 3.1 '''
            p = float(len(self.pos_feature_ids))
            n = float(len(self.neg_feature_ids))
   
            self.pp = 1.0/float(p + n)
            self.pn = 1.0/float(p + n)

            # probability of a positive term appearing in a negative doc
            self.p_given_n = self.pp * 1/self.r
            # and vice versa
            self.n_given_p = self.pn * 1/self.r


            self.alpha_n = 1/float(n)
            self.alpha_p = 1/float(p)

            self.pp_unknown = (n*(1-1/self.r))/ ((p + n) * (self.m-p-n))
            self.pn_unknown = (p*(1-1/self.r))/ ((p + n) * (self.m-p-n))
            
            
            
        def compute_alphas(self):
            '''
            compute the alphas over the training data.
            
            @returns alpha_0, alpha_1; the first corresponds
            to the standard NB model, the second to the
            background/lexical model.
            '''
            mistakes_nb = 1 # psuedo counts
            mistakes_lexical = 1 
            
            nfolds = 2.0
            fold_size = int((1.0/nfolds)*len(self.labeled_datasets[0]))
            list_of_ids = self.labeled_datasets[0].instances.keys()
            random.shuffle(list_of_ids)
            list_of_test_instance_ids = [l for l in chunks([x_id for x_id in list_of_ids], fold_size)]
            
            for i, test_instance_ids in enumerate(list_of_test_instance_ids):
                print "alpha estimation: on fold %s" % i
                self.unlabel_instances(test_instance_ids)
                self.rebuild_models(for_eval=True, compute_ps=False, recompute_alphas=False)
                for xid in test_instance_ids:
                    # note that this isn't cheating -- this is actually 
                    # a labeled example that we've momentarily unlabeled!
                    x = self.unlabeled_datasets[0].instances[xid]
                    nb_p = self.models[0].predict(x.point)
                    if nb_p != x.label:
                        mistakes_nb += 1
                    
                    bg_probs = self.background_nb(x)
                    bg_p = 1.0 if bg_probs[1.0] > bg_probs[-1.0] else -1.0
                    if bg_p != x.label:
                        mistakes_lexical += 1
                # relabel them
                self.label_instances(test_instance_ids)
            
            # rebuild the model with all data
            self.rebuild_models(for_eval=True, compute_ps=False, recompute_alphas=False)
           
            N = float(len(self.labeled_datasets[0]))
            err_nb = mistakes_nb/N
            err_lexical = mistakes_lexical/N
            alpha_0 = (1.0-err_nb)/err_nb
            alpha_1 = (1.0-err_lexical)-math.log(err_lexical)
            # normalize
            alpha_total = alpha_0 + alpha_1
            self.alphas = [alpha_0/alpha_total, alpha_1/alpha_total]
            print "\n\n--- alphas --- %s" % self.alphas
            
        def count_features(self, x_dict, feature_ids):
            return len([fid for fid in x_dict.keys() if fid in feature_ids])
            
        def predict(self, x):
            if isinstance(x, int) or isinstance(x, str):
                # then try to get the instance from the unlabeled set
                x = self.unlabeled_datasets[0].instances[x]
                
            vanilla_probs = self.models[0].prob_dist(x.point)
            
            bg_probs = self.background_nb(x)
            
            p_pos = self.alphas[0]*vanilla_probs[1.0] + self.alphas[1]*bg_probs[1.0]
            p_neg = self.alphas[0]*vanilla_probs[-1.0] + self.alphas[1]*bg_probs[-1.0]
            
            if p_pos > p_neg:
                return 1.0
            return -1.0
            
        def background_nb(self, x):
            neg_feature_count = self.count_features(x.point, self.neg_feature_ids)
            pos_feature_count  = self.count_features(x.point, self.pos_feature_ids)
            unlabeled_count = len(x.point) - neg_feature_count - pos_feature_count
                     

            p_pos = sum([math.log(self.pp) for w_i in xrange(pos_feature_count)] +\
                                       [math.log(self.n_given_p) for w_i in xrange(neg_feature_count)] +\
                                       [math.log(self.pp_unknown) for w_i in xrange(unlabeled_count)])


            p_neg = sum([math.log(self.pn) for w_i in xrange(neg_feature_count)] +\
                                      [math.log(self.p_given_n) for w_i in xrange(pos_feature_count)] +\
                                      [math.log(self.pn_unknown) for w_i in xrange(unlabeled_count)])
                                      
            return {-1.0:p_neg, 1.0:p_pos}

def chunks(l, n):
    """ 
    yield successive n-sized chunks from l.
    (for cv).
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
