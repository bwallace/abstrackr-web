'''
    Byron C Wallace
    Tufts Medical Center: Computational and Analytic Evidence Sythensis
    tuftscaes.org/curious_snake
    Curious Snake: Active Learning in Python
    co_feature_learning.py
    ---

    This class implements a co-testing algorithm based on labeled features.
    In particular, it maintains a list of features designated as
    + or -; these are then used in AL. Specifically, the examples picked for
    labeling are those for which the feature labels disagree with the current
    model's prediction.
'''


import pdb
import simple_svm_learner
from simple_svm_learner import *
import math
import os
from operator import itemgetter

class CoFeatureLearner(SimpleLearner):

        def __init__(self, pos_terms_f, neg_terms_f,  wlist_index, raw_abstract_text_dir, raw_title_text_dir,
                                unlabeled_datasets = None, models=None, undersample_before_eval = False, beta=.01, r=100, pc=.2):
            #
            # call the SimpleLearner constructor to initialize various globals
            SimpleLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models,
                                                    undersample_before_eval = undersample_before_eval)

            self.name = "CoFeature"

            print "assuming pc is %s!!!" % pc
            self.pc = pc

            # read
            print "assuming compound terms are first!!!"
            self.pos_terms = eval(open(pos_terms_f, 'r').readline())
            self.neg_terms = eval(open(neg_terms_f, 'r').readline())
            self.raw_abs_dir = raw_abstract_text_dir
            self.raw_titles_dir = raw_title_text_dir

            self.beta= beta

            print "reading word list: %s" % wlist_index
            #self.w_index = eval(open(wlist_index, 'r').readline())
            self.w_index = None
            #self.m = len(self.w_index) # count terms

            print "BAM"
            self.query_function= self.cotest
            # for memoization
            self.texts = {}
            self.psuedo_lbls = {} # as determined by feature voting
            self.feature_votes={}
            self.feature_scores={}

            self.np= None
            self.pp= None
            # better way to estimate these?
            # just using uniform weights...
            self.alpha_n = None
            self.alpha_p = None
            self.r = r
            #self.compute_ps()

        def cofl_al(self, k):
            unlabeled_dataset = self.unlabeled_datasets[0]
            k_ids_to_scores = {}
            for x_id in unlabeled_dataset.instances.keys()[:k]:
                k_ids_to_scores[x_id] = self.score(x_id)

            # now iterate over the rest
            for x_id in unlabeled_dataset.instances.keys()[k:]:
                cur_min_id, cur_min_score = self._get_min_val_key_tuple(k_ids_to_scores)
                x_score= self.score(x_id)
                if x_score > cur_min_score:
                    # then x is closer to the hyperplane than the farthest currently observed
                    # remove current max entry from the dictionary
                    k_ids_to_scores.pop(cur_min_id)
                    k_ids_to_scores[x_id] = x_score

            return k_ids_to_scores.keys()

        def cotest(self, k):
            unlabeled_dataset = self.unlabeled_datasets[0]

            # the scores can be the magnitude of the feature vote, given
            # the disagreement.
            k_ids_to_scores = {}

            count = 0
            min_max_mag = 0
            min_max_id = None
            for x_id in unlabeled_dataset.instances.keys()[k:]:
                fvote, mag = self.feature_vote(x_id)
                if fvote != self.predict(x_id) and self.get_N(x_id) != 0 and not self.not_sure(x_id):
                    if count < k:
                        k_ids_to_scores[x_id] = mag
                        count+=1
                    elif mag > min_max_mag:
                        k_ids_to_scores.pop(min_max_id)
                        k_ids_to_scores[x_id] = mag
                    min_max_id, min_max_mag = self._get_min_val_key_tuple(k_ids_to_scores)

            disagreements = k_ids_to_scores.keys()
            print "\n\ntotal disagreements: %s" % count
            print "magnitude of disagreements: %s" % " ".join([str(x) for x in k_ids_to_scores.values()])
            if count == k:
                return disagreements
            print "using SIMPLE for %s examples" % (k-count)
            disagreements.extend(self.SIMPLE(k-count, do_not_pick=list(disagreements)))
            return disagreements

        def score(self, x_id):
            return self.feature_score(x_id)

        def get_N(self, x_id):
            text = self.texts[x_id]
            neg_score, text, terms = self.count_terms(text, self.neg_terms)
            pos_score, text, terms = self.count_terms(text, self.pos_terms)
            N = pos_score + neg_score
            return N

        def has_a_term(self, x_id):
            if not self.texts.has_key(x_id):
                self.load_text(x_id)
            text = self.texts[x_id]
            neg_score, text, terms = self.count_terms(text, self.neg_terms)
            pos_score, text, terms = self.count_terms(text, self.pos_terms)
            return (pos_score > 0 or neg_score > 0)

        def not_sure(self, x_id):
            text = self.texts[x_id]
            neg_score, text, terms = self.count_terms(text, self.neg_terms)
            pos_score, text, terms = self.count_terms(text, self.pos_terms)
            return (pos_score == neg_score)

        def feature_score(self, x_id):
            # vote based on labeled features

            # note, if a token is part of a negative phrase (e.g., 'beam' in
            # 'photon beam'), this shouldn't be counted as positive

            # only need to feature vote once. do it at the start.
            if not x_id in self.feature_scores.keys():
                if not self.texts.has_key(x_id):
                    self.load_text(x_id)

                text = self.texts[x_id]
                neg_score, text = self.count_terms(text, self.neg_terms)
                pos_score, text = self.count_terms(text, self.pos_terms)
                N = pos_score + neg_score
                
                if N > 0:
                    entropy = -(pos_score/N * math.log(pos_score/N) + neg_score/N * math.log(neg_score/N))
                    self.feature_scores[x_id] = math.log(N) * entropy
                else:
                    self.feature_scores[x_id] = 0
                #self.feature_scores[x_id] = N - abs(pos_score - neg_score)

            return self.feature_scores[x_id]


        def uncertainty(self, k):
            unlabeled_dataset = self.unlabeled_datasets[0]

            # the scores can be the magnitude of the feature vote, given
            # the disagreement.
            k_ids_to_scores = {}

            count = 0
            max_min_mag = 0
            max_min_id = None
            for x_id in unlabeled_dataset.instances.keys()[k:]:
                if self.has_a_term(x_id):
                    fvote, odds_ratio = self.feature_vote(x_id)
                    score = abs(1-odds_ratio)
                    if count < k:
                        k_ids_to_scores[x_id] = score
                        count+=1
                    elif score <= max_min_mag:
                        k_ids_to_scores.pop(max_min_id)
                        k_ids_to_scores[x_id] = score
                max_min_id, max_min_mag = self._get_max_val_key_tuple(k_ids_to_scores)

            print "values: "
            #pdb.set_trace()
            print k_ids_to_scores.values()
            return k_ids_to_scores.keys()

        def doc_length(self, x_id):
            if not self.texts.has_key(x_id):
                self.load_text(x_id)
                
            text = self.texts[x_id]
            return len(text.split(" "))
            
        def feature_vote(self, x_id, include_direction=True, scaled=True):
            # returns vote, odds ratio

            # note, if a token is part of a negative phrase (e.g., 'beam' in
            # 'photon beam'), this shouldn't be counted as positive

            # only need to feature vote once. do it at the start.
            if not x_id in self.feature_votes.keys():
                if not self.texts.has_key(x_id):
                    self.load_text(x_id)

                text = self.texts[x_id]
                neg_score, text, neg_terms_found = self.count_terms(text, self.neg_terms)
                pos_score, text, pos_terms_found = self.count_terms(text, self.pos_terms)
                #pdb.set_trace()
                # psuedo counts
                neg_score+=1
                pos_score+=1
                total_terms_found = len(neg_terms_found) + len(pos_terms_found)
                odds_ratio = 0
                if pos_score >= neg_score:
                    odds_ratio = float(pos_score)/float(neg_score)
                    self.feature_votes[x_id] = (1, odds_ratio)
                else:
                    odds_ratio = float(neg_score)/float(pos_score)
                    self.feature_votes[x_id]  = (-1, odds_ratio)
                if not include_direction:
                    if neg_score==1 and pos_score == 1:
                        # no terms
                        #return None
                        return 0
                    odds_ratio = float(pos_score)/float(neg_score)
                    if not scaled:
                        self.feature_votes[x_id] = abs(math.log(odds_ratio))
                    else:
                        # scale by the feature count
                        self.feature_votes[x_id] =total_terms_found *abs(math.log(odds_ratio))
                              

            return self.feature_votes[x_id]

        def count_terms(self, doc, term_list, count_terms_only_once=True):
            t_count = 0
            terms_found = []
            #doc_sp = doc.split(" ")
            for t in term_list:
                if t in doc:
                    if count_terms_only_once:
                        t_count += 1
                    else:
                        t_count += doc.count(t)
                    doc.replace(t, "")
                    terms_found.append(t)
            return [t_count, doc, terms_found]

        def lpool(self, x_id):
            if not x_id in self.feature_votes.keys():
                if not self.texts.has_key(x_id):
                    self.load_text(x_id)

                text =  self.texts[x_id]
                neg_score, text, neg_terms_found = self.count_terms(text, self.neg_terms)
                pos_score, text, pos_terms_found = self.count_terms(text, self.pos_terms)
                unlabeled_terms = len(text.split(" "))

               # p1_pos = sum([math.log(self.alpha_p*self.pp) for w_i in pos_terms_found])
            #    p1_neg = sum([self.alpha_n*self.pn for w_i in neg_terms_found])


                # need also to add in the remaining (unlabeled) terms


                # This is how they compute the p in Melville, et. al
                #(math.log(self.pc) +\
                p_pos = -1.0*sum([math.log(self.pp) for w_i in pos_terms_found] +\
                                           [math.log(self.n_given_p) for w_i in neg_terms_found] +\
                                           [math.log(self.pp_unknown) for w_i in xrange(unlabeled_terms)])

                #*(math.log(1-self.pc) +\
                p_neg = -1.0*sum([math.log(self.pn) for w_i in neg_terms_found] +\
                                          [math.log(self.p_given_n) for w_i in pos_terms_found] +\
                                          [math.log(self.pn_unknown) for w_i in xrange(unlabeled_terms)])
                '''

                # this does poorly -- huge accuracy, terrible sensitivity
                p_pos = -1.0* sum([math.log(self.alpha_p*self.pp) for w_i in pos_terms_found] +\
                                           [math.log(self.alpha_n*self.n_given_p) for w_i in neg_terms_found]) #+\
                                           #[math.log(self.pp_unknown) for w_i in xrange(unlabeled_terms)])

                p_neg = -1.0 * sum([math.log(self.alpha_n*self.pn) for w_i in neg_terms_found] +\
                                          [math.log(self.alpha_p*self.p_given_n) for w_i in pos_terms_found]) #+\
                                          #[math.log(self.pn_unknown) for w_i in xrange(unlabeled_terms)])
                '''
                #p_pos =  -1.0* (sum([math.log(self.pp) for w_i in pos_terms_found] +\
                #                           [math.log(self.n_given_p) for w_i in neg_terms_found]))

                #p_neg =  -1.0 * (sum([math.log(self.pn) for w_i in neg_terms_found] +\
                #                           [math.log(self.p_given_n) for w_i in pos_terms_found]))

                # meanwhile, this seems to do well... why?
               # p_pos = -1.0*sum([math.log(self.alpha_p*self.pp) for w_i in pos_terms_found])
            #    p_neg = -1.0*sum([math.log(self.alpha_n*self.pn) for w_i in neg_terms_found])
                if p_pos > p_neg:
                    #pdb.set_trace()
                    #print "(+)"
                    self.feature_votes[x_id] = (1, abs(p_pos-p_neg))
                else:
                    self.feature_votes[x_id] = (-1, abs(p_pos-p_neg))

            return self.feature_votes[x_id]


        def linear_pool(self, k):
            # co-testing with linear pooling basically
            unlabeled_dataset = self.unlabeled_datasets[0]

            # the scores can be the magnitude of the feature vote, given
            # the disagreement.
            k_ids_to_scores = {}

            count = 0
            min_max_mag = 0
            min_max_id = None
            for x_id in unlabeled_dataset.instances.keys()[k:]:
                fvote, mag = self.lpool(x_id)
                if fvote != self.predict(x_id) and self.get_N(x_id) != 0 and not self.not_sure(x_id):
                    if count < k:
                        k_ids_to_scores[x_id] = mag
                        count+=1
                    elif mag > min_max_mag:
                        k_ids_to_scores.pop(min_max_id)
                        k_ids_to_scores[x_id] = mag
                    min_max_id, min_max_mag = self._get_min_val_key_tuple(k_ids_to_scores)

            disagreements = k_ids_to_scores.keys()
            #print ""
            print "\n\ntotal disagreements: %s" % count
            print "magnitude of disagreements: %s" % " ".join([str(x) for x in k_ids_to_scores.values()])
            if count == k:
                return disagreements
            print "using SIMPLE for %s examples" % (k-count)
            disagreements.extend(self.SIMPLE(k-count, do_not_pick=list(disagreements)))
            return disagreements


        def compute_ps(self):
            p = float(len(self.pos_terms))
            n = float(len(self.neg_terms))

            self.pp = 1.0/float(p + n)
            self.pn = 1.0/float(p + n)

            # probability of a positive term appearing in a negative doc
            self.p_given_n = self.pp * 1/self.r
            # and vice versa
            self.n_given_p = self.pn * 1/self.r


            self.alpha_n = 1/float(n)
            self.alpha_p = 1/float(p)

            #
            # This says the probability of seeing an unlabeled term
            # in the respective documents is different, which I don't like.
            # In particular, p is larger than n (more + than - terms) so
            # problem: p(w_u | +) is << p(w_u | -). This strongly affects
            # the probability -- so even when there are more terms
            self.pp_unknown = (n*(1-1/self.r))/ ((p + n) * (self.m-p-n))
            self.pn_unknown = (p*(1-1/self.r))/ ((p + n) * (self.m-p-n))


        def multi_nom(self, doc):
            pass

        def load_text(self, x_id):
            ti_text = open(os.path.join(self.raw_titles_dir, str(x_id)), 'r').readline().lower()
            ab_text = open(os.path.join(self.raw_abs_dir, str(x_id)), 'r').readline().lower()
            self.texts[x_id] = " ".join([ti_text, ab_text])


        def co_train(self):
            #psuedo_pos=[]
            #psuedo_neg=[]
            psuedo_pos_d={}
            psuedo_neg_d={}
            print "Co-training?"
            pdb.set_trace()
            for x_id in self.unlabeled_datasets[0].instances.keys():
                direction, mag = self.feature_vote(x_id)
                #if mag > self.beta:
                if direction > 0:
                    #psuedo_pos.append(x_id)
                    psuedo_pos_d[x_id] = mag
                else:
                    psuedo_neg_d[x_id] = mag
                    #psuedo_neg.append(x_id)

            psuedo_pos = [x[0] for x in sorted(psuedo_pos_d.items(), key=itemgetter(1), reverse=True)]
            psuedo_neg = [x[0] for x in sorted(psuedo_neg_d.items(), key=itemgetter(1), reverse=True)]

            p = self.beta#/2.0
            this_many = int(p*len(self.unlabeled_datasets[0]))
            psuedo_pos = psuedo_pos[:this_many]
            #psuedo_neg = psuedo_neg[:this_many]

            # First, set the labels to the prediction from the naive
            # stump -- i.e., feature voting
            print "psuedo labeling %s positives, %s negatives" % (len(psuedo_pos), len(psuedo_neg))
            for d in self.unlabeled_datasets:
                d.set_labels(psuedo_pos, 1)
                #d.set_labels(psuedo_neg, -1)

            # Next, 'label' all of the instances -- but note that
            # the label that will be used is the predicted label, *not*
            # the true label (necessarily) so this isn't cheating
            all_instances = psuedo_pos #+ psuedo_neg

            self.label_instances(all_instances)
            return all_instances



        def rebuild_models(self, for_eval=False, verbose=True, undersample_these=None,
                                        do_grid_search=False, beta=10):
            '''
            Rebuilds all models over the current labeled datasets. If for_eval is true,
            we undersample if this learner is set to undersample before evaluation.
            Returns a list of the undersampled ids (if any).
            '''
            dataset = None
            undersampled_ids  = []


            # here we label the examples we're most confident about
            # -- i.e., we co-train
            if for_eval and False:
                psuedo_labeled = self.co_train()

            if self.undersample_before_eval and for_eval:
                if verbose:
                    print "%s: undersampling (using %s) before building models.." % (self.name, self.undersample_function.func_name)

                #
                # @experimental 9/23
                # Here we're assuming the undersample function accepts an 'undersample_these'
                # parameter. You should implement a diffferent, more flexible strategy to allow this
                #
                if self.undersample_function.__name__ == "undersample_labeled_datasets":
                    print ">> warning -- we're making assumptions about the undersample function being used here"
                    datasets = self.undersample_function(undersample_these=undersample_these)
                else:
                    datasets = self.undersample_function()
                undersampled_ids = list(set(self.labeled_datasets[0].instances.keys()) - set(datasets[0].instances.keys()))
            else:
                datasets = self.labeled_datasets

            if verbose:
                print "training model(s) on %s instances" % datasets[0].size()

            self.models = []
            for dataset, param in zip(datasets, self.params):
                samples, labels = dataset.get_samples_and_labels()
                try:
                    problem = svm_problem(labels, samples)
                except:
                    pdb.set_trace()

                #
                # @TODO if an rbf kernel is being used for this param
                # we should do a grid search here for parameters (maybe if only for_eval)
                #
                param = svm_parameter(kernel_type = self.kernel_type, weight = self.weights)
                if do_grid_search:
                    print "running grid search..."
                    C, gamma = grid_search(problem, param, linear_kernel=(self.kernel_type==LINEAR), beta=beta)
                    print "done. best C, gamma: %s, %s" % (C, gamma)
                    param = svm_parameter(kernel_type = self.kernel_type, weight = self.weights,
                                                            C=C, gamma=gamma)
                else:
                    print "not doing grid search."
                model = svm_model(problem, param)
                self.models.append(svm_model(problem, param))


            if for_eval and False:
                # now, 'unlabel' the examples psuedo-labeled during co-training
                self.unlabel_instances(psuedo_labeled)
                # and, finally, now that they're unlabeled again, revert their label
                # back to the true label
                for d in self.unlabeled_datasets:
                    d.revert_to_true_labels(psuedo_labeled)


            #
            # Return the ids of the instances that were undersampled,
            # i.e., thrown away. This is in case you want to undersample
            # the same examples in every learner (you undersample for one
            # learner then throw the same majority examples away for the
            # others.
            return undersampled_ids

        def SIMPLE(self, k, do_not_pick=None):
            '''
            Returns the instance numbers for the k unlabeled instances closest the hyperplane.
            '''
            # randomly flip an m-sided coin (m being the number of feature spaces)
            # and pick from this space
            feature_space_index = random.randint(0, len(self.models)-1)
            model = self.models[feature_space_index]
            dataset = self.unlabeled_datasets[feature_space_index]
            return self._SIMPLE(model, dataset, k, do_not_pick=do_not_pick)
