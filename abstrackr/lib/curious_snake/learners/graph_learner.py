import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import random
import networkx as nx

class GraphLearner(SimpleLearner):
        def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False, inverse=False):
            #
            # call the SimpleLearner constructor to initialize various globals
            SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                    undersample_before_eval = undersample_before_eval)
                                                    
            self.G = None
            self.inverse = inverse
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
            
        
        def score_node(self, node, normalize=True):
            cur_score = 0.0
            e_count = 0
            for nn in self.G.neighbors_iter(node):
                for edge in self.G.edges_iter(nbunch=[node, nn], data=True):
                    e_count += 1
                    cur_w = edge[-1].values()[0]
                    
                    if self.observed_words[cur_w] is None:
                        cur_score += self.unobserved_score
                    else:
                        observations = self.observed_words[cur_w]
                        n_pos = len([x for x in observations if x > 0])
                        N = float(len(observations))
                        p_pos = float(n_pos)/N
                        n_pos = (N-p_pos)/N
                        cur_score += p_pos - n_pos
                        
            if normalize:
                if cur_score == 0:
                    return cur_score 
                else:
                    return cur_score / float(e_count)
            else:
                return cur_score
            
        def pick_central_nodes(self, k):
            inverse = self.inverse
            if self.G is None:
                self.build_graph()
                self.uncovered_vertices = self.G.nodes()
                
            for node in self.G.nodes():
                if node.id in self.labeled_datasets[0].instances.keys():
                    print "pick central. problem."
                    pdb.set_trace()
                    
            if not inverse:
                print "\nfinding most central nodes.."
            else:
                print "\nfinding *least* central nodes."
            centralities = nx.degree_centrality(self.G)
            # now filter out covered nodes
            '''
            centrality_d = {}
            uncovered_ids = [uncovered_node.id for uncovered_node in self.uncovered_vertices]
            for node,val in centralities.items():
                if node.id in uncovered_ids:
                    centrality_d[node] = val

            centralities = centrality_d
            '''
            
            top_k = dict(centralities.items()[:k])
            min_max_node, min_max_score = self.get_top_node_and_score(top_k, inverse)
            for node, centrality in centralities.items()[5:]:
                if (centrality > min_max_score and not inverse) or \
                    (centrality < min_max_score and inverse):
                    # recalculate the current min-max node
                    try:
                        top_k.pop(min_max_node)
                    except:
                        print "whoops"
                        pdb.set_trace()
                        
                    top_k[node] = centrality
                    if len(top_k) > k:
                        print "whoops; returning more instances than asked for."
                        pdb.set_trace()
                    min_max_node, min_max_score = self.get_top_node_and_score(top_k, inverse)

            # now denote 
            
            print "ok. max score: %s. removing from graph..." % max(top_k.values())               
            for node in top_k.keys():
                for neighbor in self.G.neighbors(node):
                    if neighbor in self.uncovered_vertices:
                        self.uncovered_vertices.remove(neighbor)
                    if node in self.uncovered_vertices:
                        self.uncovered_vertices.remove(node)
                self.G.remove_node(node)
                
            print "done. returning ids. number of uncovered vertices remaining: %s" % len(self.uncovered_vertices)
            label_these = [node.id for node in top_k.keys()]
            for inst_id in label_these:
                if not inst_id in self.unlabeled_datasets[0].instances.keys():
                    print "here you are"
                    pdb.set_trace()
            #if len(self.uncovered_vertices)==0:
            if len(self.labeled_datasets[0]) >= 500:
                self.query_function = self.SIMPLE
            #    pdb.set_trace()
            #    self.query_function = self.SIMPLE
            return label_these
                
            
        def get_top_node_and_score(self, top_k, inverse=False):
            min_max_score = -100000000 if not inverse else 100000000
            min_max_node = None
            for top_node, score in top_k.items():
                if (score > min_max_score and not inverse) or \
                    (score < min_max_score and inverse):
                    min_max_score = score
                    min_max_node = top_node   

            return (min_max_node, min_max_score)
                    
        def build_graph(self):
            print "\nbuilding graph..."
            self.G = nx.MultiGraph()
            d = self.unlabeled_datasets[0]
            # first add the nodes
            for inst in d.instances.values():
                # adding a makeshift property here.
                # ah, python.
                inst.is_colored = False
                self.G.add_node(inst)
            
            print "bookkeeping"
            #
            # to speed things up, keep a list of edges we've
            # already added (in fact we map to the words therein)
            #
            already_added = {}
            for id_1 in d.instances.keys():
                for id_2 in d.instances.keys():
                    already_added[(id_1, id_2)] = []
                    already_added[(id_2, id_1)] = []
            
            # now add edges
            print "ok"
            for inst1_id in d.instances.keys():
                for inst2_id in d.instances.keys():
                    if inst2_id != inst1_id:
                        inst1 = d.instances[inst1_id]
                        inst2 = d.instances[inst2_id]
                        for p1 in inst1.point.keys():
                            for p2 in inst2.point.keys():
                                if p1 == p2:
                                    self.observed_words[p1] = None
                                    e = (inst1, inst2, {"word":p1})
                                    if not p1 in already_added[(inst1_id, inst2_id)]:
                                        self.G.add_edge(e[0], e[1], word=p1)
                                        already_added[(inst1_id, inst2_id)].append(p1)
                                        already_added[(inst2_id, inst1_id)].append(p1)

            #pdb.set_trace()
            print "done."
                
        def already_has_edge(self, e):
            if not self.G.has_edge(e[0], e[1]):
                return False
            edges = self.G.edges(e[0], e[1])
            for edge in edges:
                if e[2]['word'] == edge[2]['word']:
                    return True
            return False
                