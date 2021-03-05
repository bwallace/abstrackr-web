# Imports..
import abstrackr.lib.helpers as h

import copy
import csv
import datetime
import logging
import os
import pygooglechart
import random
import re
import shutil
import smtplib
import string
import subprocess
import urllib

from abstrackr.lib.exporter_globals import *
from abstrackr.lib import xml_to_sql
from abstrackr.lib import upload_term_helper
from abstrackr.lib.base import BaseController, render
from abstrackr.lib.helpers import literal
from abstrackr.lib.markupper import MarkUpper
from abstrackr.lib.exporter import Exporter

import abstrackr.model as model
from abstrackr.model.meta import Session

import controller_globals
from controller_globals import *  # shared variables/functions
from controller_globals import _prob_histogram

from operator import itemgetter

from pygooglechart import Axis
from pygooglechart import PieChart3D, StackedHorizontalBarChart,\
    StackedVerticalBarChart

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from repoze.what.plugins.pylonshq import ActionProtector
from repoze.what.predicates import not_anonymous, has_permission

from sqlalchemy import or_, and_, desc, func, asc
from sqlalchemy.sql import select
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from random import shuffle

log = logging.getLogger(__name__)

### for term highlighting
NEG_C = "#9900FF"
STRONG_NEG_C = "#FF0000"
POS_C = "#4CC417"
STRONG_POS_C = "#3366FF"
COLOR_D = {1:POS_C, 2:STRONG_POS_C, -1:NEG_C, -2:STRONG_NEG_C}

class ReviewController(BaseController):

    @ActionProtector(not_anonymous())
    def create_new_review(self):
        c.review_count = "%s" % Session.query(func.count(model.Project.id)).scalar()
        c.error = False
        return render("/reviews/new.mako")

    @ActionProtector(not_anonymous())
    def unlock_priorities(self, project_id):
        if not self._current_user_leads_review(project_id):
            return "yeah, I don't think so."
        print("Unlocking priorities for project: %s" % project_id)
        self._clear_all_locks(project_id)

        redirect(url(controller="account", action="my_projects"))

    @ActionProtector(not_anonymous())
    def predictions_about_remaining_citations(self, id):
        if not self._current_user_leads_review(id):
            return "yeah, I don't think so."
        predictions_q = Session.query(model.Prediction)
        c.predictions_for_review = predictions_q.filter(model.Prediction.project_id == id).all()
        c.probably_included = len([x for x in c.predictions_for_review if x.num_yes_votes > 5])

        has_prob_estimates = not any(
            [pred.predicted_probability is None for pred in c.predictions_for_review])

        ### allow exporting of predictions
        c.preds_download_url = None # populated below, at least when we have predicted probs.
        num_bins = 20
        if has_prob_estimates:
            prob_estimates = [pred.predicted_probability for pred in c.predictions_for_review]
            histo = _prob_histogram(prob_estimates)
            # e.g., '11,9,9,10,14,13,13,6,3,12'
            prob_counts_str = ",".join([str(count) for count in histo])
            # not sure if we want to show this... it's different than our classification threshold,
            # which in general is much more cautious
            c.probably_included = len([x for x in prob_estimates if x>=.5])
            num_preds = len(prob_estimates)
            c.prob_plot_url = \
                    '''https://chart.apis.google.com/chart
                       ?chxl=0:|0|%s|%s|1:|0.1|0.2|0.3|0.4|0.5|0.6|0.7|0.8|0.9|1.0
                       &chxp=0,0,0.5,1|1,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1
                       &chxr=0,0,1|1,0,1
                       &chxt=y,x
                       &chxs=0,0A0808|1,0A0808
                       &chbh=a
                       &chs=700x420
                       &cht=bvg
                       &chco=C2BDDD
                       &chds=0,1
                       &chd=t:%s
                       &chtt=Relevance+scores+of+remaining+studies''' % \
                            (int(float(num_preds)/2.0), num_preds, prob_counts_str)
            c.prob_plot_url = c.prob_plot_url.replace(" ", "").replace("\n", "")

            '''
            dump predictions to a file, too (@TODO factor this out?)
            '''

            path_to_preds_out = os.path.join(STATIC_FILES_PATH, "exports", "predictions_%s.csv" % id)
            with open(path_to_preds_out, 'w') as fout:
                csv_out = csv.writer(fout)
                preds_file_headers = ["citation_id", "title", "predicted p of being relevant", "'hard' screening prediction*"]
                csv_out.writerow(preds_file_headers)
                sorted_preds = sorted(c.predictions_for_review, key=lambda x : x.predicted_probability, reverse=True)

                for pred in sorted_preds:
                    citation = self._get_citation_from_id(pred.study_id)
                    citation_title = citation.title.encode('ascii', 'ignore')
                    row_str = [citation.id, citation_title, pred.predicted_probability, pred.prediction]
                    csv_out.writerow(row_str)

                csv_out.writerow([])
                csv_out.writerow([
                    "* due to implementation details the 'hard' prediction may diverge somewhat from the more fine-grained probability prediction."])

            c.preds_download_url = "%sexports/predictions_%s.csv" % (
                                        url('/', qualified=True), id)

        else:
            # this will be phased out
            c.frequencies = [] # This is the list of frequencies of the number of 'yes' votes.
            for i in xrange(12):
                c.frequencies.append( len([x for x in c.predictions_for_review if x.num_yes_votes==i]) )

        c.review_being_predicted = self._get_review_from_id(id).name

        c.max_probability = max([pred.predicted_probability for pred in c.predictions_for_review])

        return render("/reviews/remaining_reviews.mako")

    @ActionProtector(not_anonymous())
    def create_review_handler(self):
        ## Clear c.flash
        c.flash = {"import-errors": []}
        dict_misc = {}

        # first upload the xml file
        xml_file = request.POST['db']

        local_file_path = os.path.join(PERMANENT_STORE,
                          xml_file.filename.lstrip(os.sep))
        try:
            local_file = open(local_file_path, 'w')
        except IOError:
            os.makedirs(os.path.dirname(local_file_path))
            local_file = open(local_file_path, 'w')
        finally:
            shutil.copyfileobj(xml_file.file, local_file)
            xml_file.file.close()
            local_file.close()

        new_review = self._make_new_review() # some defaults
        # now pull out user-specified settings
        new_review.name = request.params['name']
        new_review.description = request.params['description']
        new_review.sort_by = request.params['order']
        #new_review.min_citations = request.params['min_citations']
        #new_review.max_citations = request.params['max_citations']
        screening_mode_str = request.params['screen_mode']
        tag_privacy_str = request.params['tag_visibility']

        new_review.screening_mode = \
                 {"Single-screen":"single", "Double-screen":"double", "Advanced":"advanced"}[screening_mode_str]

        if 'init_size' in request.params.keys():
            new_review.initial_round_size = int(request.params['init_size'])

        new_review.tag_privacy = {"Private":True, "Public":False}[tag_privacy_str]
        # This should be changed to boolean type, AKA tinyint(1) in the mysql database.

        Session.add(new_review)
        Session.commit()

        # place an entry in the EncodeStatus table
        # for this review -- elsewhere we'll see that
        # there is an entry in the table that isn't encoded
        # and do so.
        encoded_status = model.EncodeStatus()
        encoded_status.project_id = new_review.id
        encoded_status.is_encoded = False
        Session.add(encoded_status)

        # also in the PredictionStatus table
        prediction_status = model.PredictionsStatus()
        prediction_status.project_id = new_review.id
        prediction_status.predictions_exist = False
        Session.add(prediction_status)
        Session.commit()

        # now parse the uploaded file; dispatch on type
        num_articles = None
        if xml_file.filename.lower().endswith(".xml"):
            print "parsing uploaded xml..."
            num_articles, dict_misc = xml_to_sql.xml_to_sql(local_file_path, new_review)
        elif xml_to_sql.looks_like_ris(local_file_path):
            num_articles = xml_to_sql.ris_to_sql(local_file_path, new_review)
        elif xml_to_sql.looks_like_cochrane(local_file_path):
            num_articles = xml_to_sql.cochrane_to_sql(local_file_path, new_review)
        elif xml_to_sql.looks_like_list(local_file_path):
            num_articles, dict_misc = xml_to_sql.pmid_list_to_sql(local_file_path, new_review)
        elif xml_to_sql.looks_like_tsv(local_file_path):
            num_articles, dict_misc = xml_to_sql.tsv_to_sql(local_file_path, new_review)
        else:
            c.error = True
            print "not a recognized format!!"
            return render("/reviews/new.mako")
        print "done."


        if new_review.initial_round_size > 0:
            # make sure they don't specify an initial round size comprising more
            # articles than are in the review.
            new_review.initial_round_size = min(num_articles, new_review.initial_round_size)
            self._create_initial_task_for_review(new_review.id, new_review.initial_round_size)

        # if we're single or double- screening, we create a
        # perpetual task here
        if new_review.screening_mode in (u"single", u"double"):
            self._create_perpetual_task_for_review(new_review.id)

        # join the person administrating the review to the review.
        self._join_review(new_review.id)

        c.review = new_review
        c.num_articles = num_articles

        ###
        # here is where we'll want to thread the process of *encoding*
        # the documents comprising the review for consumption by the
        # machine learning stuff.
        c.root_path = url('/', qualified=True)
        c.flash = dict(c.flash.items() + dict_misc.items())
        return render("/reviews/review_created.mako")

    @ActionProtector(not_anonymous())
    def merge_reviews(self):
        reviews_to_merge = \
            [int(review_id) for review_id in request.params.getall("merge_review")]

        merged_review = self._make_new_review()
        merged_review.name = request.params['name']
        merged_review.description = request.params['description']
        merged_review.sort_by = request.params['order']
        screening_mode_str = request.params['screen_mode']
        init_round_size = int(request.params['init_size']) # TODO verify
        tag_privacy_str = request.params['tag_visibility']


        # TODO make the below dictionary a global!
        merged_review.screening_mode = \
           {"Single-screen":"single", "Double-screen":"double", "Advanced":"advanced"}[screening_mode_str]

        merged_review.tag_privacy = {"Private":True, "Public":False}[tag_privacy_str]

        Session.add(merged_review)
        Session.commit()

        # now merge the reviews
        for review_id in reviews_to_merge:
            self._move_review(review_id, merged_review.id)

        # Eliminate duplicate citations:
        self.de_duplicate_citations(merged_review.id, False)

        if merged_review.screening_mode in (u"single", u"double"):
            self._create_perpetual_task_for_review(merged_review.id)
            # now assign this perpetual task to everyone participating
            # in the merged review
            review_participants = \
               [reviewer.id for reviewer in self._get_participants_for_review(merged_review.id)]

            for reviewer_id in review_participants:
                self._assign_perpetual_task(reviewer_id, merged_review.id)

        if init_round_size > 0:
            self._set_initial_screen_size_for_review(merged_review, init_round_size)

        redirect(url(controller="account", action="my_projects"))

    @ActionProtector(not_anonymous())
    def edit_review(self, id, message=None):
        if not self._current_user_leads_review(id):
            return "yeah, I don't think so."
        c.review = self._get_review_from_id(id)
        if message is not None:
            c.msg = message

        c.screening_mode = {"single": "Single-screen",
                            "double": "Double-screen",
                            "advanced": "Advanced"}[c.review.screening_mode]
        c.order_abstracts = c.review.sort_by
        c.tag_privacy = {True: "Private", False: "Public"}[c.review.tag_privacy]

        return render("/reviews/edit_review.mako")

    @ActionProtector(not_anonymous())
    def edit_review_settings(self, id):
        if not self._current_user_leads_review(id):
            return "yeah, I don't think so."

        review = self._get_review_from_id(id)

        ####
        # check the screening-mode
        screening_mode_str = request.params['screen_mode']
        new_screening_mode =\
            {"Single-screen":"single", "Double-screen":"double", "Advanced":"advanced"}[screening_mode_str]
        self._change_review_screening_mode(id, new_screening_mode)

        ####
        # check the tag visibility
        tag_privacy_str = request.params['tag_visibility']
        new_tag_privacy = {"Private":True, "Public":False}[tag_privacy_str]
        self._change_tag_privacy(id, new_tag_privacy)

        ####
        # now the initial (pilot) round size
        new_init_round_size = int(request.params['init_size']) # TODO verify
        self._set_initial_screen_size_for_review(review, new_init_round_size)

        ###
        # re-prioritization -- BETA
        new_ordering = request.params['order']
        review.sort_by = new_ordering
        Session.commit()
        self._re_prioritize(id, new_ordering)

        return self.edit_review(id, message="ok -- review updated.")
        #if init_round_size == cur_init_assignment.

    @ActionProtector(not_anonymous())
    def render_add_citations(self, id, message=None):
        if not self._current_user_leads_review(id):
            return "yeah, I don't think so."
        c.review = self._get_review_from_id(id)
        if message is not None:
            c.msg = message

        c.error = False
        return render("/reviews/add_citations.mako")

    @ActionProtector(not_anonymous())
    def render_term_upload_page(self, id, message=None):
        if not self._current_user_leads_review(id):
            return "yeah, I don't think so."
        c.review = self._get_review_from_id(id)
        if message is not None:
            c.msg = message

        return render("/reviews/upload_terms.mako")

    @ActionProtector(not_anonymous())
    def upload_terms(self, id):
        # Obtain the review from the review id:
        cur_review = self._get_review_from_id(id)
        cur_user = self._get_user()

        # Get the file from the user and upload it:
        xml_file = request.POST['db']
        try:
            local_file_path = os.path.join(PERMANENT_STORE, xml_file.filename.lstrip(os.sep))
        except Exception, e:
            message = "You must specify a file to continue."
            return self.render_term_upload_page(id, message=message)

        try:
            local_file = open(local_file_path, 'w')
        except IOError:
            os.makedirs(os.path.dirname(local_file_path))
            local_file = open(local_file_path, 'w')
        finally:
            shutil.copyfileobj(xml_file.file, local_file)
            xml_file.file.close()
            local_file.close()

        # Process the import of terms.
        status, code, unprocessable = upload_term_helper.import_terms(local_file_path, cur_review, cur_user)

        if status:
            if len(unprocessable) > 0:
                message = "The terms have been successfully uploaded. The following terms could not be added: %s" % unprocessable
            else:
                message = "The terms have been successfully uploaded."
        else:
            if code == 1:
                message = "Failure: Tab separated file doesn't have a header row or first column is not 'term'."
            elif code == 2:
                message = "Failure: File may not be tab delimited."
            elif code == 3:
                message = "Failure: General error."
            else:
                message = "Failure: A problem was encountered while processesing your file."

        return self.render_term_upload_page(id, message=message)

    @ActionProtector(not_anonymous())
    def add_citations(self, id):

        # Obtain the review from the review id:
        cur_review = self._get_review_from_id(id)

        # Make sure assignments are opened up,
        #   in case one or more of the added citations are actually NEW citations:
        assignments = Session.query(model.Assignment).filter(model.Assignment.project_id==id).all()
        for each_assignment in assignments:
            if each_assignment.done:
                each_assignment.done = False

        # Get the file from the user and upload it:
        xml_file = request.POST['db']
        local_file_path = os.path.join(PERMANENT_STORE, xml_file.filename.lstrip(os.sep))
        try:
            local_file = open(local_file_path, 'w')
        except IOError:
            os.makedirs(os.path.dirname(local_file_path))
            local_file = open(local_file_path, 'w')
        finally:
            shutil.copyfileobj(xml_file.file, local_file)
            xml_file.file.close()
            local_file.close()

        # Extract the citations and add them to the database:
        num_articles = None
        if xml_file.filename.lower().endswith(".xml"):
            print "parsing uploaded xml..."
            num_articles, dict_misc = xml_to_sql.xml_to_sql(local_file_path, cur_review)
        elif xml_to_sql.looks_like_ris(local_file_path):
            num_articles = xml_to_sql.ris_to_sql(local_file_path, cur_review)
        elif xml_to_sql.looks_like_cochrane(local_file_path):
            num_articles = xml_to_sql.cochrane_to_sql(local_file_path, cur_review)
        elif xml_to_sql.looks_like_list(local_file_path):
            num_articles, dict_misc = xml_to_sql.pmid_list_to_sql(local_file_path, cur_review)
        elif xml_to_sql.looks_like_tsv(local_file_path):
            num_articles, dict_misc = xml_to_sql.tsv_to_sql(local_file_path, cur_review)
        else:
            c.error = True
            print "not a recognized format!!"
            c.review = cur_review
            return render("/reviews/add_citations.mako")
        print "done."

        # Reset the encoded status of the review to 'false':
        encoded_status = model.EncodeStatus()
        encoded_status.project_id = cur_review.id
        encoded_status.is_encoded = False
        Session.add(encoded_status)
        Session.commit()

        # Reset the prediction status of the review to 'false':
        prediction_status = model.PredictionsStatus()
        prediction_status.project_id = cur_review.id
        prediction_status.predictions_exist = False
        Session.add(prediction_status)
        Session.commit()

        return self.render_add_citations(id, message="The review has been updated with the new citations.")

    @ActionProtector(not_anonymous())
    def de_duplicate_citations(self, id, is_pubmed):

        # Obtain all citations:
        citations = Session.query(model.Citation).filter(model.Citation.project_id==id).all()

 # This is what we iterate through to collapse the duplicate citations:
        list_of_duplicates = []

        # This list contains the ids of all citations we have gone over.
        # Since we do not want duplicate elements in list_of_duplicates,
        #   we keep track of which citations we have gone over, and
        #   we do that by storing their ids in the following list.
        citation_ids = []

        # Iterate through the citations:
        for citation in citations:

            # Doing this will also prevent the duplicates from being checked,
            #   which increases the speed.
            if citation.id not in citation_ids:

                # If the file is a list of pubmed ids, check for duplicate pubmed ids:
                if is_pubmed:
                    # Grab the duplicates:
                    duplicates = self._get_duplicate_citations(str(citation.pmid), id, True)
                    # Add the citation ids so we don't have to go through the remaining of the duplicates:
                    for each in duplicates:
                        citation_ids.append(each.id)
                    # IFF there exist duplicate citations, append them to list_of_duplicates:
                    if len(duplicates) > 1:
                        # Each and every element of this list is a list of duplicate citations:
                        list_of_duplicates.append(duplicates)

                # If the file is NOT a list of pmids, check for duplicate titles:
                else:
                    duplicates = self._get_duplicate_citations(citation.title, id, False)
                    for each in duplicates:
                        citation_ids.append(each.id)
                    if len(duplicates) > 1:
                        list_of_duplicates.append(duplicates)

        #   a. Merge all of the labels by making the labels of any given set of duplicate citations
        #      point to only one of those citations.
        #   b. Delete all 'non-surviving' duplicate citations.
        self._collapse_duplicate_citations(list_of_duplicates)

    def _get_duplicate_citations(self, string, id, is_pubmed):
        # The type-casting of pmids to 'string' and then back to 'int' is necessary
        # in order to make pmids and titles be passed into this function using a single parameter.

        if is_pubmed:
            # Filter the citations by the pubmed ID as well as the review ID:
            return Session.query(model.Citation).\
                    filter( and_(model.Citation.pmid==int(string), model.Citation.project_id==id) ).all()
        else:
            return Session.query(model.Citation).\
                    filter( and_(model.Citation.title==string, model.Citation.project_id==id) ).all()

    def _collapse_duplicate_citations(self, list_of_duplicates):
        for each_collection_of_duplicates in list_of_duplicates:
            counter = 0  # This will ensure the first of the duplicates is considered the survivor.
            surviving_citation_id = None  # This id belongs to the lucky survivor of the duplicate citations.

            for each_duplicate_citation in each_collection_of_duplicates:

                if counter==0:
                    surviving_citation_id = each_duplicate_citation.id

                else:
                    # Take care of all affected entries in all tables that have citation_id (or study_id) as a field:

                    # Priority table:
                    self._change_pointers_or_delete_entries('priority', each_duplicate_citation.id, surviving_citation_id)

                    # Tags table:
                    self._change_pointers_or_delete_entries('tags', each_duplicate_citation.id, surviving_citation_id)

                    # Notes table:
                    self._change_pointers_or_delete_entries('notes', each_duplicate_citation.id, surviving_citation_id)

                    # Label table:
                    self._change_pointers_or_delete_entries('labels', each_duplicate_citation.id, surviving_citation_id)

                    # Prediction table:
                    self._change_pointers_or_delete_entries('predictions', each_duplicate_citation.id, surviving_citation_id)

                    # In case of the citation table, our task is slightly different - we will be deleting entries here:
                    self._delete_citation(each_duplicate_citation.id)

                counter = counter + 1
        Session.commit()

    def _change_pointers_or_delete_entries(self, tablename, citation_id, surviving_citation_id):
        # For each of the tables below:
        #   1. Acquire the objects filtered by the citation_id.
        #   2. Iterate through the objects and change their pointers,
        #      except for the priority table where we just delete the 'expired' priority entries.
        # Subsequently, the objects should point to only one of the duplicate citations;
        #   it does not matter which one, since the purpose of this course of action is
        #   to release the 'non-surviving' duplicate citations from all label-bindings.
        # A switch statement would be nice here, wouldn't it?

        if tablename == 'priority':
            priorities = Session.query(model.Priority).filter(model.Priority.citation_id==citation_id).all()
            for priority in priorities:
                if priority.citation_id != surviving_citation_id:
                    Session.delete(priority)

        elif tablename == 'tags':
            tags = Session.query(model.Tag).filter(model.Tag.citation_id==citation_id).all()
            for tag in tags:
                tag.citation_id = surviving_citation_id

        elif tablename == 'notes':
            notes = Session.query(model.Note).filter(model.Note.citation_id==citation_id).all()
            for note in notes:
                note.citation_id = surviving_citation_id

        elif tablename == 'labels':
            labels = Session.query(model.Label).filter(model.Label.study_id==citation_id).all()
            for label in labels:
                label.study_id = surviving_citation_id

        elif tablename == 'predictions':
            predictions = Session.query(model.Prediction).filter(model.Prediction.study_id==citation_id).all()
            for prediction in predictions:
                prediction.study_id = surviving_citation_id

        # Now save your changes to the DB:
        Session.commit()

    def _delete_citation(self, id):
        Session.delete(Session.query(model.Citation).filter(model.Citation.id==id).first())

    def _update_num_labels_in_priority_queue(self, review_id):
        '''
        iterate over the priority objects in the given review
        and update the number of times the associated citations
        have been screened. strictly speaking, this shouldn't be
        necessary -- this was written to fix a particular review
        in which the counts were off, somehow.
        '''
        review = self._get_review_from_id(review_id)
        screening_mode = review.screening_mode

        # pull out associated priority entries
        priority_q = Session.query(model.Priority)


        ranked_priorities =  priority_q.filter(\
                                    model.Priority.project_id == review_id).\
                                    order_by(model.Priority.priority).all()


        for priority_obj in ranked_priorities:
            num_lbls = len(self._get_labels_for_citation(priority_obj.citation_id))
            priority_obj.num_times_labeled = num_lbls
            Session.commit()

    def _change_review_screening_mode(self, review_id, new_screening_mode):
        '''
        screening_mode assume to be one of "single", "double", "advanced"
        '''
        review = self._get_review_from_id(review_id)
        previous_screening_mode = review.screening_mode

        if previous_screening_mode == new_screening_mode:
            # nothing to do here
            return None
        if previous_screening_mode == "single":
            if new_screening_mode == "double":
                # tricky -- we have to find all citations that
                # have only one label and pop them back into
                # the priority queue
                labeled_once_ids = self._citations_for_review_with_one_label(review_id)
                # we need to add these back to the priority table
                cur_max_priority = self._get_max_priority(review_id)+1
                for cit_id in labeled_once_ids:
                    xml_to_sql.insert_priority_entry(\
                            review_id, cit_id, cur_max_priority, num_times_labeled=1)
                    cur_max_priority += 1

                # now mark all perpetual assignments as 'unfinished'
                perpetual_assignments = self._get_perpetual_assignments_for_review(review_id)
                for assignment in perpetual_assignments:
                    assignment.done = False
                    Session.commit()

            else:
                # then it must be 'advanced': simply delete the perpetual assignment
                self._delete_perpetual_assignments_for_review(review_id)
        elif previous_screening_mode == "double":
            if new_screening_mode == "single":
                # I don't think we need to do anything here.
                pass
            else:
                # advanced mode, see above.
                self._delete_perpetual_assignments_for_review(review_id)
        else:
            # was advanced: in any case just add an appropriate
            # perpetual assignment
            self._create_perpetual_task_for_review(review_id)
            # now assign the perpetual task to everyone
            participating_reviewers = self._get_participants_for_review(review_id)
            for reviewer in participating_reviewers:
                self._assign_perpetual_task(reviewer.id, review_id)

        # also update the
        review.screening_mode = new_screening_mode
        Session.commit()

    def _change_tag_privacy(self,review_id, new_privacy_setting):
        '''Possible values for new_visibility: Private and Public'''
        # Step 1: Obtain the review.
        review = self._get_review_from_id(review_id)

        # Step 2: Check if the privacy setting has been changed.
        #         If it hasn't, do nothing.
        if review.tag_privacy == new_privacy_setting:
            return None

        # Step 3: If the privacy setting has been changed,
        #         all we need to do is update the tag_privacy field in the reviews table.
        review.tag_privacy = new_privacy_setting
        Session.commit()

    def _delete_perpetual_assignments_for_review(self, review_id):
        assignment_q = Session.query(model.Assignment)
        perpetual_assignments = \
            assignment_q.filter(and_(model.Assignment.project_id == review.id),\
                                     model.Assignment.type == u"perpetual").all()
        for perpetual_assignment in perpetual_assignments:
            Session.delete(perpetual_assignment)
            Session.commit()

    def _get_max_priority(self, review_id):
        '''
        return the highest priority number for the
        specified review.
        '''
        priority_q = Session.query(model.Priority)
        priority_objs_for_review = priority_q.filter(model.Priority.project_id == review_id).all()
        priorities = [p.priority for p in priority_objs_for_review]
        if len(priorities) == 0:
            return 0
        return max(priorities)

    def _citations_for_review_with_one_label(self, review_id):
        label_q = Session.query(model.Label)
        labels = label_q.filter(model.Label.project_id == review_id).all()
        # these all have at least one label
        has_one_lbl = lambda cit_id : \
            len(label_q.filter(model.Label.study_id == cit_id).all())==1

        labeled_once_ids = \
            [lbl.study_id for lbl in labels if has_one_lbl(lbl.study_id)]

        return labeled_once_ids

    def _move_review(self, old_review_id, new_review_id):
        '''
        this 'moves' the things associated with the review specified by
        the old_review_id to the review object specified by the new_reviwe_id,
        setting the identifier on all of the following:
               * reviewers
               * citations
               * labledfeatures
               * priority entries
               * labels
               * tagtypes
        there's a lot of boilerplate here that could probably be
        refactored to be made more concise.
        Tasks and assignments are removed -- i.e., not carried over
        to the merged target review.
        @TODO encodestatus and prediction entries will need also to be
                    changed, eventually
        '''

        ###
        # move (reviewers) first
        old_project = Session.query(model.Project).\
            filter(model.Project.id == old_review_id).one()
        new_project = Session.query(model.Project).\
            filter(model.Project.id == new_review_id).one()
        users_to_move = Session.query(model.User).\
            filter(model.User.member_of_projects.any(id=old_review_id)).all()
        for user_to_move in users_to_move:
            new_project.members.append(user_to_move)

        Session.add(new_project)
        Session.commit()

        ###
        # NOTE: we *remove* all assignments and tasks (below) -- resolving the
        #   possible combinations of existing assignments proved
        #   too complicated -- it's assumed that new assignments
        #   will be added elsewhere.
        ###
        assignments_q = Session.query(model.Assignment)
        assignments = assignments_q.filter(
            model.Assignment.project_id == old_review_id).all()
        for assignment in assignments:
            Session.delete(assignment)
        Session.commit()

        ###
        # now tasks
        tasks_q = Session.query(model.Task)
        tasks = tasks_q.filter(
            model.Task.project_id == old_review_id).all()
        for task in tasks:
            Session.delete(task)
        Session.commit()

        ###
        # and citations
        citations_q = Session.query(model.Citation)
        citations = citations_q.filter(
            model.Citation.project_id == old_review_id).all()
        for citation in citations:
            citation.project_id = new_review_id
            Session.add(citation)
        Session.commit()

        ###
        # labels
        labels_q = Session.query(model.Label)
        labels = labels_q.filter(
            model.Label.project_id == old_review_id).all()
        for label in labels:
            label.project_id = new_review_id
            # we remove the associated assignment id
            # because this assignment will no longer exist
            label.assignment_id = None
            Session.add(label)
        Session.commit()

        ###
        # labeled features
        lfs_q = Session.query(model.LabeledFeature)
        lfs = lfs_q.filter(
            model.LabeledFeature.project_id == old_review_id).all()
        for lf in lfs:
            lf.project_id = new_review_id
            Session.add(lf)
        Session.commit()

        ###
        # tags (technically, TagType)
        tag_types_q = Session.query(model.TagType)
        tag_types_to_move = tag_types_q.filter(
            model.TagType.project_id == old_review_id).all()

        # issues #29/#33: need to handle duplicate tags properly
        # here -- so we pull all tags already associated with the
        # review were are moving old_review to.
        tag_texts_to_ids = {}
        tags_already_in_new_review = tag_types_q.filter(
            model.TagType.project_id == new_review_id).all()
        for existing_tag in tags_already_in_new_review:
            tag_texts_to_ids[existing_tag.text.lower()] = existing_tag.id

        # now check the tags on the review being moved
        # against those that already exist on the target
        # review; if one exists, do not move it, but instead
        # re-assign all associated tag objects to the existing
        # tag-type.
        for tag_to_move in tag_types_to_move:
            if not tag_to_move.text.lower() in tag_texts_to_ids.keys():
                # ok -- it's a new tag, simply changed its associated
                # review to the new one
                tag_to_move.project_id = new_review_id
                Session.add(tag_to_move)
                Session.commit()
            else:
                # then we've already got a tag with the same
                # text, so we de-dupe by moving all tags associated
                # with this type to the existing tag
                pre_existing_tag_id = tag_texts_to_ids[tag_to_move.text.lower()]

                # for actual tags, not tag types
                tags_q = Session.query(model.Tag)
                tags_of_this_type =\
                    tags_q.filter(model.Tag.tag_id == tag_to_move.id).all()

                for dupe_tag in tags_of_this_type:
                    # associate these tags with the already-existing
                    # tag that has the same text -- note that
                    # this tag (pre_existing_tag_id) is already
                    # associated with the target review
                    dupe_tag.tag_id = pre_existing_tag_id
                    Session.add(dupe_tag)
                Session.commit()

                # now delete the duplicate tag.
                Session.delete(tag_to_move)
                Session.commit()

        ###
        # priority
        priority_q = Session.query(model.Priority)
        priorities = priority_q.filter(
            model.Priority.project_id == old_review_id).all()
        for priority in priorities:
            priority.project_id = new_review_id
            Session.add(priority)
        Session.commit()

        # ok -- that's it. now we're going to *delete* the old review!
        # jj 2018-6-2 Request by Ethan: We do not want to delete the old project.
        # jj 2018-6-2 : Not so simple afterall.
        Session.delete(old_project)
        Session.commit()

    def _make_new_review(self):
        new_review = model.Project()

        current_user = request.environ.get('repoze.who.identity')['user']
        user = controller_globals._get_user_from_email(current_user.email)

        # we generate a random code for joining this review
        make_code = lambda N: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
        review_q = Session.query(model.Project)
        code_length=10
        cur_code = make_code(code_length)
        while review_q.filter_by(code=cur_code).first():
            cur_code = make_code(code_length)
        new_review.code = cur_code

        # The current_user will be a project leader.
        new_review.leaders.append(user)
        new_review.date_created = datetime.datetime.now()

        new_review.initial_round_size = 0
        new_review.tag_privacy = True

        Session.add(new_review)
        Session.commit()

        return new_review

    @ActionProtector(not_anonymous())
    def invite_reviewers(self, id):
        emails = request.params['emails'].split(",")
        review = self._get_review_from_id(id)
        for email in emails:
            self._invite_person_to_join(email, review)


        return self.admin(id, admin_msg="OK -- sent invites to: %s" % request.params['emails'])

    # @TODO this is redundant with code in account.py --
    # re-factor.
    def _invite_person_to_join(self, email, project):
        subject = "Invitation to join review on abstrackr"
        message = """
            Hi there!
            What luck! You've had the good fortune of being invited to join the project: %s
            on abstrackr.
            To do so, you're going to need to sign up for an account, if you don't already have one.
            Then you'll want to log in, and follow this link: %s.
            Happy screening.
        """ % (project.name, \
               "%sjoin/%s" % (url('/', qualified=True), project.code))

        host = config['smtp_host']
        port = config['smtp_port']
        sender = config['smtp_sender']
        username = config['smtp_username']
        password = config['smtp_password']
        to = email
        body = string.join((
            "From: %s" % sender,
            "To: %s" % to,
            "Subject: %s" % subject,
            "",
            message
            ), "\r\n")

        try:
            server = smtplib.SMTP_SSL(host, port)
            server.ehlo()
            server.login(username, password)
            server.sendmail(sender, [to], body)
            server.close()
        except Exception, err:
            print 'Unable to send email. Reason: ' + err

    @ActionProtector(not_anonymous())
    def join_a_review(self):
        review_q = Session.query(model.Project)
        c.all_reviews = review_q.all()
        return render("/reviews/join_a_review.mako")

    @ActionProtector(not_anonymous())
    def join(self, review_code):
        user_id = request.environ.get('repoze.who.identity')['user']
        review_q = Session.query(model.Project)

        review_to_join = review_q.filter(model.Project.code==review_code).one()
        self._join_review(review_to_join.id)
        redirect(url(controller="account", action="welcome"))

    @ActionProtector(not_anonymous())
    def leave_review(self, id):
        current_user = request.environ.get('repoze.who.identity')['user']
        self._remove_user_from_review(current_user.id, int(id))
        redirect(url(controller="account", action="welcome"))

    @ActionProtector(not_anonymous())
    def remove_from_review(self, reviewer_id, review_id):
        self._remove_user_from_review(reviewer_id, review_id)
        redirect(url(controller="review", action="admin", project_id=review_id))

    def _remove_user_from_review(self, user_id, project_id):
        project = Session.query(model.Project).filter_by(id=project_id).one()
        user = Session.query(model.User).filter_by(id=user_id).one()

        # project.members is the collection of users associated with this project
        project.members.remove(user)
        Session.commit()

        # next, we need to delete all assignments for this person and review
        assignments_q = Session.query(model.Assignment)
        assignments = assignments_q.filter(and_(\
                    model.Assignment.project_id == project_id,
                    model.Assignment.user_id == user_id
        )).all()

        for assignment in assignments:
            Session.delete(assignment)
            Session.commit()

    @ActionProtector(not_anonymous())
    def get_fields(self, review_id):
        c.review_id = review_id
        return render("/reviews/export_fragment.mako")

    @ActionProtector(not_anonymous())
    def export_labels(self, id, lbl_filter_f=None):
        fields_to_export = []
        export_type = "ris"

        for key,val in request.params.items():
            if key == "fields[]" and not val in ("", " ", "(enter new tag)"):
                fields_to_export.append(str(val))
            elif key == "export_type" and not val in ("", " "):
                export_type = str(val)

        exporter = Exporter(id, export_type)
        exporter.set_fields(fields_to_export)
        c.download_url = exporter.create_export()
        print c.download_url
        return render("/reviews/download_labels.mako")

    @ActionProtector(not_anonymous())
    def delete_review(self, id):
        review_q = Session.query(model.Project)
        review = review_q.filter(model.Project.id == id).one()

        # make sure we're actually the project lead
        current_user = request.environ.get('repoze.who.identity')['user']
        if not self._current_user_leads_review(review.id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname

        ###
        # should probably re-factor into routines...
        ###
        # first delete all associated citations
        citation_q = Session.query(model.Citation)
        try:
            citations_for_review = citation_q.filter(model.Citation.project_id == review.id).all()
        except:
            pdb.set_trace()

        for citation in citations_for_review:
            Session.delete(citation)
        Session.commit()

        label_q = Session.query(model.Label)
        labels = label_q.filter(model.Label.project_id == review.id).all()
        for l in labels:
            Session.delete(l)
        Session.commit()

        label_feature_q = Session.query(model.LabeledFeature)
        labeled_features = label_feature_q.filter(model.LabeledFeature.project_id == review.id).all()
        for l in labeled_features:
            Session.delete(l)
            Session.commit()

        priority_q = Session.query(model.Priority)
        priorities = priority_q.filter(model.Priority.project_id == review.id).all()
        for p in priorities:
            Session.delete(p)
        Session.commit()

        # remove all tasks associated with this review
        task_q = Session.query(model.Task)
        tasks = task_q.filter(model.Task.project_id == review.id).all()
        for task in tasks:
            Session.delete(task)
            Session.commit()


        # ... and any assignments
        assignment_q = Session.query(model.Assignment)
        assignments = assignment_q.filter(model.Assignment.project_id == review.id).all()
        for assignment in assignments:
            Session.delete(assignment)
            Session.commit()

        # and the encoded status/prediction entries
        encoded_q = Session.query(model.EncodeStatus)
        encoded_entries = encoded_q.filter(model.EncodeStatus.project_id == review.id).all()
        for encoded_entry in encoded_entries:
            Session.delete(encoded_entry)
            Session.commit()

        # predictions
        prediction_q = Session.query(model.Prediction)
        predictions = prediction_q.filter(model.Prediction.project_id == review.id).all()
        for pred in predictions:
            Session.delete(pred)
            Session.commit()

        # and the prediction status objects
        pred_status_q = Session.query(model.PredictionsStatus)
        pred_statuses = pred_status_q.filter(model.PredictionsStatus.project_id == review.id).all()
        for pred_stat in pred_statuses:
            Session.delete(pred_stat)
            Session.commit()

        # finally, delete the review
        Session.delete(review)
        Session.commit()

        redirect(url(controller="account", action="my_projects"))

    def get_conflict_button_fragment(self, id):
        if (controller_globals._does_a_conflict_exist(id)):
            c.display_the_button = True
        else:
            c.display_the_button = False
        c.review_id = id
        # this template will determine whether the conflicts
        # button is shown or the text is shown.
        return render("/reviews/conflict_button.mako")

    @ActionProtector(not_anonymous())
    def review_maybes(self, id):
        project_id = id
        maybe_ids = controller_globals._get_maybes(project_id)
        # TODO rename method
        self._create_conflict_task_with_ids(project_id, maybe_ids)

    @ActionProtector(not_anonymous())
    def review_conflicts(self, id):
        '''
        the basic idea here is to find all of the conflicting ids, then
        shove these into a FixedTask type task (i.e., a task with an
        enumerated set of ids to be labeled). This task is then assigned
        to the project lead (assumed to be the current user).
        '''
        project_id = id
        conflicting_ids = controller_globals._get_conflicts(project_id)
        self._create_conflict_task_with_ids(project_id, conflicting_ids)

    def _create_conflict_task_with_ids(self, review_id, citation_ids):
        task_q = Session.query(model.Task)
        conflicts_task_for_this_review = \
            task_q.filter(and_(model.Task.project_id == review_id,\
                               model.Task.task_type == "conflict")).all()

        # we delete any existing conflict Tasks for this review
        if len(conflicts_task_for_this_review) > 0:
            # we assume there is only one such conflicts Task;
            # so if one already exists, we delete it.
            Session.delete(conflicts_task_for_this_review[0])
            Session.commit()

        assignment_q = Session.query(model.Assignment)
        conflict_assignments_for_this_review = \
            assignment_q.filter(and_(model.Assignment.project_id == review_id,\
                               model.Assignment.assignment_type == "conflict")).all()

        # we delete any existing conflict Assignments for this review
        if len(conflict_assignments_for_this_review) > 0:
            for c in conflict_assignments_for_this_review:
                Session.delete(c)
                Session.commit()

        ### now create an task to review these
        conflict_task = model.Task()
        conflict_task.task_type = "conflict"
        conflict_task.project_id = review_id
        conflict_task.num_assigned = len(citation_ids)
        for conflicting_id in citation_ids:
            obj_citation = Session.query(model.Citation).\
                    filter(model.Citation.id == conflicting_id).one()
            conflict_task.citations.append(obj_citation)
        Session.add(conflict_task)
        Session.commit()

        # finally, add an assignment to (me). note that (me)
        # is the project lead.
        conflict_a = model.Assignment()
        conflict_a.project_id = review_id
        conflict_a.task_id = conflict_task.id
        conflict_a.date_assigned = datetime.datetime.now()
        conflict_a.assignment_type = conflict_task.task_type
        conflict_a.num_assigned = conflict_task.num_assigned
        conflict_a.done_so_far = 0
        Session.add(conflict_a)
        Session.commit()

        redirect(url(controller="review", action="screen", \
                        review_id=review_id, assignment_id=conflict_a.id))

    def _get_labels_for_citation(self, citation_id):
        return Session.query(model.Label).\
            filter(model.Label.study_id==citation_id).all()

    @ActionProtector(not_anonymous())
    def admin(self, project_id, admin_msg=""):
        project = Session.query(model.Project).filter_by(id=project_id).one()
        c.review = project
        current_user = request.environ.get('repoze.who.identity')['user']
        # make sure we're actually the project lead
        if not self._current_user_leads_review(project_id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname

        c.project_leader_list = project.leaders
        c.participating_reviewers = self._get_participants_for_review(project_id)
        # eliminate our the lead themselves from this list
        c.participating_reviewers = [reviewer for reviewer in c.participating_reviewers if \
                                        reviewer.id != current_user.id]

        # for the client side
        c.reviewer_ids_to_names_d = self._reviewer_ids_to_names(c.participating_reviewers)
        c.admin_msg = admin_msg
        c.root_path = url('/', qualified=True)
        return render("/reviews/admin.mako")

    @ActionProtector(not_anonymous())
    def add_admin(self, project_id, user_id):
        """Add user to the project leader group

        Sets the user specified by user_id as a leader of the
        review specified by project_id.

        """
        current_user = request.environ.get('repoze.who.identity')['user']
        user = controller_globals._get_user_from_email(current_user.email)

        # make sure we're actually the project lead
        if not self._current_user_leads_review(project_id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % user.fullname

        new_leader = Session.query(model.User).filter_by(id=user_id).one()
        review = self._get_review_from_id(project_id)
        review.leaders.append(new_leader)
        Session.add(review)
        Session.commit()

        redirect(url(controller="review", action="admin", project_id=project_id))

    @ActionProtector(not_anonymous())
    def remove_admin(self, project_id, user_id):
        """Remove user from the project leader group

        Removes the user specified by user_id from the leader of the
        project group specified by project_id.

        """
        current_user = request.environ.get('repoze.who.identity')['user']
        user = controller_globals._get_user_from_email(current_user.email)

        # make sure we're actually the project lead
        if not self._current_user_leads_review(project_id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % user.fullname

        leader_to_remove = Session.query(model.User).filter_by(id=user_id).one()
        review = self._get_review_from_id(project_id)
        review.leaders.remove(leader_to_remove)
        Session.add(review)
        Session.commit()

        redirect(url(controller="review", action="admin", project_id=project_id))

    @ActionProtector(not_anonymous())
    def assignments(self, id):
        # make sure we're actually the project lead (by the way, should probably
        # handle this verification in a decorator...)
        if not self._current_user_leads_review(id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname

        c.participating_reviewers = self._get_participants_for_review(id)
        c.reviewer_ids_to_names_d = self._reviewer_ids_to_names(c.participating_reviewers)

        assignments_q = Session.query(model.Assignment)

        assignments = assignments_q.filter(model.Assignment.project_id == id).all()

        c.d_completion_status = self._get_assignment_completion_status(assignments)

        # note that we don't show the 'conflict' assignments here.
        non_conflict_assignments = \
            [assignment for assignment in assignments if \
                     assignment.assignment_type != "conflict"]

        c.assignments = non_conflict_assignments
        return render("/reviews/assignments.mako")

    def _current_user_leads_review(self, review_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        user = controller_globals._get_user_from_email(current_user.email)
        c.review = self._get_review_from_id(review_id)
        return user in c.review.leaders

    def _reviewer_ids_to_names(self, users):
        # for the client side
        reviewer_ids_to_names_d = {}
        for user in users:
            #reviewer_ids_to_names_d[reviewer.id] = reviewer.username
            reviewer_ids_to_names_d[user.id] = user.username
        reviewer_ids_to_names_d = reviewer_ids_to_names_d
        return reviewer_ids_to_names_d

    @ActionProtector(not_anonymous())
    def participants(self, id):
        # make sure we're actually the project lead (by the way, should probably
        # handle this verification in a decorator...)
        current_user = request.environ.get('repoze.who.identity')['user']
        c.review = self._get_review_from_id(id)
        if not self._current_user_leads_review(c.review.id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname

        c.participating_reviewers = self._get_participants_for_review(id)

        return render("/reviews/participants.mako")

    def _re_prioritize(self, review_id, sort_by_str):
        citation_ids = [cit.id for cit in self._get_citations_for_review(review_id)]
        predictions_for_review = None
        if self._do_predictions_exist_for_review(review_id):
            predictions_for_review = self._get_predictions_for_review(review_id)
        else:
            # then we have to sort randomly, since we haven't any predictions
            sort_by_str = "Random"

        # we'll map citation ids to the newly decided priorities;
        # these will depend on the sort_by_str
        cit_id_to_new_priority = {}
        if sort_by_str == "Random":
            ordering = range(len(citation_ids))
            # shuffle
            random.shuffle(ordering)
            cit_id_to_new_priority = dict(zip(citation_ids, ordering))
        elif sort_by_str == "Most likely to be relevant":
            # sort the citations by ascending likelihood of relevance
            cits_to_preds = {}
            # first insert entries for *all* citations, which will be random.
            # this will take care of any citations without predictions --
            # e.g., a review may have been merged (?) -- citations for which
            # we have predictions will simply be overwritten, below
            for citation_id in citation_ids:
                cits_to_preds[citation_id] = random.randint(0,11)

            for prediction in predictions_for_review:
                cits_to_preds[prediction.study_id] = prediction.num_yes_votes

            # now we will sort by *descending* order; those with the most yes-votes first
            sorted_cit_ids = sorted(cits_to_preds.iteritems(), key=itemgetter(1), reverse=True)
            # now just assign priorities that reflect the ordering w.r.t. the predictions
            for i, cit in enumerate(sorted_cit_ids):
                cit_id_to_new_priority[cit[0]] = i

        priority_q = Session.query(model.Priority)
        priorities_for_review =  priority_q.filter(\
                                    model.Priority.project_id == review_id).all()
        for priority_obj in priorities_for_review:
            priority_obj.priority = cit_id_to_new_priority[priority_obj.citation_id]
            Session.commit()

    @ActionProtector(not_anonymous())
    def show_review(self, id):
        review_q = Session.query(model.Project)

        c.review = review_q.filter(model.Project.id == id).one()
        # grab all of the citations associated with this review
        citation_q = Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.project_id == id).all()

        c.num_citations = len(citations_for_review)
        # and the labels provided thus far
        label_q = Session.query(model.Label)
        ### TODO first of all, will want to differentiate between
        # unique and total (i.e., double screened citations). will
        # also likely want to pull additional information here, e.g.,
        # the participating reviewers, etc.
        labels_for_review = label_q.filter(model.Label.project_id == id).all()
        c.num_unique_labels = len(set([lbl.study_id for lbl in labels_for_review]))
        c.num_labels = len(labels_for_review)

        # Query object: list of study_id from labels table for this review
        # SELECT labels.study_id AS labels_study_id
        # FROM labels
        # WHERE labels.project_id = %s
        # LIMIT %s
        #subquery_aa = Session.query(model.Label.study_id).filter(model.Label.project_id==id)

        # Find citations for which no labels exist:
        # SELECT citations.id AS citations_id
        # FROM citations
        # WHERE citations.project_id = %s AND citations.id NOT IN (SELECT labels.study_id AS labels_study_id
        # FROM labels
        # WHERE labels.project_id = %s)
        #c.num_unlabeled_citations = len( Session.query(model.Citation.id).
        #                                         filter(model.Citation.project_id==id).
        #                                         filter(~model.Citation.id.in_(subquery_aa)).all() )
        c.num_unlabeled_citations = c.num_citations-c.num_unique_labels

        # generate a pretty plot via google charts
        chart = PieChart3D(500, 200)
        chart.add_data([c.num_citations-c.num_unique_labels, c.num_unique_labels])
        chart.set_colours(['224499', '80C65A'])
        chart.set_pie_labels(['unscreened', 'screened'])
        # For some reason | is represented by %7c. We unquote here to set it back to |. Only happens
        # for chart.set_pie_labels.
        c.pi_url = urllib.unquote(chart.get_url())

        c.participating_reviewers = reviewers = self._get_participants_for_review(id)
        #user_q = Session.query(model.User)
        #c.project_lead = user_q.filter(model.User.id == c.review.leader_id).one()
        c.project_leaders = c.review.leaders

        current_user = request.environ.get('repoze.who.identity')['user']
        c.is_admin = self._current_user_leads_review(id)
        n_lbl_d = {} # map users to the number of labels they've provided
        for reviewer in reviewers:
            # @TODO problematic if two reviewers have the same fullname, which
            # isn't explicitly prohibited
            n_lbl_d[reviewer.fullname] = len([l for l in labels_for_review if l.user_id == reviewer.id])

        # now make a horizontal bar graph showing the amount of work done by reviewers
        workloads = n_lbl_d.items() # first sort by the number of citations screened, descending
        workloads.sort(key = itemgetter(1), reverse=True)
        num_screened = [x[1] for x in workloads]
        names = [x[0] for x in workloads]


        ###
        # so, due to what is apparently a bug in the pygooglechart api,
        # we construct a google charts string explicitly for the horizontal bar graph here.
        height = 30*len(names)+50
        width = 500
        google_url = "https://chart.apis.google.com/chart?cht=bhg&chs=%sx%s" % (width, height)
        chart = StackedHorizontalBarChart(500, 30*len(names)+50, x_range=(0, c.num_labels))
        data_str = "chd=t:%s" % ",".join([str(n) for n in num_screened])
        google_url = "&".join([google_url, data_str])
        max_num_screened = max(num_screened)
        google_url = "&".join([google_url, "chds=0,%s" % max_num_screened])
        # we have to reverse the names here; this seems to be a quirk with
        # google maps. see: http://psychopyko.com/tutorial/how-to-use-google-charts/
        names.reverse()
        google_url = "&".join([google_url, "chxt=y,x&chxl=0:|%s|" % "|".join([name.replace(" ", "%20") for name in names])])
        # now the x axis labels
        x_ticks = [0, int(max_num_screened/3.0), int(max_num_screened/2.0), int(3 * (max_num_screened/4.0)), max_num_screened]
        google_url = "".join([google_url, "1:|%s" % "|".join([str(x) for x in x_ticks])])
        bar_width = 25
        google_url = google_url + "&chbh=%s&chco=4D89F9" % bar_width
        c.workload_graph_url = google_url

        return render("/reviews/show_review.mako")

    @ActionProtector(not_anonymous())
    def relabel_term(self, term_id, assignment_id, new_label):
        term_q = Session.query(model.LabeledFeature)
        labeled_term =  term_q.filter(model.LabeledFeature.id == term_id).one()
        labeled_term.label = new_label
        Session.add(labeled_term)
        Session.commit()
        redirect(url(controller="review", action="review_terms",
                id=labeled_term.project_id, assignment_id=assignment_id))

    @ActionProtector(not_anonymous())
    def delete_term(self, term_id, assignment_id):
        term_q = Session.query(model.LabeledFeature)
        labeled_term = term_q.filter(model.LabeledFeature.id == term_id).one()
        Session.delete(labeled_term)
        Session.commit()
        redirect(url(controller="review", action="review_terms",
                id=labeled_term.project_id, assignment_id=assignment_id))

    @ActionProtector(not_anonymous())
    def label_term(self, review_id, label):
        current_user = request.environ.get('repoze.who.identity')['user']
        new_labeled_feature = model.LabeledFeature()
        new_labeled_feature.term = request.params['term']
        new_labeled_feature.project_id = review_id
        new_labeled_feature.user_id = current_user.id
        new_labeled_feature.label = label
        new_labeled_feature.date_created = datetime.datetime.now()
        Session.add(new_labeled_feature)
        Session.commit()

    @ActionProtector(not_anonymous())
    def delete_assignment(self, review_id, assignment_id):
        if not self._current_user_leads_review(review_id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname

        assignment_q = Session.query(model.Assignment)
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).first()
        task_id = assignment.task_id
        Session.delete(assignment)
        Session.commit()

        # If this was the last assignment referencing this task, then we need to delete the task also
        assignment = Session.query(model.Assignment).filter_by(task_id=task_id).all()
        if len(assignment)==0:
            task = Session.query(model.Task).filter_by(id=task_id).first()
            Session.delete(task)
            Session.commit()

        redirect(url(controller="review", action="assignments",
                            id=review_id))

    @ActionProtector(not_anonymous())
    def add_notes(self, study_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        self._add_notes(study_id, request.params, current_user)

    def _add_notes(self, citation_id, notes, current_user):
        existing_note = self._get_notes_for_citation(citation_id, current_user.id)
        if existing_note is None:
            # create a new note, then
            existing_note = model.Note()
            Session.add(existing_note)

        char_limit = 999
        existing_note.general = notes["general_notes"][:char_limit]
        existing_note.population = notes["population_notes"][:char_limit]
        existing_note.ic = notes["ic_notes"][:char_limit]
        existing_note.outcome = notes["outcome_notes"][:char_limit]
        existing_note.creator_id = current_user.id
        existing_note.citation_id = citation_id

        Session.commit()

    def _get_notes_for_citation(self, citation_id, user_id):
        notes_q = Session.query(model.Note)
        notes = notes_q.filter(and_(\
                model.Note.citation_id == citation_id,
                model.Note.creator_id == user_id)).all()
        if len(notes) > 0:
            return notes[0]
        return None

    @ActionProtector(not_anonymous())
    def tag_citation(self, review_id, study_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        tags = []
        for key,val in request.params.items():
            if key == "tags[]" and not val in ("", " ", "(enter new tag)"):
                tags.append(val)


        # check if any are to be added (i.e., for a new tag)
        existing_tag_types = self._get_tag_types_for_review(review_id)

        tags = [tag.strip() for tag in list(set(tags))]
        for user_tag in tags:
            if user_tag not in existing_tag_types:
                self.add_tag(review_id, user_tag)

        # ok -- now, get tags for this citation; we're going to
        # untag everything first
        cur_tags = self._get_tags_for_citation(study_id, texts_only=False, only_for_user_id=current_user.id)
        for tag in cur_tags:
            Session.delete(tag)
            Session.commit()

        # now add all the new tags
        for tag in list(set(tags)):
            new_tag = model.Tag()
            new_tag.creator_id = current_user.id
            new_tag.tag_id = self._get_tag_id(review_id, tag)

            new_tag.citation_id = study_id
            Session.add(new_tag)
            Session.commit()

    @ActionProtector(not_anonymous())
    def add_tag(self, review_id, tag):
        current_user = request.environ.get('repoze.who.identity')['user']

        # make sure there isn't already an identical tag
        cur_tags = self._get_tag_types_for_review(review_id)

        if tag not in cur_tags:
            new_tag = model.TagType()
            new_tag.text = tag
            new_tag.project_id = review_id
            new_tag.creator_id = current_user.id
            Session.add(new_tag)
            Session.commit()

    @ActionProtector(not_anonymous())
    def label_citation(self, review_id, assignment_id, study_id, seconds, label):
        # unnervingly, this commit() must remain here, or sql
        # alchemy seems to get into a funk. I realize this is
        # cargo-cult programming... @TODO further investigate
        Session.commit()


        current_user = request.environ.get('repoze.who.identity')['user']

        # check if we've already labeled this; if so, handle appropriately
        existing_label = None

        # pull the associated assignment object
        assignment = self._get_assignment_from_id(assignment_id)

        label_q = Session.query(model.Label)

        # Based on the assignment type we now look for any existing
        # label. When assignment type is "conflict" we look for a label
        # by CONSENSUS_USER (ID=0), else by current_user ID
        if assignment.assignment_type == "conflict":
            user_id = CONSENSUS_USER
        else:
            user_id = current_user.id

        existing_label = label_q.filter(and_(model.Label.project_id==review_id,
                                             model.Label.study_id==study_id,
                                             model.Label.user_id==user_id,
                                             model.Label.assignment_id==assignment_id)).all()

        # Case when we re-label a citation
        if len(existing_label) > 0:
            # then this person has already labeled this example
            print "(RE-)labeling citation %s with label %s" % (study_id, label)
            existing_label = existing_label[0]
            existing_label.label = label
            existing_label.label_last_updated = datetime.datetime.now()
            existing_label.labeling_time += int(seconds)
            Session.add(existing_label)
            Session.commit()

            if existing_label.user_id == CONSENSUS_USER:
                c.consensus_review = True

            # if we are re-labelng, return the same abstract, reflecting the new
            # label. we put the single consensus label in a singleton list for the
            # client in the case that this is a 'conflict' assignment.
            c.cur_lbl = existing_label if assignment.assignment_type != "conflict" else [existing_label]

            c.assignment_id = assignment_id
            citation_q = Session.query(model.Citation)
            c.assignment_type = assignment.assignment_type
            c.cur_citation = citation_q.filter(model.Citation.id == study_id).one()
            c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
            c.review_id = review_id
            c.assignment = assignment

            user = controller_globals._get_user_from_email(current_user.email)
            # Need the above line to obtain a model.User object (which is what I need)
            # as opposed to a model.auth.User object

            # The following help determine which fields of the citation are shown.
            c.show_journal = user.show_journal
            c.show_authors = user.show_authors
            c.show_keywords = user.show_keywords

            # The following help keep tags public/private,
            # depending on which option the project leader selected.
            c.tag_privacy = self._get_review_from_id(review_id).tag_privacy
            c.user_id = user.id

            # Create assignment status dictionary
            c.d_completion_status = self._get_assignment_completion_status([assignment])

            return render("/citation_fragment.mako")

        else:
            # either there is no existing label or this is a consens label
            # being provided (or both!)
            print "labeling citation %s with label %s" % (study_id, label)
            # first push the label to the database
            new_label = model.Label()
            new_label.label = label
            new_label.project_id = review_id
            new_label.study_id = study_id
            new_label.assignment_id = assignment_id
            new_label.labeling_time = int(seconds)

            if assignment.assignment_type == "conflict":
                # the 0th reviewer can be thought of as God
                # i.e., omniscient -- this is taken to be the
                # group consensus user
                new_label.user_id = CONSENSUS_USER
            else:
                new_label.user_id = current_user.id

            new_label.first_labeled = new_label.label_last_updated = datetime.datetime.now()
            Session.add(new_label)

            assignment.done_so_far += 1
            Session.add(assignment)
            Session.commit()

            ###
            # for finite assignments, we need to check if we're through.
            #if assignment.assignment_type != "perpetual":
            if assignment.assignment_type not in ["perpetual", "assigned"]:
                # in the case of conflict (and 'review maybe') assignments,
                # we don't do fancy cacheing and hence just return the next
                # citation here. may want to implement this in the future.
                if  assignment.assignment_type == "conflict":
                    c.consensus_review = False
                    return self.get_next_citation_fragment(review_id, assignment_id)
                elif assignment.done_so_far >= assignment.num_assigned:
                    assignment.done = True
                    Session.commit()
            else:
                # for `perpetual' (single, double or n-screening) case or `assigned',
                # we need to keep track of the priority table.
                #
                # update the number of times this citation has been labeled;
                # if we have collected a sufficient number of labels, pop it from
                # the queue
                priority_obj = self._get_priority_for_citation_review(study_id, review_id)
                priority_obj.num_times_labeled += 1
                priority_obj.is_out = False
                priority_obj.locked_by = None
                Session.add(priority_obj)
                Session.commit()

                # are we through with this citation/review?
                review = self._get_review_from_id(review_id)

                if review.screening_mode in ["single", "double", "advanced"]:
                    num_times_to_screen  = {"single": 1, "double": 2, "advanced": 1}[review.screening_mode]

                    if priority_obj.num_times_labeled >= num_times_to_screen:
                        Session.delete(priority_obj)
                        Session.commit()

                    # has this person already labeled everything in this review?
                    num_citations_in_review = controller_globals._get_cnt_citations_in_project_by_project_id(review_id)
                    num_screened = len(self._get_already_labeled_ids(review.id, reviewer_id=user_id))

                    if num_screened >= num_citations_in_review:
                        assignment.done = True
                        Session.add(assignment)
                        Session.commit()

                if review.screening_mode in ["advanced"]:
                    num_screened_in_assignment = len(self._get_already_labeled_ids(review.id,
                                                                                   reviewer_id=user_id,
                                                                                   assignment_id=assignment.id))
                    if num_screened_in_assignment>=assignment.num_assigned:
                        assignment.done = True
                        Session.add(assignment)
                        Session.commit()

            # Create assignment status dictionary
            c.d_completion_status = self._get_assignment_completion_status([assignment])

            progress_html_str = None
            if assignment.num_assigned and assignment.num_assigned > 0:
                progress_html_str = \
                    "you've screened <b>%s</b> out of <b>%s</b> so far (nice going!)" % (c.d_completion_status[assignment.id], assignment.num_assigned)
            else:
                progress_html_str = \
                    "you've screened <b>%s</b> abstracts thus far (keep it up!)"  % c.d_completion_status[assignment.id]
            print "returning progress html str %s" % progress_html_str

            return progress_html_str

    @ActionProtector(not_anonymous())
    def markup_citation(self, id, assignment_id, citation_id):
        citation_q = Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.id == citation_id).one()
        c.review_id = id
        c.assignment_id = assignment_id

        # issue #41
        assignment = self._get_assignment_from_id(assignment_id)
        c.assignment_type = assignment.assignment_type
        c.cur_citation = self._mark_up_citation(id, c.cur_citation)

        current_user = request.environ.get('repoze.who.identity')['user']
        label_q = Session.query(model.Label)
        c.cur_lbl = label_q.filter(and_(
                                     model.Label.study_id == citation_id,
                                     model.Label.user_id == current_user.id)).all()
        if len(c.cur_lbl) > 0:
            c.cur_lbl = c.cur_lbl[0]
        else:
            c.cur_lbl = None

        user = controller_globals._get_user_from_email(current_user.email)
        # Need the above line because the environment gives
        #   a model.auth.User object
        # as opposed to
        #   a model.User object (which is what I need)

        # The following help determine which fields of the citation are shown.
        c.show_journal = user.show_journal
        c.show_authors = user.show_authors
        c.show_keywords = user.show_keywords

        # The following help in the execution of the 'tag-privacy' option.
        c.tag_privacy = self._get_review_from_id(id).tag_privacy
        c.user_id = user.id

        return render("/citation_fragment.mako")

    @ActionProtector(not_anonymous())
    def screen(self, review_id, assignment_id):
        user = self._get_user()

        assignment = self._get_assignment_from_id(assignment_id)

        if assignment is None:
            # Redirect to the screen page again...essentially trigger a reload.
            redirect(url(controller="review", action="screen", \
                        review_id=review_id, assignment_id = assignment_id))
        else:
            # Update the done_so_far count. Sometimes this count is off.
            self._update_done_so_far_count(assignment)

        # Force a assignment done check.
        if controller_globals._check_assignment_done(assignment):
            assignment.done = True
            Session.add(assignment)
            Session.commit()
            redirect(url(controller="account", action="welcome"))

        review = self._get_review_from_id(review_id)

        # clear our locks for this review
        self._clear_all_my_locks(review.id)

        c.review_id = review_id
        c.review_name = review.name
        c.assignment_id = assignment_id
        c.assignment_type = assignment.assignment_type
        c.assignment = assignment

        # The following help determine which fields of the citation are shown.
        c.show_journal = user.show_journal
        c.show_authors = user.show_authors
        c.show_keywords = user.show_keywords

        c.cur_citation = self._get_next_citation(assignment, review)

        if c.cur_citation is None:
            if assignment.assignment_type == "conflict":
                ###
                # TODO add more explanation here / return an actual page
                return "nothing to see here (i.e., not conflicting labels and/or no maybe labels). hit back?"
            else:
                #TODO
                assignment.done = controller_globals._check_assignment_done(assignment)
                Session.commit()
                redirect(url(controller="account", action="welcome"))

        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)

        c.cur_lbl = None
        if assignment.assignment_type == "conflict":
            c.cur_lbl = self._get_labels_for_citation(c.cur_citation.id)
            c.reviewer_ids_to_names_d = self._labels_to_reviewer_name_d(c.cur_lbl)
            c.tags = set(self._get_tags_for_citation(c.cur_citation.id))
        else:
            c.tags = self._get_tags_for_citation(c.cur_citation.id, only_for_user_id=user.id)

        # Now get tags for this citation
        # First check to make sure tag_privacy is not 'null' in the database.
        if review.tag_privacy==None:
            review.tag_privacy = False

        if review.tag_privacy:
            # Only get tags that *this* reviewer has created
            c.tag_types = self._get_tag_types_for_review(review_id, only_for_user_id=user.id)
        else:
            # Get tags that anyone in this project has created
            c.tag_types = self._get_tag_types_for_review(review_id)

        # now get any associated notes
        notes = self._get_notes_for_citation(c.cur_citation.id, user.id)
        c.notes = notes

        # These help keep tags public/private, depending on project lead's selection.
        c.tag_privacy = review.tag_privacy
        c.user_id = user.id

        Session.commit()
        return render("/screen.mako")

    @ActionProtector(not_anonymous())
    def update_tags(self, study_id, tag_privacy, assignment_type=None):
        user = self._get_user()

        # get tags for this citation and maintain the tag-privacy setting
        c.tag_privacy = tag_privacy

        if assignment_type=='conflict':
            c.tags = set(self._get_tags_for_citation(study_id))
        else:
            c.tags = self._get_tags_for_citation(study_id, only_for_user_id=user.id)
        return render("/tag_fragment.mako")

    @ActionProtector(not_anonymous())
    def update_tag_types(self, review_id, study_id):
        user = self._get_user()

        # now get tags for this citation
        c.tag_privacy = self._get_review_from_id(review_id).tag_privacy
        c.tags = self._get_tags_for_citation(study_id, only_for_user_id=user.id)
        if c.tag_privacy:
            c.tag_types = self._get_tag_types_for_review(review_id, only_for_user_id=user.id)
        else:
            c.tag_types = self._get_tag_types_for_review(review_id)

        return render("/tag_dialog_fragment.mako")

    @ActionProtector(not_anonymous())
    def get_next_citation_fragment(self, review_id, assignment_id):
        user = self._get_user()
        assignment = self._get_assignment_from_id(assignment_id)
        review = self._get_review_from_id(review_id)

        c.review_id = review_id
        c.review_name = review.name
        c.assignment_id = assignment_id
        c.assignment_type = assignment.assignment_type
        c.assignment = assignment

        # The following help determine which fields of the citation are shown.
        c.show_journal = user.show_journal
        c.show_authors = user.show_authors
        c.show_keywords = user.show_keywords

        # in the case of getting the next citation for cacheing, we
        # respect the user's locks
        c.cur_citation = self._get_next_citation(assignment, review, ignore_my_own_locks=False)

        # but wait -- is the last one currently being screened?
        assignment.done = controller_globals._check_assignment_done(assignment, offset=-1)

        if assignment.done or c.cur_citation is None:
            assignment.done = True
            Session.add(assignment)
            Session.commit()
            return render("/assignment_complete.mako")

        # mark up the labeled terms
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)

        if c.cur_citation is not None:
            print "\n this is the next citation: \n %s \n" % c.cur_citation.title

        c.cur_lbl = None
        if assignment.assignment_type == "conflict":
            c.cur_lbl = self._get_labels_for_citation(c.cur_citation.id)
            c.reviewer_ids_to_names_d =  self._labels_to_reviewer_name_d(c.cur_lbl)

        # now get tags for this citation
        # Make sure tag_privacy is not 'null' in the database.
        if review.tag_privacy==None:
            review.tag_privacy = False

        # You should only see your own citation tags
        c.tags = self._get_tags_for_citation(c.cur_citation.id, only_for_user_id=user.id)

        # Get tag_types by visibility setting
        if review.tag_privacy:
            c.tag_types = self._get_tag_types_for_review(review_id, only_for_user_id=user.id)
        else:
            c.tag_types = self._get_tag_types_for_review(review_id)

        # now get any associated notes
        notes = self._get_notes_for_citation(c.cur_citation.id, user.id)
        c.notes = notes

        # These help in the execution of the tag-privacy option:
        c.tag_privacy = review.tag_privacy
        c.user_id = user.id

        Session.commit()

        return render("/citation_fragment.mako")

    def _labels_to_reviewer_name_d(self, labels):
        reviewer_ids_to_names_d = {}
        for label in labels:
            reviewer_ids_to_names_d[label.user_id] = \
                self._get_username_from_id(label.user_id)
        return reviewer_ids_to_names_d

    def _get_next_citation(self, assignment, review, ignore_my_own_locks=True):
        assignment_id = assignment.id
        assignment_type = assignment.assignment_type
        task_id = assignment.task_id
        num_assigned = assignment.num_assigned
        user = self._get_user()
        user_id = user.id
        project_id = review.id
        next_id = None

        if not ignore_my_own_locks:
            # then we're fetching the *next* citation, so we
            # we may futz with the assignment object a bit (see
            # below). we copy it here to avoid modifying it.
            c.assignment = copy.deepcopy(assignment)


        # if the current assignment is a 'fixed' assignment (i.e.,
        # comprises a finite set of ids to be screened -- an initial round,
        # conflicting round, or assigned assignment) then we pull from the FixedAssignments table
        if assignment_type in ["initial", "conflict"]:
            # in the case of initial assignments, we never remove the citations,
            # thus we need to ascertain that we haven't already screened it
            eligible_pool = self._get_ids_for_task(task_id)
            # a bit worried about runtime here (O(|eligible_pool| x |already_labeled|)).
            # hopefully eligible_pool shrinks as sufficient labels are acquired (and it
            # shoudl always be pretty small for initial assignments).

            if assignment_type=="conflict":
                # the 0th user is the omniscient consensus reviewer,
                # by convention. in the case that we're reviewing conflicts
                # we use this special user.
                reviewer_id = 0
            elif assignment_type=="initial":
                reviewer_id = user_id

            already_labeled = \
                    self._get_already_labeled_ids(review.id, reviewer_id=reviewer_id, assignment_id=assignment_id)

            eligible_pool = [xid for xid in eligible_pool if not xid in already_labeled]
            next_id = None
            # here we handle the case of fetching the *next* citation, i.e.,
            # for cacheing the next example. we assume that if ignore_my_own_locks
            # is False, then we are grabbing the *next* eligible citation in line
            # and return this, rather than the first available citation
            offset = 0 if ignore_my_own_locks else 1

            if len(eligible_pool)>offset:
                next_id = eligible_pool[offset]

        # Else we are in 'perpetual' or 'assigned' assignment type
        elif assignment_type in ["perpetual", "assigned"]:
            if assignment_type=="assigned":
                already_labeled_by_me = controller_globals._get_labels_by_assignment(assignment)
                if len(already_labeled_by_me)==num_assigned:
                    return None
                # If we are in the process of fetching the 'next' citation
                # then we need to stop one (1) short of num_assigned.
                # ignore_my_own_locks is false in the case that we are caching
                # the 'next' citation
                if not ignore_my_own_locks:
                    if len(already_labeled_by_me)+1==num_assigned:
                        return None

            priority = self._get_next_priority(review, assignment, ignore_my_own_locks=ignore_my_own_locks)

            if priority is not None:
                # 8/29/11 -- remedy for issue wherein antiquated
                # (deployed) code was not popping priority items
                # after a sufficient number of labels were acquired
                # (i.e,. after they were screened). this checks that this
                # isn't the case here, and removes the priority object
                # if so. may went to drop this down the road, it's
                # technically unnecessary with the current codebase (
                # in which priority objects are dropped at label time correctly)
                next_id = priority.citation_id
                num_times_to_label = 2 if review.screening_mode == "double" else 1
                while (priority.num_times_labeled >= num_times_to_label):
                    Session.delete(priority)
                    Session.commit()
                    priority = self._get_next_priority(review, assignment, ignore_my_own_locks=ignore_my_own_locks)

                next_id = priority.citation_id
                ## 'check out' / lock the citation
                priority.is_out = True
                priority.locked_by = request.environ.get('repoze.who.identity')['user'].id
                priority.time_requested = datetime.datetime.now()
                Session.commit()

        # we want to increment the 'num done so far' field in the
        # case that we're queueing up the *next* citation to label, because
        # when this is shown, one additional study will have been labeled.
        # we again assume that if we're *not* ignoring our own locks
        # then we are fetching the *next* citation in line
        if not ignore_my_own_locks:
            c.assignment.done_so_far += 1

        print "DONE SO FAR %s and ignore_my_own_locks is %s" % (c.assignment.done_so_far, ignore_my_own_locks)
        return None if next_id is None else self._get_citation_from_id(next_id)

    @ActionProtector(not_anonymous())
    def edit_tags(self, review_id, assignment_id):
        user = self._get_user()

        tag_q = Session.query(model.TagType)
        tags = None

        # fix for issue #35: allow admins to edit everyone's
        #   tags
        if self._current_user_leads_review(review_id):
            tags = tag_q.filter(model.TagType.project_id == review_id).all()
        else:
            tags = tag_q.filter(
                and_(model.TagType.project_id == review_id,\
                     model.TagType.creator_id == user.id
                     )).all()
        c.tags = tags
        c.assignment_id = assignment_id
        c.review_id = review_id
        return render("/reviews/edit_tags.mako")

    @ActionProtector(not_anonymous())
    def edit_tag(self, tag_id, assignment_id):
        tag_q = Session.query(model.TagType)
        c.tag = tag_q.filter(model.TagType.id == tag_id).one()

        c.assignment_id = assignment_id
        return render("/reviews/edit_tag_fragment.mako")

    @ActionProtector(not_anonymous())
    def edit_tag_text(self, id):
        user = self._get_user()

        tag_q = Session.query(model.TagType)
        tag = tag_q.filter(model.TagType.id == id).one()
        if user.id == tag.creator_id or self._current_user_leads_review(tag.project_id):
            tag.text = request.params['new_text']
            Session.commit()


    @ActionProtector(not_anonymous())
    def delete_tag(self, tag_id, assignment_id):
        user = self._get_user()

        tag_q = Session.query(model.TagType)
        tag = tag_q.filter(model.TagType.id == tag_id).one()
        review_id = tag.project_id
        if user.id == tag.creator_id:
            Session.delete(tag)
            Session.commit()

            # also delete all the tag objects associated
            # with this TagType
            tag_obj_q = Session.query(model.Tag)
            tags_of_this_type = tag_obj_q.filter(model.Tag.tag_id == tag_id).all()
            for tag_obj in tags_of_this_type:
                Session.delete(tag_obj)
            Session.commit()

            redirect(url(controller="review", action="edit_tags", \
                            review_id=review_id, assignment_id=assignment_id))
        else:
            return "tsk, tsk."


    @ActionProtector(not_anonymous())
    def review_terms(self, id, assignment_id=None):
        review_id = id
        current_user = request.environ.get('repoze.who.identity')['user']

        term_q = Session.query(model.LabeledFeature)
        labeled_terms =  term_q.filter(and_(\
                                model.LabeledFeature.project_id == review_id,\
                                model.LabeledFeature.user_id == current_user.id
                         )).all()
        c.terms = labeled_terms
        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name

        # if an assignment id is given, it allows us to provide
        # a 'get back to work' link.
        c.assignment = assignment_id
        if assignment_id is not None:
            c.assignment = self._get_assignment_from_id(assignment_id)

        return render("/reviews/edit_terms.mako")


    @ActionProtector(not_anonymous())
    def filter_labels(self, review_id, assignment_id=None, lbl_filter=None):
        ''' @TODO finish or remove this '''
        current_user = request.environ.get('repoze.who.identity')['user']

        label_q = Session.query(model.Label)
        labels = None
        if lbl_filter in ("included", "excluded", "maybe (?)"):

            lbl_filter_num = {"included":1, "excluded":-1, "maybe (?)":0}[lbl_filter]

            '''
            labels = [label for label in label_q.filter(\
                                   and_(model.Label.project_id == review_id,\
                                        model.Label.user_id == current_user.id),\
                                        model.Label.label == lbl_filter_num)).\
                                            order_by(desc(model.Label.label_last_updated)).all()]
            '''
        c.given_labels = labels
        return render("/reviews/review_labels_fragment.mako")

    @ActionProtector(not_anonymous())
    def review_labels(self, review_id, assignment_id=None, lbl_filter=None):
        current_user = request.environ.get('repoze.who.identity')['user']


        # if an assignment id is given, it allows us to provide a
        # 'get back to work' link/button.
        c.assignment = assignment_id
        if assignment_id is not None:
            c.assignment = self._get_assignment_from_id(assignment_id)

        label_q = Session.query(model.Label)

        already_labeled_by_me = None
        ####
        # issue #36; if this is a fixed assignment (e.g., reviewing maybes, etc.) then
        # we want to only review those labels relevant to this assignment, i.e., labels
        # for citations that are a part of this task

        # TODO 'conflict' is a misnomer; this variety subsumes
        #           both 'conflict' and 'maybes' assignments

        if c.assignment is not None and c.assignment.assignment_type == "conflict":
            already_consensus_labeled = label_q.filter(\
                                          model.Label.assignment_id == c.assignment.id).all()
            already_labeled_by_me = already_consensus_labeled

        else:
            # otherwise, pull all labels from the current reviewer associated
            # with the given review
            already_labeled_by_me = [label for label in label_q.filter(\
                                   and_(model.Label.project_id == review_id,\
                                        model.Label.user_id == current_user.id)).\
                                            order_by(desc(model.Label.label_last_updated)).all()]


        c.given_labels = already_labeled_by_me
        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name

        # now get the citation objects associated with the given labels
        c.citations_d = {}
        for label in c.given_labels:
            c.citations_d[label.study_id] = self._get_citation_from_id(label.study_id)


        return render("/reviews/review_labels.mako")

    @ActionProtector(not_anonymous())
    def show_labeled_citation(self, review_id, citation_id, assignment_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        c.review_id = review_id
        review = self._get_review_from_id(review_id)
        c.review_name = review.name

        citation_q = Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.id == citation_id).one()
        # mark up the labeled terms
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)

        # issue #36 -- making label reviewing more intuitive
        assignment = self._get_assignment_from_id(assignment_id)
        c.assignment_type = assignment.assignment_type
        c.consensus_review = False

        if c.assignment_type == "conflict":
            # then the assumption is that we're reviewing the labels provided
            # by the 'consensus_user'
            c.consensus_review = True

            # we return the single result in a list to make life easier on the client
            # side; this way, the code doesn't care if it's reviewing a consensus
            # label or showing a label with conflicts (multiple labels) -- it
            # behaves the same.
            c.cur_lbl = [self._get_one_label(CONSENSUS_USER, citation_id)]

        else:
            # then get the label that the current user gave
            c.cur_lbl = self._get_one_label(current_user.id, citation_id)

        # pass the assignment id back to the client
        c.assignment_id = assignment_id

        # grab the tags for this study:
        # issue #34; blinding screeners to others' tags...

        # First check to make sure tag_privacy is not 'null' in the database.
        if review.tag_privacy==None:
            review.tag_privacy = False

        if review.tag_privacy:
            c.tag_types = self._get_tag_types_for_review(review_id, only_for_user_id=current_user.id)
        else:
            c.tag_types = self._get_tag_types_for_review(review_id)

        c.tags = None
        # ... unless either we're in review conflicts mode
        #if (c.assignment_type == "conflict") or (not review.tag_privacy):
        if c.assignment_type=="conflict":
            c.tags = self._get_tags_for_citation(citation_id)
        else:
            c.tags = self._get_tags_for_citation(citation_id, only_for_user_id=current_user.id)

        # also grab the notes
        # @TODO what should we show for notes in the case of conflict mode,
        #   i.e., if multiple users have made notes..??
        c.notes = self._get_notes_for_citation(c.cur_citation.id, current_user.id)

        user = controller_globals._get_user_from_email(current_user.email)
        # Need the above line because the first line of this function gives
        #   a model.auth.User object
        # as opposed to
        #   a model.User object (which is what I need)

        # The following help determine which fields of the citation are shown.
        c.show_journal = user.show_journal
        c.show_authors = user.show_authors
        c.show_keywords = user.show_keywords

        # These help keep tags public/private, depending on project lead's selection:
        c.tag_privacy = review.tag_privacy
        c.user_id = user.id

        return render("/screen.mako")

    @ActionProtector(not_anonymous())
    def create_assignment(self, id):
        assign_to = request.params.getall("assign_to")
        due_date = request.params['due_date']
        #p_rescreen = float(request.params['p_rescreen'])

        # Validate parameters
        if assign_to==[]:
            self._set_flash_redirect(
                    "You did not choose a user to assign a task to. Please correct and try again",
                     url(controller="review", action="assignments", id=id))

        if not due_date=="":
            try:
                m,d,y = [int(x) for x in request.params['due_date'].split("/")]
                due_date = datetime.date(y,m,d)
            except:
                self._set_flash_redirect(
                        "Problem with due date format. Please correct and try again.",
                         url(controller="review", action="assignments", id=id))
        else:
            due_date = None

        try:
            n_assigned = int(request.params['n'])
        except ValueError as e:
            self._set_flash_redirect(
                    "Invalid value for number of citations assigned. Please correct and try again",
                    url(controller="review", action="assignments", id=id))

        if n_assigned<=0:
            self._set_flash_redirect(
                    "Please choose an integer greater than 0 for number of citations for each assignee to screen.",
                     url(controller="review", action="assignments", id=id))

        citations_cnt = len(self._get_citations_for_review(id))

        if n_assigned > citations_cnt:
            self._set_flash_redirect(
                    "You cannot assign more citations to a user than the total number of citations in the project (" + str(citations_cnt) + ")",
                     url(controller="review", action="assignments", id=id))

        task = model.Task()
        task.project_id = id
        task.task_type = "assigned"
        task.num_assigned = n_assigned

        Session.add(task)
        Session.commit()

        assign_to_ids = [self._get_id_from_username(username) for username in assign_to]
        for reviewer_id in assign_to_ids:
            new_assignment = model.Assignment()
            new_assignment.project_id = id
            new_assignment.user_id = reviewer_id
            new_assignment.task_id = task.id
            new_assignment.done_so_far = 0
            new_assignment.date_assigned = datetime.datetime.now()
            new_assignment.date_due = due_date
            new_assignment.done = False
            new_assignment.num_assigned = n_assigned
            #new_assignment.p_rescreen = p_rescreen
            new_assignment.assignment_type = 'assigned'
            Session.add(new_assignment)

        Session.commit()

        redirect(url(controller="review", action="assignments", id=id))

    def _set_flash_redirect(self, msg, url):
        session['flash'] = msg
        session.save()
        redirect(url)


    def _get_priority_for_citation_review(self, citation_id, review_id):
        priority_q = Session.query(model.Priority)
        p_for_cit_review =  priority_q.filter(and_(\
                                model.Priority.project_id == review_id,\
                                model.Priority.citation_id == citation_id,\
                         )).one()
        return p_for_cit_review

    def _join_review(self, review_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        ###
        # this is super-hacky, but there was a bug that was causing
        # the current_user object to be None for reasons I cannot
        # ascertain. refreshing the page inexplicably works; hence we
        # do it here. need to test this further.
        ####
        if current_user is None:
            return self._join_review(review_id)

        user = controller_globals._get_user_from_email(current_user.email)

        # first, make sure this person isn't already in this review.
        #user_projs = Session.query(model.User).\
        #        filter(model.User.id == current_user.id).\
        #        filter(model.User.projects.any(id=review_id)).all()
        project = Session.query(model.Project).filter_by(id=review_id).one()
        user_projs = user.member_of_projects

        if project not in user_projs:
            # we only add them if they aren't already a part of the review.
            project.members.append(user)
            Session.add(project)
            Session.commit()

            # now we check what type of screening mode we're using
            review = self._get_review_from_id(review_id)
            if review.screening_mode in (u"single", u"double"):
                # then we automatically add a `perpetual' assignment
                self._assign_perpetual_task(user.id, review.id)

            # assign any initial tasks for this review to the joinee.
            self._assign_initial_tasks(user.id, review.id)
            return True
        return False

    def _clear_all_my_locks(self, review_id):
        me = self._get_user().id
        priority_q = Session.query(model.Priority)
        locked_priorities =  priority_q.filter(and_(\
                                    model.Priority.project_id == review_id,\
                                    model.Priority.locked_by == me)).all()
        self._unlock_priorities(locked_priorities)

    def _clear_all_locks(self, project_id):
        priority_q = Session.query(model.Priority)
        locked_priorities =  priority_q.filter(model.Priority.project_id == project_id).all()
        self._unlock_priorities(locked_priorities)

    def _unlock_priorities(self, listof_Priority):
        print "unlocking %s priorities" % len(listof_Priority)
        for p in listof_Priority:
            p.is_out = False
            p.locked_by = None
            Session.add(p)
        Session.commit()

    def _get_next_priority(self, review, assignment, ignore_my_own_locks=True):
        '''
        returns citation ids to be screened for the specified
        review, ordered by their priority (in the priority table).
        this is effectively how AL is implemented in our case --
        we assume the table has been sorted/ordered by some
        other process.

        this will not return ids for instances that are
        currently being labeled, with the exception that
        if ignore_my_own_locks is True, then citations currently
        locked by the current user *will* be returned; if this is
        False, these locks will be respected.
        '''
        review_id = review.id
        me = request.environ.get('repoze.who.identity')['user'].id
        project_member_count = len(review.members)
        assignment_type = assignment.assignment_type
        screening_mode = review.screening_mode
        times_to_screen = {'single': 1, 'double': 2, 'advanced': 1}[screening_mode]


        # jjap 2014-04-04: Decision was made to give priority strictly by priority
        #                  position. Do not need to look for priority item with no
        #                  labels yet
        # This finds the next priority that no one has screened
        #ranked_priorities_q = Session.query(model.Priority).\
        #        outerjoin(model.Label, model.Priority.citation_id==model.Label.study_id).\
        #        filter(model.Priority.project_id==review_id).\
        #        filter(model.Label.user_id==None).\
        #        order_by(asc(model.Priority.priority)).\
        #        limit(project_member_count*10)

        #ranked_priorities = ranked_priorities_q.all()

        # if none were found then we get the next priority that this user hasn't screened
        # and does not have the required number of labels (project-wide) yet.
        #if len(ranked_priorities)==0:

        # in sql this is what we want:
        # SELECT priorities.*,lbl_cnt.* FROM priorities left JOIN
        #    (  SELECT     study_id, user_id, count(*) AS label_count
        #       FROM       labels
        #       WHERE      project_id=1
        #       GROUP BY   study_id
        #    ) AS lbl_cnt
        # ON            priorities.citation_id=lbl_cnt.study_id
        # WHERE         priorities.project_id=1
        # AND          (lbl_cnt.user_id != 1 OR lbl_cnt.user_id is NULL)
        # AND           COALESCE(lbl_cnt.label_count, 0) < 2
        # ORDER BY      priorities.priority;



        inner_query = Session.query(model.Label.study_id, model.Label.user_id, func.count('*').\
                                    label('label_count')).\
                            filter(model.Label.project_id==review_id).\
                            group_by(model.Label.study_id).\
                            subquery()

        ranked_priorities_q = Session.query(model.Priority).\
                                    outerjoin(inner_query, model.Priority.citation_id==inner_query.c.study_id).\
                                    filter(model.Priority.project_id==review_id).\
                                    filter(or_(inner_query.c.user_id!=me, inner_query.c.user_id==None)).\
                                    filter(or_(inner_query.c.label_count==None, inner_query.c.label_count<times_to_screen)).\
                                    order_by(asc(model.Priority.priority)).\
                                    limit(project_member_count*10)

        ranked_priorities = ranked_priorities_q.all()

        # now filter the priorities, excluding those that are locked
        # note that we also will remove locks here if a citation has
        # been out for > 2 hours.
        EXPIRE_TIME = 3600 # 3600 *seconds*: i.e., 1 hours

        count = 0
        for priority in ranked_priorities:
            print "\n\n on priority: %s " % count
            print "associated citation is: %s" % priority.citation_id
            print "citation priority is: %s" % priority.priority
            print "priority is_out? %s" % priority.is_out
            print "locked by me? %s" % (priority.locked_by==me)
            print "ignore_my_own_locks? %s" % ignore_my_own_locks
            #if priority.citation_id not in already_labeled_by_me:
            if priority.is_out:
                # priority is out for screening
                if priority.locked_by != me:
                    # currently locked by someone else; here we check
                    # if the lock should be 'expired'
                    td = datetime.datetime.now()-priority.time_requested
                    time_locked = (td).seconds + (td).days*86400
                    if time_locked > EXPIRE_TIME:
                        priority.is_out = False
                        priority.locked_by = None
                        Session.commit()
                        return priority
                elif ignore_my_own_locks:
                    # then *the current user* has a lock on this priority
                    # we ignore this (and return the priority object anyway)
                    # iff ignore_my_own_locks is true; otherwise, we refuse
                    # to return this. this should be set to false, for example,
                    # when fetching the next citation to cache
                    if priority.citation_id not in already_labeled_by_me:
                        return priority
            else:
                # priority is not locked and we haven't screened the associated
                # citation
                print "(regular) returning priority with citation_id %s" % \
                                         priority.citation_id
                return priority
            count+=1

        # this person has nothing more to do!
        return None

    def _get_initial_task_for_review(self, review_id):
        task_q = Session.query(model.Task)
        # there should only be one of these!

        init_task = task_q.filter(and_(\
                            model.Task.project_id == review_id,\
                            model.Task.task_type == "initial")).all()
        if len(init_task) == 0:
            return False # no initial task for this review
        # really there should only be one!
        return init_task[0]

    def _get_tag_id(self, review_id, text):
        tag_q = Session.query(model.TagType)

        tag_type = tag_q.filter(and_(
                model.TagType.project_id == review_id,
                model.TagType.text == text)).all()[0]
        return tag_type.id

    def _get_tags_for_citation(self, citation_id, texts_only=True, only_for_user_id=None):

        tag_q = Session.query(model.Tag)
        tags = None
        if only_for_user_id:
            # then filter on the study and the user
            tags = tag_q.filter(and_(\
                    model.Tag.citation_id == citation_id,\
                    model.Tag.creator_id == only_for_user_id)).all()
        else:
            # all tags for this citation, regardless of user
            tags = tag_q.filter(model.Tag.citation_id == citation_id).all()

        if texts_only:
            return self._tag_ids_to_texts([tag.tag_id for tag in tags])
        return tags

    def _tag_ids_to_texts(self, tag_ids):
        return [self._text_for_tag(tag_id) for tag_id in tag_ids]

    def _text_for_tag(self, tag_id):
        tag_type_q = Session.query(model.TagType)
        tag_obj = tag_type_q.filter(model.TagType.id == tag_id).one()
        return tag_obj.text

    def _get_tag_types_for_citation(self, citation_id, objects=False):
        tags = self._get_tags_for_citation(citation_id)
        # now map those types to names
        tag_type_q = Session.query(model.TagType)
        tags = []

        for tag in tags:
            tag_obj = tag_type_q.filter(model.TagType.id == tag.tag_id).one()

            if objects:
                tags.append(tag_obj)
            else:
                tags.append(tag_obj.text)

        return tags

    def _get_tag_types_for_review(self, review_id, only_for_user_id=None):
        tag_q = Session.query(model.TagType)

        if only_for_user_id:
            tag_types = tag_q.filter(and_(\
                        model.TagType.project_id == review_id,\
                        model.TagType.creator_id == only_for_user_id
                )).all()
        else:
            tag_types = tag_q.filter(model.TagType.project_id == review_id).all()
        return [tag_type.text for tag_type in tag_types]

    def _get_ids_for_task(self, task_id):
        '''
        returns all the citation ids associated with the
        given task -- note that we order these by the
        citation id (somewhat arbitrarily!)
        '''
        q = Session.query(model.Task)
        citations = q.filter_by(id=task_id).one().citations
        eligible_ids = [cite.id for cite in citations]
        #eligible_ids.sort()
        eligible_ids = sorted(eligible_ids)
        return eligible_ids

    def _get_already_labeled_ids(self, review_id, reviewer_id=None, assignment_id=None):
        '''
        returns a list of citation ids corresponding to those citations that
        the current reviewer (or the reviewer specified by user_id) has labeled
        for the specified review.
        '''
        label_q = Session.query(model.Label)

        if reviewer_id is None:
            # This is to find all labels across all screeners within the project
            already_labeled_ids = [label.study_id for label in label_q.filter(model.Label.project_id == review_id).all()]
        elif assignment_id is None:
            # This is to find all labels for a specific user
            already_labeled_ids = [label.study_id for label in label_q.filter(and_(\
                                                        model.Label.project_id==review_id,\
                                                        model.Label.user_id==reviewer_id)).all()]
        else:
            # This is to find all labels for a specific user and assignment
            already_labeled_ids = [label.study_id for label in label_q.filter(and_(\
                                                        model.Label.project_id==review_id,\
                                                        model.Label.user_id==reviewer_id,\
                                                        model.Label.assignment_id==assignment_id)).all()]


        return list(set(already_labeled_ids))

    def _get_participants_for_review(self, project_id):
        project = Session.query(model.Project).filter(model.Project.id == project_id).one()
        members = project.members
        return members

    def _get_username_from_id(self, id):
        if id == CONSENSUS_USER:
            return "consensus"
        user_q = Session.query(model.User)
        return user_q.filter(model.User.id == id).one().username

    def _get_id_from_username(self, username):
        user_q = Session.query(model.User)
        return user_q.filter(model.User.username == username).one().id

    def _get_review_from_id(self, review_id):
        review_q = Session.query(model.Project)
        return review_q.filter(model.Project.id == review_id).one()

    def _get_predictions_for_review(self, review_id):
        prediction_q = Session.query(model.Prediction)
        predictions_for_review = prediction_q.filter(model.Prediction.project_id==review_id).all()
        return predictions_for_review

    def _do_predictions_exist_for_review(self, review_id):
        pred_status_q = Session.query(model.PredictionsStatus)
        pred_status_of_review = \
            pred_status_q.filter(model.PredictionsStatus.project_id == review_id).all()
        if len(pred_status_of_review) > 0 and pred_status_of_review[0].predictions_exist:
            return True
        return False

    def _get_citations_for_review(self, review_id):
        citation_q = Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.project_id == review_id).all()
        return citations_for_review

    def _get_citation_from_id(self, citation_id):
        citation_q = Session.query(model.Citation)
        return citation_q.filter(model.Citation.id == citation_id).first()

    def _get_assignment_from_id(self, assignment_id):
        assignment_q = Session.query(model.Assignment)
        try:
            return assignment_q.filter(model.Assignment.id == assignment_id).one()
        except:
            return None

    def _create_perpetual_task_for_review(self, review_id):
        new_task = model.Task()
        new_task.project_id = review_id
        new_task.task_type = u"perpetual"
        new_task.num_assigned = -1 # this is meaningless for `perpetual' assignments
        Session.add(new_task)
        Session.commit()
        return new_task

    def _set_initial_screen_size_for_review(self, review, n):
        '''
        sets the initial screening size for the review specified by
        the review_id to n. if n is smaller than the original initial
        round size, then studies from the allocated FixedTask will be
        removed. if it's bigger, then studies will be added.

        --- warning -- this is typically an 'expensive' routine
        '''

        if n == review.initial_round_size:
            # nothing to do
            return None


        cur_init_task = self._get_initial_task_for_review(review.id)

        if not cur_init_task:
            # if there isn't an initial task already, create one
            # here comprising 1 abstract
            self._create_initial_task_for_review(review.id, 0)
            cur_init_task = self._get_initial_task_for_review(review.id)
            # now we need to assign the task to every participant
            participants = self._get_participants_for_review(review.id)

            for participant in participants:
                self._assign_task(participant.id, cur_init_task, review.id)

        if n < review.initial_round_size:
            num_to_remove = review.initial_round_size - n
            task_citations_to_remove = cur_init_task.citations[-num_to_remove:]

            # this is for re-inserting entries into the priority queue
            cur_max_priority = self._get_max_priority(review.id)+1

            if len(task_citations_to_remove) > 0:
                for citation in task_citations_to_remove:
                    cur_init_task.citations.remove(citation)
                    Session.add(cur_init_task)
                    Session.commit()
                    ###
                    # crucial -- we need to add this guy back onto
                    # the priority queue!
                    #
                    # TODO (maybe?) right now, we're setting the num_times_labeled
                    #       field to 0. but it's possible (though unlikely?) that someone
                    #       (or multiple people!) have, in fact, labeled this as part of the
                    #       initial round. this is only a 'problem' if someone sets the
                    #       the initial round, screens screens screens, then re-sets the
                    #       the initial round to something smaller such that they've already
                    #       screened beyond the latter number. I don't know why someone would
                    #       do this. but in this case, they would end up re-screening some abstracts
                    #       from the original initial round.
                    xml_to_sql.insert_priority_entry(\
                                review.id, citation.id, \
                                    cur_max_priority, num_times_labeled=0)
                    cur_max_priority += 1

        else:
            # then n > review.init_round_size: we have to add
            # citations to the fixed_task.

            # Let's find all the citations that are currently not associated with a task
            citations_not_tasked = Session.query(model.Citation).\
                    filter(model.Citation.project_id == review.id).\
                    filter(~model.Citation.tasks.any()).all()

            # Add random citations to task associations via citations_tasks_table
            num_to_add = min(n-review.initial_round_size, len(citations_not_tasked))
            shuffle(citations_not_tasked)

            # Use extend here instead of append to Task.citations list or else we end up
            # with something like [a, b, [c, d, e]]. We could have used itertools to chain
            # the lists, but I think this is simpler, ergo more pythonic
            cur_init_task.citations.extend(citations_not_tasked[:num_to_add])
            Session.add(cur_init_task)
            Session.commit()

            # Additional citations have been associated with the initial task.
            # Time to remove them from the priority queue
            for citation in citations_not_tasked[:num_to_add]:
                self._remove_citation_from_priority_queue(citation.id)

        # update the assignment objects
        init_assignments_for_tasks = \
                self._get_assignments_associated_with_task(cur_init_task.id)

        for assignment in init_assignments_for_tasks:
            assignment.done = (assignment.done_so_far >= n)
            assignment.num_assigned = n
            Session.commit()


        # update the initial task object, too
        initial_task = self._get_initial_task_for_review(review.id)
        initial_task.num_assigned = n
        Session.commit()

        # update the assignment object
        initial_task = self._get_initial_task_for_review(review.id)
        initial_task.num_assigned = n
        model.Session.commit()


        # finally, update the initial round size field
        # onthe review object
        review.initial_round_size = n
        Session.commit()

    def _get_assignments_associated_with_task(self, task_id):
        assignment_q = Session.query(model.Assignment)
        return assignment_q.filter(model.Assignment.task_id == task_id).all()

    def _remove_citation_from_priority_queue(self, citation_id):
        priority_q = Session.query(model.Priority)
        priority_entries = priority_q.filter(model.Priority.citation_id == citation_id).all()
        for pe in priority_entries:
            Session.delete(pe)
        Session.commit()

    def _create_initial_task_for_review(self, project_id, n):
        '''
        picks a random set of the citations from the specified review and
        adds them into the citations_tasks table -- participants in this
        review should subsequently be tasked with Assignments that reference this.
        '''

        # Retrieve a list of all citation objects associated with this project id
        citation_objs_lst = self._get_citations_for_review(project_id)

        # Let's shuffle this list and grab what we need
        shuffle(citation_objs_lst)
        citations_for_initial_task = citation_objs_lst[:n]

        # create an entry in the Assignments table
        init_task = model.Task()
        init_task.task_type = "initial"
        init_task.project_id = project_id
        init_task.num_assigned = n

        # Use SQLAlchemy's ORM model to add citations to the task
        for citation in citations_for_initial_task:
            init_task.citations.append(citation)

        Session.add(init_task)
        Session.commit()

        # Remove ID's from the priority queue
        for citation_id in [cite.id for cite in citations_for_initial_task]:
            priority_q = Session.query(model.Priority)
            priority_entry = priority_q.filter(model.Priority.citation_id == citation_id).one()
            Session.delete(priority_entry)
            Session.commit()

    def _assign_initial_tasks(self, user_id, review_id):
        task_q = Session.query(model.Task)
        initial_tasks_for_review = task_q.filter(and_(\
                        model.Task.project_id == review_id,
                        model.Task.task_type == u"initial"
                    )).all()

        for task in initial_tasks_for_review:
            self._assign_task(user_id, task, review_id)

    def _get_perpetual_assignments_for_review(self, review_id):
        assignment_q =  Session.query(model.Assignment)
        perpetual_assignments = \
            assignment_q.filter(and_(model.Assignment.project_id == review_id,\
                                     model.Assignment.assignment_type == u"perpetual")).all()
        return perpetual_assignments

    def _assign_perpetual_task(self, user_id, review_id):
        '''
        If there is a perpetual task associated with the
        given review, it assigns it to user_id.
        '''
        perpetual_tasks_for_review = self._get_perpetual_tasks_for_review(review_id)

        if len(perpetual_tasks_for_review) > 0:
            # note that we assume there's only *one* perpetual
            # task per review, or in any case we ignore any
            # others.
            self._assign_task(user_id, perpetual_tasks_for_review[0], \
                                review_id)

    def _get_perpetual_tasks_for_review(self, review_id):
        task_q = Session.query(model.Task)

        perpetual_tasks_for_review = task_q.filter(and_(\
                        model.Task.project_id == review_id,
                        model.Task.task_type == u"perpetual"
                    )).all()
        return perpetual_tasks_for_review

    def _assign_task(self, user_id, task, review_id, due_date=None):
        assignment = model.Assignment()
        assignment.project_id = review_id
        assignment.user_id = user_id
        assignment.task_id = task.id
        if due_date is not None:
            assignment.due_date = due_date
        assignment.date_assigned = datetime.datetime.now()
        assignment.done_so_far = 0
        ##
        # note that we keep these two fields
        # in the assignment table, even though
        # they are redundant with the entries in
        # the task table. we do this for convienence.
        assignment.num_assigned = task.num_assigned
        assignment.assignment_type = task.task_type

        Session.add(assignment)
        Session.commit()

    def _mark_up_citation(self, review_id, citation):
        global COLOR_D
        # pull the labeled terms for this review
        labeled_term_q = Session.query(model.LabeledFeature)
        reviewer_id = request.environ.get('repoze.who.identity')['user'].id
        labeled_terms = labeled_term_q.filter(and_(\
                            model.LabeledFeature.project_id == review_id,\
                            model.LabeledFeature.user_id == reviewer_id)).all()
        citation.marked_up_title = citation.title
        citation.marked_up_abstract = citation.abstract
        citation.marked_up_keywords = citation.keywords

        # sort the labeled terms by length (inverse)
        labeled_terms.sort(cmp=lambda x,y: len(y.term) - len(x.term))

        # strip these to sanitize input to RE.
        # note that this means users cannot provide REs
        # themselves.
        meta_chars = ". ^ $ * + ? { } [ ] \ | ( )".split(" ")

        m_upper = MarkUpper(labeled_terms)

        citation.marked_up_title = m_upper.markup(citation.marked_up_title)

        if citation.marked_up_abstract is not None:
            # ... and in the abstract text
            citation.marked_up_abstract = m_upper.markup(citation.marked_up_abstract)
        else:
            citation.marked_up_abstract = ""

        if citation.marked_up_keywords is not None:
            # ... and in the abstract keywords
            citation.marked_up_keywords = m_upper.markup(citation.marked_up_keywords)

        else:
            citation.marked_up_keywords = ""

        citation.marked_up_title = literal(citation.marked_up_title)
        citation.marked_up_abstract = literal(citation.marked_up_abstract)
        citation.marked_up_keywords = literal(citation.marked_up_keywords)

        return citation

    def _get_user(self):
        current_user = request.environ.get('repoze.who.identity')['user']
        return controller_globals._get_user_from_email(current_user.email)

#    def _is_assignment_done(self, review, assignment):
#        user = self._get_user()
#        review_id = review.id
#        reviewer_id = user.id
#
#        if assignment.assignment_type in ['initial', 'conflict']:
#            # in the case of initial assignments, we never remove the citations,
#            # thus we need to ascertain that we haven't already screened it
#            eligible_pool = self._get_ids_for_task(assignment.task_id)
#            reviewer_id = None
#            if assignment.assignment_type == "conflict":
#                # the 0th user is the omniscient consensus reviewer,
#                # by convention. in the case that we're reviewing conflicts
#                # we use this special user.
#                reviewer_id = 0
#
#            already_labeled = self._get_already_labeled_ids(review.id, reviewer_id=reviewer_id)
#            eligible_pool = [xid for xid in eligible_pool if not xid in already_labeled]
#            return len(eligible_pool) == 0
#        elif assignment.assignment_type in ['perpetual', 'assigned']:
#            citations_in_priority_queue = self._get_citations_in_priority_queue(review)
#            if len(citations_in_priority_queue) == 0:
#                return True
#            else:
#                labels= self._get_labels_for_user(review, assignment, user)
#                labeled_citation_ids = [label.study_id for label in labels]
#                citations_in_priority_queue = [cit.id for cit in citations_in_priority_queue]
#                citations_not_yet_labeled = [x for x in citations_in_priority_queue if x not in labeled_citation_ids]
#                if len(citations_not_yet_labeled) == 0:
#                    return True
#                else:
#                    return sorted(labeled_citation_ids) == sorted(citations_in_priority_queue)

    def _get_citations_in_priority_queue(self, project):
        Session.commit()
        priority_q = Session.query(model.Priority)
        priority_list = priority_q.filter_by(project_id=project.id).all()
        return priority_list

    def _get_labels_for_user(self, project, assignment, user):
        """Returns a user's list of labels for this assignment"""
        return Session.query(model.Label).filter(and_(model.Label.user_id==user.id,
                                                      model.Label.project_id==project.id,
                                                      model.Label.assignment_id==assignment.id)).all()

    def _get_assignment_completion_status(self, assignments):
        """Returns how many labels have been recorded for each assignment ID.

        The returned object is a dictionary with the assignment ID as key
        and the number of citations screened for this assignment as the
        value

        """

        status_summary = {}

        for a in assignments:
            project_id = a.project_id
            user_id = a.user_id
            lof_labels_for_assignment = self._get_users_labels_for_assignment(project_id,
                                                                              user_id,
                                                                              a.id)
            status_summary[a.id] = len(lof_labels_for_assignment)
        return status_summary

    def _get_users_labels_for_assignment(self, project_id, user_id, assignment_id):
        """Returns a user's list of labels across a specific project"""
        labels_q = Session.query(model.Label)
        labels = labels_q.filter_by(project_id=project_id,
                                    user_id=user_id,
                                    assignment_id=assignment_id).all()
        return labels

    def _update_done_so_far_count(self, assignment):
        user = self._get_user()
        labels = self._get_users_labels_for_assignment(assignment.project_id,
                                                       user.id,
                                                       assignment.id)
        assignment.done_so_far = len(labels)
        Session.add(assignment)
        Session.commit()
        return False

    def _get_one_label(self, user_id, citation_id):
        label_q = Session.query(model.Label)
        try:
            label_q_result = label_q.filter(and_(model.Label.study_id == citation_id, model.Label.user_id == user_id)).one()
        except MultipleResultsFound, e:
            label_q_result = label_q.filter(and_(model.Label.study_id == citation_id, model.Label.user_id == user_id)).order_by(model.Label.id.desc()).first()
        return label_q_result
