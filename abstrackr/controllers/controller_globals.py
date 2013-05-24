# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
#                                                                      #
#  collection of helper routines, primarily for querying the database  #
#                                                                      #
# # # # # # # # # # # # # # # # # # # # # # # # #  # # # # # # # # # # #



CONSENSUS_USER = 0

from abstrackr.lib.base import BaseController, render
import abstrackr.model as model
import pdb
import logging

from sqlalchemy.orm import exc

Session = model.meta.Session

log = logging.getLogger(__name__)

# This method facilitates access to User attributes that are NOT auth.User attributes.
def _get_user_from_email(email):
    '''
    If a user with the provided email exists in the database, their
    object is returned; otherwise this method returns False.
    '''
    user_q = model.meta.Session.query(model.User)
    try:
        return user_q.filter(model.User.email == email).one()
    except (exc.NoResultFound, exc.MultipleResultsFound) as err:
        log.debug(err)
        return False


def _does_a_conflict_exist(review_id):
    # these will be orderd by citation

    citation_query_obj = _get_all_citations_for_review(review_id, return_query_obj=True)
    labels_for_cur_citation, last_citation = [], None

    for citation, label in citation_query_obj:
        if last_citation is not None and last_citation != citation.id:
            labels_for_cur_citation = [label.label]
        else:

            labels_for_cur_citation.append(label.label)
            # note that this isn't expensive because the set
            # cardinality likely <= ~10
            if len(set(labels_for_cur_citation)) > 1:
                return True
        last_citation = citation.id

    return False


def _get_conflicts(review_id):
    """Finds all conflicting labels and returns as a dictionary"""

    citation_ids_to_labels = \
        _get_labels_dict_for_review(review_id)

    # now figure out which citations have conflicting labels
    citation_ids_to_conflicting_labels = {}

    for citation_id in [c_id for c_id in citation_ids_to_labels.keys() if citation_ids_to_labels[c_id]>1]:
        if len(set([label.label for label in citation_ids_to_labels[citation_id]])) > 1 and\
                not CONSENSUS_USER in [label.user_id for label in citation_ids_to_labels[citation_id]]:
            citation_ids_to_conflicting_labels[citation_id] = citation_ids_to_labels[citation_id]

    return citation_ids_to_conflicting_labels


def _get_labels_dict_for_review(review_id):
    citation_ids_to_labels = {}
    for citation, label in _get_all_citations_for_review(review_id):
            if citation.id in citation_ids_to_labels.keys():
                citation_ids_to_labels[citation.id].append(label)
            else:
                citation_ids_to_labels[citation.id] = [label]

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
            filter(model.Citation.id==model.Label.study_id).\
            filter(model.Label.project_id==review_id).order_by(model.Citation.id)
    if return_query_obj:
        return citation_query_obj
    # this can be expensive!
    return citation_query_obj.all()


def _get_bin(prob, upper_bounds):
    for bucket_index, upper_bound in enumerate(upper_bounds):
        if prob < upper_bound:
            return bucket_index
    return bucket_index


def _prob_histogram(probs):
    buckets = [.1*x for x in range(1,11,1)]
    counts = [0]*10

    for prob in probs:
        counts[_get_bin(prob, buckets)] += 1

    # normalize
    z = float(sum(counts))
    if z == 0:
        # this should never happen... but just in case
        z = 1.0

    counts = [count/z for count in counts]
    return counts

def _get_project_member_ids(project_id):
    members = Session.query(model.Project).\
            filter_by(id=project_id).one().members
    return [member.id for member in members]
