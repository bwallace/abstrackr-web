
import pdb
import base_svm_learner
from base_svm_learner import BaseSVMLearner
from base_svm_learner import *
from operator import itemgetter

class CommunityLearner(BaseSVMLearner):
    def __init__(self, ordered_list, unlabeled_datasets = None, models=None, undersample_before_eval = False):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
    
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models, 
                                                undersample_before_eval = undersample_before_eval,
                                                kernel_type=LINEAR)

        # ovewrite svm parameters here 
        self.params = [svm_parameter()  for d in unlabeled_datasets]
        # there's no reason to rebuild the models during active learning,
        # since we're just randomly picking things to label
        self.rebuild_models_at_each_iter = False 

        self.query_function = self.cheat
        self.name = "Community"
        self.sorted_papers = ordered_list
        
        
        ### 
        # goodness of each community
        '''
        self.payoff_estimates = {}
        self.comms_to_papers = {}
        self.papers_to_comms = {}
        for paper_id in self.ids_to_authors.keys():
            self.papers_to_comms[paper_id] = []
            
        for i,comm in enumerate(comms):
            self.comms_to_papers[i]=[]
            for paper in self.unlabeled_datasets[0].instances.keys():
                if has_at_least_one(ids_to_authors[paper], comm):
                    self.comms_to_papers[i].append(paper)
                    self.papers_to_comms[paper].append(i)
        self.sorted_papers = []
        '''
        self.last_i = 0


    def cheat(self,k):
        label_these = self.sorted_papers[self.last_i:self.last_i+k]
        self.last_i = self.last_i + k
        return label_these
        
        
    def best_community(self,k):
        '''
        Greedily exploits the best community so far
        '''
        selected_ids = []
        best_payoff = -1
        already_selected_papers = []
        payoffs = self.payoff_estimate.items()
        payoffs.sort(key = itemgetter(1), reverse=True)

        while len(selected_ids) < k:
            for comm_i, payoff in payoffs():
                if len(self.comms_to_papers[comm_i])>=1:
                    selected_ids.append(self.comms_to_papers[comm_i][:k])
                    # remove the selected guys
                    self.comms_to_papers[comm_i] = self.comms_to_papers[k:]
                    # ugh. have to remove the selected ids from all other lists, too...
                    for i in self.comms_to_papers.keys():
                        for xid in selected_ids:
                            self.comms_to_papers[i].pop(xid)
        
    
        
    def rank_papers(self):
        papers_to_scores = {}
        
    def score(self, paper_id):
        return sum([self.payoffs[comm_i] for comm_i in self.papers_to_comms[paper_id]])
        
def has_at_least_one(s1, s2):
    # true if at least one element of s1 is in s2
    for x in s1:
        if x in s2:
            return True
    return False
    
    
    