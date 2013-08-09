import pdb
import base_svm_learner
from base_svm_learner import BaseSVMLearner
from base_svm_learner import *

import whoosh
from whoosh.qparser import QueryParser
from whoosh.query import *
import whoosh.index as index


class IRLearner(BaseSVMLearner):
    def __init__(self, unlabeled_datasets = None, models=None, undersample_before_eval = False, \
                         whoosh_index_path=None, pos_terms=None, neg_terms=None):
        #
        # call the BaseLearner constructor to initialize various globals and process the
        # datasets, etc.; of course, these can subsequently be overwritten.
    
        BaseSVMLearner.__init__(self, unlabeled_datasets=unlabeled_datasets, models=models, 
                                                undersample_before_eval = True)

        # ovewrite svm parameters here 
        self.params = [svm_parameter() for d in unlabeled_datasets]
        self.pos_terms = eval(open(pos_terms).readline())
        
        self.whoosh_index_path = whoosh_index_path
        self.ix = index.open_dir(self.whoosh_index_path)

        self.sorted_ids = []
        self.cur_i = 0
        self.query = unicode(" OR ".join(["'%s'" % t for t in self.pos_terms]))
        self.ranked_ids = None
        
        self.query_function = self.ir_query
        self.name = "IR"
        print "%s learner intialized with %s labeled examples" % (self.name, self.labeled_datasets[0].size())
        
    
    def ir_query(self, k):
        if self.ranked_ids is None:
          self._sort_U()
            
        next_docs = self.ranked_ids[self.cur_i:self.cur_i+k]
        self.cur_i += k
        if len(next_docs) == 0:
          pdb.set_trace()
        print "returning these ids! %s" % next_docs
        return next_docs
        
    def _sort_U(self):
         parser = QueryParser("content",schema=self.ix.schema)
         q = parser.parse(self.query)
         searcher = self.ix.searcher()
         res=searcher.search(q, limit=None)
         #pdb.set_trace()
         #pdb.set_trace()
         self.ranked_ids = [int(x['title']) for x in res]
         self.ranked_ids = [x for x in self.ranked_ids if x in self.unlabeled_datasets[0].instances.keys()]