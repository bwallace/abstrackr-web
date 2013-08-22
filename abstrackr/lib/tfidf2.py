#!/usr/bin/env python
# encoding: utf-8
#
# 
# The MIT License
# 
# Copyright (c) 2009 Byron Wallace
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

'''
Byron C Wallace
Tufts Medical Center

A module for encoding text documents. Used to be just tf-idf; has since grown
to include domain adaptation tricks, &etc.

Assumes you have cleaned individual title files in "Titles" directory
It is also assumed that the names of these files (e.g,. 1.*) map
to an ID (e.g., refman ID). I.e., 1.* -> reference id 1. These are used as identifiers.

Usage (assuming you've a directory of text files "Titles"')
>titles = tfidf2.build_bag_of_words_over_dir("Titles")

You'll need a list of ids that are 'positives' (e.g., "relevant")
>pos_indices = { read in and build this list }

Now we can dump to some file specified by outpath
>tfidf_to_file_for_lib_SVM(titles, pos_indices, outpath)

Alternatively, do it all at once with the encode_docs method.
'''

import re
import math
import string
import os
import pdb
import csv
import sys
import random
from operator import itemgetter
import pickle

###
# 5/6/11
# if you want to do stuff with author networks, you need
# to import the networks module. however, this leads to a
# circular import, which is problematic...
#import networks
try:
  import nose
except:
  print "nose isn't installed -- can't run unittests!"

### 
# 9/20/11
# required stuff for SCL, &etc.
###
try:
  import numpy
  import liblinear
  import liblinearutil
  from liblinear import *
  from liblinearutil import *
except:
  print "either numpy or liblinear isn't installed -- won't be able to do fancy stuff like SCL"

import copy


#stop_list_path=os.getcwd() + "/abstrackr/lib/stop_list.txt"
stop_list_path = "/Users/abstrackr-user/Hive/abstrackr/abstrackr/lib/stop_list.txt"

print "stop word list path is %s" % stop_list_path

def build_stop_list(stop_list_path):
    exclude_words = ["a", "about", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thick", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves"]
#    exclude_words = []
#    if stop_list_path != None:
#        f = open(stop_list_path)
#        while 1:
#            line = f.readline()
#            if not line:
#                break
#            # Every line is assumed to be a single word
#            exclude_words.append(line.strip())
    return exclude_words

# if you don't want to use a stop list, just set the stop_list global
# to an empty list (stop_list = [])
print "building stop word list..."
stop_list = build_stop_list(stop_list_path)
print "done."


def add_labels(new_path, lbl_dict):
    lbls = [x for x in csv.reader(open(new_path, 'r'))]
    for l in lbls:
        #lbl_dict[eval(l[0])] = "-1" if l[1]=="n" else "1"
        lbl_dict[eval(l[0])] = "1" if l[1] in ("y", "m") else "-1"
    return lbl_dict
    

def update_labels(fpath, outpath, new_lbl_d, unlabel_if_not_in_dict=False, ignore_these=[]):
    ''' relabels the instances in fpath with new_lbl_d; writes to outpath. '''
    if not isinstance(new_lbl_d.keys()[0] , int):
        new_lbl_d = lbls_to_strs(new_lbl_d)
        
    new_file = []
    lines = open(fpath).readlines()
    for line in lines:
        line_sp = line.split(" ")
        cur_id = eval(line_sp[0])

        if cur_id not in ignore_these:
            if cur_id in new_lbl_d.keys():
                line_sp[1] = str(new_lbl_d[cur_id])
            elif unlabel_if_not_in_dict:
                line_sp[1] = "?"
            try:
                new_file.append(" ".join(line_sp))
            except:
                pdb.set_trace()
    outf = open(outpath, 'w')
    outf.write("".join(new_file))
    

def lbls_to_strs(lbl_d):
    new_d = {}
    for xid in lbl_d:
        new_d[xid] = str(lbl_d[xid])
    return new_d

def abstrackr_encode(dir_path, out_dir, label_d=None, \
                        fields=["AB", "MH", "TI"], min_word_count=3,\
                        bi_grams_too=False):
    cleaned_dir_d = {}
    for field in fields:
        field_path = os.path.join(dir_path, field)
        clean_docs_path = os.path.join(field_path, "Cleaned")
        if not os.path.exists(clean_docs_path):
            _mkdir(clean_docs_path)
        clean_up_docs(field_path, out_dir=clean_docs_path)
        cleaned_dir_d[field] = clean_docs_path
    
    merge_fields(cleaned_dir_d, out_dir)

    print "ok -- fields cleaned and written out. building BOW"

    encode_docs(out_dir, os.path.join(out_dir, "encoded"), "merged_encoded", \
                lbl_dict=label_d, clean_first=False, bi_grams_too=bi_grams_too,\
                min_word_count=min_word_count)

def encode_docs(dir_path, out_path, out_f_name, 
                lbl_dict=None, clean_first=True, binary=True, 
                min_word_count=3, bi_grams_too=False, delete_files_after=False):
    '''
    Given a directory path, this method cleans, then encodes and writes out all text files therein.
    '''
    
    if lbl_dict is not None and len(lbl_dict)>0:
        if not isinstance(lbl_dict.values()[0], str):
            print "\n\n\n*****labels are *not* strings, but they need to be!\n going to force this, MAKE SURE THIS IS SANE\n\n"
            lbl_dict = lbls_to_strs(lbl_dict)
 
            
    # first, clean the documents
    if clean_first:
        print "cleaning documents.."
        clean_docs_path = os.path.join(dir_path, "Cleaned")
        if not os.path.exists(clean_docs_path):
            _mkdir(clean_docs_path)
        clean_up_docs(dir_path, out_dir=clean_docs_path)
        print "done cleaning."
    else:
        clean_docs_path = dir_path

    if not os.path.exists(out_path):
        _mkdir(out_path)

    # now build tf/idf representation
    print "encoding..."
    encoded_docs = build_bag_of_words_over_dir(
          clean_docs_path, binary_encode=binary, 
          min_word_count=min_word_count, bi_grams_too=bi_grams_too,
          word_index_path=os.path.join(out_path, "word_index.txt"))
    print "done encoding."
    
    # now write it out
    print "writing doc out..."
    pos_ids = []
    neg_ids = []      
    if lbl_dict is not None:
        ### note that we count 0s as positive!
        pos_ids = [str(x_id) for x_id in lbl_dict.keys() if lbl_dict[x_id] in ["1", "1.0", "0"]]
        neg_ids = [str(x_id) for x_id in lbl_dict.keys() if not lbl_dict[x_id] in ["1", "1.0"]]
     

    tfidf_to_file_for_lib_SVM_multi_label(encoded_docs, pos_ids, neg_ids,
                                                            None, os.path.join(out_path, out_f_name))
    
    if delete_files_after:
        # then we wipe out the files from disk
        print "removing files from disk..."
        # remove the original files
        clean_up(dir_path)
        # and the 'clean' files
        clean_up(clean_docs_path)
        print "all clean."

    print "done."
    
def clean_up(dir_path, word_file_name="word_index.txt"):
    
    #word_index_path = os.path.join(dir_path, "word_index.txt")

    files_to_del = [f for f in os.listdir(dir_path) 
                        if f != word_file_name and 
                        not os.path.isdir(os.path.join(dir_path, f))]

    for p in files_to_del:
        full_file_path = os.path.join(dir_path, p)
        try:
            os.remove(full_file_path)
        except:
            print "failed to delete file %s!" % p


def bag_of_authors(ids_to_authors):
    all_authors = []
    for author_list in ids_to_authors.values():
        all_authors.extend(author_list)
    
    authors_set = list(set(all_authors))
    # filter list
    authors_set = [author for author in authors_set if all_authors.count(author)>=3]
    author_indices_d = {}
    for i, author in enumerate(authors_set):
        author_indices_d[author] = i
    
    # now walk over all ids
    bag_o_authors = {}
    for article_id in ids_to_authors.keys():
        bag_o_authors[article_id] = {}
        for author in [article_author for article_author in ids_to_authors[article_id] if article_author in authors_set]:
            bag_o_authors[article_id][author_indices_d[author]] = 1.0
            
    return bag_o_authors
        
def xml_to_bag_of_authors(xml_path, lbl_d, out_path):
    ids_to_authors = networks.get_ids_to_authors(xml_path)
    assert(lbl_d.keys() == ids_to_authors.keys()) # although ordering doesn't matter...
    boa = bag_of_authors(ids_to_authors)
    out_str = []
    for xid in ids_to_authors.keys():
        #id, level1_lbl, level2_lbl, x
        out_str.append(lib_svm_str_multi_label(xid, lbl_d[xid], None, boa[xid]))
    fout = open(out_path, 'w')
    fout.write("\n".join(out_str))
    

def remove_docs(f_path, ids_to_remove):
    pass
    

def tdidf(wordfreqs, freqvecs):
    '''
    Returns tf-idf feature vectors. For a simple explanation, see: http://instruct.uwo.ca/gplis/601/week3/tfidf.html
  
    wordfreqs -- Vector s.t. w[i] is the total number of times word i was seen over all documents.
    freqvecs -- A dictionary mapping document ids to (raw) frequency vectors. 
    
    returns a dictionary mapping the keys in freqvecs to their tf-idf feature-vector representation
    '''
    N = len(freqvecs.keys()) # Total number of documents
    num_terms = len(wordfreqs) # Number of terms
    print "Number of documents: %s, number of terms %s" % (N, num_terms)
    print "Building n_vec..."
  
    # i is the document index; j the word/term index
    print "Building n_vec..."
    n_vec = [0 for j in range(num_terms)]
    for i in range(N):
      cur_doc = freqvecs[freqvecs.keys()[i]]
      for j in range(num_terms):
          if cur_doc[j] > 0:
              n_vec[j]+=1

    print "Word counts built, Now constructing TDF vector."
    tdfvecs = {}
    last_key = None
    for i in range(N):
      cur_key = freqvecs.keys()[i]
      last_key = cur_key
      
      if i%100 == 0:
          print "On document %s" % i
  
      cur_doc = freqvecs[cur_key]
      tdfvec = [0 for k in range(num_terms)] 

      for j in range(num_terms):
          # tf * idf
          tdfvec[j] = cur_doc[j] * math.log(N/n_vec[j], 2.0)
      # Normalize by the l2 norm
      cos_norm = math.sqrt(sum([tdfvec[j]**2 for j in range(num_terms)]))
      if cos_norm == 0:
          # None of the terms were in this document. Just return a vector of zeros.
          tdfvec = [0 for i in range(num_terms)]
      else:
          tdfvec = [tdfvec[j]/cos_norm for j in range(num_terms)]
  
      if cur_key in tdfvecs:
        print "Error -- key (doc id) already exists???"
        pdb.set_trace()
        
    
      tdfvecs[cur_key]=tdfvec
    return tdfvecs
  

def build_word_count_vector_for_doc(words, doc):
    '''
    Returns a vector V where V_i corresponds to the number of times words_i is contained in doc
    '''
    ### TODO implement sparse encoding here!
    count_vec = [doc.count(word) for word in words]
    return count_vec

    
def build_bag_of_words_feature_vectors(ids_to_texts, words, binary_encode=False):
    freq_vecs = {}
    for id in ids_to_texts.keys():
        if not binary_encode:
            freq_vecs[id] = build_word_count_vector_for_doc(words, ids_to_texts[id])
        else:
            # binary encoding -- 1or 0 for each word (present or not, respectively)
            
            ####
            # 12/17/10 -- sparse encoding now!
            ####
            doc = ids_to_texts[id]
            freq_vecs[id] = {}
            for i in xrange(len(words)):
                word = words[i]
                if word in doc:
                    freq_vecs[id][i] = 1.0
	
    if binary_encode:
        return freq_vecs
        
    word_freqs = [sum([ids_to_texts[id].count(w) for id in ids_to_texts.keys()]) for w in words]
    return tdidf(word_freqs, freq_vecs)

def build_bag_of_words_feature_vectors_scaled(ids_to_texts, words, labeled_terms, c=2):
    #
    # !!! Not finished. May want to implement this. 
    # Idea: scale entries in feature vectors to weight 
    # labeled terms more heavily than the rest (see Raghaven et al)
    #
    
    freq_vecs = {}
    for id in ids_to_texts.keys():
        # binary encoding -- 1or 0 for each word (present or not, respectively)
        doc = ids_to_texts[id]
        for word in words:
            cur_fv = []
            if word in doc:
                if word in labeled_terms:
                    cur_fv.append(c)
                else:
                    cur_fv.append(1.0)
            else:
                cur_fv.append(0.0)
                
        freq_vecs[id] = [1.0 if word in doc else 0.0 for word in words]

    return freq_vecs
    
    
    
def build_bag_of_words_over_dir(dir_path, split_txt_on = " ", binary_encode = False, \
                                word_index_path = None, word_index_out_dir=None,\
                                min_word_count = 3, bi_grams_too=False):
    '''
    Build bag of words representation vectors over *all of the documents* in dir_path.
    Note that we assume the documents are already clean.
    '''
    
    if word_index_path is None:
        word_index_path = os.path.join(dir_path, "word_index.txt")
    
    # read all the words in     
    s_words = []
    files_in_dir = [f for f in os.listdir(dir_path) if not os.path.isdir(os.path.join(dir_path, f))]

    for p in files_in_dir:
      try:
          doc_text = open(os.path.join(dir_path, p), 'r').readlines()[0].split(" ")
          s_words.extend(doc_text)
          if bi_grams_too:
            # then append bi-grams
            bi_grams = extract_bi_grams(doc_text)
            s_words.extend(bi_grams)
      except:
          pass
    
    unique_word_dict = {}
    set_words = list(set(s_words))
    for w in set_words:
        unique_word_dict[w] = 0
    
    ids_to_txt = {}
    words = []
    # ignore the word_index.txt file, which we generated
    for p in [f for f in files_in_dir if not "word_index.txt" in f]:
        cur_txt =[""]

        try:
            cur_txt = open(os.path.join(dir_path, p), 'r').readline().split(split_txt_on)

            if bi_grams_too:
                cur_txt.extend(extract_bi_grams(cur_txt))

            for word in cur_txt:
                unique_word_dict[word] += 1
        

        except  Exception, e:
            # abstract is missing!
            pass
        
        id = p.split(".")[0]
        ids_to_txt[id] = cur_txt
        words.extend(cur_txt)
    
    print "number of words: %s; number of unique words: %s" % (len(words), len(set_words))
    words = [word for word in unique_word_dict.keys() if unique_word_dict[word] >= min_word_count]

    word_index_out = open(word_index_path, 'w')
    word_index_out.write(str(words))
    word_index_out.close()

    return build_bag_of_words_feature_vectors (ids_to_txt, words, binary_encode=binary_encode)

def extract_bi_grams(words):
    # assumes words is an *ordered* list of strings
    bi_grams = []
    for w_i in xrange(len(words)-1):
        bi_grams.append("%s %s" % (words[w_i], words[w_i+1]))
    return bi_grams

def clean_up_txt(doc):
    ''' 
    Cleans and returns the parametric abstract text. I.e., strips punctuation, etc. Also removes
    any words in the stop list (if provided).
    '''
    words = []
    exclude_words = []
            
    # for hyphenated words, it makes more sense to split the
    # atoms and append both parts to the word list.
    split_on = ["-", "/"]
    for sp_char in split_on:
        for word in doc: 
            if sp_char in word:
                doc.extend(word.split(sp_char))
                try:
                    doc.remove(word)
                except:
                    pdb.set_trace()
    
    exclude = set(string.punctuation)
    for word in doc:
        word = word.lower()
        clean_word = ''.join(c for c in word if c not in exclude).strip()
        if clean_word and not clean_word in stop_list:
            if isnumerical(clean_word):
                clean_word = "NUMBER"
            words.append(clean_word)

    return words

def isnumerical(w):
    try:
        xfl = float(w)
        return True
    except:
        return False
    
    
def clean_up_docs(dir_path, out_dir = None, overwrite_dirty=False, grammar_only=False):
    if out_dir is not None:
        try:
            _mkdir(out_dir)
        except:
            pass # presumably the directory already exists
    else:
        out_dir = dir_path
    
    print "\ncleaning documents in %s..." % dir_path
    for doc in [f for f in os.listdir(dir_path) if not os.path.isdir(os.path.join(dir_path, f))]:
        dirty_path = os.path.join(dir_path, doc)
        ###
        # NOTE: we used to just read the first line and split on the
        #dirty_doc = open(dirty_path, 'r').readline().split(" ")
        all_text = " ".join(open(dirty_path, 'r').readlines())
        dirty_doc = all_text.split(" ")
        
        if not grammar_only:
            clean_doc = clean_up_txt(dirty_doc)
        else:
            # just stripping commas
            clean_doc = [x.replace(",", "") for x in dirty_doc]

        out_path = dirty_path if overwrite_dirty else dirty_path + ".cleaned"
        if out_dir != dir_path:
            # then an output directory was passed in
            out_path = os.path.join(out_dir, doc)
        clean_doc_out = open(out_path, 'w')
        clean_doc_out.write(" ".join(clean_doc))
    print "documents cleaned and written."


def merge_fields(cleaned_dirs_d, out_dir):
    '''
    cleaned_dirs_d -- dictionary mapping fields to directories containing
                        (cleaned) files. e.g., "abstract" -> "my_path/abstracts/Cleaned"
    '''
    try:
        _mkdir(out_dir)
    except:
        pass # probably already exists


    for file_id in [f for f in os.listdir(cleaned_dirs_d.values()[0]) if not f=="word_index.txt"]:
        merged = [] # will contain all the words from this file, for all fields
        for field in cleaned_dirs_d.keys():
            cur_field_words = open(os.path.join(cleaned_dirs_d[field], file_id)).readline()
            cur_field_words = ["%s_%s" % (field.upper(), word) for word in cur_field_words.split(" ")]
            merged.extend(cur_field_words)
        
        # now write the merged file out
        fout = open(os.path.join(out_dir, file_id), 'w')
        fout.write(" ".join(merged))
        fout.close()


def gen_train_test(fv_file_path, n, train_path="train", test_path="test"):
    # splits the train file found @ fv_file_path
    # into train/test sets; the train set will
    # comprise the first n instances. 
    lines = open(fv_file_path).readlines()
    train = lines[:n]
    test = lines[n:]

    fout = open(train_path, 'w')
    fout.write("".join(train))
    fout.close()

    fout = open(test_path, 'w')
    fout.write("".join(test))
    fout.close()


def scl(src_folder, src_fv_name, tgt_folder, tgt_fv_name, \
            out_path, pivot_features=None, num_pivots=50, \
            src_word_list_name="word_index.txt", \
            tgt_word_list_name="word_index.txt"):
    '''
    structural correspondence learning (Blitzer, McDonal, Pereira; ACL 06)

    note: this will only work on Python 2.6+!

    pivot_features -- use this argument if you want to specify a list of
                    pivot features to use explicitly. the list should
                    be the words themselves (not indices). if it is None, the top 
                    num_pivots features (default 50, per Blitzer et al, section 7.1)
                    occuring in both the source and target domain will be used as pivots
    
    '''
    src_fv = os.path.join(src_folder, src_fv_name)
    tgt_fv = os.path.join(tgt_folder, tgt_fv_name)

    src_word_list_path = os.path.join(src_folder, src_word_list_name)
    tgt_word_list_path = os.path.join(tgt_folder, tgt_word_list_name)

    ### note that the indices_to_words are just lists!
    src_indices_to_words = eval(open(src_word_list_path).readline())
    tgt_indices_to_words = eval(open(tgt_word_list_path).readline())

    # all words, i.e., unioned lexicon
    shared_space = list(set(src_indices_to_words + tgt_indices_to_words))

    ### this changes things!! ahh
    import random
    random.shuffle(shared_space)

    shared_words_to_indices = {}
    for i, word in enumerate(shared_space):
        shared_words_to_indices[word] = i

    num_features = len(shared_space)

    source_instances = [l.replace("\n", "").split(" ") for l in open(src_fv).readlines()]
    target_instances = [l.replace("\n", "").split(" ") for l in open(tgt_fv).readlines()]

    W = [] # the columns of W will be the weight vectors corresponding to the pivots

    # going to have to create a new dataset for each pivot feature
    for pf_l in pivot_features:
        ###
        # first transform the instances to a shared space
        # the labels here denote whether or not the corresponding
        # instance contains the current pivot feature (pf_l)
        ###
        src_instances_l, src_lbls_l = _transform_instances(pf_l, \
                                            source_instances, src_indices_to_words,\
                                            shared_words_to_indices, shared_space)
         
        tgt_instances_l, tgt_lbls_l = _transform_instances(pf_l, \
                                            target_instances, tgt_indices_to_words,\
                                            shared_words_to_indices, shared_space) 
      
                                                                    
        instances_l = src_instances_l + tgt_instances_l
        lbls_l = src_lbls_l + tgt_lbls_l

        ###
        # now feed this to liblinear and get the weight
        # vector out. 
        #
        # note -- the try: block is due to Windows consistently
        # yelling about memory read errors. grr. so I'm just being
        # uber-hacky about things for now. 
        success = False
        while not success:
            try:

                m =  train(lbls_l, instances_l)
                print "pf_l: %s" % pf_l

                print lbls_l.count(1)
                #w_l = m.w[:num_features]
                #pdb.set_trace()
                w_l = m.w[:num_features]
   
                success = True
            except:
                print "fail."
                pass

                                                        
        ###
        # 1. _create_dataset_for_pf
        # 2. feed this dataset to liblinear
        # 3. get the W out
        W.append(w_l)

    ### SVD of pivot predictor matrix
    W = numpy.mat(W)
    W = W.transpose()
    U, D, Vt = numpy.linalg.svd(W, full_matrices=0)
    # here's our projector. in the paper, they
    # truncate this guy, but i'm not entirely sure why?
    # I suppose if you've a ton of pivots..?
    theta = U.transpose()

    ###
    # now we augment the feature vectors with the projections
    # note that the projection itself is done inside of the
    # _to_scl_str method
    ###

    # first the source
    out_str = []
    for x in source_instances:
        out_str.append(\
            _to_scl_str(x, theta, src_indices_to_words, shared_words_to_indices, num_features))

    for x in target_instances:
        out_str.append(\
            _to_scl_str(x, theta, tgt_indices_to_words, shared_words_to_indices, num_features))



    # finally, write out to a file
    fout = open(outpath, 'w')
    fout.write("\n".join(out_str))
    fout.close()

def _to_scl_str(x, theta, indices_to_words, shared_words_to_indices, num_features):
        
        x_str = [" ".join(x[:3])] # id level1 level2
        #x = " ".join(x[3:])
        x = x[3:]

        x_dict = {}
        x_arr = numpy.zeros(num_features)

        for f_index, value in [s.split(":") for s in x]:
            f_index = int(f_index)
            the_word = indices_to_words[f_index]
            shared_index = shared_words_to_indices[the_word]
            #x_dict[shared_index] = float(value)
            x_str.append("%s:%s" % (shared_index, value))
            x_arr[shared_index] = float(value)
        
        ###
        # project to shared space; append proction to
        # feature vector
        projection = numpy.dot(theta, x_arr).tolist()[0]
        for j in range(len(projection)):
            # append the projection to the feature vector
            x_str.append("%s:%s" % ((num_features+j), projection[j]))

        return " ".join(x_str)

def _transform_instances(pf_l, instances, indices_to_words, \
                            shared_words_to_indices, shared_space):
    instances_l = []
    lbls_l = []
    
    # just IN CASE (get it???)
    pf_l = pf_l.lower()

    total_slows = 0
    yes_slows = 0

    for x in instances:
        # for debuggign
        cur_doc = []
        cur_doc_shared = []
        slow_in_it = False

        cur_inst = {} # dictionary mapping feature indices to values
        y = -1 # assume the word pf_l is not in x
        x = x[3:] # ignore id lbl1 lbl2
        for f_index, value in [s.split(":") for s in x]:
            f_index = int(f_index)
            the_word = indices_to_words[f_index]
            cur_doc.append(the_word)
            
            if the_word.startswith("MH_"):
                # TODO remove numbers -- TEMP HACK need regex
                the_word.replace("11061", "").replace("57", "")

            ### remove field tokens
            the_word = the_word.replace("AB_", "").\
                            replace("TI_", "").replace("MH_", "")

            if the_word == pf_l or the_word + "s" == pf_l:
                # note also that in this case we *do not*
                # add the word to the instances feature
                # vector, since this would make it trivially
                # easy to classify
                y = 1
            else:
                # we retrieve the word again, since we butchered
                # it above to check it against the pivot feature
                the_word = indices_to_words[f_index]
                shared_index = shared_words_to_indices[the_word]
                cur_doc_shared.append(shared_space[shared_index])
                cur_inst[shared_index] = float(value)
        
        # feats= [int(s.split(":")[0]) for s in x]
        # words = [indices_to_words[xid] for xid in feats]

        if slow_in_it:
            total_slows += 1
            if y == 1:
                yes_slows += 1
            #pdb.set_trace()

        instances_l.append(copy.deepcopy(cur_inst))
        lbls_l.append(y)

    return (instances_l, lbls_l)



def output_word_probs(input_folder, fv_name, 
                            word_list_path, \
                            fout_path=None):
    '''
    output a file with rows as follows:

        word | index | p(y=1|word) | p(y=1|word)
    '''
    ###
    # we need access to the learners.
    ###
    sys.path.append("../modeling/curious_snake")
    import dataset
    import learners.base_nb_learner as base_nb_learner # naive bayes
    import pickle

    path_to_src = os.path.join(input_folder, fv_name)
    source_dataset = dataset.build_dataset_from_file(path_to_src)
    
    word_list = eval(open(word_list_path).readline())


    ###
    # construct a naive bayes learner over the source
    # dataset.
    nb_learner_src = base_nb_learner.BaseNBLearner([source_dataset])
    nb_learner_src.label_all_data() # legal, because this is the source data
    nb_learner_src.rebuild_models(True)

    cond_probs = nb_learner_src.models[0].conditional_probs
    out_d = {}
    for f_j in cond_probs.keys():
        word = word_list[f_j]
        out_d[word]=cond_probs[f_j]

    '''
    out_str = ["word\tsource_index\tp(y=1|x)\tp(y=-1|x)"]
    for f_j in cond_probs:
        if f_j % 100 == 0:
            print "on feature %s" % f_j

        word = source_word_list[f_j]
        if word in target_word_list:
            tgt_index = target_word_list.index(word)
            target_word_list.pop(word)
            p_1, p_0 = cond_probs[f_j][1], cond_probs[f_j][-1]
            out_str.append("%s\t%s\t%s\t%s\t%s" % (word, f_j, tgt_index, p_1, p_0))
    '''
    if fout_path is None:
        fout_path = os.path.join(input_folder, "%s_probs_d" % fv_name)

    fout = open(fout_path, 'w')
    pickle.dump(out_d, fout)
    fout.close()
    #pdb.set_trace()


def pooling_adapt(input_folder, src_fv_name, tgt_fv_name, fout_path,\
                    shared_word_list_name="shared_word_list.txt",
                    N=200):
    '''
    note that we assume instances are here represented in
    a *shared* space (comprising the words in shared_word_list_name) 

    sample call

        pooling_adapt("_transfer/prostate", 
                      "prostate_as_ab_mh_ti_shared_representation", 
                      "prostate_ab_mh_ti_shared_representation", 
                      "_transfer/prostate/pooling_adapt", 
                      "shared_word_list.txt")
    '''

    ###
    # we need access to the learners.
    ###
    sys.path.append("../modeling/curious_snake")
    import dataset
    import learners.base_nb_learner as base_nb_learner # naive bayes

    path_to_src = os.path.join(input_folder, src_fv_name)
    source_dataset = dataset.build_dataset_from_file(path_to_src)
    
    path_to_tgt = os.path.join(input_folder, tgt_fv_name)
    target_dataset = dataset.build_dataset_from_file(path_to_tgt)

    ###
    # make sure that the ids are unique
    s1 = set(source_dataset.instances.keys())
    s2 = set(target_dataset.instances.keys())
    if len(s1.intersection(s2))  > 0:
        raise Exception, "whoops, you don't have unique ids bro."
    
    # the start index for psuedo instances 
    start_index = max(max(source_dataset.instances.keys()), \
                      max(target_dataset.instances.keys())) + 1
                    
    shared_word_list = \
            eval(open(os.path.join(input_folder, shared_word_list_name)).readline())
    ###
    # construct a naive bayes learner over the source
    # dataset.
    nb_learner_src = base_nb_learner.BaseNBLearner([source_dataset])
    nb_learner_src.label_all_data() # legal, because this is the source data
    nb_learner_src.rebuild_models(True)

    ####
    # construct a learner on the *target*
    # we're going to cheat for now on the 
    # features -- this is our ORACLE
    nb_learner_test = base_nb_learner.BaseNBLearner([target_dataset])
    nb_learner_test.label_all_data() # CHEATING
    nb_learner_test.rebuild_models(True)

    best_features = _top_k_features(nb_learner_src.models[0].conditional_probs, 100)
    best_feature_words = [shared_word_list[f[0]] for f in best_features]


    # map features to their \deltas in the target task
    conditional_probs = nb_learner_test.models[0].conditional_probs
    test_features_to_deltas = {}
    for f_j in conditional_probs:
        test_features_to_deltas[f_j] = conditional_probs[f_j][1]-conditional_probs[f_j][-1]
    
    # what are the deltas in the test set for the features that were the 'best'
    # in the source set?
    best_f_deltas_in_test = [test_features_to_deltas[f_star[0]] for f_star in best_features]
    
    # generate our psuedo instance string
    psuedo_instance_str = _psuedo_positives(best_features, N, start_index)

    ###
    # assemble a string containing
    #       <the source dataset>
    #       # target dataset starts here
    #       <the target dataset>
    #       # psuedo-instances start here   
    #       <psuedo-instances>
    out_str = open(path_to_src).readlines()
    out_str.append("\n# target dataset starts here! \n")
    out_str.extend(open(path_to_tgt).readlines())
    out_str.append("\n# psuedo instances start here! \n")
    out_str.append("\n".join(psuedo_instance_str))
    fout = open(fout_path, 'w')
    pdb.set_trace()
    fout.write("".join(out_str))
    fout.close()
    print "ok -- file written to %s" % fout_path
    #pdb.set_trace()


def _psuedo_positives(feature_ids, N, start_feature_id, m=20):
    return_str = []
    for i in xrange(N):
        cur_str = ["%s 1 ? " % (start_feature_id + i)]
        feats = random.sample(feature_ids, m)
        for f_j in feats:
            cur_str.append("%s:1.0" % f_j[0])

        
        return_str.append(" ".join(cur_str))
    return return_str
        

def _top_k_features(conditional_probs, k):
    ''' top k most discriminative features '''
    features_to_deltas = {}
    ## greatest margin between estimate (P) given c=1 versus
    # for c=-1.
    for f_j in conditional_probs:
        features_to_deltas[f_j] = conditional_probs[f_j][1]-conditional_probs[f_j][-1]
    
    sorted_features = sorted(features_to_deltas.items(), key=itemgetter(1), reverse=True)
    return sorted_features[:k]


def map_src_to_tgt(src_folder, src_fv_name, tgt_folder, \
                    src_word_list_name="word_index.txt", \
                    tgt_word_list_name="word_index.txt"):

    '''
    this simple transformation simply maps the src instances
    into the target instances' feature space.
    '''
    src_word_list_path = os.path.join(src_folder, src_word_list_name)
    tgt_word_list_path = os.path.join(tgt_folder, tgt_word_list_name)

    src_fv = os.path.join(src_folder, src_fv_name)
    
    src_indices_to_words = eval(open(src_word_list_path).readline())
    tgt_indices_to_words = eval(open(tgt_word_list_path).readline())

    tgt_words_to_indices = {}
    for i, word in enumerate(tgt_indices_to_words):
        tgt_words_to_indices[word] = i

    # now we transform the target instances
    mapped_src = []
    src_vector = [l.replace("\n", "").split(" ") for l in open(src_fv).readlines()]
    for line_index, x in enumerate(src_vector):
        if line_index % 100 == 0:
            print "on line %s of %s" % (line_index, src_fv_name)
        x_transformed = x[:3] # grap id lbl1 lbl2
        total_count, intersect_count = 0, 0
        for src_index, value in [s.split(":") for s in x[3:]]:
            word = src_indices_to_words[int(src_index)]
            total_count += 1
            if word in tgt_indices_to_words:    
                intersect_count += 1
                transformed_index = tgt_words_to_indices[word]
                x_transformed.append("%s:%s" % (transformed_index, value))
        
        mapped_src.append(x_transformed)
    print "ok -- done with %s. intersction size: %s out of %s" % \
                (src_fv_name, intersect_count, total_count)
    return mapped_src

def easy_adaptation(src_folder, src_fv_name,\
                    tgt_folder, tgt_fv_name, \
                    out_path, \
                    src_word_list_name="word_index.txt", \
                    tgt_word_list_name="word_index.txt", \
                    shared_space_only=False,
                    separate_files=False, enforce_unique_ids=True):
    '''
        Daume III's frustratingly easy domain adaptation (ACL, 2007).

        the feature vectors in the respective directories will be mapped
        into a shared representation. the only difference between src and
        tgt here is that the latter will be at the end of the file (the 
        former at the start), so the first m entries of the produced feature
        vector file will correspond to the source data (assuming the source
        data comprises m instances) and the rest to target. labels will be
        kept.

        both folders are to contain feature vectors (src/tgt_fv_name) and word
        lists which are python lists (literally, strings; not pickled) like:
            [hello, world, ... , blah]
        and the ith word corresponds to index i (obviously).

        out_path is a directory

        shared_space_only will simply map both feature sets
        to a shared space (useful for, e.g., using our pooling adapt method)
    '''
    src_word_list_path = os.path.join(src_folder, src_word_list_name)
    tgt_word_list_path = os.path.join(tgt_folder, tgt_word_list_name)

    src_fv = os.path.join(src_folder, src_fv_name)
    tgt_fv = os.path.join(tgt_folder, tgt_fv_name)

    # map source/target words to thei new indices
    ### note that the indices_to_words are just lists!
    src_indices_to_words = eval(open(src_word_list_path).readline())
    tgt_indices_to_words = eval(open(tgt_word_list_path).readline())

    all_words = src_indices_to_words + tgt_indices_to_words
    print "total words in two datasets: %s" % len(all_words)
    shared_word_list = list(set(all_words))
    print "length of shared representation: %s" % len(shared_word_list)
    print "total words in common: %s" % (len(all_words) - len(shared_word_list))
 
    _mkdir(out_path)
    outf = open(os.path.join(out_path, "shared_word_list.txt"), 'w')
    outf.write(str(shared_word_list))
    outf.close()
    shared_size = len(shared_word_list)

    words_to_shared_indices = {}
    for i, word in enumerate(shared_word_list):
        words_to_shared_indices[word] = i

    transformed_representation = []
    ''' 
         map x -> <x, x, 0> in source and
             x -> <x, 0, x> in target
    '''
    source_vector = [l.replace("\n", "").split(" ") for l in open(src_fv).readlines()]
    list_of_source_xids = []
    for x in source_vector:
        x_transformed = x[:3] #  id lbl1 lbl2
        list_of_source_xids.append(int(x_transformed[0]))
        for src_index, value in [s.split(":") for s in x[3:]]:
            word = src_indices_to_words[int(src_index)]
            transformed_index = words_to_shared_indices[word]

            ### <x, x, 0>
            # *shared* version
            x_transformed.append("%s:%s" % (transformed_index, value))

            if not shared_space_only:
                # *specific* version
                x_transformed.append("%s:%s" % ((transformed_index + shared_size), value))

        transformed_representation.append(" ".join(x_transformed))
    
    if separate_files:
        # write out the src in the transformed space
        fout = open(os.path.join(out_path, "%s_shared_representation" % src_fv_name), 'w')
        fout.write("\n".join(transformed_representation))
        fout.close()
        transformed_representation = []
    else:
        transformed_representation.append("# here is the start of the target file (%s)" % tgt_fv_name)
        print "first target instance will be @ %s" % len(transformed_representation)

    # now we transform the target instances
    target_vector = [l.replace("\n", "").split(" ") for l in open(tgt_fv).readlines()]
    for x in target_vector:
        x_transformed = x[:3] # grap id lbl1 lbl2
        cur_x_id = int(x_transformed[0])
        if enforce_unique_ids and cur_x_id in list_of_source_xids:
            # we're going to append '000' to the id
            # this is kind of hacky
            x_transformed[0] = str(cur_x_id) + '000'

        for tgt_index, value in [s.split(":") for s in x[3:]]:
            word = tgt_indices_to_words[int(tgt_index)]
            transformed_index = words_to_shared_indices[word]

            ### <x, 0, x>
            # *shared* version
            x_transformed.append("%s:%s" % (transformed_index, value))

            if not shared_space_only:
                # *specific* version (note the 2x)
                x_transformed.append("%s:%s" % ((transformed_index + 2*shared_size), value))
        transformed_representation.append(" ".join(x_transformed))

    if separate_files:
        fout = open(os.path.join(out_path, "%s_shared_representation" % tgt_fv_name), 'w')
        fout.write("\n".join(transformed_representation))
        fout.close()
    else:
        fout = open(os.path.join(out_path, "%s-%s" % (src_fv_name, tgt_fv_name)), 'w')
        fout.write('\n'.join(transformed_representation))
        fout.close()


def _map_indices_to_values(l):
    indices_to_vals = {}
    for i, val in enumerate(l):
        indices_to_vals[i] = val
    return indices_to_vals

#############################
#   File encoding routines  #
#############################
def tfidf_to_file_for_lib_SVM(tfidf, pos_ids, out_path):
    out_s  = []
    for id in tfidf.keys():
        lbl = None
        if pos_ids is None:
            lbl = "?"
        else:
            lbl = -1
            if id in pos_ids:
                lbl = 1
        out_s.append(lib_svm_str(lbl, tfidf[id]))

    open(out_path, "w").write("\n".join(out_s))
          
    
def tfidf_to_file_for_lib_SVM_multi_label(tfidf, level1_pos_ids, level1_neg_ids, 
                                                 level2_pos_ids, out_path):
    ''' For the abstract screening scenario, in which there are two 'levels' of labels. '''
    out_s  = []
    
    if level1_pos_ids is not None and len(level1_pos_ids) > 0:
        if type(tfidf.keys()[0]) != type(level1_pos_ids[0]):
            print "keys and level 1 ids are not of the same type!!!"
            pdb.set_trace()
        
    for id in tfidf.keys():
        level1_lbl, level2_lbl = None, None
        
        if level1_pos_ids is None or (id not in level1_neg_ids and id not in level1_pos_ids):
            level1_lbl = "?"
        else:
            level1_lbl = -1
            if id in level1_pos_ids:
                level1_lbl = 1
                
        if level2_pos_ids is None:
            level2_lbl = "?"
        else:
            level2_lbl = -1
            
            if id in level2_pos_ids:
                level2_lbl = 1
        out_s.append(lib_svm_str_multi_label(id, level1_lbl, level2_lbl, tfidf[id]))

    open(out_path, "w").write("\n".join(out_s))
    
    
def lib_svm_str(lbl, x):
    ''' Returns a (sparse-format) feature vector string for the provided example'''
    x_str = [str(lbl)]
    for i in range(len(x)):
        if x[i] > 0.0:
            x_str.append("%s:%s" % (i, x[i]))
    return " ".join(x_str)
  
def lib_svm_str_multi_label(id, level1_lbl, level2_lbl, x):
    # 12/17/10 -- we are now assuming that x is a *dictionary*!
    # this is going to break if you try to do tf-idf instead
    # of binary
    if level2_lbl is None:
        level2_lbl = "?"
    x_str = [str(id), str(level1_lbl), str(level2_lbl)]
    if isinstance(x, dict):
        for i, val in x.items():
            x_str.append("%s:%s" % (i, val))
    else:
        for i, val in enumerate(x):
            if val > 0:
                x_str.append("%s:%s" % (i, val))
            
    return " ".join(x_str)

def generate_weka_file(labels, frequency_vectors, words, out_path):
    '''
    Builds and writes out a WEKA formatted file with the word frequencies 
    as attributes for each instance.
    '''
    weka_str = ["@RELATION abstracts"]
    for i in range(len(words)):
        # e.g.,: @ATTRIBUTE sepallength NUMERIC
        weka_str.append("@ATTRIBUTE " + words[i] + " INTEGER")
    weka_str.append("@ATTRIBUTE class {0,1}")
    weka_str.append("\n@DATA")
    for instance in range(len(frequency_vectors)):
        weka_str.append(build_weka_line_str(labels[instance], frequency_vectors[instance]))
    f_out = open(out_path, "w")
    f_out.write("\n".join(weka_str))
    
  
def build_weka_line_str(label, word_freq):
    '''
    Create a WEKA style (ARFF) line for the document associated with the provided 
    wordFreq parameter.
    '''
    line = ["{"]
    for i in range(len(wordFreq)):
        # Sparse formatting: Give the attribute 'index' first, then the value if it's non zero
        if wordFreq[i] > 0:
            line.append(str(i) + " " + str(wordFreq[i]))
    return ", ".join(line) + ", " + str(len(wordFreq)) + " " + str(label) + "}"
    
def _mkdir(newdir):
    """
    works the way a good mkdir should
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
        if tail:
            os.mkdir(newdir)


################################################################
#
#  Unit tests! Use nose 
#           [http://somethingaboutorange.com/mrl/projects/nose/0.11.1/]. 
#  
#   e.g., while in this directory:
#           > nosetests tfidf2
#
################################################################
'''
@nose.with_setup(clean_datasets, remove_cleaned)
def binary_encode_test():
    bow = build_bag_of_words_over_dir(os.path.join("test_corpus", "cleaned"), min_word_count=1, 
                                                            binary_encode = True)
    # hand verified
    assert(bow["1"] == [0.0, 1.0, 0.0, 1.0])
    assert(bow["2"] == [1.0, 0.0, 1.0, 1.0])

    
def clean_datasets():
    clean_path = os.path.join("test_corpus", "cleaned")
    _mkdir(clean_path)
    clean_up_docs("test_corpus", out_dir=clean_path)
     
def clean_paths():
    return [os.path.join("test_corpus", "cleaned", "%s.txt") % (i+1) for i in range(2)]

def remove_cleaned():
    print clean_paths
    for f in clean_paths():
        os.remove(f)
    
@nose.with_setup(clean_datasets, remove_cleaned)
def tf_idf_test():
    bow = build_bag_of_words_over_dir(os.path.join("test_corpus", "cleaned"), min_word_count=1)
    # these are hand calculated / verified
    assert(bow["1"] == [0.0, 1.0, 0.0, 0.0])
    assert(bow["2"] == [0.70710678118654746, 0.0, 0.0, 0.70710678118654746])
   

@nose.with_setup(clean_datasets, remove_cleaned)
def clean_docs_test():
    d1, d2 = [open(p, "r").readline() for p in clean_paths()]
    assert(d1 == "humans monkeys")
    assert(d2 == "snakes like monkeys")
'''
