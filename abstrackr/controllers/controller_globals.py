''''''
# collection of helper routines, primarily for querying the database
''''''

CONSENSUS_USER = 0

from abstrackr.lib.base import BaseController, render
import abstrackr.model as model
import pdb

def _does_a_conflict_exist(review_id):
    # these will be orderd by citation

    citation_query_obj = _get_all_citations_for_review(review_id, return_query_obj=True)
    labels_for_cur_citation, last_citation = [], None
    
    for citation, label in citation_query_obj:
        if last_citation is not None and last_citation != citation.citation_id:
            labels_for_cur_citation = [label.label]
        else:
            labels_for_cur_citation.append(label.label)
            # note that this isn't expensive because the set 
            # cardinality <= ~10
            if len(set(labels_for_cur_citation)) > 1:
                return True
        last_citation = citation.citation_id
        
    return False

def _get_conflicts(review_id):
    citation_ids_to_labels = \
        _get_labels_dict_for_review(review_id)

    # now figure out which citations have conflicting labels
    citation_ids_to_conflicting_labels = {}
    
    for citation_id in [c_id for c_id in citation_ids_to_labels.keys() if citation_ids_to_labels[c_id]>1]:
        if len(set([label.label for label in citation_ids_to_labels[citation_id]])) > 1 and\
                not CONSENSUS_USER in [label.reviewer_id for label in citation_ids_to_labels[citation_id]]:
            citation_ids_to_conflicting_labels[citation_id] = citation_ids_to_labels[citation_id]
    
    return citation_ids_to_conflicting_labels


def _get_labels_dict_for_review(review_id):
    citation_ids_to_labels = {}
    for citation, label in _get_all_citations_for_review(review_id):
            if citation.citation_id in citation_ids_to_labels.keys():
                citation_ids_to_labels[citation.citation_id].append(label)
            else:
                citation_ids_to_labels[citation.citation_id] = [label]

    return citation_ids_to_labels


def _get_maybes(review_id):
    citation_ids_to_labels = _get_labels_dict_for_review(review_id)

    # which have 'maybe' labels?
    citation_ids_to_maybe_labels = {}
    for citation_id, labels_for_citation in citation_ids_to_labels.items():
        if 0 in [label.label for label in labels_for_citation]:
            citation_ids_to_maybe_labels[citation_id] = labels_for_citation

    return citation_ids_to_maybe_labels


def _get_all_citations_for_review(review_id, return_query_obj=False):
    citation_query_obj = model.meta.Session.query(model.Citation, model.Label).\
            filter(model.Citation.citation_id==model.Label.study_id).\
            filter(model.Label.review_id==review_id).order_by(model.Citation.citation_id)
    if return_query_obj:
        return citation_query_obj
    # this can be expensive!
    return citation_query_obj.all()
