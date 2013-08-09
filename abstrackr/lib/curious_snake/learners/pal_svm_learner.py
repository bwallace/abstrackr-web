import pdb
import simple_svm_learner
from simple_svm_learner import *
import math

class PALLearner(SimpleLearner):
        def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False, 
                                epsilon = 0.075, kappa = 8, label_at_least = 0, win_size=3):
            #
            # call the SimpleLearner constructor to initialize various globals
            SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                    undersample_before_eval = undersample_before_eval)
            
            print "PAL learner: switching query function to Random!"
            self.query_function = self.get_random_unlabeled_ids 
            self.name = "PAL"
            self.kappa = kappa
            self.epsilon = epsilon
            self.label_at_least = label_at_least
            self.switched_to_exploit = False
            self.win_size = win_size
            
            # here we instantiate two lists with length equal to the number
            # of feature spaces. 
            #
            # datasets_converged holds booleans indicating
            # whether or not individual feature spaces have converged (i.e.,
            # their diversities have stabilized w.r.t. epsilon and kappa) --
            # so datasets_converged[i] tells us whether we need to keep checking
            # feature space i.
            self.datasets_converged = [False for d in self.unlabeled_datasets]
            # diversity_scores maintains lists for each feature space
            # of the observed diversity scores, as computed after new positives
            # are discovered.
            self.diversity_scores = [[] for d in self.unlabeled_datasets]
            self.found_new_cluster =  [[] for d in self.unlabeled_datasets]
            self.observed_minorities = [[] for d in self.unlabeled_datasets]
        
        def active_learn(self, num_examples_to_label, batch_size=5):
            #
            # call the base active learn method
            #
            BaseLearner.active_learn(self, num_examples_to_label, batch_size=batch_size)
            labeled_so_far = len(self.labeled_datasets[0])
            N = labeled_so_far + len(self.unlabeled_datasets[0])
            
            if not self.switched_to_exploit and labeled_so_far >= self.label_at_least * N:
                self.check_if_we_should_switch_to_exploit()


            # @experimental 10/15/09 always calling "check.." method
            # for experimental purposes
            #self.check_if_we_should_switch_to_exploit()
            
        
        def check_if_we_should_switch_to_exploit_experimental(self):
            already_observed_ids = [minority.id for minority in self.observed_minorities[0]]
            for i, dataset in enumerate(self.labeled_datasets):
                if not self.datasets_converged[i]:
                    # first update the diversity scores
                    new_minorities = [minority for minority in self.labeled_datasets[i].get_minority_examples() 
                                                if minority.id not in already_observed_ids]
                    for new_minority in new_minorities:

                        # now compute the diversity score
                        div_score = self.angle_to_closest_min_neighbor(new_minority, model_index=i)
                        updated_scores = [self.angle_to_closest_min_neighbor(min_inst) for min_inst in self.observed_minorities[i]]
                        self.found_new_cluster[i].append(self.is_new_cluster(div_score, updated_scores, model_index=i))
                        num_clusters = len([f for f in self.found_new_cluster[i] if f])
                        m = len(self.labeled_datasets[0])
                        n = len(self.labeled_datasets[0]) + len(self.unlabeled_datasets[0])
                        if i==0:
                            # m, n, s
                            cur_probs = posterior_probs(m, n, num_clusters)

                        self.diversity_scores[i].append(div_score)     
                        # first add the newly observed minority to the list (of observed minorities)
                        self.observed_minorities[i].append(new_minority)


        def check_if_we_should_switch_to_exploit(self):
            # @experimental 10/14/09 this is the original method; supplanting with new
            # (above) for experimentation
            already_observed_ids = [minority.id for minority in self.observed_minorities[0]]
            for i, dataset in enumerate(self.labeled_datasets):
                if not self.datasets_converged[i]:
                    # first update the diversity scores
                    new_minorities = [minority for minority in self.labeled_datasets[i].get_minority_examples() 
                                                if minority.id not in already_observed_ids]
                    for new_minority in new_minorities:
                        # first add the newly observed minority to the list (of observed minorities)
                        self.observed_minorities[i].append(new_minority)
                        # now compute the diversity score
                        div_score = self.compute_div_score(model_index=i)
                        # now append the diversity score to the list (of diversity scores)
                        self.diversity_scores[i].append(div_score)        
                        
                    # now that we've calculated and appended the scores for
                    # each newly labeled minority instance, check if we can switch

                    # note that the denominator (x) is constant (step_size), 
                    # so we can ignore it here
                    dydxs = _numerical_deriv(self.diversity_scores[i])
                    smoothed = [abs(div) for div in _median_smooth(dydxs, window_size=self.win_size)]
                    
                    #print "\n\n"
                    #print dydxs
                    #print smoothed
                    #print self.kappa
                    #print self.epsilon
                    
                    max_change = 1.0
                    if len(smoothed) >= self.kappa + self.win_size:
                        max_change = max(smoothed[-self.kappa:])
            
                    if max_change <= self.epsilon:
                        print "\nlearner %s: feature space %s has converged after %s labels" % (self.name, self.labeled_datasets[i].name,
                                                                                                                            len(self.labeled_datasets[i]))
                        self.datasets_converged[i] = True
                    else:
                        print "NOT SWITCHING time series: %s, epsilon: %s\n" % (smoothed, self.epsilon)
                # finally, check how many feature spaces have converged
                # we switch to exploitation if more than half have (this is arbitrary)
                if self.datasets_converged.count(True) >= len(self.labeled_datasets) :
                    print "learner %s: more than half of the feature spaces have stabilized: switching to exploit!" % self.name
                    self.query_function = self.SIMPLE
                    self.switched_to_exploit = True
                    
            return (dydxs, smoothed)
            

        def angle_to_closest_min_neighbor(self, new_inst, model_index=0):
            thetas = []
            min_instances = self.observed_minorities[model_index]
            for min_inst in [inst for inst in min_instances if inst.id != new_inst.id]:
                cos = self._compute_cos(model_index, new_inst, min_inst)
                #theta = math.acos(cos)
                thetas.append(cos)
            # i.e., the angle to its closest neighbor in kernel-space
            if len(thetas) > 0:
                return max(thetas)
            return 0
            
                
        def z_score(self, x, u, s):
            return (x - u)/ s
            
        def is_new_cluster(self, new_score, prev_scores, model_index=0):
            X = prev_scores
            if len(X) == 0:
                 return True
            
            m = sum(X)/ len(X)
            s = numpy.std(X)
            z = self.z_score(new_score, m, s)
            print z
            if z <= -1.0:
                return True
            return False

            
        def compute_div_score(self, model_index=0):
            '''
            computes a diversity score over the positive labeled examples
            '''
            div_sum, pwise_count = 0.0, 0.0
            min_instances = self.observed_minorities[model_index]
            if len(min_instances) == 1:
                # only one instance
                return 0
            
            for instance_1 in min_instances:
                for instance_2 in [inst for inst in min_instances if inst.id != instance_1.id]:
                    div_sum+=self._compute_cos(model_index, instance_1, instance_2)
                    pwise_count+=1.0

            # average pairwise cosine 
            return div_sum / pwise_count
                        
            
            
def posterior_probs(m, n, s):
    post_probs = []
    for j in range(s, n-m-s):
        numer = choose(j, s) * choose(n-j, m-s)
        denom = choose(n+1, m+1)
        log_p_j =  math.log(numer) - math.log(denom)
        post_probs.append(exp(log_p_j))

    return post_probs
        
def round_figure(x, n):
    return round(x, int(n - math.ceil(math.log10(abs(x)))))

def factorial(n):
    """
    factorial(n): return the factorial of the integer n.
    factorial(0) = 1
    factorial(n) with n<0 is -factorial(abs(n))
    """
    result = 1
    for i in xrange(1, abs(n)+1):
        result *= i
    if n >= 0:
        return result
    else:
        return -result

def choose(n, k):
    if 0 <= k <= n:
        p = 1
        for t in xrange(min(k, n - k)):
            p = (p * (n - t)) // (t + 1)
        return p
    print "whoops"
    pdb.set_trace()
    return 0
    
def _median_smooth(X, window_size=3):
    smoothed = []
    window_index = 0
    for i in range(len(X)):
        if i+1 <= window_size/2.0:
            smoothed.append(X[i])
        else:
            smoothed.append(_median(X[window_index:window_index+window_size]))
            window_index += 1
    return smoothed
    
     

                   
def _median(X):
    median = None
    if len(X) % 2:
      # odd number of elements
      median = float(X[len(X)/2])
    else:
       # Number of elements in data set is even.
       mid_point = len(X)/2   
       median = (X[mid_point-1] + X[mid_point])/2.0
    return median
  
def _numerical_deriv(X):
    dxs = [1]
    diffs = [X[i+1] - X[i] for i in range(len(X)-1)]
    dxs.extend(diffs)
    return dxs