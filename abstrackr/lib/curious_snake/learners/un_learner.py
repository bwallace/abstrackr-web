import pdb
import simple_svm_learner
from simple_svm_learner import *
import math

class UnLearner(SimpleLearner):
    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)
                                                
        self.e_dict = {}
        self.e_max = None
        self.h_max = None
        self.name = "UN"
        self.query_function = self.un
        
    def un(self, k):        
        self.e_max = self.get_e_max()
        print "e max %s" % self.e_max
        self.dh_max = self._max_dists_to_hyperplanes()[0]
        print "\n\ndh_max is: %s\n"  % self.dh_max
        
        U = self.unlabeled_datasets[0]
        
        min_max_score, min_max_inst = -10000000000, None
        top_k = {}
        
        for inst in U.instances.values():
            cur_score = self.score_inst(inst)
            #print "cur score: %s, true label: %s" % (cur_score, inst.label)
            if len(top_k) < k:
                top_k[inst] = cur_score
                min_max_inst, min_max_score = self.get_top_node_and_score(top_k)
            elif cur_score > min_max_score:
                top_k.pop(min_max_inst)
                top_k[inst] = cur_score
                print "new top score! %s" % cur_score
                min_max_inst, min_max_score = self.get_top_node_and_score(top_k)
                
        
        selected_instances = top_k.keys()
        return [inst.id for inst in selected_instances]
        
        
    def score_inst(self, inst):
        d_h = self.models[0].distance_to_hyperplane(inst.point, signed=True)
        d_h = d_h/self.dh_max
        #e = self.e_dict[inst.id]
        e = self.e_dict[inst.id]
        #return (e/self.e_max + (1-d_h/self.dh_max))/2.0
        #print "e is: %s, d_h is: %s; total score is: %s" % (e, d_h, ((1.0-e) + (1.0-d_h/self.dh_max))/2.0)
        #return ((1.0-e) + (1.0-d_h))/2.0
        #print "1-e: %s. d_h: %s\n" % (1-e, d_h)
        #return max(1.0-e, 1.0-d_h)
        return max(1-0-e, d_h)
        #return 1-e
        
    def get_e_max(self):
        self.e_dict = {}
        e_max = 0
        for x_u in self.unlabeled_datasets[0].instances.values():
            for x_l in self.labeled_datasets[0].instances.values():
                cur_e = self._compute_cos(0, x_u, x_l)
                if not x_u.id in self.e_dict:
                    self.e_dict[x_u.id] = cur_e
                elif cur_e > self.e_dict[x_u.id]:
                    self.e_dict[x_u.id] = cur_e
                    
                if  cur_e > e_max:
                    e_max = cur_e
        return e_max
        
    def get_top_node_and_score(self, top_k):
        min_max_score = -10000000000
        min_max_node = None
        for top_node, score in top_k.items():
            if score > min_max_score:
                min_max_score = score
                min_max_node = top_node   

        return (min_max_node, min_max_score)
        
        