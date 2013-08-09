import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import random
import igraph

class CollectiveLearner(SimpleLearner):
        def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False, inverse=False, \
                        xml_path=None):
            if xml_path is None:
                raise Exception, "GraphLearner -- no graph (xml) provided!!!"
            #
            # call the SimpleLearner constructor to initialize various globals
            SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                    undersample_before_eval = undersample_before_eval)
                                                    
            self.G = igraph.Graph.Read_GraphML(xml_path)
            
            self.max_feature_index = self._max_feature_index()
            self.gid_to_id = {} # map the graph's id to the `true' id
            self._gindex_to_id()
            self.name = "cc_learner"
            
        def augment_fvs(self, use_predicted=False):
            O = self.G.vs
            labeled_set = [v for v in O if self.labeled_datasets[0].\
                                instances.has_key(v['ref_id'])]
            labeled_negs = [v['ref_id'] for v in labeled_set if v['label'] < 0]
            labeled_pos = [v['ref_id'] for v in labeled_set if v['label'] > 0]
            
            max_n_pos, max_n_neg = 0, 0
            pos_num_no_neighbors = 0
            all_num_no_neighbors = 0
            pos_avg_num_neighbors = 0
            all_avg_num_neighbors = 0
            pos_count = 0
            for x in O:
                # now set the features
                x_id = self.gid_to_id[x.index]
                
                neighbors = list(set(self.G.neighbors(x.index)))
                
                if x['label'] > 0:
                    pos_count += 1
                    if len(neighbors) == 0:
                        pos_num_no_neighbors += 1
                        all_num_no_neighbors += 1
                    else:
                        pos_avg_num_neighbors += len(neighbors)
                        all_avg_num_neighbors += len(neighbors)
                else:
                        if len(neighbors) == 0:
                            all_num_no_neighbors += 1
                        else:
                            all_avg_num_neighbors += len(neighbors)
                        
                n_pos, n_neg = 0, 0
                for v_index in neighbors:
                    v_id = self.gid_to_id[v_index]
                    if v_id in labeled_negs:
                        n_neg += 1
                    elif v_id in labeled_pos:
                        n_pos += 1
                    elif use_predicted:
                        # then this example wasn't labeled, but we want
                        # to use predicted labels, so do that here
                        prediction = self.predict(v_id)
                        if prediction > 0:
                            n_pos += 1
                        else:
                            n_neg += 1
                
                if x_id in self.labeled_datasets[0].instances.keys():
                    self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+1] = n_pos
                    self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+2] = n_neg
                else:
                    # unlabeled
                    self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+1] = n_pos
                    self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+2] = n_neg
            pos_avg_num_neighbors = pos_avg_num_neighbors/float(pos_count)
            all_avg_num_neighbors = all_avg_num_neighbors/float(len(self.G.vs))
         
                            
        def _gindex_to_id(self):
            for v in self.G.vs:
                self.gid_to_id[v.index] = v['ref_id']
            
            
        def _max_feature_index(self):
            max_index = 0
            for x in self.unlabeled_datasets[0].instances.values():
                if len(x.point.keys()) > 0:
                    max_index = max(max_index, max(x.point.keys()))
            return max_index
            
        def ICA_train(self, iters=500):
            # this is just using the BOW 
            self.rebuild_models(for_eval=True)
            
            # label initial / boostrap
            self.augment_fvs(use_predicted=False)
        
            for i in range(iters):
                print "\nICA -- on iteration %s" % i
                self.augment_fvs(use_predicted=True)
                self.rebuild_models(for_eval=True)
     
  
            