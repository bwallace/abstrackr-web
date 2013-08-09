import pdb
import base_svm_learner
from base_svm_learner import *
import math
import random

class TermLearner(BaseSVMLearner):

    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False, normalize=True):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)
                                                    
            
        self.query_function = self.term_select
        self.observed_words = {}
        self.normalize = normalize
        self.unobserved_score = 1.0
        self.term_counts = {}
        self.setup_term_counts()
        print "Term Learner: changing query function to %s" % self.query_function.__name__
     
            
    def term_select(self, k):            
        print "picking highest scoring examples..."
        
        min_max_score, min_max_inst = -10000000000, None
        top_k = {}
        U = self.unlabeled_datasets[0]
        
        for inst in U.instances.values():
            cur_score = self.score_inst(inst, normalize=self.normalize)
            #print "cur score: %s, true label: %s" % (cur_score, inst.label)
            if len(top_k) < k:
                top_k[inst] = cur_score
                min_max_inst, min_max_score = self.get_top_node_and_score(top_k)
            elif cur_score > min_max_score:
                top_k.pop(min_max_inst)
                top_k[inst] = cur_score
                min_max_inst, min_max_score = self.get_top_node_and_score(top_k)
            
        print "done. now adding counts to observed terms.."
        selected_instances = top_k.keys()
        for inst in selected_instances:
            for term in inst.point.keys():
                if self.observed_words[term] is None:
                    self.observed_words[term] = [inst]
                else:
                    self.observed_words[term].append(inst)

        return [inst.id for inst in selected_instances]
            
        
    def score_inst(self, inst, normalize=True):
        cur_score = 0.0
        if len(inst.point)==0:
            return cur_score
            
        for term in inst.point.keys():
            if self.observed_words[term] is None:
                # this term hasn't yet been observed in a labeled instance
                cur_score += self.unobserved_score
            else:
                pos_instances = [p_inst for p_inst in self.observed_words[term] if p_inst.label > 0.0]
                total_observed = float(len(self.observed_words[term]))
                p = float(len(pos_instances))/total_observed
                # weight according to the fraction of the terms we've observed
                w = total_observed / self.term_counts[term]
                # if w is high, we've observed most of the examples with this term; if it is
                # low, we have observed a small fraction of instances with this word. in the
                # latter case we want a higher score, because this means we're uncertain
                # about the term; whereas in the former case we want a lower score
                # because we're more certain in this term, so it's less important that we
                # query for examples with it
                cur_score += w * p
                
        if normalize:
            cur_score = cur_score / float(len(inst.point))
        return cur_score
        

    def get_top_node_and_score(self, top_k):
        min_max_score = -10000000000
        min_max_node = None
        for top_node, score in top_k.items():
            if score > min_max_score:
                min_max_score = score
                min_max_node = top_node   

        return (min_max_node, min_max_score)
                
    def setup_term_counts(self):
        print "\nsetting up term counts..."
        U = self.unlabeled_datasets[0]
        #pdb.set_trace()
        for inst in U.instances.values():
            for term in inst.point.keys():
                self.observed_words[term] = None
                self.term_counts[term]=0.0
                
        for inst in U.instances.values():
            for term in inst.point.keys():
                self.term_counts[term]+=1.0
                
        print "done."


                