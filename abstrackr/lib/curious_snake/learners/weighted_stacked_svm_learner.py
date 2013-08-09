from stacked_svm_learner import StackedSVMLearner
from stacked_svm_learner import *
import numpy
from numpy import matrix
import random
import Queue
import curious_snake # for the evaluation methods
import weight_finder

sign = lambda x: 1.0 if x>0.0 else -1.0
 
class WeightedStackedSVMLearner(StackedSVMLearner):   
    
    def __init__(self, learners, unlabeled_datasets=None, undersample_before_eval = False, 
                        weights=[1,100], use_raw=False, name="weighted STACKED", step_size=.2, beta=10):
        StackedSVMLearner.__init__(self, learners, unlabeled_datasets=unlabeled_datasets,
                                                     undersample_before_eval = undersample_before_eval, name=name)
        self.step_size = step_size
        self.beta = beta
        self.W = None

    def predict(self, x_id):
        '''
        This overrides the base predict function.
        '''
        points = [learner.unlabeled_datasets[0].get_point_for_id(x_id) for learner in self.learners]
        stacked_vector = self.get_distance_vector(points)
        return weight_finder.n_at_least_alpha(stacked_vector, 2, self.W)
        
        '''
        return sign(numpy.dot(self.W, stacked_vector))
        '''
    def rebuild_models(self, for_eval=False, undersample_these=None, 
                                    do_grid_search=True, beta=2, verbose=True):
                                    
        # rebuild the base learners
        for learner in self.learners:
            learner.rebuild_models(for_eval=for_eval, do_grid_search=do_grid_search, 
                                                    undersample_these = undersample_these)
        
        # these are stacked    
        self.labeled_datasets = [self.get_stacked_dataset(True)]
        self.unlabeled_datasets = [self.get_stacked_dataset(False)]
        
        self.find_weights()
        
    def find_weights(self):
        stacked_dataset = self.labeled_datasets[0].copy()

        
        #
        # Need to build P, the prediction matrix
        #
        P, y = self.build_P()

        solver = weight_finder.WeightSolver([(-1,1)]*len(self.learners), 30, 50000,
                          args=[P, self.beta, 3, y], goal_error=1/(self.beta + 1), verbose=False,
                          use_pp = False, pp_modules=['numpy'])


        pdb.set_trace()
        self.W = solver.best_individual
        '''
        W = numpy.zeros(shape=(len(self.learners), 1))
        W_star = W
        num_steps = (2.0/self.step_size)**len(self.learners)
        #num_steps = 100000/2
        print "taking %s steps to cover the space" % num_steps
        cur_step = 0
        m_star = -1.0
        q = Queue.Queue()
        q.put(W)
        while cur_step < num_steps:
            #cur_w = q.get()
            cur_w = [random.random() for x in xrange(len(self.learners))]
            for i,x in enumerate(cur_w):
                if random.random() > .5:
                    cur_w[i] = -1 * x
            #pdb.set_trace()
            cur_w = numpy.array(cur_w)
            P_hat = numpy.dot(P, cur_w)
            #pdb.set_trace()
            y_hat = [sign(y_i) for y_i in P_hat]
            # now compute metric!
            conf_mat = curious_snake._evaluate_predictions(y_hat, y)
            results = {}
            curious_snake._calculate_metrics(conf_mat, results, verbose=False)
            metric_score = self.beta * results["sensitivity"] + results["specificity"]
            #print "cur_W: %s. sensitivity: %s. specificity: %s" % (cur_w, results["sensitivity"], results["specificity"])
            if metric_score > m_star:
                print "found new best weights: %s with score: %s (sensitivity: %s, specificity: %s) on step: %s" % \
                                    (cur_w, metric_score,  results["sensitivity"], results["specificity"], cur_step)
                m_star = metric_score
                W_star = cur_w
            #for W_pr in self.step(cur_w):
            #    q.put(W_pr)
            cur_step += 1
            #if cur_step == float(num_steps)/2.0:
            #    pdb.set_trace()
        #pdb.set_trace()    
        self.W = W_star
        '''
          
        
    def step(self, p):
        '''
        Computes and returns all points reachable from p in a single 
        step.
        '''
        all_steps = [] # all points reachable from p in one step
        for d_i in range(p.shape[0]):
            cur_point = p.copy()
            #pdb.set_trace()
            cur_point[d_i, 0] += self.step_size
            all_steps.append(cur_point)
        
        # also take negative steps
        for d_i in range(p.shape[0]):
            cur_point = p.copy()
            cur_point[d_i, 0] -= self.step_size
            all_steps.append(cur_point)
            
        #pdb.set_trace()
        return all_steps
        
    def build_P(self, nfolds=4):
        ''' 
        This method builds the P matrix of predicted values for
        each instance for each base learner.
        '''
        all_ids = self.labeled_datasets[0].get_instance_ids()[:]
        # randomize
        random.shuffle(all_ids)
        N = len(self.learners[0].labeled_datasets[0])
        fold_size = int(float(N)/float(nfolds))
        test_sets = []
        # assemble train and test set id lists
        slices = [all_ids[i*fold_size:(i+1)*fold_size] for i in xrange(nfolds)]

        for k in xrange(nfolds):
            test_sets.append(slices[k])
        
        y = numpy.zeros(shape=(N)) # true labels
        P = numpy.zeros(shape=(N, len(self.learners)))
        sorted_ids = None
        for learner_index, learner in enumerate(self.learners):    
            preds_for_learner = {}

            #for train_set, test_set in zip(train_sets, test_sets):
            for test_set in test_sets:
                # 'unlabel' the examples in the test set
                learner.unlabel_instances(test_set)
                # note; this is undersampling *at random*
                learner.rebuild_models(for_eval=True, do_grid_search=True)
                # again we are assuming that the base classifiers are
                # using only one dataset/view each
                model = learner.models[0]
                dataset = learner.unlabeled_datasets[0]
                for test_id in test_set:
                    preds_for_learner[test_id] = model.distance_to_hyperplane(dataset.get_point_for_id(test_id), signed=True)
                    
                # finally, re-label instances in this validation fold
                learner.label_instances(test_set)
        
            # finished with this learner. now, we sort
            sorted_ids = sorted(preds_for_learner.keys())
            for inst_index, inst_id in enumerate(sorted_ids):
                P[inst_index, learner_index] = preds_for_learner[inst_id]
                y[inst_index] = self.learners[0].labeled_datasets[0].get_label_for_id(inst_id)
        
        return (P, y)


        
        