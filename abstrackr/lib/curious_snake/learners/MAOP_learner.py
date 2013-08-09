import pdb
import base_svm_learner
from base_svm_learner import *
import math
import random
import numpy

class MAOPLearner(BaseSVMLearner):

    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False, normalize=True):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)
                                                    
            
        self.query_function = self.maop
        self.observed_words = {}
        self.dimensions = [d.get_dim() for d in self.unlabeled_datasets]
        self.normalize = normalize
        self.unobserved_score = 1.0
        self.term_counts = {}
        self.setup_term_counts()
        self.dimension = len(self.observed_words.keys())
        print "maop learner: changing query function to %s" % self.query_function.__name__
        print "dimension: %s" % self.dimension
        self.name = "MAOP"
        self.beta = 1.0
            
    def maop(self, k):            
        print "(maop)"
        # coin flip
        #m_index = random.randint(0, len(self.models)-1)
        min_max_score, min_max_inst = -10000000000, None
        top_k = {}
        
        unobserved_w = 0
        for w in self.observed_words.keys():
            if self.observed_words[w] is None:
                unobserved_w+=1
        
            
            
        U = self.unlabeled_datasets[0]
        
        
        # @TODO this is stupidly inefficient
        max_orth = 0
        for inst in U.instances.values():
            orth_score, k_val = self.score_inst(inst)
            max_orth = max(max_orth, orth_score)
                
        for inst in U.instances.values():
            orth_score, k_val = self.score_inst(inst)
            if self.normalize and max_orth>0:
                orth_score = orth_score / max_orth
            cur_score = (orth_score + k_val)/2.0
            #print "cur score: %s, true label: %s" % (cur_score, inst.label)
            if len(top_k) < k:
                top_k[inst] = cur_score
                min_max_inst, min_max_score = self.get_top_node_and_score(top_k)
            elif cur_score > min_max_score:
                top_k.pop(min_max_inst)
                top_k[inst] = cur_score
                print "new top score! %s" % cur_score
                min_max_inst, min_max_score = self.get_top_node_and_score(top_k)
        print "max orth: %s" % max_orth
        print "done. now adding counts to observed terms.."
        selected_instances = top_k.keys()
        unobserved_w = 0
        for inst in selected_instances:
            for term in inst.point.keys():
                if self.observed_words[term] is None:
                    self.observed_words[term] = [inst]
                    unobserved_w = True
                else:
                    self.observed_words[term].append(inst)
        

        
        print "\n\nunobserved word count: %s\nbeta is: %s\n\n" % (unobserved_w, self.beta)
        return [inst.id for inst in selected_instances]
            
        
    def score_inst(self, inst, m_index=0):
      
        k_val = self.models[m_index].distance_to_hyperplane(inst.point, signed=True)
        
        if len(inst.point)==0:
            return (0, k_val)
    
        orth_score = 0.0
        for term in inst.point.keys():
            if self.observed_words[term] is None:
                # this term hasn't yet been observed in a labeled instance
                orth_score += 1.0
                
        # if normalize:
        #    orth_score =orth_score / float(self.dimensions[m_index])
        
        return (orth_score, k_val)
        

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


                