import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import random
import numpy
import pylab
import rpy2
from rpy2 import robjects as ro
    
class NLNLearner(SimpleLearner):

    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)
                                                    
            
        print "NLN for the win!"
        self.eps = {}
        self.lambdas = {}
        #self.query_function = self.nln
        self.query_function = self.discordant_distro
        self.name = "NLN"
        self.n = 0
        self.nln_dist = []
        ro.r("library(stats)")


    def discordant_distro(self, k):
        #all_discordant_pairs = self.get_labeled_discordant_pairs()
        #distances_between_pairs = [self._compute_cos(0, x, y) for x,y in all_discordant_pairs]
        distances_between_pairs = self.get_nln_dps()
        pylab.clf()
        n, bins,patches = pylab.hist(distances_between_pairs, 50)
        pylab.savefig("temp/hist_nlndp_%s.png"%str(len(self.labeled_datasets[0])))
        #self.n+=1
        
        if len(self.nln_dist)==0:
            return self.get_random_unlabeled_ids(k)
        
        done= True
        max_min_conf = 1.0
        max_min_id = None
        k_least = {}
        lowers = []
        uppers = []
        total_nln = len(self.nln_dist)
        for x in self.unlabeled_datasets[0].instances.values():
            nn, nn_sim = self.nearest_labeled_neighbor(x)
            #if len(self.labeled_datasets[0]) > 200:
            #    pdb.set_trace()
            n_discordant = len([dist for dist in self.nln_dist if dist > nn_sim])
            score = float(n_discordant)/float(total_nln)
            #print "number discordant: %s" % n_discordant
            lower, upper = ro.r("binom.test(%s, %s)" % (n_discordant , total_nln))[3]
            lowers.append(lower)
            uppers.append(upper)
            #print "score: %s, lower: %s, upper: %s" % (score, lower, upper)
            if len(k_least) < k:
                k_least[x.id] = score
                max_min_id, max_min_conf = self.get_max_node_and_score(k_least)
            elif score < max_min_conf:
                k_least.pop(max_min_id)
                k_least[x.id] = score
                max_min_id, max_min_conf = self.get_max_node_and_score(k_least)     
      
    
        #return k_least.keys()
        #if max(k_least.values()) <= .05:
        #print min(lowers)
        print "max uppers: %s" % max(uppers)
        if max(uppers) < .05:
            pdb.set_trace()
            self.query_function = self.SIMPLE
            
        return self.get_random_unlabeled_ids(k)
        
    def get_labeled_discordant_pairs(self):
        positives = self.labeled_datasets[0].get_minority_examples()
        negatives = self.labeled_datasets[0].get_majority_examples()
        all_pairs = []
        for pos in positives:
            for neg in negatives:
                all_pairs.append((pos, neg))
        return all_pairs
        
        
    def get_nln_dps(self):
        positives = self.labeled_datasets[0].get_minority_examples()
        negatives = self.labeled_datasets[0].get_majority_examples()
        dists_to_ndln=[]
        for pos in positives:
            cur_d = -1
            for neg in negatives:
                d = self._compute_cos(0, pos, neg)
                if d > cur_d:
                    cur_d = d
            dists_to_ndln.append(cur_d)
            self.nln_dist = dists_to_ndln
        return dists_to_ndln
        
    def nln(self, k):
        if len(self.labeled_datasets[0]) < 25:
            return self.get_random_unlabeled_ids(k)
        
        # update epislons, lambdas
        self.compute_nlns()
        ok = True
        
        k_most_uncertain = {}
        max_min_id, max_min_score = None, 1.0
        total_lower, total_p = 0.0, 0.0
        
        # consider/score each unlabeled instance in turn
        for x_u in self.unlabeled_datasets[0].instances.values():
            nln_x, e_x = self.nearest_labeled_neighbor(x_u)
            
            # build a set of labeled examples that are within e_x of their nln
            #L_e = [inst for inst in self.labeled_datasets[0].instances.values() if self.eps[inst.id] >= e_x]
            L_e = [inst for inst in self.labeled_datasets[0].get_minority_examples() if self.eps[inst.id] >= e_x]
            
            # our confidence is a function of the nln. if no labeled examples
            # have a nearest labeled neighbor as far as or further than e_x,
            # we have zero confidence in the current assessment
            confidence = 0.0
            L_e_size = len(L_e)
            
            #print "size: %s" % L_e_size
            
            # if the length is zero, we ignore it, since we classify it as +
            # regardless
            lower = 0.0 if len(x_u.point)!=0 else 1.0
            if L_e_size > 0:
                # otherwise, we treat the probability that the model
                # is correct as a bernoulli random variable
                n_same_labels = sum([self.lambdas[inst.id] for inst in L_e])
                p_hat = float(n_same_labels)/float(L_e_size)
                #samp_error = 1.96 * math.sqrt(p_hat*(1-p_hat)/L_e_size)
                lower, upper = ro.r("binom.test(%s, %s)" % (n_same_labels, L_e_size))[3]
            else:
                p_hat = 0.0
                #pdb.set_trace()
            
            
            #print "lower: %s, p_hat: %s, L_e_size: %s" % (lower, p_hat, L_e_size)
            #print "sampling error: %s" % samp_error
            if len(x_u.point) == 0:
                pass
                #print "ignoring 0 length point!"
            else:
                if lower <= .5:
                    ok = False
                total_lower+=lower
                total_p += p_hat
            

            if len(k_most_uncertain) < k:
                k_most_uncertain[x_u.id] = lower
                # we want to keep track of the highest scoring node id,
                # i.e., the instant we're maximally confident about out of 
                # those we're not confident about
                max_min_id, max_min_score = self.get_max_node_and_score(k_most_uncertain)
            elif lower < max_min_score:
                k_most_uncertain.pop(max_min_id)
                k_most_uncertain[x_u.id] = lower
                max_min_id, max_min_score = self.get_max_node_and_score(k_most_uncertain)                    

                #pdb.set_trace()
        if ok:
            pdb.set_trace()
            self.query_function = self.SIMPLE

        
        print "number of minorities: %s" % len(self.labeled_datasets[0].get_minority_examples())
        N = len(self.unlabeled_datasets[0])
        print "average p, lower @ %s labeled examples: %s, %s" % (len(self.labeled_datasets[0]), total_p/N, total_lower/N )
        #pdb.set_trace()
        #return k_most_uncertain.keys()
        return self.get_random_unlabeled_ids(k)
        
    def get_max_node_and_score(self, top_k):
        max_min_score = -1
        min_max_node = None
        for top_node, score in top_k.items():
            if score > max_min_score:
                max_min_score = score
                max_min_node = top_node   

        return (max_min_node, max_min_score)
       
          
    def compute_nlns(self, pos_only=True):
        #for x_i in self.labeled_datasets[0].instances.values():
        for x_i in self.labeled_datasets[0].get_minority_examples():
            # perhaps get all neighbors within e here
            y, self.eps[x_i.id] = self.nearest_labeled_neighbor(x_i)
            # it's ok; both y and x are in the labeled dataset
            self.lambdas[x_i.id] = 1.0 if y.label == x_i.label else 0.0
            
        
    def nearest_labeled_neighbor(self, x):
        nearest_n = None
        d = -1.0
        for y in self.labeled_datasets[0].instances.values():
            if y.id != x.id:
                cur_d = self._compute_cos(0, x, y)
                if cur_d > d:
                    d = cur_d
                    nearest_n = y
                
        # important: we return 1-d, because the cosine similarity is big (near 1) when
        # things are similar and small (0 or -1, depending on if there are negative valued
        # features) when things are dissimiliar. thus 1-d flips this; a small value implies similariaty,
        # a large value implies dissimiliarity, as is intuitive for distance metrics
        return (nearest_n, 1-d)   
        
    def rcos_sim(self, col_i1, col_i2):
        cos = self.cos_sim(self.col_to_vec(self.P_comp, col_i1).T, self.col_to_vec(self.P_comp, col_i2)).flatten()[0]
        return cos
        
    def _cos_sim(self, col_i1, col_i2):
        # memoize
        if not self.memoized.has_key((col_i1, col_i2)):
            #pdb.set_trace()
            cos = self.cos_sim(self.col_to_vec(self.PX, col_i1).T, self.col_to_vec(self.PX, col_i2)).flatten()[0]
            #cos = self.cos_sim(self.col_to_vec(self.P_comp, col_i1).T, self.col_to_vec(self.P_comp, col_i2)).flatten()[0]
            self.memoized[(col_i1, col_i2)] = cos
            self.memoized[(col_i2, col_i1)] = cos
        return self.memoized[(col_i1, col_i2)]
        
    def cos_sim(self, A, B):
        return numpy.dot(A,B) / (self.magnitude(A) * self.magnitude(B))
        
        
  
        
    
    


                