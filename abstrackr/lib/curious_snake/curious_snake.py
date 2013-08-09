'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
	curious_snake.py
	--
	This module is for running experiments to compare active learning strategies. It uses the active learning framework.
	See the in-line documentation for examples.
	
	Two general notes: 
	
	(1) Curious Snake was originally written for a scenario in which multiple feature spaces,
	sometimes called 'views' were being exploited (see "Active Learning with Multiple Views" by 
	Muslea, Minton & Knoblock), thus pluralizing many of the attributes in this class. For example, 
    *lists* of unlabeled_datasets and models are kept. If you only have one view that you're 
    interested in, as is often the case, simply pass around unary lists.
     
    (2) It is assumed throughout the active learning is being done over binary datasets.
     
    ... Now for some legal stuff.
    
    ----
    CuriousSnake is distributed under the modified BSD licence
    Copyright (c)  2009,  byron c wallace
    All rights reserved.
    
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in the
          documentation and/or other materials provided with the distribution.
        * Neither the name of Tufts Medical Center nor the
          names of its contributors may be used to endorse or promote products
          derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY byron c wallace 'AS IS'' AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL byron wallace BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    
    
    The files comprising the libsvm library are also under the modified BSD and are:
    
    Copyright (c) 2000-2008 Chih-Chung Chang and Chih-Jen Lin
    All rights reserved.
'''

import random
import pdb
import os
import math
import pickle
import dataset
from operator import itemgetter


import learners.base_svm_learner as base_svm_learner
import learners.simple_svm_learner as simple_learner
import learners.random_svm_learner as random_learner
import learners.pal_svm_learner as pal_learner
import learners.co_test_svm_learner as co_test_learner
import learners.stacked_svm_learner as stacked_svm_learner
#import learners.weighted_stacked_svm_learner as weighted_stacked_svm_learner
#import learners.graph_learner as graph_learner
import learners.term_learner as term_learner
#import learners.MAOP_learner as MAOP_learner
#import learners.span_learner as span_learner
#import learners.un_learner as un_learner
#import learners.nln_learner as nln_learner
#import learners.co_feature_learning as cfal_learner
#import learners.fake_learner as fake_learner
#import learners.collective_learner as collective_learner
#import learners.collective_author_learner as collective_author_learner
#import learners.pooling_multis as pm_learner
#import learners.base_nb_learner as nb_learner
#import learners.community_svm_learner as community_learner
#import learners.IR_learner as IR_learner
#import results_reporter



#import outlier_detection


import svm 
from svm import *
pprint_str = "".join(["*" for x in range(40)])

def pred_prob(committee, X):
    committee_sum = 0.0 # from the 11 (or whatever) committee members
    for learner in committee:
      probs_sum = 0.0 # from the different views
      for i, x_i in enumerate(X):
        probs_sum += learner.models[i].predict_probability(x_i)[1][1]
     
      committee_sum += probs_sum/float(len(X)) # average over views 
    return committee_sum/float(len(committee))
   
def abstrackr_predict(data_paths, committee_size=11):
    # first figure out which instances are and are not labeled
    a_dataset = dataset.build_dataset_from_file(data_paths[0])

    ###
    # figure out which instances are labeled and which are not.
    # each will (or better!) have the same set of labels
    labeled_ids = \
        [xid for xid in a_dataset.instances.keys() if a_dataset.instances[xid].label != "?"]

    unlabeled_ids = [xid for xid in a_dataset.instances.keys() if not xid in labeled_ids]

    if len(labeled_ids) < 100 or len(unlabeled_ids) == 0:
        return None

    # now build our datasets.
    train_datasets = [dataset.build_dataset_from_file(f, only_these = labeled_ids) for f in data_paths]
    
    # make sure we have at least one positive (minority)
    if train_datasets[0].number_of_minority_examples() == 0:
        return None

    test_datasets = [dataset.build_dataset_from_file(f, only_these = unlabeled_ids) for f in data_paths]
    
    # temporary fix for cases in which the key words are missing; in such
    # instances, the feature-space size will effectively be zero.
    if train_datasets[-1].num_features() < 5:
        print "dropping keywords!"
        train_datasets = train_datasets[:-1]
        test_datsets = test_datasets[:-1]
   
    ####
    # build our ensemble
    committee = []
    param = svm_parameter(kernel_type=LINEAR, probability=1) # adding probability estimation 5/4/12
    for i in xrange(committee_size):
        learner = simple_learner.SimpleLearner(\
                [d.copy() for d in train_datasets], undersample_before_eval=True, svm_params=param)
        learner.label_all_data()
        print "training learner %s..." % i
        #try:
        learner.rebuild_models(for_eval=True)#, do_grid_search=True)
        
        #except:
        #    pdb.set_trace()
        #    print "ah -- something went wrong building an SVM. returning nothing"
        #    return None
        print "done."
        committee.append(learner)

    # make predictions
    prediction_dict = {} # map instance ids to predictions
    test_ids = test_datasets[0].get_instance_ids()

    for xid in test_ids:
        X_vec = [d.get_point_for_id(xid) for d in test_datasets]
        committee_predictions = [learner.predict(X=X_vec) for learner in committee]

        # probability estimates, a la UAI
        #committee_probs = [pred_prob(learner, X_vec) for learner in committee]
        #overall_prob = sum(committee_probs)/float(len(committee_probs))
        overall_prob = pred_prob(committee, X_vec)

        yes_votes = committee_predictions.count(1)
        confidence = None
        if yes_votes >= len(committee)/2.0:
            prediction = 1.0
        else:
            prediction = -1.0
            no_votes = committee_size-yes_votes
        
        prediction_dict[xid] = {"prediction":prediction, "num_yes_votes":yes_votes, "pred_prob":overall_prob}
    
    train_size = len(train_datasets[0])
    num_positives = train_datasets[0].number_of_minority_examples()

    return prediction_dict, train_size, num_positives


def run_experiments_finite_pool(data_paths, out_path, datasets_for_eval = None, upto=None, step_size = 25, 
                                                    initial_size = 2, batch_size = 5, num_runs=10,  pick_balanced_initial_set = True,
                                                    report_results_after_runs=False, list_of_init_ids=None):
    '''
    This method is for evaluation of learners in 'finite-pool' scenarios, i.e., when one wants to evaluate
    performance *only* over the instances in the pool U. Thus the predictive performance is less
    important here than it is in the holdout evaluations. Finite pool evaluations work by allowing each
    learner to pick m examples from U, then evaluating their predictive performance over the remaining
    N-m unlabeled instances, and combining this evaluation with the TPs and TNs requested during learning.
    '''
    if not os.path.isdir(out_path):
        _mkdir(out_path)  
     
    print data_paths   
    
    for run in range(num_runs):
        print "\n********\non run %s\n" % run

        num_labels_so_far = initial_size # set to initial size for first iteration

        # if a string (pointing to a single dataset) is passed in, box it in a list
        data_paths = box_if_string(data_paths)
        # note that we're assuming special, multi-label formatted data files here
        # ie., we assume both level1 and level2 labels are provided in the data
        # file.
        datasets = [dataset.build_dataset_from_file(f, name=os.path.basename(f)) for f in data_paths]
        total_num_examples = len(datasets[0].instances) # N = |U|
                    
                
        # if no upper bound was passed in, use the whole pool U
        if upto is None:
            upto = total_num_examples
                
        print "U has cardinality: %s" % datasets[0].size()
        
        ################################
        #  Here we set the learners up #
        ################################
        
        rando_reg = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=True)
        rando_reg.name="random"

        simp = simple_learner.SimpleLearner([d.copy() for d in datasets], undersample_before_eval=True)
        simp.name = "simp"
        
        cheat_path = "data/proton_beam/proton_community_cheating"
        cheat_list = eval(open(cheat_path).readline())
        comm = community_learner.CommunityLearner(cheat_list, [d.copy() for d in datasets], undersample_before_eval=True)
        comm.name = "comm"

        # Here's the list of learners
        learners = [rando_reg, simp, comm]
         
        #learners = [rand_learner, simp_learner, pal, maop_l]#, maop_l, maop_l2, term_l2]
        #for learner in learners:
        #    learner.predict_func = learner.majority_predict
        
        # For yield/burden output
        output_file_paths = [os.path.join(out_path, learner.name + "_" + str(run) + ".txt") for learner in learners]
        print output_file_paths
        output_files = [open(output_file, 'w') for output_file in output_file_paths]
        

        # Also write out the false negative ids for each learner since these are of particular interest
        output_fn_paths = [os.path.join(out_path, learner.name + "_FNs_" + str(run) + ".txt") for learner in learners]
        fn_out_files = [open(output_fn, 'w') for output_fn in output_fn_paths]
        
        cur_size = initial_size
        total_num_examples = len(datasets[0].instances)
        
        # we arbitrarily pick the initial ids from the first learner; this doesn't matter, as we just use the instance ids
        initial_f = learners[0].get_random_unlabeled_ids 
        init_size = num_labels_so_far
        if pick_balanced_initial_set:
            initial_f = learners[0].pick_balanced_initial_training_set
            init_size = int(num_labels_so_far/2.0) # equal number from both classes
            
        # again, you could call *.initial_f on any learner -- it just returns the ids to label initially. these will
        # be the same for all learners.
        init_ids = None
        if list_of_init_ids is None:
            init_ids =initial_f(init_size)
        else:
            init_ids = list_of_init_ids[run]
        
 
        # label instances and build initial models
        for learner in learners:
            print "on learner %s" % learner.name
            learner.label_instances_in_all_datasets(init_ids)
            learner.rebuild_models(for_eval=True, do_grid_search=True)

        # report initial results, to console and file.
        #report_yield_burden(learners, output_files, fn_out_files)
        #kdd_report(learners, output_files)
        finite_pool_report(learners, output_files, write_out_headers=True, ensembles=True)
        
        first_iter = True
        while num_labels_so_far <= upto - step_size:
            print "entering active learning loop..."
            #
            # the main active learning loop
            #
            cur_step_size = step_size
            cur_batch_size = batch_size
            if first_iter:
                # here we account for the initial labeled dataset size. for example, suppose
                # the step_size is set to 25 (we want to report results every 25 labels), 
                # but the initial size was 2; then we want to label 23 on the first iteration
                # so that we report results when 25 total labels have been provided
                cur_step_size = step_size - num_labels_so_far if num_labels_so_far <= step_size \
                                else step_size - (num_labels_so_far - step_size)
                # in general, step_size is assumed to be a multiple of batch_size, for the first iteration, 
                # when we're catching up to to the step_size (as outlined above), we set the
                # batch_size to 1 to make sure this condition holds.
                cur_batch_size = 1 
                first_iter = False
            
            for learner in learners:
                print "learner: %s" % learner.name
                if learner.models is None:
                    pdb.set_trace()
                learner.active_learn(cur_step_size, batch_size = cur_batch_size)

                            
            num_labels_so_far += cur_step_size
            print "\n***labeled %s examples out of %s so far***\n" % (num_labels_so_far, upto)

            # do a final rebuild before evaluating the learners; 
            # we do this because we may want to alter the parameters of the training
            # algorithm for the final classifier to be used in evaluation
            for learner in learners:
                learner.rebuild_models(for_eval=True, do_grid_search=True)

            #report_yield_burden(learners, output_files, fn_out_files)
            #kdd_report(learners, output_files)
            finite_pool_report(learners, output_files, ensembles=True)
            
            
            
        # close files
        for output_file, out_fn_file in zip(output_files, fn_out_files):
            output_file.close()
            out_fn_file.close()

    
    # post-experimental reporting
    if report_results_after_runs:
        results_reporter.report_yield_burdens(out_path, [learner.name for learner in learners],  num_runs)



def finite_pool_report(learners, output_files, write_out_headers=False, ensembles=False):
    for learner, output_file in zip(learners, output_files):
        print "\n\n"
        print "evaluating %s..." % learner.name
        results = None
        if not ensembles:
            results = kdd_evaluate_finite_pool_learner(learner)
        else:
            results = evaluate_ensemble_finite_pool(learner)
        for key,val in results.items():
            print "%s: %s" % (key, val)
        print pprint_str
        metric_keys = results.keys()
        print "these are the metrics I'm reporting: %s" % str(metric_keys)
        print pprint_str
        print "results for %s" % learner.name
        write_out_results(results, output_file, write_headers=write_out_headers, metrics = metric_keys)
        
            
def report_yield_burden(learners, output_files, output_fn_files):
    '''
    Calculate the yield/burden over the (finite-pool) learners
    '''
    for learner, output_file, output_fn_file in zip(learners, output_files, output_fn_files):
        print "\n" + pprint_str
        print learner.name
        print "results for %s @ %s labeled examples:" % (learner.name, len(learner.labeled_datasets[0]))
        print "using query function %s" % learner.query_function.func_name
        print "number of level 1 +s: %s, level 2 +s: %s" % (learner.labeled_datasets[0].number_of_minority_examples(), 
                                                                                        learner.labeled_datasets[0].number_of_l2_positives())
        results = evaluate_finite_pool_learner(learner)
        for key,val in results.items():
            if key != "fns" and key != "tns":
                print "%s: %s" % (key, val)
        print pprint_str
        print "\n"
        
        # write out level 2 false negative ids
        output_fn_file.write(", ".join([str(id) for id in results["fns"]]))
        output_fn_file.write("\n")
        # yield/burden
        write_out_results(results, output_file, metrics = ["num_labels", "yield", "burden"])
        

def retro_diversity(data_paths):
    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
    pal = pal_learner.PALLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    pal.name = "PAL"
    pal.longer_name = "PAL; linear kernel, with regular undersampling"
    pal.predict_func  = pal.majority_predict
    print "figuring out which examples are labeled.."
    instance_dict =  pal.unlabeled_datasets[0].instances
    
    # label those instances that actually.. have labels
    labeled_set = [x_id for x_id in instance_dict.keys() if instance_dict[x_id].label != "?"]
    pal.label_instances_in_all_datasets(labeled_set)
    pal.rebuild_models()
    smoothed = pal.check_if_we_should_switch_to_exploit()
    pdb.set_trace()
    
    
def relabel(data_paths):
    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
    total_num_examples = len(datasets[0])
    
    print "curious snake -- NOT UNDERSAMPLING"
    svm_learner = simple_learner.SimpleLearner ([d.copy() for d in datasets], 
                                                                        undersample_before_eval=False)    
    svm_learner.predict_func = svm_learner.at_least
    svm_learner.name = "SVM_Learner"
    
    
    print "figuring out which examples are labeled.."
    instance_dict =  svm_learner.unlabeled_datasets[0].instances
    # label those instances that actually.. have labels
    labeled_set = [x_id for x_id in instance_dict.keys() if instance_dict[x_id].label != "?"]
    svm_learner.label_instances_in_all_datasets(labeled_set)
    print "done. there are %s labeled instances." % len(svm_learner.labeled_datasets[0])
    
    print "training..."
    svm_learner.rebuild_models()
    
    T = svm_learner.labeled_datasets[0] # train set
    rejects = [xid for xid in T.instances.keys() if T.instances[xid].label < 0]
    rejects_to_dists = {}
    for xid in rejects:
        dist = svm_learner.models[0].distance_to_hyperplane(T.get_point_for_id(xid))
        rejects_to_dists[xid] = dist

    from operator import itemgetter
    items = rejects_to_dists.items()
    items.sort(key = itemgetter(1), reverse=True)
    return items
    
def prospective_active_learn(data_paths, out_file, k=20):
    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
    total_num_examples = len(datasets[0])
    
      
    print "curious snake -- NOT UNDERSAMPLING"
    svm_learner = simple_learner.SimpleLearner ([d.copy() for d in datasets], 
                                                                        undersample_before_eval=False)    
    svm_learner.predict_func = svm_learner.at_least
    svm_learner.name = "SVM_Learner"
    
    print "figuring out which examples are labeled.."
    instance_dict =  svm_learner.unlabeled_datasets[0].instances
    # label those instances that actually.. have labels
    labeled_set = [x_id for x_id in instance_dict.keys() if instance_dict[x_id].label != "?"]
    svm_learner.label_instances_in_all_datasets(labeled_set)
    print "done. there are %s labeled instances." % len(svm_learner.labeled_datasets[0])
    
    # train
    print "training..."
    svm_learner.rebuild_models()
    
    pdb.set_trace()
    
    # let's pick some more docs to label
    docs_to_label = svm_learner.query_function(k)
    
    print "writing out to %s..." % out_file

    fout = open(out_file, 'w')
    fout.write("\n".join([str(x) for x in docs_to_label]))
    fout.close()
    print "done."
    return docs_to_label
    
def prospective(data_paths,  out_dir, out_file, undersampling=True, beta=10, datasets=None, committee_size=11):
    print "\n****\nprospective\nusing beta: %s" % beta
    if datasets is None:
        data_paths = box_if_string(data_paths)
        datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
        
    total_num_examples = len(datasets[0])
    

    svm_learner = simple_learner.SimpleLearner ([d.copy() for d in datasets], 
                                                                        undersample_before_eval=True)    
    svm_learner.predict_func = svm_learner.at_least
    svm_learner.name = "SVM_Learner"
    
    print "figuring out which examples are labeled.."
    instance_dict =  svm_learner.unlabeled_datasets[0].instances
    # label those instances that actually.. have labels
    labeled_set = [x_id for x_id in instance_dict.keys() if instance_dict[x_id].label != "?"]
    svm_learner.label_instances_in_all_datasets(labeled_set)
    svm_learner.rebuild_models(for_eval=True, do_grid_search=True)
    
    print "done. there are %s labeled instances." % len(svm_learner.labeled_datasets[0])
    

    
    # let's pick some more docs to label
    #docs_to_label = svm_learner.query_function(200)
    # ensemble time?
    print "building a committee..."
    committee = []
    for i in range(committee_size):
        learner = simple_learner.SimpleLearner([d.copy() for d in datasets], undersample_before_eval=True)
        learner.label_instances_in_all_datasets(labeled_set)
        print "training learner %s..." % i
        learner.rebuild_models(for_eval=True, do_grid_search=True)
        print "done."
        committee.append(learner)
    
    print "ok -- committee built; assembling test sets..."
        

    print "predicting..."
    ids, predictions = [], []
    out_str = []
    for x_id in svm_learner.unlabeled_datasets[0].get_instance_ids():
        committee_preds = [svm_learner.predict(x_id) for svm_learner in committee]
        prediction = 1.0 if committee_preds.count(1.0) > committee_preds.count(-1.0) else -1.0
        #prediction = svm_learner.predict(x_id)
        predictions.append(prediction)
        ids.append(x_id)
        out_str.append("%s: %s" % (x_id, prediction))
    

    ids_to_predicts = dict(zip(ids, predictions))
    ids_to_confs = {}
    pos_preds = [x_id for x_id in ids_to_predicts.keys() if ids_to_predicts[x_id] > 0]

    outf = open("pos_preds.csv", 'w')
    outf.write("\n".join([str(x) for x in pos_preds]))
    #for x_id in svm_learner.unlabeled_datasets[0].get_instance_ids():
        #dist_to_h = svm_learner.models[1].distance_to_hyperplane()
        #predictions.append(prediction)
        #ids.append(id)
        #out_str.append("%s: %s" % (x_id, prediction))
        
        
    print "done."
    if not os.path.isdir(out_dir):
        _mkdir(out_dir)  
        
    pdb.set_trace()
    fout = open(os.path.join(out_dir, out_file), 'w')
    fout.write("\n".join(out_str))
    fout.close()
    
    p_pos = float(len([x for x in predictions if x>0]))/float(len(predictions))

    print p_pos
    return (pos_preds, svm_learner.unlabeled_datasets[0].instances.keys())

def mice(data_path, outpath, committee_size=3):
    if not os.path.isdir(outpath):
        _mkdir(outpath)  
    
    data = dataset.build_dataset_from_file(data_path, ignore_unlabeled_instances=True)
    all_ids = data.instances.keys()
    n = len(all_ids)
    train_len = int(float(n)/2.0) # close enough
    train_ids = all_ids[:train_len]
    test_ids = all_ids[train_len:]
    instances = data.remove_instances(test_ids)
    new_d = dict(zip([x.id for x in instances], [x for x in instances]))
    test_dataset = dataset.dataset(new_d)
    
    #last_xid=1
    '''
    cur_in_seizure = False
    for xid in data.get_instance_ids():
        lbl = data.instances[xid].label
        if not cur_in_seizure and lbl==1:
            cur_in_seizure=True
            data.instances[xid].label = -1
        elif cur_in_seizure and lbl==-1:
            data.instances[xid-2].label = 1
            data.instances[xid-1].label = 1
            cur_in_seizure=False
        elif cur_in_seizure:
            data.instances[xid].label = -1
            
    ''' 
           
        
        
    committee=[]
    #test_dataset = dataset.build_dataset_from_file(data_path, only_these=test_ids)
    for i in range(committee_size):
        learner = simple_learner.SimpleLearner([data.copy()], undersample_before_eval=True)
        #learner.weights = [1,1]
        learner.label_instances_in_all_datasets(train_ids)
        print "training learner %s..." % i
        learner.rebuild_models(for_eval=True, do_grid_search=False, beta=10)
        print "done."
        committee.append(learner)
              
    results = evaluate_ensemble_mice(committee, [test_dataset])       
    output_file = open(os.path.join(outpath, "mice.txt"), 'w')                                       
    write_out_results(results, output_file, write_headers=True)
    output_file.close()
    
    
def forest_cv(data_paths, outpath, nfolds=10, beta=10, committee_size=11, undersample=True):
        
    if not os.path.isdir(outpath):
        _mkdir(outpath)  
        
    list_of_test_instance_ids = None
    datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in data_paths]
    fold_size = int((1.0/float(nfolds))*len(datasets[0]))
    print "fold size: %s" % fold_size
    # shuffle the ids
    list_of_ids = datasets[0].instances.keys()
    #random.shuffle(list_of_ids)
    list_of_test_instance_ids = [l for l in chunks([x_id for x_id in list_of_ids], fold_size)]
                                              
    for run in range(nfolds):
        print "\n********\non fold %s" % run
        test_instance_ids = list_of_test_instance_ids[run]
        train_ids = [x_id for x_id in list_of_ids if not x_id in test_instance_ids]
        test_datasets = [dataset.build_dataset_from_file(f, only_these = test_instance_ids) for f in data_paths]
        # building a forest!
        committee = []
        for i in range(committee_size):
            learner = simple_learner.SimpleLearner([d.copy() for d in datasets], undersample_before_eval=undersample)
            #learner.weights = [1,1]
            learner.label_instances_in_all_datasets(train_ids)
            print "training learner %s..." % i
            learner.rebuild_models(for_eval=True, do_grid_search=False, beta=beta)
            print "done."
            committee.append(learner)
        
        output_file = open(os.path.join(outpath,"committee_%s.txt" % run), 'w')
        ensemble_report_results(committee, test_datasets, output_file, write_headers=True)
        
        output_file.close()
        
     
def forest_train_test(train_data_paths, test_data_paths, outpath, out_f_name,\
                         beta=1, committee_size=11, undersample=True, weights=[1,1],
                         num_runs=1, do_grid_search=True):
        
    if not os.path.isdir(outpath):
        _mkdir(outpath)  
        
    train_datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in train_data_paths]
    test_datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in test_data_paths]
                   
    for run in range(num_runs):
        # building a forest!
        committee = []
        for i in range(committee_size):
            learner = simple_learner.SimpleLearner([d.copy() for d in train_datasets], undersample_before_eval=undersample)
            learner.weights = weights
            learner.label_all_data()
            print "training learner %s..." % i
            learner.rebuild_models(for_eval=True, do_grid_search=do_grid_search, beta=beta)
            #pdb.set_trace()
            print "done."
            committee.append(learner)
        
        print "\n\nresults ON TRAIN set"
        output_file = open(os.path.join(outpath, out_f_name + "_on_%s_%s.csv"%(os.path.basename(train_data_paths[0]), run)), 'w')
        pfile = open(os.path.join(outpath, out_f_name + "_on_%s_%s.predictions"%(os.path.basename(train_data_paths[0]), run)), 'w')
        ensemble_report_results(committee, train_datasets, output_file, write_headers=True, predictions_file=pfile)
        pfile.close()
        output_file.close()
    
        print "\n\nresults ON TEST set"
        output_file = open(os.path.join(outpath, out_f_name + "_on_%s_%s.csv"%(os.path.basename(test_data_paths[0]), run)), 'w')
        pfile = open(os.path.join(outpath, out_f_name + "_on_%s_%s.predictions"%(os.path.basename(test_data_paths[0]), run)), 'w')
        ensemble_report_results(committee, test_datasets, output_file, write_headers=True, predictions_file=pfile)
        pfile.close()
        output_file.close()
                                                      
        
        
def run_ICML_experiments_with_test_data(train_data_path, test_data_path, outpath):
    if not os.path.isdir(outpath):
        _mkdir(outpath)
        
    train_datasets = [dataset.build_dataset_from_file(train_data_path)]
    test_datasets = [dataset.build_dataset_from_file(test_data_path)] 
    
    naive_learner = nb_learner.BaseNBLearner([d.copy() for d in train_datasets], \
                                            undersample_before_eval = False)
    naive_learner.label_all_data()
    naive_learner.rebuild_models(for_eval=True)
    naive_learner.name = "NaiveBayes"
    #nb_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
    
    # ... and, the multinomial learner
    '''
    pos_f_ids_file = "data/movies/positive_indices"
    neg_f_ids_file = "data/movies/negative_indices"
    # m is the size of the vocabulary, i.e., the dimensionality of our feature space
    m_train = max([max(inst.point.keys()) for inst in train_datasets[0].instances.values()])
    m_test  = max([max(inst.point.keys()) for inst in test_datasets[0].instances.values()])
    m = max(m_train, m_test)
    print "\nm is: %s" % m
    multi_learner = pm_learner.PMLearner(pos_f_ids_file, neg_f_ids_file, m, unlabeled_datasets = [d.copy() for d in train_datasets], \
                                            undersample_before_eval = False, r=100, pc=.5)
    multi_learner.name = "Pooler"
    multi_learner.label_all_data()
    multi_learner.rebuild_models(for_eval=True)
    #multi_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
    '''
        
    nb_learners = [naive_learner]#, multi_learner]
    output_files = [open(os.path.join(outpath, learner.name), 'w') for learner in nb_learners]
    for outf in output_files:
        outf.write(",".join(["tps", "tns", "fps", "fns", "size", "accuracy", "sensitivity", "specificity"]))
        outf.write("\n")
        
    for learner, output_file in zip(nb_learners, output_files):
        predictions, true_labels = [], []
        for x in test_datasets[0].instances.values():
            predictions.append(learner.predict(x))
            true_labels.append(x.label)
            
        conf_mat =  _evaluate_predictions(predictions, true_labels)
        results={"size":len(learner.labeled_datasets[0])}
        _calculate_metrics(conf_mat, results)
        write_out_results(results, output_file)
        
    for f in output_files:
        f.close()
    print "DONE."    
    
    
def run_movies_experiments(train_paths, test_path, outpath, rseed=12345):
    
    random.seed(rseed) # in honor of Tom
    
    if not os.path.isdir(outpath):
        _mkdir(outpath)
        
    train_datasets = [dataset.build_dataset_from_file(f) for f in train_paths]
    test_dataset = dataset.build_dataset_from_file(test_path)
    
    # svm learner
    '''
    svm_learner = simple_learner.SimpleLearner(train_datasets, undersample_before_eval=False)
    svm_learner.label_all_data()
    svm_learner.rebuild_models(for_eval=True, do_grid_search=True, beta=1)
    
    results = evaluate_learner_with_holdout(svm_learner, len(train_datasets[0]), [test_dataset])    
    fout = open(os.path.join(outpath, "vanilla_svm"), 'w')
    write_out_results(results, fout)
    fout.close()
    '''

    naive_learner = nb_learner.BaseNBLearner([d.copy() for d in train_datasets], \
                                            undersample_before_eval = False)
    naive_learner.label_all_data()
    naive_learner.rebuild_models(for_eval=True)
    naive_learner.name = "NaiveBayes"
    #nb_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
    
    # ... and, the multinomial learner
    pos_f_ids_file = "data/movies/positive_indices"
    neg_f_ids_file = "data/movies/negative_indices"
    # m is the size of the vocabulary, i.e., the dimensionality of our feature space
    m_train = max([max(inst.point.keys()) for inst in train_datasets[0].instances.values()])
    m_test  = max([max(inst.point.keys()) for inst in test_dataset.instances.values()])
    m = max(m_train, m_test)
    print "\nm is: %s" % m
    multi_learner = pm_learner.PMLearner(pos_f_ids_file, neg_f_ids_file, m, unlabeled_datasets = [d.copy() for d in train_datasets], \
                                            undersample_before_eval = False, r=100, pc=.5)
    multi_learner.name = "Pooler"
    multi_learner.label_all_data()
    multi_learner.rebuild_models(for_eval=True)
    #multi_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
        
    nb_learners = [naive_learner, multi_learner]
    output_files = [open(os.path.join(outpath, learner.name), 'w') for learner in nb_learners]
    
    for learner, output_file in zip(nb_learners, output_files):
        predictions, true_labels = [], []
        for x in test_dataset.instances.values():
            predictions.append(learner.predict(x))
            true_labels.append(x.label)
            
        conf_mat =  _evaluate_predictions(predictions, true_labels)
        results={"size":len(learner.labeled_datasets[0])}
        _calculate_metrics(conf_mat, results)
        write_out_results(results, output_file)

    for f in output_files:
        f.close()
    print "DONE."
                                            
def run_cv_experiments_with_test_data(data_paths, test_data_paths, outpath, test_datasets=None, hold_out_p=0.25, 
                                                    report_results_after_runs=False, num_runs=10, undersampling=True, 
                                                    beta=10, n_fold_cv=True):
    '''
    Runs n-fold cross-validation over data
    '''
    if not os.path.isdir(outpath):
        _mkdir(outpath)  
        

    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in data_paths]
    
    ### largest feature index

    #m = max([max(inst.point.keys()) for inst in datasets[0].instances.values()])
    
    # separate test datasets
    if test_datasets is not None and not n_fold_cv:
        test_datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in test_data_paths]
        total_num_examples = len(test_datasets[0])
        hold_out_size = int(hold_out_p * total_num_examples)
    else:
        total_num_examples = len(datasets[0])
        
    list_of_test_instance_ids = None
    n=num_runs
    if n_fold_cv:
        print "cross-fold validation"
        fold_size = int((1.0/float(n))*len(datasets[0]))
        print "fold size: %s" % fold_size
        # shuffle the ids
        list_of_ids = datasets[0].instances.keys()
        random.shuffle(list_of_ids)
        list_of_test_instance_ids = [l for l in chunks([x_id for x_id in list_of_ids], fold_size)]
    
            
    for run in range(num_runs):
        print "\n********\non %s %s" % ("fold" if n_fold_cv else "run", run)
        test_instance_ids = None if not n_fold_cv else list_of_test_instance_ids[run]
            
        #
        # Set up the learners
        #
        
        '''
        # first, the naive bayes model
        naive_learner = nb_learner.BaseNBLearner([d.copy() for d in datasets], undersample_before_eval=True)
        naive_learner.name = "NaiveBayes"
        #nb_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
        
        # ... and, the multinomial learner
        pos_f_ids_file = "data/copd/icml/pos_feature_ids"
        neg_f_ids_file = "data/copd/icml/neg_feature_ids"
        print "\nm is: %s" % m
        multi_learner = pm_learner.PMLearner(pos_f_ids_file, neg_f_ids_file, m, unlabeled_datasets = [d.copy() for d in datasets], \
                                                undersample_before_eval=True, r=100, pc=.5)
        multi_learner.name = "Pooler"
        '''
        
        learners = [random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=True)]
        
        #learners = [naive_learner, multi_learner]
        output_files = [open("%s//%s_%s.txt" % (outpath, learner.name, run), 'w') for learner in learners]
    
        init_ids = [x_id for x_id in learners[0].get_unlabeled_ids() if not x_id in test_instance_ids]
        
        # label instances
        for learner in learners:
            print learner.name
            learner.label_instances_in_all_datasets(init_ids)
            learner.rebuild_models(for_eval=True) 
            
        '''
        #
        # build models; note that we make sure that the same examples
        # are undersampled from each set. this allows us to directly compare
        # classifier performance
        print "\n--rebuilding model(s) for %s--" % learners[0].name
        undersampled_ids = learners[0].rebuild_models(for_eval=True, do_grid_search=True, beta=1)
        ids_for_training = set(learners[0].labeled_datasets[0].instances.keys())
        for learner in learners[1:]:
            print "\n--rebuilding model(s) for %s--" % learner.name
            learner.rebuild_models(for_eval=True, undersample_these=undersampled_ids, 
                                                do_grid_search=True, beta=beta)
            
            # ascertaing that all learners have the same labeled examples
            assert(set(learner.labeled_datasets[0].instances.keys()) == ids_for_training)    
            
        '''
        
        labeled_ids = set(learners[0].labeled_datasets[0].instances.keys())
        unlabeled_ids = set(learners[0].unlabeled_datasets[0].instances.keys())
        for learner in learners[1:]:
            assert(set(learner.labeled_datasets[0].instances.keys()) == labeled_ids)
            assert(set(learner.unlabeled_datasets[0].instances.keys()) == unlabeled_ids)
        print "\n-- asserted that learners have the same train/test instances --\n"
        
        #false_negs_out = open("%s//false_negative_ids_%s" % (outpath, run), 'w')
        # (learner, num_labels, test_sets):
        #results = evaluate_learner_with_holdout(learners[0], len(learners[0].labeled_datasets[0]), None)
        report_results(learners, None,
                               len(learners[0].labeled_datasets[0]), output_files)

        for outf in output_files:
            outf.close()
            
 
def rank_uncertainties(data_paths):
    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in data_paths]
    
    total_num_examples = len(datasets[0])
    
    learners = [random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=False)]
      
             
    '''             
    #### commenting out term uncertainty stuff for now                                        
    pos_path = os.path.join("data", "crohns", "pos_terms")
    neg_path = os.path.join("data", "crohns", "neg_terms")
    
    abstracts_path = os.path.join("data", "crohns", "Abstracts")
    titles_path = os.path.join("data", "crohns", "Titles")

    
    cofl_learner = cfal_learner.CoFeatureLearner(pos_path, neg_path, None, abstracts_path, titles_path, 
                                                                            unlabeled_datasets=[d.copy() for d in datasets], undersample_before_eval=True)
    '''
                                                                        
    learners[0].label_all_data()
    learners[0].rebuild_models(for_eval=False, do_grid_search=True, beta=1)
    ids_to_dists = {}
    instances =  learners[0].labeled_datasets[0].instances
    for x_id in instances.keys():
        ids_to_dists[x_id] = learners[0].models[0].distance_to_hyperplane(instances[x_id].point)
    
    
    sorted_points = sorted(ids_to_dists.items(), key=itemgetter(1))
    #pdb.set_trace()
    #learners[0].cotest()
    '''
    ids_to_scores = {}
    for x_id in cofl_learner.unlabeled_datasets[0].instances.keys():
        #ids_to_scores[x_id] = cofl_learner.feature_vote(x_id, include_direction=False)
        #ids_to_scores[x_id] = cofl_learner.doc_length(x_id)
        lor = cofl_learner.feature_vote(x_id, include_direction=False, scaled=True)
        if lor is not None:
            ids_to_scores[x_id] = lor
    '''
    
    #outf = open("ids_to_scaled_feature_lors", 'w')
    #pickle.dump(ids_to_scores, outf)
    #outf.close()
    return sorted_points
    
def run_passive_mv_experiments(data_paths, outpath, hold_out_p=0.25, 
                                                    report_results_after_runs=False, num_runs=10, undersampling=True, 
                                                    beta=10, n_fold_cv=True):
    '''
    For passive (non-active) learning. 
    '''
    if not os.path.isdir(outpath):
        _mkdir(outpath)  
        
    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f, ignore_unlabeled_instances=True) for f in data_paths]
    
    total_num_examples = len(datasets[0])
    hold_out_size = int(hold_out_p * total_num_examples)
    # if a string (pointing to a single dataset) is passed in, box it in a list

    list_of_test_instance_ids = None
    n=num_runs
    if n_fold_cv:
        print "cross-fold validation"
        fold_size = int((1.0/float(n))*len(datasets[0]))
        print "fold size: %s" % fold_size
        # shuffle the ids
        list_of_ids = datasets[0].instances.keys()
        random.shuffle(list_of_ids)
        list_of_test_instance_ids = [l for l in chunks([x_id for x_id in list_of_ids], fold_size)]
    
            
    for run in range(num_runs):
        print "\n********\non %s %s" % ("fold" if n_fold_cv else "run", run)
        test_instance_ids = None if not n_fold_cv else list_of_test_instance_ids[run]
            
        #
        # Set up the learners
        #
        learners = [random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=undersampling)]
        
        #learners[0].undersample_function= learners[0].aggressive_undersample_labeled_datasets                                                            
        learners[0].predict_func = learners[0].at_least
        learners[0].name = "SVM_Learner"

        output_files = [open("%s//%s_%s.txt" % (outpath, learner.name, run), 'w') for learner in learners]
    
        if not n_fold_cv:
            # we arbitrarily pick the initial ids from the first learner; this doesn't matter, 
            # as we just use the instance ids
            initial_f = learners[0].get_random_unlabeled_ids
            init_size = len(datasets[0]) - hold_out_size
            init_ids =initial_f(init_size)
        else:
            init_ids = [x_id for x_id in learners[0].get_unlabeled_ids() if not x_id in test_instance_ids]
        
        # label instances
        for learner in learners:
            print learner.name
            learner.label_instances_in_all_datasets(init_ids)
            
    
        #
        # build models; note that we make sure that the same examples
        # are undersampled from each set. this allows us to directly compare
        # classifier performance
        print "\n--rebuilding model(s) for %s--" % learners[0].name
        learners[0].rebuild_models()
        undersampled_ids = learners[0].rebuild_models(for_eval=True, do_grid_search=True, beta=10)
        ids_for_training = set(learners[0].labeled_datasets[0].instances.keys())
        for learner in learners[1:]:
            print "\n--rebuilding model(s) for %s--" % learner.name
            learner.rebuild_models(for_eval=True, undersample_these=undersampled_ids, 
                                                do_grid_search=True, beta=beta)
            # ascertaing that all learners have the same labeled examples
            assert(set(learner.labeled_datasets[0].instances.keys()) == ids_for_training)    
            

        labeled_ids = set(learners[0].labeled_datasets[0].instances.keys())
        unlabeled_ids = set(learners[0].unlabeled_datasets[0].instances.keys())
        for learner in learners[1:]:
            assert(set(learner.labeled_datasets[0].instances.keys()) == labeled_ids)
            assert(set(learner.unlabeled_datasets[0].instances.keys()) == unlabeled_ids)
        print "\n-- asserted that learners have the same train/test instances --\n"
        
        false_negs_out = open("%s//false_negative_ids_%s" % (outpath, run), 'w')
        # (learner, num_labels, test_sets):
        #results = evaluate_learner_with_holdout(learners[0], len(learners[0].labeled_datasets[0]), None)
        report_results(learners, None,
                               len(learners[0].labeled_datasets[0]), output_files, fns_out=false_negs_out)

        for outf in output_files:
            outf.close()
        
        # @experimental 9/23/09
        # Note that we pass a list of None objects as the test_sets argument; this
        # tells the report_results to use the unlabeled examples in each of
        # our learners, which will be the same in this case
        #report_results_diff_test_sets(learners, [None for learner in learners], \
        #                                                output_files, init_size)
    
        #
        # here we write out raw predictions, etc., for ROC curve generation
        #
        '''
        learners_to_ids_to_preds = {}
        for learner in learners:
            preds_lbls_raw = learner.get_raw_predictions()
            ids = [x[0] for x in preds_lbls_raw]
            preds = [x[2] for x in preds_lbls_raw]
            ids_to_preds = dict(zip(ids, preds))
            learners_to_ids_to_preds[learner.name] = ids_to_preds
            preds_and_labels = ["\t".join([str(x) for x in l]) for l in preds_lbls_raw]
            preds_out = open("%s//%s_raw_predictions_%s.txt" % (outpath, learner.name, run), 'w') 
            preds_out.write("ids\tlabels\tpredictions\n")
            preds_out.write("\n".join(preds_and_labels))
            preds_out.close()
        
    
        rout = open("%s//heat_map_R_%s.txt" % (outpath, run), 'w') 
        rout.write("\t" + "\t".join([learner.name for learner in learners]) + "\n")
        for inst_id in learners_to_ids_to_preds[learners[0].name].keys():
            rout.write(str(inst_id) + "\t" + "\t".join([str(learners_to_ids_to_preds[l.name][inst_id]) for l in learners]))
            rout.write("\n")
        rout.close()
        '''
        
def collective_classification(data_paths,  outpath, xml_path, ids_to_groups_path=None, nfolds=2, undersampling=True, beta=10, datasets=None):
    print "\n****\n... collective classification ...: " 
    if not os.path.isdir(outpath):
        _mkdir(outpath)  
        
        
    data_paths = box_if_string(data_paths)
    datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
        
    total_num_examples = len(datasets[0])
    
    list_of_test_instance_ids = None

    print "building folds.."
    fold_size = int((1.0/float(nfolds))*len(datasets[0]))
    print "fold size: %s" % fold_size
    # shuffle the ids
    list_of_ids = datasets[0].instances.keys()
    random.shuffle(list_of_ids)
    list_of_test_instance_ids = [l for l in chunks([x_id for x_id in list_of_ids], fold_size)]
    print "ok"    

    
    for fold in range(nfolds):
        print "\n********\non fold %s" % fold
        test_instance_ids = list_of_test_instance_ids[fold]
            
        #
        # Set up the learners
        #
        cc_learner = collective_author_learner.CollectiveAuthorLearner([d.copy() for d in datasets], undersample_before_eval=True,\
                                                        xml_path=xml_path, ids_to_groups_path=ids_to_groups_path)    
                                                        
        simp_learner = simple_learner.SimpleLearner([d.copy() for d in datasets], undersample_before_eval=True)                                                     
        learners = [cc_learner, simp_learner]
    
        output_files = [open(os.path.join("%s" % outpath, "%s_%s.txt" % (learner.name, fold)), 'w') for learner in learners]
    
        init_ids = [x_id for x_id in learners[0].get_unlabeled_ids() if not x_id in test_instance_ids]
        
        # label instances
        for learner in learners:
            print learner.name
            learner.label_instances_in_all_datasets(init_ids)
            
        #####
        # collective classification time
        ####
        print "magic..."
        learners[0].ICA_train()
        #pdb.set_trace()
        print "ok magic."
        
        #
        # build models; note that we make sure that the same examples
        # are undersampled from each set. this allows us to directly compare
        # classifier performance
        print "\n--rebuilding model(s) for %s--" % learners[0].name
        undersampled_ids = learners[0].rebuild_models(for_eval=True, do_grid_search=True, beta=beta)
        ids_for_training = set(learners[0].labeled_datasets[0].instances.keys())
        for learner in learners[1:]:
            print "\n--rebuilding model(s) for %s--" % learner.name
            learner.rebuild_models(for_eval=True, undersample_these=undersampled_ids, 
                                                do_grid_search=True, beta=beta)
            # ascertaing that all learners have the same labeled examples
            assert(set(learner.labeled_datasets[0].instances.keys()) == ids_for_training)    
            

        labeled_ids = set(learners[0].labeled_datasets[0].instances.keys())
        unlabeled_ids = set(learners[0].unlabeled_datasets[0].instances.keys())
        for learner in learners[1:]:
            assert(set(learner.labeled_datasets[0].instances.keys()) == labeled_ids)
            assert(set(learner.unlabeled_datasets[0].instances.keys()) == unlabeled_ids)
        print "\n-- asserted that learners have the same train/test instances --\n"
        
        report_results(learners, None,
                               len(learners[0].labeled_datasets[0]), output_files)

        for outf in output_files:
            outf.close()
    
def run_movies_experiments(train_paths, test_path, outpath, rseed=12345):
    
    random.seed(rseed) # in honor of Tom
    
    if not os.path.isdir(outpath):
        _mkdir(outpath)
        
    train_datasets = [dataset.build_dataset_from_file(f) for f in train_paths]
    test_dataset = dataset.build_dataset_from_file(test_path)
    
    # svm learner
    '''
    svm_learner = simple_learner.SimpleLearner(train_datasets, undersample_before_eval=False)
    svm_learner.label_all_data()
    svm_learner.rebuild_models(for_eval=True, do_grid_search=True, beta=1)
    
    results = evaluate_learner_with_holdout(svm_learner, len(train_datasets[0]), [test_dataset])    
    fout = open(os.path.join(outpath, "vanilla_svm"), 'w')
    write_out_results(results, fout)
    fout.close()
    '''

    naive_learner = nb_learner.BaseNBLearner([d.copy() for d in train_datasets], \
                                            undersample_before_eval = False)
    naive_learner.label_all_data()
    naive_learner.rebuild_models(for_eval=True)
    naive_learner.name = "NaiveBayes"
    #nb_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
    
    # ... and, the multinomial learner
    pos_f_ids_file = "data/movies/positive_indices"
    neg_f_ids_file = "data/movies/negative_indices"
    # m is the size of the vocabulary, i.e., the dimensionality of our feature space
    m_train = max([max(inst.point.keys()) for inst in train_datasets[0].instances.values()])
    m_test  = max([max(inst.point.keys()) for inst in test_dataset.instances.values()])
    m = max(m_train, m_test)
    print "\nm is: %s" % m
    multi_learner = pm_learner.PMLearner(pos_f_ids_file, neg_f_ids_file, m, unlabeled_datasets = [d.copy() for d in train_datasets], \
                                            undersample_before_eval = False, r=100, pc=.5)
    multi_learner.name = "Pooler"
    multi_learner.label_all_data()
    multi_learner.rebuild_models(for_eval=True)
    #multi_results = evaluate_learner_with_holdout(multi_learner, len(train_datasets[0]), [test_dataset])  
        
    nb_learners = [naive_learner, multi_learner]
    output_files = [open(os.path.join(outpath, learner.name), 'w') for learner in nb_learners]
    
    for learner, output_file in zip(nb_learners, output_files):
        predictions, true_labels = [], []
        for x in test_dataset.instances.values():
            predictions.append(learner.predict(x))
            true_labels.append(x.label)
            
        conf_mat =  _evaluate_predictions(predictions, true_labels)
        results={"size":len(learner.labeled_datasets[0])}
        _calculate_metrics(conf_mat, results)
        write_out_results(results, output_file)

    for f in output_files:
        f.close()
    print "DONE."


    
def run_update_experiments(data_paths, train_ids, test_ids, outpath, committee_size = 11, nruns=1, rseed=12345):
    
    random.seed(rseed) # in honor of Tom
    
    if not os.path.isdir(outpath):
        os.mkdir(outpath)
        
    fns_out = open(os.path.join(outpath, "fn_ids.txt"), 'w')
        
    train_datasets = [dataset.build_dataset_from_file(f, only_these = train_ids) for f in data_paths]
    test_datasets = [dataset.build_dataset_from_file(f, only_these = test_ids) for f in data_paths]
    
    num_train_examples = len(train_datasets[0])
    print "there are %s training examples." % num_train_examples
    
    for run in range(nruns):
        committee = []
        for i in range(committee_size):
            learner = simple_learner.SimpleLearner([d.copy() for d in train_datasets], undersample_before_eval=True)
            learner.label_all_data()
            print "training learner %s..." % i
            learner.rebuild_models(for_eval=True)#, do_grid_search=True)
            print "done."
            committee.append(learner)
        
        print "ok -- committee built; assembling test sets..."
        
        #report_results([learner], test_datasets, num_labels_so_far, output_files)
        outf = open(os.path.join(outpath, str(run)), 'w')
        results = ensemble_report_results(committee, test_datasets, outf)
        fns_out.write(", ".join([str(x) for x in results["fn_ids"]]))
        fns_out.write("\n")
        outf.close()
    fns_out.close()
  
def run_experiments_hold_out_ECML(data_paths, outpath, hold_out_p = 0.25, datasets_for_eval = None, upto = 1000, step_size = 25,
                                                  initial_size = 2, batch_size = 5, pick_balanced_initial_set = True,
                                                  num_runs=10, report_results_after_runs=True):
    '''
    This method demonstrates how to use the active learning framework, and is also a functional routine for comparing learners. Basically,
    a number of runs will be performed, the active learning methods will be evaluated at each step, and results will be reported. The results
    for each run will be dumped to a text files, which then can be combined (e.g., averaged), elsewhere, or you can use the results_reporter
    module to aggregate and plot the output.
    @parameters
    --
    data_paths -- this is either a list (pointing to multiple feature spaces for the same instances) or a string pointing to a single data file (this will be
    the typical case). e.g., data_paths = "mydata.txt". curious_snake uses a sparse-formated weka-like format, documented elsewhere.
    outpath -- this is a directory under which all of the results will be dumped.
    hold_out_p -- the hold out percentage, i.e., how much of your data will be used for evaluation. you can ignore this is you're providing your own
    dataset(s) for evaluation (i.e., datasets_for_eval is not None)'.
    datasets_for_eval -- use this is you have datasets you want to use for testing -- i.e., to specify your hold out set independent of the data
    in data_paths.
    upto -- active learning will stop when upto examples have been labeled. if this is None, upto will default to the total unlabeled pool available
    initial_size -- the size of 'bootstrap' set to use prior to starting active learning (for the initial models)
    batch_size -- the number of examples to be labeled at each iteration in active learning -- optimally, 1
    step_size -- results will be reported every time another step_size examples have been labeled
    pick_balanced_initial_set -- if True, the initial train dataset will be built over an equal number (initial_size/2) of both classes.
    num_runs -- this many runs will be performed
    report_results -- if true, the results_reporter module will be used to generate output.
    '''
    
    if not os.path.isdir(outpath):
        os.mkdir(outpath)
        
    for run in range(num_runs):
        print "\n********\non run %s" % run
 
        print data_paths
        num_labels_so_far = initial_size # set to initial size for first iteration
         
        # if a string (pointing to a single dataset) is passed in, box it in a list
        data_paths = box_if_string(data_paths)
        datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
        original_datasets = [d.copy() for d in datasets]
        
        #####
        # @ experimental -- experimenting with augmented feature vectors -- remove when done
        #communities =  dataset.build_dataset_from_file("data/copd/copd_communities")
        communities =  dataset.build_dataset_from_file("data/proton_beam/proton_communities")
        communities_only = [communities.copy()]
        combined_datasets = [dataset.combine_datasets(datasets[0], communities)]
        #####
        
        total_num_examples = len(datasets[0])

        test_datasets = []
        #### @ experimental 
        test_datasets_combined = [] 
        test_communities = []
        ####
        
        if datasets_for_eval is not None:
            # if a test set datafile is specified, use it.
            datasets_for_eval = box_if_string(datasets_for_eval)
            test_datasets = [dataset.build_dataset_from_file(f) for f in datasets_for_eval]
            # currently no way to join externally provided test sets!
            if upto is None:
                upto = total_num_examples
        else:
            # other wise, we copy the first (even if there are multiple datasets, it won't matter,
            # as we're just using the labels) and pick random examples
            hold_out_size = int(hold_out_p * total_num_examples)
            
            test_instance_ids = random.sample(datasets[0].instances, hold_out_size)
            # now remove them from the dataset(s)
            for d in datasets:
                cur_test_dataset = dataset.dataset(dict(zip(test_instance_ids, d.remove_instances(test_instance_ids))), name=d.name)
                test_datasets.append(cur_test_dataset)
                
            #### @ experimental
            for d in combined_datasets:
                cur_test_dataset = dataset.dataset(dict(zip(test_instance_ids, d.remove_instances(test_instance_ids))), name=d.name)
                test_datasets_combined.append(cur_test_dataset)                

            for d in communities_only:
                cur_test_dataset = dataset.dataset(dict(zip(test_instance_ids, d.remove_instances(test_instance_ids))), name=d.name)
                test_communities.append(cur_test_dataset)    
                
                  
            #####
            
            
            # if no upper bound was passed in, use the whole pool U
            if upto is None:
                upto = total_num_examples - hold_out_size
                
        print "using %s out of %s instances for test set" % (hold_out_size, total_num_examples)
        print "U has cardinality: %s" % datasets[0].size()
        
        # e.g., _setup_fv_learners
        #print "need to call one of the setup* functions -- no learners specified!"
        #learners =None
        #
        # @TODO parameterize undersampling
        #
        
        #learners =_setup_PAL_learner(datasets, undersampling=True)
        #learners = _setup_psuedo_PALs(datasets, undersampling=True)
        #learners = _setup_graph(datasets)
        #learners = _setup_cofl(datasets)
        #learners = _setup_span(datasets)
        #ir = IR_learner.IRLearner([d.copy() for d in datasets], undersample_before_eval=True, \
        #                            pos_terms=os.path.join("data", "proton_beam", "new_pos_terms"), \
        #                            whoosh_index_path = os.path.join("data","proton_beam", "proton_index"))

        
        print "\n OK -- combined datasets!!!"
        #simp =  simple_learner.SimpleLearner([d.copy() for d in datasets], undersample_before_eval=True)
        rando_reg = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=True)
        rando_reg.name="random_regular"
        
        rando_comb = random_learner.RandomLearner([d.copy() for d in combined_datasets], undersample_before_eval=True)
        rando_comb.name = "random_combined"
        
        rando_comm = random_learner.RandomLearner([d.copy() for d in communities_only], undersample_before_eval=True)
        rando_comm.name = "comm_only"
        
        rando_reg2 = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=True)
        rando_reg2.name = "rando2"
        
        ###### @ experimental 
        ####
        # @TODO build collective_author_learner here!
        ####
        xml_path = os.path.join("data", "proton_beam", "proton_author_network.xml")
        ids_to_groups_path = os.path.join("data", "proton_beam", "proton_ids_to_groups")
        ### note that the collective learner gets the 'original' datasets, because it needs access to both the
        # labeled and unlabeled instances in the network. 
        collective = collective_author_learner.CollectiveAuthorLearner([d.copy() for d in original_datasets], undersample_before_eval=True, \
                                                        xml_path=xml_path, ids_to_groups_path=ids_to_groups_path)
        collective.name = "collective"
        
        #learners = [rando_reg, rando_comb, rando_comm, collective]
        learners = [rando_reg, rando_reg2]
        
        output_files = [open("%s//%s_%s.txt" % (outpath, learner.name, run), 'w') for learner in learners]
        
        
        # we arbitrarily pick the initial ids from the first learner; this doesn't matter, as we just use the instance ids
        initial_f = learners[0].get_random_unlabeled_ids
        init_size = num_labels_so_far
        if pick_balanced_initial_set:
            initial_f = learners[0].pick_balanced_initial_training_set
            init_size = int(num_labels_so_far/2.0) # equal number from both classes
            
        # Again, you could call *.initial_f on any learner -- it just returns the ids to label initially. these will
        # be the same for all learners.
        init_ids =initial_f(init_size)
        
        
        # label datasets, build initial model(s)
        for learner in learners:
            print "on learner %s" % learner.name
            learner.label_instances_in_all_datasets(init_ids)
            ### @ EXPERIMENTAL
            if "collective" in learner.name:
                learner.ICA_train()
                collective_test_datasets = \
                    [dataset.dataset(dict(zip(test_instance_ids, \
                        learner.unlabeled_datasets[0].get_instances(test_instance_ids))))]
                collective_train_datasets = [learner.labeled_datasets[0].copy()]
            learner.rebuild_models(for_eval=True)
        
        # report initial results, to console and file.
        # committee_evaluate(learners, datasets, test_datasets, output_files, write_headers=True)
        
        ### @ experimental 
        undersampled, models =committee_evaluate([learners[0]], datasets, test_datasets, [output_files[0]], write_headers=True)
        undersampled2, models2 = committee_evaluate([learners[1]], datasets, test_datasets, \
                                    [output_files[1]], undersample_id_sets=undersampled, write_headers=True)
                                    
        #pdb.set_trace()
        '''
        #committee_evaluate([learners[1]], combined_datasets, test_datasets_combined, [output_files[1]], write_headers=True)
        committee_evaluate([learners[1]], combined_datasets, test_datasets_combined, [output_files[1]], \
                                            undersample_id_sets=undersampled, write_headers=True)
        committee_evaluate([learners[2]], communities_only, test_communities, [output_files[2]], \
                                            undersample_id_sets=undersampled, write_headers=True)
        committee_evaluate([learners[3]], collective_train_datasets, collective_test_datasets, \
                                    [output_files[3]], undersample_id_sets=undersampled)
        '''
        ####
        
        first_iter = True
        while num_labels_so_far <= upto - step_size:
            #
            # the main active learning loop
            #
            cur_step_size = step_size
            cur_batch_size = batch_size
            if first_iter:
                # here we account for the initial labeled dataset size. for example, suppose
                # the step_size is set to 25 (we want to report results every 25 labels),
                # but the initial size was 2; then we want to label 23 on the first iteration
                # so that we report results when 25 total labels have been provided
                cur_step_size = step_size - num_labels_so_far if num_labels_so_far <= step_size \
                                else step_size - (num_labels_so_far - step_size)
                # in general, step_size is assumed to be a multiple of batch_size, for the first iteration,
                # when we're catching up to to the step_size (as outlined above), we set the
                # batch_size to 1 to make sure this condition holds.
                cur_batch_size = 1
                first_iter = False
            
            ####
            ### THIS IS WHAT YOU USUALLY WANT TO DO
            #for learner in learners:
            #    learner.active_learn(cur_step_size, batch_size = cur_batch_size)
            #### 
            
            ### @ EXPERIMENTAL
            # you usually want above
            print "\n\n\n\nWARNING only using the first learner's active learning algorithm!!!!!!!"
            labeled_ids = learners[0].active_learn(cur_step_size, batch_size = cur_batch_size)  
            
            for learner in learners[1:]:
                print "on learner %s" % learner.name
                learner.label_instances_in_all_datasets(labeled_ids)
                
                if "collective" in learner.name:
                    learner.ICA_train()
                    collective_test_datasets = \
                        [dataset.dataset(dict(zip(test_instance_ids, \
                            learner.unlabeled_datasets[0].get_instances(test_instance_ids))))]
                    collective_train_datasets = [learner.labeled_datasets[0].copy()]
                            
            assert(learners[0].labeled_datasets[0].instances.keys() ==learners[1].labeled_datasets[0].instances.keys())
            #####
            
            ### @ EXPERIMENTAL 
            ### now build/evaluate learners -- using committee
            #committee_evaluate(learners, datasets, test_datasets, output_files)
            undersampled, models =committee_evaluate([learners[0]], datasets, test_datasets, [output_files[0]])
            undersampled2, models2 = committee_evaluate([learners[1]], datasets, test_datasets, \
                                    [output_files[1]], undersample_id_sets=undersampled)
        
            for xid in test_datasets[0].get_instance_ids():
                X_vec = [test_datasets[0].get_point_for_id(xid) for d in test_datasets]
                committee_predictions = [learner.predict(X=X_vec) for learner in models]  
                committee_predictions2 = [learner.predict(X=X_vec) for learner in models2]  
                if committee_predictions != committee_predictions2:              
                    #pdb.set_trace()
                    print "\n\n\nwhoops..."
            '''
            committee_evaluate([learners[1]], combined_datasets, test_datasets_combined, \
                                    [output_files[1]], undersample_id_sets=undersampled)
            committee_evaluate([learners[2]], communities_only, test_communities, \
                                    [output_files[2]], undersample_id_sets=undersampled)
            committee_evaluate([learners[3]], collective_train_datasets, collective_test_datasets, \
                                    [output_files[3]], undersample_id_sets=undersampled)
            '''
            #### 
            
            num_labels_so_far += cur_step_size
            print "\n***labeled %s examples out of %s so far***" % (num_labels_so_far, upto)

 
        # close files
        for output_file in output_files:
            output_file.close()

    
    # post-experimental reporting
    if report_results_after_runs:
        results_reporter.post_runs_report(outpath, [l.name for l in learners], num_runs)
        
def run_experiments_hold_out(data_paths, outpath, hold_out_p = 0.25, datasets_for_eval = None, upto = 1000, step_size = 25,
                                                  initial_size = 2, batch_size = 5, pick_balanced_initial_set = True,
                                                  num_runs=10, report_results_after_runs=True):
    '''
    This method demonstrates how to use the active learning framework, and is also a functional routine for comparing learners. Basically,
    a number of runs will be performed, the active learning methods will be evaluated at each step, and results will be reported. The results
    for each run will be dumped to a text files, which then can be combined (e.g., averaged), elsewhere, or you can use the results_reporter
    module to aggregate and plot the output.
    @parameters
    --
    data_paths -- this is either a list (pointing to multiple feature spaces for the same instances) or a string pointing to a single data file (this will be
    the typical case). e.g., data_paths = "mydata.txt". curious_snake uses a sparse-formated weka-like format, documented elsewhere.
    outpath -- this is a directory under which all of the results will be dumped.
    hold_out_p -- the hold out percentage, i.e., how much of your data will be used for evaluation. you can ignore this is you're providing your own
    dataset(s) for evaluation (i.e., datasets_for_eval is not None)'.
    datasets_for_eval -- use this is you have datasets you want to use for testing -- i.e., to specify your hold out set independent of the data
    in data_paths.
    upto -- active learning will stop when upto examples have been labeled. if this is None, upto will default to the total unlabeled pool available
    initial_size -- the size of 'bootstrap' set to use prior to starting active learning (for the initial models)
    batch_size -- the number of examples to be labeled at each iteration in active learning -- optimally, 1
    step_size -- results will be reported every time another step_size examples have been labeled
    pick_balanced_initial_set -- if True, the initial train dataset will be built over an equal number (initial_size/2) of both classes.
    num_runs -- this many runs will be performed
    report_results -- if true, the results_reporter module will be used to generate output.
    '''
    
    if not os.path.isdir(outpath):
        os.mkdir(outpath)
        
    for run in range(num_runs):
        print "\n********\non run %s" % run
 
        print data_paths
        num_labels_so_far = initial_size # set to initial size for first iteration
         
        # if a string (pointing to a single dataset) is passed in, box it in a list
        data_paths = box_if_string(data_paths)
        datasets = [dataset.build_dataset_from_file(f) for f in data_paths]
        total_num_examples = len(datasets[0])
        test_datasets = []

        if datasets_for_eval is not None:
            # if a test set datafile is specified, use it.
            datasets_for_eval = box_if_string(datasets_for_eval)
            test_datasets = [dataset.build_dataset_from_file(f) for f in datasets_for_eval]
            # currently no way to join externally provided test sets!
            if upto is None:
                upto = total_num_examples
        else:
            # other wise, we copy the first (even if there are multiple datasets, it won't matter,
            # as we're just using the labels) and pick random examples
            hold_out_size = int(hold_out_p * total_num_examples)
            
            test_instance_ids = random.sample(datasets[0].instances, hold_out_size)
            # now remove them from the dataset(s)
            for d in datasets:
                cur_test_dataset = dataset.dataset(dict(zip(test_instance_ids, d.remove_instances(test_instance_ids))), name=d.name)
                test_datasets.append(cur_test_dataset)
            
            # if no upper bound was passed in, use the whole pool U
            if upto is None:
                upto = total_num_examples - hold_out_size
                
        print "using %s out of %s instances for test set" % (hold_out_size, total_num_examples)
        print "U has cardinality: %s" % datasets[0].size()
        
        rando_reg = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=True)
        rando_reg.name="random"

        simp = simple_learner.SimpleLearner([d.copy() for d in datasets], undersample_before_eval=True)
        simp.name = "simp"
        
        cheat_path = "data/proton_beam/proton_community_cheating"
        cheat_list = eval(open(cheat_path).readline())
        comm = community_learner.CommunityLearner(cheat_list, [d.copy() for d in datasets], undersample_before_eval=True)
        comm.name = "comm"

        learners = [rando_reg, simp, comm]
        
        output_files = [open("%s//%s_%s.txt" % (outpath, learner.name, run), 'w') for learner in learners]
        
        
        # we arbitrarily pick the initial ids from the first learner; this doesn't matter, as we just use the instance ids
        initial_f = learners[0].get_random_unlabeled_ids
        init_size = num_labels_so_far
        if pick_balanced_initial_set:
            initial_f = learners[0].pick_balanced_initial_training_set
            init_size = int(num_labels_so_far/2.0) # equal number from both classes
            
        # Again, you could call *.initial_f on any learner -- it just returns the ids to label initially. these will
        # be the same for all learners.
        init_ids =initial_f(init_size)
        
        
        # label datasets, build initial model(s)
        for learner in learners:
            print "on learner %s" % learner.name
            learner.label_instances_in_all_datasets(init_ids)
            learner.rebuild_models(for_eval=True)
        
        #### 
        # @ EXPERIMENTAL
        comm.sorted_papers = [x for x in comm.sorted_papers if not x in test_datasets[0].instances.keys() and not x in init_ids]
        
        #####
        
        # report initial results, to console and file.
        committee_evaluate(learners, datasets, test_datasets, output_files, write_headers=True)
        
        first_iter = True
        while num_labels_so_far <= upto - step_size:
            #
            # the main active learning loop
            #
            cur_step_size = step_size
            cur_batch_size = batch_size
            if first_iter:
                # here we account for the initial labeled dataset size. for example, suppose
                # the step_size is set to 25 (we want to report results every 25 labels),
                # but the initial size was 2; then we want to label 23 on the first iteration
                # so that we report results when 25 total labels have been provided
                cur_step_size = step_size - num_labels_so_far if num_labels_so_far <= step_size \
                                else step_size - (num_labels_so_far - step_size)
                # in general, step_size is assumed to be a multiple of batch_size, for the first iteration,
                # when we're catching up to to the step_size (as outlined above), we set the
                # batch_size to 1 to make sure this condition holds.
                cur_batch_size = 1
                first_iter = False
            
            for learner in learners:
                learner.active_learn(cur_step_size, batch_size = cur_batch_size)
                
            committee_evaluate(learners, datasets, test_datasets, output_files)
            
            num_labels_so_far += cur_step_size
            print "\n***labeled %s examples out of %s so far***" % (num_labels_so_far, upto)

 
        # close files
        for output_file in output_files:
            output_file.close()

    
    # post-experimental reporting
    if report_results_after_runs:
        results_reporter.post_runs_report(outpath, [l.name for l in learners], num_runs)
      

def committee_evaluate(learners, datasets, test_datasets, output_files, comittee_size=11, \
                        write_headers=False, undersample_id_sets=None):
    print "evaluating ensembles!"
    undersampled_ids = [] # maintain a list of lists with undersampled ids
    #pdb.set_trace()
    for i, learner in enumerate(learners):
        cur_committee = []
        for j in range(comittee_size):
            new_learner = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=True)
            new_learner.name = learner.name
            new_learner.label_instances_in_all_datasets(learner.labeled_datasets[0].instances.keys())
            undersample_ids = None
            if undersample_id_sets is not None:
                undersample_ids = undersample_id_sets[j]
                
            cur_undersampled = new_learner.rebuild_models(for_eval=True, do_grid_search=True, verbose=False, undersample_these=undersample_ids)
            undersampled_ids.append(cur_undersampled)
            cur_committee.append(new_learner)
                        
        ensemble_report_results(cur_committee, test_datasets, output_files[i], write_headers=write_headers)
    
    return (undersampled_ids, cur_committee)
    
    
    
def report_results_diff_test_sets(learners, list_of_test_datasets, output_files, cur_size):
    ''' 
    Same as below, but doesn't assume that the learners will use the same test datasets.
    Thus a list of test datasets (which are in turn expected to be lists) needs to passed in.
    '''
    for learner_index, learner in enumerate(learners):
        print "\n" + pprint_str
        print "results for %s @ %s labeled examples:" % (learner.name, len(learner.labeled_datasets[0].instances))
        results = evaluate_learner_with_holdout(learner, cur_size, list_of_test_datasets[learner_index])
        write_out_results(results, output_files[learner_index])
        print pprint_str + "\n"

def report_results(learners, test_datasets, cur_size, output_files, fns_out=None):
    ''' 
    Writes results for the learners, as evaluated over the test_dataset(s), to the console and the parametric
    output files.
    '''
    for learner_index, learner in enumerate(learners):
        print "\nresults for %s @ %s labeled examples:" % (learner.name, len(learner.labeled_datasets[0].instances))
        print "using query function %s" % learner.query_function.func_name
        print "labeled +s: %s" % len(learner.labeled_datasets[0].get_list_of_minority_ids())
        
        results = evaluate_learner_with_holdout(learner, cur_size, test_datasets)
        
        write_out_results(results, output_files[learner_index])
        if fns_out is not None:
            print "writing out false negatives..."
            fns_out.write(str(results["fn_ids"]))
            fns_out.close()


def ensemble_report_results(committee, test_datasets, output_file, write_headers=False, predictions_file=None):
    learner = committee[0]
    print "\nresults for %s @ %s labeled examples:" % (learner.name, len(learner.labeled_datasets[0].instances))
    print "using query function %s" % learner.query_function.func_name
    print "labeled +s: %s" % len(learner.labeled_datasets[0].get_list_of_minority_ids())
    
    results, preds = evaluate_ensemble(committee, test_datasets, return_preds=True)
    #### make sure these aren't all 1s!!!!!!!! wtf is going on??!
    write_out_results(results, output_file, write_headers=write_headers)
    if predictions_file is not None:        
        predictions_file.write(str(preds))
    
    return results

            
     
def write_out_divs(results, tp_outf, fn_outf):
    # @experimental
    tp_outf.write(str(results["tp_div_scores"]) + "\n")
    fn_outf.write(str(results["fn_div_scores"]) + "\n")
    
    
def box_if_string(s):
    ''' If s is a string, returns a unary list [s] '''
    if type(s) == type(""):
        return [s]
    return s
           
    
def kdd_evaluate_finite_pool_learner(learner, print_confusion_matrices=True):
    '''
    Returns a dictionary containing various metrics for learner performance, as measured over the
    examples in the unlabeled_datasets belonging to the learner.
    '''
    print "((kdd evaluate))"

    results = {}
    
 
    # first we count the number of true positives and true negatives discovered in learning. this is so we do not
    # unfairly penalize active learning strategies for finding lots of the minority class during training.
    tps = learner.labeled_datasets[0].number_of_minority_examples()
    tns = learner.labeled_datasets[0].number_of_majority_examples()
    
    print "evaluating learner over %s instances." % len(learner.unlabeled_datasets[0].instances)
    fns, fps = 0, 0
    unlabeled_ids = learner.unlabeled_datasets[0].get_instance_ids()
    for unlabeled_set in learner.unlabeled_datasets[1:]:
        # ascertain that all datasets have the same unlabeled pool --
        # if they don't, something is off, since this would mean
        # an example was labeled in one feature space, but not
        # another.
        assert(unlabeled_set.get_instance_ids() == unlabeled_ids)
    
    true_l1_labels = [learner.unlabeled_datasets[0].instances[id].label for id in unlabeled_ids]
    predictions = []
    for xid in unlabeled_ids:
        # get the points in all feature spaces (or just the one) for this example
        # id. 
        #points = [d.get_point_for_id(id) for d in learner.unlabeled_datasets]
        prediction = learner.predict(xid)
        predictions.append(prediction)
        
    level1_conf_mat, fn_ids, tn_ids =  _evaluate_predictions(predictions, true_l1_labels, unlabeled_ids)
    # just overwrite the level 1 fn ids, we don't care about them.

    if print_confusion_matrices:
        print "confusion matrix over unlabeled data:"
        print level1_conf_mat

    
    # fraction of tps correctly identified
    tp_t = learner.labeled_datasets[0].number_of_minority_examples() # number of tps found during training
    tn_t = learner.labeled_datasets[0].number_of_majority_examples()
    tp_u = level1_conf_mat["tp"] # predictive true positives
    fn_u = level1_conf_mat["fn"] # predictive false negatives
    tn_u = level1_conf_mat["tn"]
    
    #classifier_yield = float(tp_t + tp_u)  / float(tp_t + fn_u + tp_u)
    
    fp_u = level1_conf_mat["fp"] # predictive false positives
    labeled_in_training = learner.labeled_datasets[0].size()
    N = labeled_in_training + learner.unlabeled_datasets[0].size() # total size
    #classifier_burden = float(labeled_in_training + tp_u + fp_u) / float(N)

    return {"tp_u":tp_u, "tn_u":tn_u, "fp_u":fp_u, "fn_u":fn_u, "labeled_pos":tp_t, "labeled_neg":tn_t}
    
def evaluate_finite_pool_learner(learner, print_confusion_matrices=True):
    '''
    Returns a dictionary containing various metrics for learner performance, as measured over the
    examples in the unlabeled_datasets belonging to the learner.
    '''
    tps, tns  = 0,0
    results = {}
    # first we count the number of true positives and true negatives discovered in learning. this is so we do not
    # unfairly penalize active learning strategies for finding lots of the minority class during training.
    tps = learner.labeled_datasets[0].number_of_l2_positives()
    tns = learner.labeled_datasets[0].number_of_l2_negatives()
    
    print "evaluating learner over %s instances." % len(learner.unlabeled_datasets[0].instances)
    fns, fps = 0, 0
    unlabeled_ids = learner.unlabeled_datasets[0].get_instance_ids()
    for unlabeled_set in learner.unlabeled_datasets[1:]:
        # ascertain that all datasets have the same unlabeled pool --
        # if they don't, something is off, since this would mean
        # an example was labeled in one feature space, but not
        # another.
        assert(unlabeled_set.get_instance_ids() == unlabeled_ids)
    
    true_l1_labels = [learner.unlabeled_datasets[0].instances[id].label for id in unlabeled_ids]
    true_l2_labels = [learner.unlabeled_datasets[0].instances[id].level_2_label for id in unlabeled_ids]
    predictions = []
    for id in unlabeled_ids:
        # get the points in all feature spaces (or just the one) for this example
        # id. 
        #points = [d.get_point_for_id(id) for d in learner.unlabeled_datasets]
        prediction = learner.predict(id)
        predictions.append(prediction)
        
    level1_conf_mat, fn_ids, tn_ids =  _evaluate_predictions(predictions, true_l1_labels, unlabeled_ids)
    # just overwrite the level 1 fn ids, we don't care about them.
    level2_conf_mat, fn_ids, tn_ids =  _evaluate_predictions(predictions, true_l2_labels, unlabeled_ids)

    
    if print_confusion_matrices:
        print "level 1 confusion matrix:"
        print level1_conf_mat
    
        print "level 2 confusion matrix:"
        print level2_conf_mat
    
    # fraction of tps correctly identified
    tp_t = learner.labeled_datasets[0].number_of_minority_examples() # number of tps found during training
    tp_u = level2_conf_mat["tp"] # predictive true positives
    fn_u = level2_conf_mat["fn"] # predictive false negatives
    classifier_yield = float(tp_t + tp_u)  / float(tp_t + fn_u + tp_u)
    
    fp_u = level2_conf_mat["fp"] # predictive false positives
    labeled_in_training = learner.labeled_datasets[0].size()
    N = labeled_in_training + learner.unlabeled_datasets[0].size() # total size
    classifier_burden = float(labeled_in_training + tp_u + fp_u) / float(N)

    return {"num_labels":labeled_in_training, "yield":classifier_yield, "burden":classifier_burden, "fns":fn_ids, "tns":tn_ids}
    
   
def evaluate_ensemble_finite_pool(learner, committee_size = 11):
    results = {"size":len(learner.labeled_datasets[0])}
    # labeled true positives / true negatives
    tp_L = learner.labeled_datasets[0].number_of_minority_examples()
    tn_L = learner.labeled_datasets[0].number_of_majority_examples()
    print "evaluating learner over %s instances." % len(learner.unlabeled_datasets[0].instances)
    fns, fps = 0, 0
    
    unlabeled_ids = learner.unlabeled_datasets[0].get_instance_ids()
    unlabeled_ids.sort()
    
    true_labels = [learner.unlabeled_datasets[0].instances[xid].label for xid in unlabeled_ids]
    
    # now build the committee
    print "building an ensemble for learner %s..." % learner.name
    
    committee = []
    datasets = [d.copy() for d in learner.labeled_datasets]
    for j in range(committee_size):
        new_learner = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=True)
        new_learner.label_instances_in_all_datasets(learner.labeled_datasets[0].instances.keys())
        new_learner.rebuild_models(for_eval=True, do_grid_search=True)
        committee.append(new_learner)
    
    print "\ndone. making predictions..."
    # now make predictions
    predictions = []
    for xid in unlabeled_ids:
        # get the points in all feature spaces (or just the one) for this example
        # id. 
        X_vec = [d.get_point_for_id(xid) for d in learner.unlabeled_datasets]
            
        committee_predictions = [c_learner.predict(X=X_vec) for c_learner in committee]
        yes_votes = committee_predictions.count(1)
        if yes_votes >= len(committee)/2.0:
            prediction = 1.0
        else:
            prediction = -1.0
            
        predictions.append(prediction)

    print "\nok."
    # predictive results (over U)
    conf_mat, fn_ids, tn_ids =  _evaluate_predictions(predictions, true_labels, unlabeled_ids)
    tp_U = conf_mat["tp"] # predictive true positives
    fn_U = conf_mat["fn"] # predictive false negatives
    tn_U = conf_mat["tn"] # predictive true negatives
    fp_U = conf_mat["fp"] # predictive false positives

    # some metrics, for convienence
    classifier_yield = float(tp_L + tp_U)  / float(tp_L + fn_U + tp_U)
    labeled_in_training = len(learner.labeled_datasets[0])
    N = labeled_in_training + len(learner.unlabeled_datasets[0])# total pool size
    classifier_burden = float(labeled_in_training + tp_U + fp_U) / float(N)
    pool_results = {"tp":tp_U, "tn":tn_U, "fn":fn_U, "fp":fp_U,\
                         "yield":classifier_yield, "burden":classifier_burden}
  
    return pool_results
  
        
    
def evaluate_ensemble_mice(committee, test_sets):
    '''
    mice!
    '''
    results={"size":len(committee[0].labeled_datasets[0])}
    true_labels = test_sets[0].get_labels()
    print "evaluating learner over %s instances." % len(test_sets[0].instances)
    
    true_seizure_start_times = []
    in_seizure_window, start_time = False, None
    predictions, ids = [], []
    for xid in test_sets[0].get_instance_ids():
        X_vec = [d.get_point_for_id(xid) for d in test_sets]
        true_lbl = test_sets[0].instances[xid].label
        
        if in_seizure_window and xid - start_time > 225:
            in_seizure_window = False
        #pdb.set_trace()
        if not in_seizure_window and true_lbl == 1:
            in_seizure_window = True
            start_time = xid
            true_seizure_start_times.append(xid)
            
        committee_predictions = [learner.predict(X=X_vec) for learner in committee]
        #prediction = learner.predict(X = X_vec)
        yes_votes = committee_predictions.count(1)
        if yes_votes >= len(committee)/2.0:
            prediction = 1.0
        else:
            prediction = -1.0
            
        predictions.append(prediction)
        ids.append(xid)
            
    print "\nthere are %s true seizures in the test data" % len(true_seizure_start_times)
    ### now evaluate
    tps, fps = 0,0
    correctly_predicted_seizures = []
    for t, prediction in zip(ids, predictions):
        if prediction == 1:
            # in pre-ictal window?
            is_a_tp = False
            for seizure_time in true_seizure_start_times:
                if seizure_time - t <= 225:
                    is_a_tp = True
                    correctly_predicted_seizures.append(seizure_time)
                    
            if is_a_tp:
                tps += 1
            else:
                fps += 1
    
    correctly_predicted_seizures = list(set(correctly_predicted_seizures))
    tps = len(correctly_predicted_seizures)
    fns = len(true_seizure_start_times) - tps
    tns = len(ids) - (tps+fps+fns)
    conf_mat = {"fn":fns, "tn":tns, "fp":fps, "tp":tps}
    _calculate_metrics(conf_mat, results)
    
    return results
    
def evaluate_ensemble(committee, test_sets, return_preds=False):
    '''
    for the updates paper.
    '''
    results={"size":len(committee[0].labeled_datasets[0])}
    true_labels = test_sets[0].get_labels()
    print "evaluating learner over %s instances." % len(test_sets[0].instances)

    predictions, ids = [], []
    test_ids = test_sets[0].get_instance_ids()
    test_ids.sort()
    for xid in test_ids:
        X_vec = [d.get_point_for_id(xid) for d in test_sets]
        committee_predictions = [learner.predict(X=X_vec) for learner in committee]
        #prediction = learner.predict(X = X_vec)
        yes_votes = committee_predictions.count(1)
        if yes_votes >= len(committee)/2.0:
            prediction = 1.0
        else:
            prediction = -1.0
            
        predictions.append(prediction)
        ids.append(xid)
            
    conf_mat, fn_ids, tn_ids =  _evaluate_predictions(predictions, true_labels, ids)
    
    results["fn_ids"] = fn_ids
    results["tn_ids"] = tn_ids
    _calculate_metrics(conf_mat, results)
    if return_preds:
        return (results, predictions)
    return results
    
    
             
def evaluate_learner_with_holdout(learner, num_labels, test_sets):
    '''
    If you're not considering a "finite pool" problem, this is the correct way to evaluate the trained classifiers. 
    
    @params
    learner -- the learner to be evaluated
    num_labels -- how many labels have been provided to the learner thus far
    test_sets -- the set(s) of examples to be used for evaluation. if there are multiple, it is assumed that they correspond to multiple feature
                            spaces, thus they will have to be cominbed somehow. The 'predict' method in the learner class(es) handles this, see that 
                            method in, e.g., base_learner, for more. If test sets is None, the unla
    '''
    results={"size":num_labels}
    true_l1_labels, true_l2_labels = None, None
    if test_sets is None or test_sets[0] is None:
        print "evaluating learner over %s instances." % len(learner.unlabeled_datasets[0].instances)
        print "******* warning! not explicitly using a holdout set -- using unlabeled ids *******"
        unlabeled_ids = learner.unlabeled_datasets[0].get_instance_ids()
    
        # the labels are assumed to be the same; thus we only use the labels for the first dataset
        true_l1_labels = [learner.unlabeled_datasets[0].instances[id].label for id in unlabeled_ids]
        true_l2_labels = [learner.unlabeled_datasets[0].instances[id].level_2_label for id in unlabeled_ids]
    else:
        print "evaluating learner over %s instances." % len(test_sets[0].instances)
        true_l1_labels = test_sets[0].get_labels()
        true_l2_labels = test_sets[0].get_level_2_labels()
        
    predictions = []
    ids = []
    if test_sets is None or test_sets[0] is None:
        # in this case the assumption is that the learner will be evaluated
        # on the (test) datasets that were passed in.
        for id in learner.unlabeled_datasets[0].get_instance_ids():
            # Note that we've changed the predict API so that
            # it accepts an ID, rather a vector. This is more flexible
            # (e.g., it allows stacking); however, see comment below
            # -- we currently do not do this when test sets are passed 
            # in explicitly
            #
            prediction = learner.predict(id)
            predictions.append(prediction)
            ids.append(id)
    else:
        
        #
        #@experimental 10/15/09 for diversity scores; experimentation;
        # delete or refactor when done.
        #tp_div_scores, fn_div_scores = [], []
        for id in test_sets[0].get_instance_ids():
            # when using a test set, we pass X's vector
            # representation directly to the predict method,
            # because the test_set is not directly available to
            # the learner (and thus using x_id won't work). 
            # we might want to refactor this to allow the learner
            # to accept a test dataset, because it's going to be tricky
            # to evaluate stacked learners, e.g., in this way (above
            # we solved this by handing ids to the learner).
            X_vec = [d.get_point_for_id(id) for d in test_sets]
            prediction = learner.predict(X = X_vec)
            predictions.append(prediction)
            ids.append(id)
            
            '''
            # @experimental 10/15/09 testing a theory here
            # assuming learner is a PAL learner; delete or refactor
            cur_inst = test_sets[0].instances[id]
            if cur_inst.label > 0.0:
                div_score = learner.angle_to_closest_min_neighbor(cur_inst, model_index=0 )
                if prediction < 0.0:
                    # false negative
                    fn_div_scores.append(div_score)
                else:
                    # false positive
                    tp_div_scores.append(div_score)
            '''

    conf_mat, fn_ids, tn_ids =  _evaluate_predictions(predictions, true_l1_labels, ids)
    
    #@experimental
    #results["tp_div_scores"] = tp_div_scores
    #results["fn_div_scores"] = fn_div_scores
    results["fn_ids"] = fn_ids
    results["tn_ids"] = tn_ids
    _calculate_metrics(conf_mat, results)
    
    return results
    
    
def _evaluate_predictions(predictions, true_labels, ids=None):
    conf_mat = {"tp":0, "fp":0, "tn":0, "fn":0}
    fn_ids, tn_ids = [], []
    
    # Sometimes we're interested in the ids of the examples
    # that were, e.g., false negatives. In this csae a list of the 
    # example ids needs to be passed in. If it is not, these ids
    # will not be returned.
    return_ids = True
    if ids is None:
        return_ids = False
        # this is a dummy vector; it won't really
        # be used
        ids = range(len(predictions))
    for prediction, true_label, id in zip(predictions, true_labels, ids):
        if prediction == true_label:
            # then the learner was correct
            if true_label > 0:
                conf_mat["tp"]+=1
            else:
                conf_mat["tn"]+=1
                tn_ids.append(id)
        else:
            # then the learner was mistaken
            if true_label > 0:
                # actual label was 1; predicted -1
                conf_mat["fn"]+=1
                fn_ids.append(id)
            else:
                # actual label was -1; predicted 1
                conf_mat["fp"]+=1
    if return_ids:
        return (conf_mat, fn_ids, tn_ids)
    return conf_mat
    
    
def _calculate_metrics(conf_mat, results, F_beta=2, verbose=True):
    '''
    Computes a number of metrics from the provided confusion matrix, conf_mat. In particular,
    returns: accuracy, sensitivity and specificity (sensitivity is, arbitrarily, defined w.r.t.
    the positive class). 
    
    Note that we calculate an F-measure using sens./spec., rather than 
    precision and recall!
    '''
    results["confusion_matrix"] = conf_mat
    results["tps"] = conf_mat["tp"]
    results["tns"] = conf_mat["tn"]
    results["fps"] = conf_mat["fp"]
    results["fns"] = conf_mat["fn"]
    
    results["accuracy"] = float (conf_mat["tp"] + conf_mat["tn"]) / float(sum([conf_mat[key] for key in conf_mat.keys()]))
    if float(conf_mat["tp"]) == 0:
        results["sensitivity"] = 0
    else:
        results["sensitivity"] = float(conf_mat["tp"]) / float(conf_mat["tp"] + conf_mat["fn"])
    results["specificity"] = float(conf_mat["tn"]) / float(conf_mat["tn"] + conf_mat["fp"])
    precision = 0.0
    if verbose:
        print "true positives: %s, false positives: %s" % (conf_mat["tp"], conf_mat["fp"])
    if (conf_mat["tp"] + conf_mat["fp"]) > 0:
        precision = float(conf_mat["tp"]) / float(conf_mat["tp"] + conf_mat["fp"])
    if verbose:
        print "precision: %s" % precision

    recall = None
    if conf_mat["tp"] + conf_mat["fn"] == 0:
        recall = 1.0
    else:
        recall = float(conf_mat["tp"]) / float((conf_mat["tp"] + conf_mat["fn"]))
    f_denom = ((F_beta**2 * results["specificity"]) + recall)
    results["F%s"%F_beta] = 0.0 if f_denom == 0.0 else \
                (1 + F_beta**2) * ((results["specificity"]*recall) / f_denom)
    
    results["U19"] = (19*results["sensitivity"]+results["specificity"])/20.0
    
    if verbose:
        for k in results.keys():
            if k not in ["tn_ids", "fn_ids"]:
                print "%s: %s" % (k, results[k])    
    
    
    
def write_out_results(results, outf, write_headers=False,\
                 metrics = ["tps", "tns", "fps", "fns", "size", "F2", "accuracy", "sensitivity", "specificity", "U19"]):
    if write_headers:
        outf.write(",".join(metrics)+"\n")
    write_these_out = [results[k] for k in metrics]
    outf.write(",".join([str(s) for s in write_these_out]))
    outf.write("\n")
    
def _mkdir(newdir):
    """
    works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

################################################################
#                                                                                                                                           #
#               The following routines are for setting up particular types of learners                 #
#                                                                                                                                           #
################################################################
def _setup_multi_and_single_view_learners(datasets, joined_dataset, undersampling=True): 
    multi_view_learner_at_least = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval= undersampling)
    multi_view_learner_at_least.name = "multi_view_at_least 2"
    multi_view_learner_at_least.predict_func = multi_view_learner_at_least.at_least
    
    multi_view_learner_at_least1 = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval=undersampling)
    multi_view_learner_at_least1.name = "multi_view_at_least 1"
    multi_view_learner_at_least1.predict_func = lambda X: multi_view_learner_at_least1.at_least(X, 1)

    multi_view_learner_unan = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval= undersampling)
    multi_view_learner_unan.predict_func = multi_view_learner_unan.unanimous
    multi_view_learner_unan.name = "multi_view_unan" 
    
    multi_view_learner_maj = random_learner.RandomLearner([d.copy() for d in datasets], undersample_before_eval= undersampling)
    multi_view_learner_maj.predict_func = multi_view_learner_maj.majority_predict
    multi_view_learner_maj.name = "multi_view_majority" 

    joined_learner = random_learner.RandomLearner([joined_dataset], undersample_before_eval=undersampling)
    joined_learner.predict_func = joined_learner.majority_predict
    joined_learner.name = "single_view"
    
    learners = [joined_learner, multi_view_learner_unan, multi_view_learner_at_least, \
                         multi_view_learner_at_least1, multi_view_learner_maj]

    return learners


def _setup_span(datasets, undersampling=True):
    
    random_l = random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=True)
    random_l.predict_func = random_l.majority_predict
    #random_l.undersample_function = random_l.aggressive_undersample_labeled_datasets
    
    span_l = span_learner.SPANLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    span_l.name = "SPAN"
    span_l.predict_func = span_l.majority_predict
    #span_l.undersample_function =span_l.aggressive_undersample_labeled_datasets
    
    # and a SIMPLE
    simp_learner = simple_learner.SimpleLearner([d.copy() for d in datasets], 
                                                                            undersample_before_eval=True)
    simp_learner.predict_func = simp_learner.majority_predict 
    #simp_learner.undersample_function = simp_learner.aggressive_undersample_labeled_datasets
                                                                 
    pal = pal_learner.PALLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    pal.name = "PAL"
    pal.longer_name = "PAL; linear kernel, with regular undersampling"
    pal.predict_func  = pal.majority_predict

    return [random_l, simp_learner, span_l]
    
    
def _setup_cofl(datasets):#, neg_path, pos_path, abstracts_path, titles_path):
    #self, pos_terms_f, neg_terms_f, raw_abstract_text_dir, raw_title_text_dir,
    print "..."

    data = [dataset.join_datasets(datasets)]
    
    simp_learner = simple_learner.SimpleLearner([d.copy() for d in datasets], 
                                                                            undersample_before_eval=True)
    simp_learner.predict_func = simp_learner.at_least
    
    random_l = random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=True)
    random_l.predict_func = random_l.at_least
    
    '''
    print "Proton Beam!! (USING NEW TERMS)"
    pos_path = os.path.join("data", "proton_beam", "new_pos_terms")
    neg_path = os.path.join("data", "proton_beam", "new_neg_terms")
    abstracts_path = os.path.join("data", "proton_beam", "Abstracts")
    titles_path = os.path.join("data", "proton_beam", "Titles")



    print "Sleep Apnea!!"
    pos_path = os.path.join("data", "sleep_apnea", "pos_terms")
    neg_path = os.path.join("data", "sleep_apnea", "neg_terms")
    abstracts_path = os.path.join("data", "sleep_apnea", "Abstracts")
    titles_path = os.path.join("data", "sleep_apnea", "Titles")  

    

    print "COPD!!"
    pos_path = os.path.join("data", "copd", "pos_terms")
    neg_path = os.path.join("data", "copd", "neg_terms")
    abstracts_path = os.path.join("data", "copd", "Abstracts")
    titles_path = os.path.join("data", "copd", "Titles")
    '''
        
    print "MICRO!!!"
    pos_path = os.path.join("data", "micro_nutrients", "pos_terms")
    neg_path = os.path.join("data", "micro_nutrients", "neg_terms")
    abstracts_path = os.path.join("data", "micro_nutrients", "Abstracts")
    titles_path = os.path.join("data", "micro_nutrients", "Titles")

    
    w_index_path = os.path.join("data", "proton_beam", "combined_word_index.txt")
    #cofl_learner = cfal_learner.CoFeatureLearner(pos_path, neg_path, w_index_path, abstracts_path, titles_path, 
    #                                                                    unlabeled_datasets=datasets, undersample_before_eval=True)
    cofl_learner = cfal_learner.CoFeatureLearner(pos_path, neg_path, w_index_path, abstracts_path, titles_path, 
                                                                            unlabeled_datasets=[d.copy() for d in datasets], undersample_before_eval=True)
    cofl_learner.predict_func = cofl_learner.at_least
    
    cofl_un = cfal_learner.CoFeatureLearner(pos_path, neg_path, w_index_path, abstracts_path, titles_path, 
                                                                            unlabeled_datasets=[d.copy() for d in datasets], undersample_before_eval=True)
    cofl_un.predict_func = cofl_un.at_least
    cofl_un.query_function = cofl_un.uncertainty
    cofl_un.name = "COFL_uncertainty"
    
    return [simp_learner, cofl_learner, cofl_un, random_l]
    
def _setup_graph(datasets, undersampling=True):
    '''
    graph_l = graph_learner.GraphLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    graph_l.name = "GRAPH INVERTED"
    graph_l.predict_func = graph_l.majority_predict
    '''
    '''
    graph_l2 = graph_learner.GraphLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True, inverse=False)
    graph_l2.name = "graph learner"
    graph_l2.predict_func = graph_l2.majority_predict
    '''

    term_l = term_learner.TermLearner([d.copy() for d in datasets], undersample_before_eval= True)
    term_l.name = "term learner" 
    term_l.predict_func = term_l.majority_predict
    
    term_l2 = term_learner.TermLearner([d.copy() for d in datasets], undersample_before_eval= True, normalize=False)
    term_l2.name = "term learner not normalized" 
    term_l2.predict_func = term_l2.majority_predict

    
    #
    #   MAOP learner
    #
    maop_l = MAOP_learner.MAOPLearner([d.copy() for d in datasets], undersample_before_eval= True)
    maop_l.predict_func = maop_l.majority_predict        
    
    '''
    maop_l2 = MAOP_learner.MAOPLearner([d.copy() for d in datasets], undersample_before_eval= True, normalize=False)
    maop_l2.name = "MAOP_aggressive"       
    maop_l2.predict_func = maop_l2.majority_predict        
    maop_l2.undersample_function = maop_l2.aggressive_undersample_labeled_datasets
    '''
    
    '''
    maop_l = MAOP_learner.MAOPLearner([d.copy() for d in datasets], undersample_before_eval= True, normalize=False)
    maop_l.name = "MAOP_not_normed"       
    maop_l.predict_func = maop_l.majority_predict        

    maop_N = MAOP_learner.MAOPLearner([d.copy() for d in datasets], undersample_before_eval= True, normalize=True)  
    maop_N.predict_func = maop_N.majority_predict 
    maop_N.name = "MAOP_normed"    
    '''
    ul = un_learner.UnLearner([d.copy() for d in datasets], undersample_before_eval= True)
    ul.predict_func = ul.majority_predict

    #maop_N2 = MAOP_learner.MAOPLearner([d.copy() for d in datasets], undersample_before_eval= True, normalize=True)  
    #maop_N2.predict_func = maop_N2.majority_predict   
    #maop_N2.undersample_function  = maop_N2.aggressive_undersample_labeled_datasets
    #maop_N2.name = "MAOP_normed_aggressive"

     
    pal = pal_learner.PALLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    pal.name = "PAL"
    pal.longer_name = "PAL; linear kernel, with regular undersampling"
    pal.predict_func  = pal.majority_predict
    
    # also a random learner
    random_l = random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=True)
    random_l.predict_func = random_l.majority_predict
    
    random_l2 = random_learner.RandomLearner([d.copy() for d in datasets], 
                                                                        undersample_before_eval=True)
    random_l2.predict_func = random_l2.majority_predict
    random_l2.undersample_function = random_l2.aggressive_undersample_labeled_datasets
    random_l2.name = "random aggressive"
    
    # and a SIMPLE
    simp_learner = simple_learner.SimpleLearner([d.copy() for d in datasets], 
                                                                            undersample_before_eval=True)
                                                                            
    simp_learner.predict_func = simp_learner.majority_predict
    simp_learner.name = "SIMPLE"
    
    simp_learner2 = simple_learner.SimpleLearner([d.copy() for d in datasets], 
                                                                            undersample_before_eval=True)
                                                                            
    simp_learner2.predict_func = simp_learner2.majority_predict
    simp_learner2.undersample_function = simp_learner2.aggressive_undersample_labeled_datasets
    simp_learner2.name = "SIMPLE aggressive"
    
    nln = nln_learner.NLNLearner([d.copy() for d in datasets], undersample_before_eval= True)
    nln.predict_func = nln.majority_predict
    
    #learners = [random_l, simp_learner, pal,  ul] #term_l, term_l2] #maop_l
    learners = [nln]
    return learners
    
    
    
def _setup_psuedo_PALs(datasets, dataset_names=None, undersampling=True):
    # @experimental
    random_pal = pal_learner.PALLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    random_pal.name = "Random"
    random_pal.longer_name = "Random learner; standard undersampling"
    random_pal.predict_func = random_pal.majority_predict
    
    simple_pal = pal_learner.PALLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    simple_pal.query_function = simple_pal.SIMPLE
    simple_pal.predict_func = simple_pal.majority_predict
    simple_pal.name = "SIMPLE"
    
    return [random_pal, simple_pal]
    

def _setup_PAL_learner(datasets, dataset_names=None, undersampling=True):
    '''
    Just a plain-old PAL learner.
    '''
    pal = pal_learner.PALLearner([d.copy() for d in datasets], 
                                                  undersample_before_eval= True)
    pal.name = "PAL"
    pal.longer_name = "PAL; linear kernel, with regular undersampling"
    
    return [pal]
    
def _setup_fv_learners(datasets, dataset_names, undersampling=True):
    '''
    Sets up learners over each of the respective feature spaces, or views -- i.e., creates one 
    learner per view.
    '''
    learners = []
    for dataset, dataset_name in zip(datasets, dataset_names):
        learner = random_learner.RandomLearner([dataset], undersample_before_eval=undersampling)
        learner.predict_func = learner.majority_predict
        learner.name = dataset_name
        learners.append(learner)
        
    return learners
      
def chunks(l, n):
    """ 
    yield successive n-sized chunks from l.
    (for cv).
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]



if __name__ == "__main__":
    feature_sets = [os.path.join("data", "proton_beam",s) for s in ["keywords_redux", "titles_redux", "title_concepts_redux"]]
    curious_snake.run_experiments_finite_pool(feature_sets, os.path.join("output", "kernel_test"), upto=2200)        

'''
curious_snake.run_experiments_hold_out(feature_sets, os.path.join("output", "wooty"), initial_size=500, upto=500, pick_balanced_initial_set=False, report_results_after_runs=False, num_runs=1)

feature_sets = [os.path.join("data", "trec100",s) for s in ["titles", "abstracts", "keywords", "title_concepts","abstracts_400_topics"]]
curious_snake.run_passive_mv_experiments(feature_sets, os.path.join("output", "trec100", "test"))
'''
    
