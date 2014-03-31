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
from sqlalchemy import func

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


def _get_maybes(review_id):
    labels_marked_maybe = _get_maybe_labels(review_id)
    study_ids_marked_maybe = [l.study_id for l in labels_marked_maybe]

    labels_by_consensus_user = _get_labels_by_consensus_user(review_id)
    study_ids_by_consensus_user = [l.study_id for l in labels_by_consensus_user]

    study_ids_not_resolved = [x for x in study_ids_marked_maybe if x not in study_ids_by_consensus_user]

    return study_ids_not_resolved


def _get_maybe_labels(project_id):
    labels_q = Session.query(model.Label)
    labels_marked_maybe = labels_q.filter_by(project_id=project_id,
                                             label=0).all()
    return labels_marked_maybe


def _get_labels_by_consensus_user(project_id):
    labels_q = Session.query(model.Label)
    labels_by_consensus_user = labels_q.filter_by(project_id=project_id,
                                                  user_id=0).all()
    return labels_by_consensus_user


def _get_labels_dict_for_review(review_id):
    citation_ids_to_labels = {}
    for citation, label in _get_all_citations_for_review(review_id):
            if citation.id in citation_ids_to_labels.keys():
                citation_ids_to_labels[citation.id].append(label)
            else:
                citation_ids_to_labels[citation.id] = [label]

    return citation_ids_to_labels


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

def _check_assignment_done(a, offset=0):
    project_id = a.project_id
    user_id = a.user_id
    task_id = a.task_id
    done_so_far = a.done_so_far
    done = a.done
    num_assigned = a.num_assigned
    assignment_type = a.assignment_type

    if assignment_type=='perpetual':
        return _check_assignment_done_perpetual_type(a)
    elif assignment_type=='conflict':
        return _check_assignment_done_conflict_type(a)
    elif assignment_type=='initial':
        return _check_assignment_done_initial_type(a)
    elif assignment_type=='assigned':
        return _check_assignment_done_assigned_type(a)

def _check_assignment_done_perpetual_type(a):
    done_so_far = a.done_so_far
    screening_mode = Session.query(model.Project).filter_by(id=a.project_id).first().screening_mode
    cnt_citations_in_project = _get_cnt_citations_in_project_by_project_id(a.project_id)
    if screening_mode in ['single', 'advanced']:
        cnt_citations_labeled_by_anyone = _get_cnt_citations_labeled(a.project_id)
        return cnt_citations_labeled_by_anyone>=cnt_citations_in_project
    elif screening_mode in ['double']:
        # In double screening it may be the case that we are already done because 2 other members
        # finished screening all. So we have to check two conditions. Either the current user already
        # screened all the citations in the project, or the number of citations that have been labeled
        # twice is equal to the number of citations in the project
        cnt_citations_labeled_twice_by_anyone = _get_cnt_citations_labeled_twice_by_anyone(a.project_id)
        cnt_citations_labeled_by_me = _get_cnt_citations_labeled(a.project_id, a.user_id)
        if cnt_citations_labeled_by_me>=cnt_citations_in_project:
            return True
        else:
            return cnt_citations_labeled_twice_by_anyone>=cnt_citations_in_project
def _get_cnt_citations_labeled_twice_by_anyone(project_id):
    labels_q = Session.query(model.Label).\
                        filter_by(project_id=project_id).\
                        group_by(model.Label.study_id).\
                        having(func.count(model.Label.study_id) >= 2)
    return len(labels_q.all())

def _get_cnt_citations_in_project_by_project_id(project_id):
    citations = Session.query(model.Citation).filter_by(project_id=project_id).all()
    return len(citations)

def _get_cnt_citations_labeled(project_id, user_id=None):
    if user_id==None:
        labels = Session.query(model.Label).filter_by(project_id=project_id).all()
    else:
        labels = Session.query(model.Label).filter_by(project_id=project_id).filter_by(user_id=user_id).all()
    lof_citation_ids = [l.study_id for l in labels]
    return len(set(lof_citation_ids))

# This is just like _check_assignment_done_assigned_type
# Going to keep this for now in case the requirements change.
def _check_assignment_done_conflict_type(a):
    cnt_labels_by_assignment = _get_cnt_labels_by_assignment(a)
    num_assigned = a.num_assigned
    return cnt_labels_by_assignment==num_assigned

# This is just like _check_assignment_done_assigned_type
# Going to keep this for now in case the requirements change.
def _check_assignment_done_initial_type(a):
    cnt_labels_by_assignment = _get_cnt_labels_by_assignment(a)
    num_assigned = a.num_assigned
    return cnt_labels_by_assignment>=num_assigned

def _check_assignment_done_assigned_type(a):
    project = Session.query(model.Project).filter_by(id=a.project_id).one()
    screening_mode = project.screening_mode
    cnt_labels_by_assignment = _get_cnt_labels_by_assignment(a)
    num_assigned = a.num_assigned
    cnt_citations_in_project = _get_cnt_citations_in_project_by_project_id(a.project_id)

    if cnt_labels_by_assignment>=num_assigned:
        return True
    elif screening_mode=="single":
        cnt_citations_labeled_by_anyone = _get_cnt_citations_labeled(a.project_id)
        return cnt_citations_labeled_by_anyone>=cnt_citations_in_project
    elif screening_mode=="double":
        cnt_citations_labeled_twice_by_anyone = _get_cnt_citations_labeled_twice_by_anyone(a.project_id)
        return cnt_citations_labeled_twice_by_anyone>=cnt_citations_in_project
    elif screening_mode=="advanced":
        cnt_citations_labeled_by_anyone = _get_cnt_citations_labeled(a.project_id)
        return cnt_citations_labeled_by_anyone>=cnt_citations_in_project

def _get_cnt_labels_by_assignment(a):
    labels_q = Session.query(model.Label)
    return labels_q.filter_by(user_id=a.user_id).filter_by(assignment_id=a.id).count()

def _get_labels_by_assignment(a):
    labels_q = Session.query(model.Label)
    labels = labels_q.filter_by(project_id=a.project_id).\
                      filter_by(user_id=a.user_id).\
                      filter_by(assignment_id=a.id).all()
    return labels