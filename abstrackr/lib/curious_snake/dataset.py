'''
	Byron C Wallace
	Tufts Medical Center: Computational and Analytic Evidence Sythensis 
	tuftscaes.org/curious_snake
	Curious Snake: Active Learning in Python
    dataset.py
    --
    This is a modified version of the original dataset.py module; it is specially
    adapted for abstract screening data. For examples, the format expected is different
    here. Note that the unit tests for the dataset module will currently fail, as
    this change is not reflected in them.
    
    This module contains methods and classes for parsing
    and manipulating datasets.
'''

import pdb
import random 
try:
    import numpy
except:
    print "numpy not found; won't be able to convert to numpy matrix."

def build_dataset_from_file(fpath, name="", citation_screening_style=True, 
                                            ignore_unlabeled_instances=False,
                                            only_these=None):
    '''
    Builds and returns a dataset from the file @ the path provided. 
    This assumes the file is in a (sparse!) format amenable to libsvm. E.g.,:
      id1 1 1 3:.5 4:.8 6:.3
      id2 1 -1 1:.2 3:.8 6:.4
    Would correspond to two instances, both with '1' level-1 labels, and level-2
    labels of 1 and -1, respectively. The first column is assumed to be a (unique)
    *integer* identifier (e.g., a pubmed ID)
    
    The dictionary (sparse) representation of the feature vectors maps dimensions to values. 
    '''
    print "building dataset from file: %s" % fpath
    data = open(fpath, 'r').readlines()
    #instances = [line_to_instance(line) for line in data]
    
    instances = []
    for i, line in enumerate(data):
        cur_inst = None
        if citation_screening_style:
            cur_inst = line_to_instance(line, citation_screening_style=True)
        else:
            cur_inst = line_to_instance(line, citation_screening_style=False, xid=i)
        instances.append(cur_inst)
    
    # if we want to ignore unlabeled instances -- this
    # might be useful to perform cross-validation, for
    # example -- we do so here by filtering out those
    # instances with no label
    if ignore_unlabeled_instances:
        print "dropping unlabeled instances from dataset"
        instances = [inst for inst in instances if not inst.label=="?"]
    
    if only_these is not None:
        # then exclude all other ides
        if isinstance(only_these[0], str):
            print "warning -- your list of ids to include are strings! Will attempt to recast as ints"
            only_these = [int(x) for x in only_these]
            
        instances = [inst for inst in instances if inst.id in only_these]
        
    inst_dict = {}
    for inst in instances:
        inst_dict[inst.id] = inst
    return dataset(inst_dict, name=name)

def join_datasets(datasets):
    joined_dataset = datasets[0].copy()
    for d in datasets[1:]:
        joined_dataset = combine_datasets(joined_dataset, d)
    return joined_dataset
            
def combine_datasets(d1, d2):
    inst_dict = d1.copy().instances # the new dictionary
    offset = d1.num_features()
    for inst_id in d2.instances.keys():
        for feature_id, feature_val in d2.instances[inst_id].point.items():
            inst_dict[inst_id].point[offset+feature_id] = feature_val
            
    return dataset(inst_dict, name="_".join([d1.name, d2.name]))
    
def line_to_instance(l, citation_screening_style=True, xid=None):
    ''' 
    Again, specially adapted for abstract screening data.
    
    @TODO if citation_screening_style is False, should be able to
    handle single label datasets with no ids
    '''
    l = l.replace("\r\n", "").replace("\n", "")
    l_split = l.split(" ")
    l_split = [l for l in l_split if l != '']
    level_1_label, level_2_label = None, None
    point = None
    
    if citation_screening_style:
        try:
            xid = eval(l_split[0]) # first column is ID
            level_1_label = "?"
            if l_split[1] != "?":     
                level_1_label = eval(l_split[1]) # second column is level-1 label
                
            level_2_label = "?"
            if l_split[2] != "?":
                level_2_label = eval(l_split[2]) # third column is level-2 label
            point = l_split[3:]
        except:
            print "hrmm.. something is wrong with this instance %s\n\n" % l_split
            pdb.set_trace()
    else:
        # vanilla libsvm style -- only 1 label
        level_1_label = eval(l_split[0])
        point = l_split[1:]
         

    dict_point = {}
    
    for coord, value in [dimension.split(":") for dimension in point if point[0] != '']:
      dict_point[eval(coord)] = eval(value)

    return instance(xid, dict_point, level_1_label = level_1_label, level_2_label=level_2_label)

        
class instance:
    '''
    Represents a single point/label combination. The label doesn't necessarily
    need to be provided. The point should be a dictionary mapping coordinates
    (dimensions) to values.
    '''
    def __init__(self, id, point, level_1_label=None, level_2_label = None, name="", 
                            is_synthetic=False):
        self.id = id
        self.point = point
        self.label = level_1_label
        # the true_label field is here in case you want
        # to artificially label the instance, e.g., via
        # co-training; the true_label can be a repository for
        # the actual label in this scenario
        self.true_label = level_1_label
        self.level_2_label = level_2_label
        self.name = name
        

    
    
class dataset:
    '''
    This class represents a set of data. It is comprised mainly of a list of instances, and 
    various operations -- e.g., undersampling -- can be performed on this list.
    '''
    minority_class = 1
    
    def __len__(self):
        return self.size()
        
    def __init__(self, instances=None, name=""):
        self.instances = instances or dict({})
        self.name = name
    
    def size(self):
        if self.instances is not None:
            return len(self.instances)
        else:
            return 0
        
    def remove_instances(self, ids_to_remove):
        ''' Remove and return the instances with ids in ids_to_remove '''
        try:
            return [self.instances.pop(id) for id in ids_to_remove]
        except:
            print "\n[dataset.py] wtf. you're trying to remove an instance that doesn't exist."
            pdb.set_trace()
      
    def get_instances(self, ids_to_get):
        try:
            return [self.instances[xid] for xid in ids_to_get]
        except:
            print "\n[dataset.py] wtf. you're trying to get an instances that doesn't exist."
            pdb.set_trace()
       
    def copy(self):
         return dataset(instances = self.instances.copy(), name=self.name) 
      
    def get_point_for_id(self, xid):
        return self.instances[xid].point
        
    def get_label_for_id(self, xid):
        return self.instances[xid].label
        
    def get_level_2_label_for_id(self, xid):
        return self.instances[xid].level_2_label
        
    def undersample(self, n):
        ''' 
        Remove and return a random subset of n *majority* examples
        from this dataset
        '''
        majority_ids = self.get_list_of_majority_ids()
        print "total number of examples: %s; number of minority examples: %s, number of majority examples: %s" % \
                (len(self.instances), len(self.get_minority_examples()), len(majority_ids))
        picked_so_far = 0
        
        if len(majority_ids) < n:
            n = 0
            #raise Exception, "you asked me to remove more (majority) instances than I have!"
        remove_these = random.sample(majority_ids, n)
        for inst_id in remove_these:
            self.instances.pop(inst_id)         
        return remove_these
    

    def add_instances(self, instances_to_add):
        '''
        Adds every instance in the instances list to this dataset.
        '''
        for inst in instances_to_add:
            if inst.id in self.instances.keys():
                pdb.set_trace()
                raise Exception, "dataset.py: error adding instances; duplicate instance ids!"
            self.instances[inst.id] = inst

                 
    def pick_random_minority_instances(self, k):
        min_ids = self.get_list_of_minority_ids()

        if not len(min_ids) >= k:
            raise Exception, "not enough minority examples in dataset!"
            
        ids = random.sample(min_ids, k)
        return [self.instances[id] for id in ids]
        
        
    def pick_random_majority_instances(self, k):
        maj_ids = self.get_list_of_majority_ids()
 
        if not len(maj_ids) >= k:
            raise Exception, "not enough majority examples in dataset!"
            
        ids = random.sample(maj_ids, k)
        return [self.instances[id] for id in ids]
        
    def get_list_of_minority_ids(self, ids_only=True):
        minorities = []
        for id, inst in self.instances.items():
            if inst.label == self.minority_class:
                if ids_only:
                    minorities.append(id)
                else:
                    minorities.append(inst)
        return minorities
        
    def get_minority_examples(self):
        return self.get_list_of_minority_ids(ids_only=False)
        
    def get_points_str(self):
        out_s = []
        for inst in self.instances.values():
            inst_str = []
            inst_str.append(str(inst.label))
            for v in inst.point.values():
                inst_str.append(str(v))
            out_s.append(",".join(inst_str))
        return "\n".join(out_s)
        
        
    def get_dim(self):
        '''  Returns the dimensionality of the data '''
        max_d = 0
        for p in self.instances.values():
            for d in p.point.keys():
                if d > max_d:
                    max_d = d
        return max_d
        
    def to_numpy_array(self, indicator=False, build_id_dict=True):
        return self.to_numpy_arr(indicator=indicator, build_id_dict=build_id_dict)
        
    def to_numpy_arr(self, indicator=False, build_id_dict=True):
        '''  Converts the dataset into a numpy matrix  '''
        max_d = self.get_dim()
        index_to_id_dict = {}
        
        all_points = []
        i = 0
        for p in self.instances.values():
            cur_point = []
            for x in range(max_d):
                if not p.point.has_key(x):
                    cur_point.append(0.0)
                else:
                    if indicator:
                        cur_point.append(1.0)
                    else:
                        cur_point.append(p.point[x])
            all_points.append(cur_point)

            index_to_id_dict[i] = p.id
            i+=1 
        
        if build_id_dict:
            return (index_to_id_dict, numpy.array(all_points))
        return numpy.array(all_points)
        
    def get_list_of_majority_ids(self, majority_id=-1, ids_only=True):
        majorities = []
        for id, inst in self.instances.items():
            inst_lbl = inst.label
            if inst_lbl == majority_id:
                if ids_only:
                    majorities.append(inst.id)
                else:
                    majorities.append(inst)
        return majorities
        
    def get_majority_examples(self):
        return self.get_list_of_majority_ids(ids_only=False)
        
    def number_of_minority_examples(self):
        ''' Counts and returns the number of minority examples in this dataset.'''
        return len(self.get_minority_examples())
        
    def number_of_l2_positives(self):
        return len([inst for inst in self.instances.values() if inst.level_2_label == 1.0])
    
    def number_of_l2_negatives(self):
        return len([inst for inst in self.instances.values() if inst.level_2_label == -1.0])
    
    def get_instance_ids(self):
        return self.instances.keys()

    def number_of_majority_examples(self):
        ''' Counts and returns the number of majority examples in this dataset. '''
        return len(self.instances) - self.number_of_minority_examples()
    
    
    def get_examples_with_label(self, label):
        ''' Returns a new dataset with all the examples that have the parametric label. '''
        examples = []
        for inst in self.instances.values():
            if inst.label == label:
                examples.append(inst)
        return dataset(examples)
        
    def get_data_subset(self, inst_ids):
        ''' Returns a new dataset with all the examples that have the parametric label. '''
        examples = {}
        for inst_id in inst_ids:
            examples[inst_id] = self.instances[inst_id]
        return dataset(examples)
        
    def set_labels(self, inst_ids, label):
        for i, inst_id in enumerate(inst_ids):
            self.instances[inst_id].label = label
        
    def revert_to_true_labels(self, inst_ids):
        for inst_id in inst_ids:
            self.instances[inst_id].label = self.instances[inst_id].true_label
            
    def get_and_remove_random_subset(self, n):
        ''' Remove and return a random subset of n examples from this dataset'''
        subset = random.sample(self.instances.keys(), n)
        return self.remove_instances(subset)
        
    def get_samples(self):
        return [inst.point for inst in self.instances.values()]

    def get_labels(self):
        return [inst.label for inst in self.instances.values()]

    def get_level_2_labels(self):
        return [inst.level_2_label for inst in self.instances.values()]
        
    def num_features(self):
        cur_max = 0
        for inst in self.instances.values():
            if not inst.point.keys() == []:
                cur_max = max(max(inst.point.keys()), cur_max)
        # +1 because dimensions are zero indexed (or, assumed to be)
        return cur_max + 1
        
    def get_samples_and_labels_for_ids(self, ids):
        samples, labels = [], []
        for id in ids:
            inst = self.instances[id]
            samples.append(inst.point)
            labels.append(inst.label)
        return [samples, labels]
        
    def get_samples_and_labels(self):
        '''
        Returns a tuple of [[s_1, s_2, ..., s_n], [l_1, l_2, ..., l_n]] where s_i is the ith feature 
        vector and l_i is its label.
        '''
        samples = []
        labels = []
        for inst in self.instances.values():
            samples.append(inst.point)
            labels.append(inst.label)   
        return [samples, labels]
    
    def write_out(self, out_path, write_out_level_2_labels=True):
        out_str = []
        for inst in self.instances.values():
            if write_out_level_2_labels:
                cur_line = "%s %s %s " % (inst.id, inst.label, inst.level_2_label)
            else:
                cur_line = "%s %s " % (inst.id, inst.label)    
            
            cur_line += " ".join(["%s:%s" % (key, item) for key, item in inst.point.items()])
            out_str.append(cur_line)
        f_out = open(out_path, 'w')
        f_out.write("\n".join(out_str))
        f_out.close()
            
