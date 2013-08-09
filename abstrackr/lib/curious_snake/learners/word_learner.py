import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import random
import networkx as nx

class WordLearner(SimpleLearner):
        def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False):
            #
            # call the SimpleLearner constructor to initialize various globals
            SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                    undersample_before_eval = undersample_before_eval)
                                                    
       
            self.uncovered_vertices = None
            self.query_function = self.pick_highest_scoring_nodes#self.pick_central_nodes
            self.observed_words = {}
            self.unobserved_score = 1.0
            
            #print "INVERSE: %s" % inverse
            print "Graph Learner: changing query function to %s" % self.query_function.__name__
     
            
        def pick_highest_scoring_nodes(self, k):            
            print "\npicking highest scoring nodes."
            if self.G is None:
                self.build_graph()
                self.uncovered_vertices = self.G.nodes()
                
            uncolored_nodes = [node for node in self.G.nodes_iter() if not node.is_colored]
            
            if len(self.labeled_datasets[0]) < 25:
                print "less < 25 labels; returning most connected nodes instead"
                centralities = dict(zip(uncolored_nodes, 
                                            [nx.degree_centrality(self.G, v=uncolored_node) for uncolored_node in uncolored_nodes]))

                top_k = dict(centralities.items()[:k])
                min_max_node, min_max_score = self.get_top_node_and_score(top_k)
                for node, centrality in centralities.items()[5:]:
                    if centrality > min_max_score:
                        # recalculate the current min-max node
                        top_k.pop(min_max_node)    
                        top_k[node] = centrality
                        min_max_node, min_max_score = self.get_top_node_and_score(top_k)              
                        
                for node in top_k.keys():
                    node.is_colored = True
                    for w in node.point.keys():
                        if not self.observed_words.has_key(w) or self.observed_words[w] is None:
                            self.observed_words[w] = [node.label]
                        else:
                            self.observed_words[w].append(node.label)
                return [node.id for node in top_k.keys()]
            
            min_max_score, min_max_node = -10000000000, None
            top_k = {}
            #nodes = random.sample(self.G.nodes(), 500)
            

            nodes = random.sample(uncolored_nodes, 50)
            print "iterating over nodes..."
            for node in nodes:
                # (ignore already labeled nodes)
                if not node.is_colored:
                    if len(top_k) < k:
                        top_k[node] = self.score_node(node)
                        min_max_node, min_max_score = self.get_top_node_and_score(top_k)
                    else:
                        print "scoring node..."
                        cur_score = self.score_node(node)
                        print "cur score: %s, true label: %s" % (cur_score, node.label)
                        if cur_score > min_max_score:
                            top_k.pop(min_max_node)
                            top_k[node] = cur_score
                            min_max_node, min_max_score = self.get_top_node_and_score(top_k)
            print "iterated over all nodes."
            selected_nodes = top_k.keys()
            for node in selected_nodes:
                node.is_colored = True
                # since we're going to label these next, reveal the
                # label now and add it to the respective +/- accounts
                # for each word/edge incident to the labeled examples
                for w in node.point.keys():
                    if not self.observed_words.has_key(w) or self.observed_words[w] is None:
                        self.observed_words[w] = [node.label]
                    else:
                        self.observed_words[w].append(node.label)
                
            return [node.id for node in selected_nodes]