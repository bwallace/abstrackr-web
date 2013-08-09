import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import random
import igraph
import pickle

#######################################################
# @TODO should really implement a generalized          #
# CollectiveLearner and subclass... redundancies...   #  
#######################################################        
class CollectiveAuthorLearner(SimpleLearner):
        def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False, inverse=False, \
                        ids_to_groups_path=None, xml_path=None):
                        
            # we're assuming that the graph in the xml path connects nodes (articles)
            # iff they are authored by the same group
            if xml_path is None:
                raise Exception, "GraphLearner -- no graph (xml) provided!!!"
            
            #
            # call the SimpleLearner constructor to initialize various globals
            SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                    undersample_before_eval = undersample_before_eval)
                                                    
            self.G = igraph.Graph.Read_GraphML(xml_path)            
            self.max_feature_index = self._max_feature_index()
            self.ids_to_groups = pickle.load(open(ids_to_groups_path))
            self.gid_to_id = {}
            self._gindex_to_id()
            # normalizer for distance
            #self.z = float(max(self.G.es["weight"]))
            self.name = "author_collective_learner"
            
    
            
        def augment_fvs(self, use_predicted=False):
            O = self.G.vs
            labeled_set = [v for v in O if self.labeled_datasets[0].\
                                instances.has_key(v['ids'])]
            labeled_negs = [v['ids'] for v in labeled_set if v['label'] < 0]
            labeled_pos = [v['ids'] for v in labeled_set if v['label'] > 0]
            
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
                
                num_neighbors = float(len(neighbors))
                
                '''
                ## for research
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
                '''        
                
                n_pos, n_neg = 0, 0
                pos_weight, neg_weight = 0.0, 0.0
                for v_index in neighbors:
                    v_id = self.gid_to_id[v_index]
                    
                    ###
                    # previously we were doing euclidean distance over communities;
                    # now we just have binary links, 1 if papers share an author,
                    # 0 otherwise
                    #edge_weight = self.G.es[self.G.get_eid(x.index, v_index)]["weight"]
                    # edge weight was Euclidean distance; we want this to be 
                    # high (strongly connected) when the distance is small and
                    # vice versa
                    #edge_weight = 1.0 - edge_weight/self.z
                    if v_id in labeled_negs:
                        n_neg += 1
                        #neg_weight += edge_weight
                    elif v_id in labeled_pos:
                        n_pos += 1
                        #pos_weight += edge_weight
                    elif use_predicted:
                        # then this example wasn't labeled, but we want
                        # to use predicted labels, so do that here
                        prediction = self.predict(v_id)
                        if prediction > 0:
                            n_pos += 1
                            #pos_weight += edge_weight
                        else:
                            n_neg += 1
                            #neg_weight += edge_weight
                
                if x_id not in self.labeled_datasets[0].instances.keys() and x_id not in self.unlabeled_datasets[0].instances.keys():
                    pdb.set_trace()
                    
                if x_id in self.labeled_datasets[0].instances.keys():
                    self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+1] = n_pos/max(num_neighbors, 1.0)
                    #self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+1] = pos_weight/max(num_neighbors, 1.0)
                
                    self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+2] = n_neg/max(num_neighbors, 1.0)
                    #self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+2] = neg_weight/max(num_neighbors, 1.0)
                    
                     # also append the group id
                    #self.labeled_datasets[0].instances[x_id].point[self.max_feature_index+3+self.ids_to_groups[x_id]] = 1.0
                else:
                    # unlabeled
                    self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+1] = n_pos/max(num_neighbors, 1.0)
                    #self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+1] = pos_weight/max(num_neighbors, 1.0)
                    
                    self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+2] = n_neg/max(num_neighbors, 1.0)
                    #self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+2] = neg_weight/max(num_neighbors, 1.0)
                    
                    #self.unlabeled_datasets[0].instances[x_id].point[self.max_feature_index+3+self.ids_to_groups[x_id]] = 1.0
               
        
                
            #pos_avg_num_neighbors = pos_avg_num_neighbors/float(pos_count)
            #all_avg_num_neighbors = all_avg_num_neighbors/float(len(self.G.vs))
            #pdb.set_trace()
                            
        def _gindex_to_id(self):
            for v in self.G.vs:
                self.gid_to_id[v.index] = v['ids']
            
            
        def _max_feature_index(self):
            max_index = 0
            for x in self.unlabeled_datasets[0].instances.values():
                if len(x.point.keys()) > 0:
                    max_index = max(max_index, max(x.point.keys()))
            return max_index
            
        def ICA_train(self, iters=25):
            # this is just using the BOW 
            self.rebuild_models(for_eval=True)
            
            # label initial / boostrap
            self.augment_fvs(use_predicted=False)
        
            for i in range(iters):
                print "\nICA -- on iteration %s" % i
                self.augment_fvs(use_predicted=True)
                self.rebuild_models(for_eval=True)
     
  
            