import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import random
import numpy
import pca
from numpy.linalg import svd
from numpy import sum,where
import pylab

def matrixrank(A,tol=1e-8):
    s = svd(A,compute_uv=0)
    return sum( where( s>tol, 1, 0 ) )
    
class SPANLearner(SimpleLearner):

    def __init__(self, unlabeled_datasets = [], models=None, undersample_before_eval = False, r=400):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
        SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                undersample_before_eval = undersample_before_eval)
                                                    
            
                
       
        self.indices_to_ids = None
        # @TODO parameterize r; make it cover 90% of the 
        # variance
        self.r = r
        
        self.P = None # Projector matrix
        self.var = .9
        self.X = None # raw X
        self.PX = None # projected X
        
        self.LX = None # labeled (raw) x
        self.LPX = None # labeled (projected) X
        
        self.query_function = self.pick_l_i
        self.V = None
        self.l_rank = 0
        self.total_rank = None
        self.ranks = []
        self.dimensions = [d.get_dim() for d in self.unlabeled_datasets]
        self.U_cols = None
        print "SPAN learner: changing query function to %s" % self.query_function.__name__
        self.name = "SPANer"
        self.memoized  ={}
        self.labeled_cols=[]
        
        self.full_P = None
        self.P_comp = None
        self.avg_pp = None
        self.avg_nn = None
        self.L_p = None
        self.L_n = None
        
        self.since_r = None
        
    def compute_fraction(self, up_to, eigenvals):
        return sum(eigenvals[:up_to])/sum(eigenvals)
        
        
    def setup_X(self):
        '''
        PCA project the observation matrix
        '''
        #
        # transpose then mean-substract the matrix; 
        # these are necessary steps for PCA
        #
        # first transpose; resulting in a FxN
        # matrix where F is the number of 
        # features and N is the number of
        # instances
        self.indices_to_ids, self.X = self.unlabeled_datasets[0].to_numpy_arr(indicator=True, build_id_dict=True)
        X_t = self.X.T
        # substract the mean from each row
    
        X_t_bar = [r-r.mean() for r in X_t]
        # build a new matrix
        X_t_bar = numpy.array(X_t_bar)
        
        # now run pca on the mean substracted
        # transposed matrix
        self.V,P = pca.pca(X_t_bar)
        self.full_P = P
        #pdb.set_trace()
        # keep only the top r principal components
        drop_n = 0
        if self.r is not None:
            drop_n = P.shape[1]-self.r
            P = P[:,:-drop_n]
            self.P = P.T
  
        
        # finally, project X onto the lower-dimensional
        # space. note that PX will be an r x N matrix
        # wherein each column corresponds to an 
        # instance projected onto the top r principal 
        # components
        self.PX = numpy.dot(P.T, X_t)    
        
        
    def pick_l_i(self, k):
        if self.PX is None:
            print "pca projecting..."
            self.setup_X()
            print "done. computing rank..."
            self.total_rank = 500#matrixrank(self.PX)
            self.U_cols = range(self.PX.shape[1])
            
        inst_cols = None

    
        positives = self.labeled_datasets[0].get_minority_examples()
        if self.L_p is not None and len(self.labeled_datasets[0])>100:
            pos_keys = [p_inst.id for p_inst in positives]
            pos_d = dict(zip(pos_keys, positives))
            L_pos = dataset.dataset(pos_d).to_numpy_array()
            #self.plot_diffs()
            if self.since_r is None or self.since_r == 5:
                self.find_r()
                print "*** found r: %s" % self.r
                self.since_r = 1
            else:
                self.since_r+=1
            #pdb.set_trace()
            print "picking most similiar"
            inst_cols = self.pick_most_sim(math.ceil(k/2.0))
            print "...and most diverse"
            inst_cols.extend(self.pick_most_diff(math.floor(k/2.0)))
        else:
            inst_cols = random.sample(self.U_cols, k)

        #pdb.set_trace()
        for cur_col in inst_cols:
            self.label(cur_col)
            #inst_cols.append(cur_col)
            self.U_cols.remove(cur_col)
            
        
        ids = []
        for col in inst_cols:
            #self.U_cols.remove(col)
            inst_id = self.indices_to_ids[col]
            if inst_id not in self.unlabeled_datasets[0].instances.keys():
                print "something is wrong"
                pdb.set_trace()
            ids.append(inst_id)
            #pdb.set_trace()
            v = self.col_to_vec(self.X.T, col)

            if self.unlabeled_datasets[0].instances[inst_id].label >0:
                # positive
                if self.L_p is None:
                    self.L_p = numpy.vstack([v]).T
                else:
                    self.L_p = numpy.vstack([self.L_p, v.T])
            else:
                # negative
                if self.L_n is None:
                    self.L_n = numpy.vstack([v]).T
                else:
                    self.L_n = numpy.vstack([self.L_n, v.T])
            #self.label(col)
        #pdb.set_trace()
        print "\n returning %s ids!!!" % len(ids)
        return ids
        

    #def most_similar
    def find_r(self, plot=True):
        vs = []
        mags = []
        diffs = []
        max_diff=0
        cur_i = 0
        for v_i in xrange(2, self.full_P.shape[1]-1):
            if (v_i-1)%10==0:
                P_temp = self.full_P[:,:v_i].T
                P_comp = (numpy.eye(P_temp.shape[0], P_temp.shape[1]) - P_temp)
                L_pp = numpy.dot(P_comp, self.L_p.T)
                L_np = numpy.dot(P_comp, self.L_n.T)
                
                avg_pp = L_pp.sum(axis=1)/L_pp.shape[1]
                avg_pn = L_np.sum(axis=1)/L_np.shape[1]
                
                delta_m = avg_pp - avg_pn
                cur_mag = self.magnitude(delta_m)
                mags.append(cur_mag)
                vs.append(v_i)
                
                if len(mags) > 1:
                    cur_diff = mags[cur_i] - mags[cur_i-1]
                    diffs.append(cur_diff)
                    if cur_diff > max_diff and v_i > 400:
                        max_diff = cur_diff
                        self.r = v_i
                        self.P_comp = P_comp
                        self.avg_pp = avg_pp
                        self.avg_nn = avg_pn
                cur_i+=1
        
        if plot:
            pylab.clf()
            pylab.plot(vs, mags)
            pylab.savefig("mags.pdf")
            #pdb.set_trace()
            pylab.clf()
            pylab.plot(vs[1:], diffs)
            pylab.axvline(x=self.r)
            pylab.savefig("mag_diffs.pdf")
        
            
    def plot_diffs(self):
        vs = []
        mags = []
        diffs = []
        cur_i = 0
        for v_i in xrange(2, self.full_P.shape[1]-1):
            if (v_i-1)%10==0:
                P_temp = self.full_P[:,:v_i].T
                P_comp = (numpy.eye(P_temp.shape[0], P_temp.shape[1]) - P_temp)
                L_pp = numpy.dot(P_comp, self.L_p.T)
                L_np = numpy.dot(P_comp, self.L_n.T)
                avg_pp = L_pp.sum(axis=1)/L_pp.shape[1]
                avg_pn = L_np.sum(axis=1)/L_np.shape[1]
                
                delta_m = avg_pp - avg_pn
                cur_mag = self.magnitude(delta_m)
                vs.append(v_i)
                #mags.append(cur_mag/float(v_i))
                mags.append(cur_mag)
                if len(mags) > 1:
                    diffs.append(mags[cur_i] - mags[cur_i-1])
                cur_i+=1
                #pdb.set_trace()
                # now take the difference in row (?) averages,
                # subtract and check magnitude
                #avg_pp = L_pp.sum(axis=0)
        pylab.clf()
        pylab.plot(vs, mags)
        pylab.savefig("mags.pdf")
        pdb.set_trace()
        pylab.clf()
        pylab.plot(vs[1:], diffs)
        pylab.savefig("mag_diffs.pdf")
        
        
        
    def pick_most_diff(self, k, from_both=False):
        print "k is %s" % k
        max_min_col = None
        max_min_score = 100
        k_most_diff = {}
        count = 0
        for col_index in random.sample(self.U_cols, 500):
            if count % 10 == 0:
                print count
            count+=1
            # raw vector
            cur_v = self.col_to_vec(self.X.T, col_index)
            # now project
            cur_vp = numpy.dot(self.P_comp, cur_v)
            
            # check similarity to current positives
            # should we only check diversity w.r.t. positives, or
            # also to negatives? 
            sim_score = self.cos_sim(self.avg_nn, cur_vp)[0] + self.cos_sim(self.avg_pp, cur_vp)[0]
            #sim_score = self.cos_sim(self.avg_pp, cur_vp)[0]
            #print sim_score
            if sim_score < max_min_score or len(k_most_diff.keys())<k:
                k_most_diff[col_index] = sim_score
                if max_min_col is not None and len(k_most_diff.keys())>k:
                    k_most_diff.pop(max_min_col)
                max_min_score = sim_score
                max_min_col = col_index
                for key,val in k_most_diff.items():
                    if val > max_min_score:
                        max_min_score = val
                        max_min_col = key
        print "winners (diff)! %s" % k_most_diff
        return k_most_diff.keys()
        
    def pick_most_sim(self, k):
        print "k is %s" % k
        min_max_col = None
        min_max_score = 0
        k_most_sim = {}
        count = 0
        for col_index in random.sample(self.U_cols, 500):
            if count % 10 == 0:
                print count
            count+=1
            # raw vector
            cur_v = self.col_to_vec(self.X.T, col_index)
            # now project
            cur_vp = numpy.dot(self.P_comp, cur_v)
            # check similarity to current positives
            sim_score = self.cos_sim(self.avg_pp, cur_vp)[0]
            #print sim_score
            if sim_score > min_max_score or len(k_most_sim.keys())<k:
                k_most_sim[col_index] = sim_score
                if min_max_col is not None and len(k_most_sim.keys())>k:
                    k_most_sim.pop(min_max_col)
                min_max_score = sim_score
                min_max_col = col_index
                for key,val in k_most_sim.items():
                    if val < min_max_score:
                        min_max_score = val
                        min_max_col = key
        print "winners! %s" % k_most_sim
        return k_most_sim.keys()
            
            
    def pick_most_diverse(self):
        print "picking most diverse..."
        best_col = None
        minimax_dist = None
        for col_index in self.U_cols:
            #v_raw = self.X.T.take([col_index], axis=1)
            #v_raw = v_raw.flatten()
            # project
            #v_hat = numpy.dot(self.P, v_raw)
            #v_hat = self.col_to_vec(self.PX, )
            if len(self.labeled_cols) > 0:
                closest_cos= max([self._cos_sim(col_index, labeled_index) for labeled_index in self.labeled_cols])
                #pdb.set_trace()
            else:
                closest_cos = 0
                
            if best_col is None:
                best_col = col_index
                minimax_dist = closest_cos
            elif closest_cos < minimax_dist:
                # remember; cosine similarity is between 0 and 1; 0 is orthogonal
                # (most dissimiliar) and 1means they're the same
                best_col = col_index
                minimax_dist = closest_cos
        print "ok.. returning col with dist: %s" % minimax_dist
        
        return best_col
             
       
    def col_to_vec(self, m, j):
        return m.take([j], axis=1)
        
    def magnitude(self, x):
        return numpy.sqrt(numpy.square(x).sum())
        
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
        
        
    def label(self, col_index):
        #
        #
        #
        
        #v = self.PX.take([col_index], axis=1)
        v_raw = self.X.T.take([col_index], axis=1)
        
        #v = v.flatten()
        v_raw = v_raw.flatten()
        
        #
        # here's where the magic happens
        #
        if self.LX is not None:
            row_maxes = self.LX.max(axis=1)
            try:
                for i, v_i in enumerate(v_raw):
                    if v_i  < 1.0:
                        v_raw[i] = v_i + row_maxes[i]
            except:
                pdb.set_trace()
                        
        
        v = numpy.dot(self.P, v_raw)
        if self.LPX is not None:
            self.LPX = numpy.vstack([self.LPX.T, v]).T
            self.LX = numpy.vstack([self.LX.T, v_raw]).T
        else:
            self.LPX = numpy.vstack([v]).T
            self.LX = numpy.vstack([v_raw]).T
        
        # @experimental
        self.l_rank+=1
        cur_rank = self.l_rank
        
        if cur_rank == self.l_rank:
            print "no rank-gain?"
        self.ranks.append(cur_rank)
        self.l_rank = cur_rank
        self.labeled_cols.append(col_index)
        print "labeled d rank: %s; total rank: %s" % (self.l_rank, self.total_rank)
        
    
    


                