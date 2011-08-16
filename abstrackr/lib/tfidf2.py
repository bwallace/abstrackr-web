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

A module for tf/idf encoding text documents.

Assumes you have cleaned individual title files in "Titles" directory
It is also assumed that the names of these files (e.g,. 1.*) map
to an ID (e.g., refman ID). I.e., 1.* -> reference id 1. These are used as identifiers.

Usage (assuming you've a directory of text files "Titles"')
>titles = tfidf2.build_bag_of_words_over_dir("Titles")

You'll need a list of ids that are 'positives' (e.g., "relevant")
>pos_indices = { read in and build this list }

Now we can dump to some file specified by outpath
>tfidf_to_file_for_lib_SVM(titles, pos_indices, outpath)
'''

import re
import math
import string
import os
import pdb
import csv
try:
  import nose
except:
  print "nose isn't installed -- can't run unittests!"


stop_list_path = "./abstrackr/lib/stop_list.txt"
print "stop word list path is %s" % stop_list_path

def build_stop_list(stop_list_path):
    exclude_words = []
    if stop_list_path != None:
        f = open(stop_list_path, 'r')
        while 1:
            line = f.readline()
            if not line:
                break
            # Every line is assumed to be a single word
            exclude_words.append(line.strip())
    return exclude_words

# if you don't want to use a stop list, just set the stop_list global
# to an empty list (stop_list = [])
print "building stop word list..."
stop_list = build_stop_list(stop_list_path)
print "done."


def add_labels(new_path, lbl_dict):
    lbls = [x for x in csv.reader(open(new_path, 'r'))]
    #pdb.set_trace()
    for l in lbls:
        #lbl_dict[eval(l[0])] = "-1" if l[1]=="n" else "1"
        lbl_dict[eval(l[0])] = "1" if l[1] in ("y", "m") else "-1"
    return lbl_dict
    
def update_labels(fpath, outpath, new_lbl_d, unlabel_if_not_in_dict=False, ignore_these=[]):
    ''' relabels the instances in fpath with new_lbl_d; writes to outpath. '''
    if not isinstance(new_lbl_d.keys()[0] , int):
        print "your lbl_d keys (instance ids) are strings; they need to be ints!\nReturning false"
        return False
        
    new_file = []
    lines = open(fpath, 'r').readlines()
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
    
    
def encode_docs(dir_path, out_path, out_f_name, lbl_dict=None, clean_first=True, binary=False):
    '''
    Given a directory path, this method cleans, then encodes and writes out all text files therein.
    '''
    
    #tfidf_to_file_for_lib_SVM(encoded_docs, lbl_dict.keys(), os.path.join(out_path, out_f_name))
    if lbl_dict is not None:
        if not isinstance(lbl_dict.values()[0], str):
            print "labels are *not* strings, but they need to be!"
            pdb.set_trace()
 
            
    # first, clean the documents
    if clean_first:
        print "cleaning documents.."
        clean_docs_path = os.path.join(dir_path, "Cleaned")
        if not os.path.exists(clean_docs_path):
            _mkdir(clean_docs_path)
        clean_up_docs(dir_path, out_dir = clean_docs_path)
        print "done cleaning."
    else:
        clean_docs_path = dir_path

    # now build tf/idf representation
    print "encoding..."
    encoded_docs = build_bag_of_words_over_dir(clean_docs_path, binary_encode=binary)
    print "done encoding."
    
    # now write it out
    print "writing doc out..."

    if not os.path.exists(out_path):
        _mkdir(out_path)


    pos_ids = []
    neg_ids = []      
    if lbl_dict is not None:
        pos_ids = [str(x_id) for x_id in lbl_dict.keys() if lbl_dict[x_id] in ["1", "1.0"]]
        neg_ids = [str(x_id) for x_id in lbl_dict.keys() if x_id not in pos_ids]
     
    #pdb.set_trace()
    tfidf_to_file_for_lib_SVM_multi_label(encoded_docs, pos_ids, neg_ids,
                                                            None, os.path.join(out_path, out_f_name))
    print "done."
    

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
    count_vec = [doc.count(word) for word in words]
    return count_vec

    
def build_bag_of_words_feature_vectors(ids_to_texts, words, binary_encode=False):
    freq_vecs = {}
    for id in ids_to_texts.keys():
        if not binary_encode:
            freq_vecs[id] = build_word_count_vector_for_doc(words, ids_to_texts[id])
        else:
            # binary encoding -- 1or 0 for each word (present or not, respectively)
            doc = ids_to_texts[id]
            freq_vecs[id] = [1.0 if word in doc else 0.0 for word in words]
	
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
    
    
    
def build_bag_of_words_over_dir(dir_path, split_txt_on = " ", binary_encode = False, 
                                                    word_index_path = "word_index.txt",  min_word_count = 3):
    '''
    Build bag of words representation vectors over *all of the documents* in dir_path.
    Note that we assume the documents are already clean.
    '''
    
    # read all the words in 
    word_index_path = os.path.join(dir_path, word_index_path)
    s_words = []
    files_in_dir = [f for f in os.listdir(dir_path) if not os.path.isdir(os.path.join(dir_path, f))]
    for p in files_in_dir:
      try:
          s_words.extend(open(os.path.join(dir_path, p), 'r').readlines()[0].split(" "))
      except:
          pass
    
    unique_word_dict = {}
    set_words = list(set(s_words))
    for w in set_words:
        unique_word_dict[w] = 0
    
    ids_to_txt = {}
    words = []
    # ignore the word_index.txt file, which we generated
    for p in [f for f in files_in_dir if not f == word_index_path]:
        cur_txt =[""]
        try:
            cur_txt = open(os.path.join(dir_path, p), 'r').readline().split(split_txt_on)
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

    return build_bag_of_words_feature_vectors (ids_to_txt,  words, binary_encode=binary_encode)


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

def isnumerical(w)    :
    try:
        xfl = float(w)
        return True
    except:
        return False
    
    
def clean_up_docs(dir_path, out_dir = None, overwrite_dirty=False):
    if out_dir is not None:
        try:
            os._mkdir(out_dir)
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
        
        clean_doc = clean_up_txt(dirty_doc)
        out_path = dirty_path if overwrite_dirty else dirty_path + ".cleaned"
        if out_dir != dir_path:
            # then an output directory was passed in
            out_path = os.path.join(out_dir, doc)
        clean_doc_out = open(out_path, 'w')
        clean_doc_out.write(" ".join(clean_doc))
    print "documents cleaned and written."


################################################################
#
#   File encoding routines
#
################################################################
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
    x_str = [str(id), str(level1_lbl), str(level2_lbl)]
    for i in range(len(x)):
        if x[i] > 0.0:
            x_str.append("%s:%s" % (i, x[i]))
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
