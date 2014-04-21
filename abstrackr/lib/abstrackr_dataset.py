import pdb 

import numpy as np

###
# feature extraction & encoding
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer

class Dataset:

    def __init__(self, ids, titles, abstracts, mesh, lbl_dict, name=None, 
                    stop_word_fpath="/Users/bwallace/dev/abstrackr-web/abstrackr/lib/stop_list.txt"):
        '''
        assumes the ordering of ids is the same as the ordering of titles 
        and abstracts! 
        '''
        self.all_ids = ids
        self.N = len(self.all_ids)
        self.ids_to_indices = dict(zip(self.all_ids, range(self.N)))

        for i, id_ in enumerate(self.all_ids):
            self.ids_to_indices[id_] = i 
        
        self.titles = self._replace_None(titles)
        self.abstracts = self._replace_None(abstracts)
        self.mesh = self._replace_None(mesh)
        
        assert(len(ids) == len(titles) == len(abstracts))
        
        self.lbl_dict = lbl_dict

        print "done. now reading labels in..."
        self._setup_lbl_vecs()
        self.stop_word_list_path = stop_word_fpath
        #self.stop_word_list_path = "/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/stop_list.txt"
        self._load_stopwords()
        print "alright -- encoding!"
        self.encode()

    def _replace_None(self, x):
        for i, x_i in enumerate(x):
            if x_i is None:
                x[i] = ""
        return x

    def __len__(self):
        return self.N

    def get_train_X_y(self):
        train_indices = self._get_train_indices()
        if len(train_indices) == 0:
            raise Exception, "nothing has been labeled yet!"
        
        return self.get_X_y(indices=train_indices)

    def _get_train_indices(self):
        return [self.ids_to_indices[id_] for id_ in self.labeled_ids]

    def _get_test_indices(self):
        return [self.ids_to_indices[id_] for id_ in self.unlabeled_ids]

    def get_test_X_y(self):
        test_indices = self._get_test_indices()
        return self.get_X_y(indices=test_indices)

    def get_test_ids(self):
        return self.unlabeled_ids

    def get_train_level_1_y(self):
        train_indices = self._get_train_indices()
        return self.l1s[train_indices].tolist()

    def get_X_y(self, indices=None):
        ids = []
        if indices is not None:
            if len(indices) == 0:
                raise Exception, "list of indices is empty."
            return self.abstracts_X[indices], self.titles_X[indices], self.mesh_X[indices], self.l1s[indices]
        return self.abstracts_X, self.titles_X, self.mesh_X, self.l1s

    def encode(self):
        self.abstracts_vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=50000, min_df=3, 
                                                    stop_words=self.stopwords)
        print "vectorizing abstracts..."
        self.abstracts_X = self.abstracts_vectorizer.fit_transform(self.abstracts)
        print "done. %s abstract features. now titles ..." % self.abstracts_X.shape[1]

        self.titles_vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=50000, min_df=3, 
                                                    stop_words=self.stopwords)
        self.titles_X = self.titles_vectorizer.fit_transform(self.titles)
        print "ok. %s title features." % self.titles_X.shape[1]
        self.mesh_X = None
        
        print "and finally, mesh..."
        self.mesh_vectorizer = TfidfVectorizer(max_features=50000, min_df=3)
        self.mesh_X = self.mesh_vectorizer.fit_transform(self.mesh)
        print "ok -- %s mesh features." % self.mesh_X.shape[1]

        print "all encoded!"

    def _load_stopwords(self):
        self.stopwords = [w.strip() for w in open(self.stop_word_list_path, 'rU').readlines()]

    def _setup_lbl_vecs(self):
        self.l1s = np.zeros(self.N)
        self.labeled_count = 0
        self.labeled_ids, self.unlabeled_ids = [], []
        for i, id_ in enumerate(self.all_ids):
            # now set the labels
            if id_ not in self.lbl_dict:
                # not yet labeled
                self.l1s[i] = None
                self.unlabeled_ids.append(id_)
            else:
                self.labeled_ids.append(id_)
                self.labeled_count += 1
                if self.lbl_dict[id_] > 0:
                    self.l1s[i] = 1.0
                else:
                    self.l1s[i] = -1.0

        count_ones = lambda a: len([x for x in a if x == 1])
        print "%s total labeled; %s includes" % (
                        self.labeled_count,
                        count_ones(self.l1s))