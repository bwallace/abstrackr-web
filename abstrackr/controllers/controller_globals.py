''''''
# collection of helper routines, primarily for querying the database.
''''''

CONSENSUS_USER = 0

from abstrackr.lib.base import BaseController, render
import abstrackr.model as model


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
    
 

def _get_labels_dict_for_review(review_id, get_names=False, lbl_filter_f=None):
    citation_ids_to_labels = {}
    for citation, label in _get_all_citations_for_review(review_id):
        if get_names:
            if lbl_filter_f is None:
                lbl_filter_f = lambda x: True
                
            labeler_names = ["consensus"] # always export the consensus
            # first collect labels for all citations taht pass our
            # filtering criteria
            for citation, label in model.meta.Session.query(\
                model.Citation, model.Label).filter(model.Citation.citation_id==model.Label.study_id).\
                filter(model.Label.review_id==id).order_by(model.Citation.citation_id).all():
                # the above gives you all labeled citations for this review
                # i.e., citations that have at least one label
                if lbl_filter_f(label):
                    cur_citation_id = citation.citation_id
                    if last_citation_id != cur_citation_id:
                        citation_ids_to_lbls[citation.citation_id] = {}
                        citations_to_export.append(citation)

                    # NOTE that we are assuming unique user names per-review
                    labeler = self._get_username_from_id(label.reviewer_id)
                    if not labeler in labeler_names:
                        labeler_names.append(labeler)

                    citation_to_lbls_dict[cur_citation_id][labeler] = label.label
                    last_citation_id = cur_citation_id
        else:
            if citation.citation_id in citation_ids_to_labels.keys():
                citation_ids_to_labels[citation.citation_id].append(label)
            else:
                citation_ids_to_labels[citation.citation_id] = [label]

    return citation_ids_to_labels
        
  
def _get_all_citations_for_review(review_id):
    return model.meta.Session.query(model.Citation, model.Label).\
            filter(model.Citation.citation_id==model.Label.study_id).\
            filter(model.Label.review_id==review_id).all()
