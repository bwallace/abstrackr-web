import pdb
import os
import shutil
import datetime
import random
import re
import time
from operator import itemgetter
import csv
import random
import string
import smtplib


from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
import abstrackr.controllers.controller_globals as controller_globals
from controller_globals import * # shared variables
import logging
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector
from abstrackr.lib.base import BaseController, render
import abstrackr.model as model
from abstrackr.lib import xml_to_sql
from sqlalchemy import or_, and_, desc, func
from abstrackr.lib.helpers import literal

import pygooglechart
from pygooglechart import PieChart3D, StackedHorizontalBarChart, StackedVerticalBarChart
from pygooglechart import Axis

# this is the path where uploaded databases will be written to
permanent_store = "/uploads/"

log = logging.getLogger(__name__)

### for term highlighting
NEG_C = "#7E2217"
STRONG_NEG_C = "#FF0000"
POS_C = "#4CC417"
STRONG_POS_C = "#347235"
COLOR_D = {1:POS_C, 2:STRONG_POS_C, -1:NEG_C, -2:STRONG_NEG_C}

import subprocess

class ReviewController(BaseController):

    @ActionProtector(not_anonymous())
    def create_new_review(self):
        c.review_count = "%s" % model.meta.Session.query(func.count(model.Review.review_id)).scalar()
        return render("/reviews/new.mako")
    
    @ActionProtector(not_anonymous())
    def predictions_about_remaining_citations(self, id):
        if not self._current_user_leads_review(id):
            return "yeah, I don't think so."
        
        predictions_q = model.meta.Session.query(model.Prediction)
        #pdb.set_trace()
        c.predictions_for_review =  predictions_q.filter(model.Prediction.review_id == id).all()
        c.probably_included = len([x for x in c.predictions_for_review if x.num_yes_votes > 5])
        
        c.frequencies = [] # This is the list of frequencies of the number of 'yes' votes.
        for i in xrange(12):
            c.frequencies.append( len([x for x in c.predictions_for_review if x.num_yes_votes==i]) )
        
        c.review_being_predicted = self._get_review_from_id(id).name
        
        return render("/reviews/remaining_reviews.mako")
    
    
    @ActionProtector(not_anonymous())
    def create_review_handler(self):
        # first upload the xml file
        xml_file = request.POST['db']

        local_file_path = "." + os.path.join(permanent_store, 
                          xml_file.filename.lstrip(os.sep))
        local_file = open(local_file_path, 'w')
        shutil.copyfileobj(xml_file.file, local_file)
        xml_file.file.close()
        local_file.close()
        
        new_review = self._make_new_review() # some defaults
        # now pull out user-specified settings
        new_review.name = request.params['name']
        new_review.project_description = request.params['description']
        new_review.sort_by = request.params['order']
        screening_mode_str = request.params['screen_mode']

        new_review.screening_mode = \
                 {"Single-screen":"single", "Double-screen":"double", "Advanced":"advanced"}[screening_mode_str]
        
        if 'init_size' in request.params.keys():
            new_review.initial_round_size = int(request.params['init_size'])
        
        model.Session.add(new_review)
        model.Session.commit()

        # place an entry in the EncodeStatus table
        # for this review -- elsewhere we'll see that 
        # there is an entry in the table that isn't encoded
        # and do so.
        encoded_status = model.EncodeStatus()
        encoded_status.review_id = new_review.review_id
        encoded_status.is_encoded = False
        model.Session.add(encoded_status)

        # also in the PredictionStatus table
        prediction_status = model.PredictionsStatus()
        prediction_status.review_id = new_review.review_id
        prediction_status.predictions_exist = False
        model.Session.add(prediction_status)
        model.Session.commit()
        
        # now parse the uploaded file; dispatch on type
        num_articles = None
        if xml_file.filename.lower().endswith(".xml"):
            print "parsing uploaded xml..."
            num_articles = xml_to_sql.xml_to_sql(local_file_path, new_review)
        elif xml_file.filename.lower().endswith(".ris"):
            print "parsing RIS file..."
            num_articles = xml_to_sql.ris_to_sql(local_file_path, new_review)
        elif xml_to_sql.looks_like_tsv(local_file_path):
            num_articles = xml_to_sql.tsv_to_sql(local_file_path, new_review)
        else:
            print "assuming this is a list of pubmed ids"
            num_articles = xml_to_sql.pmid_list_to_sql(local_file_path, new_review)
        print "done."
        

        if new_review.initial_round_size > 0:
            # make sure they don't specify an initial round size comprising more 
            # articles than are in the review.
            new_review.initial_round_size = min(num_articles, new_review.initial_round_size)
            self._create_initial_task_for_review(new_review.review_id, new_review.initial_round_size)
            
        # if we're single or double- screening, we create a 
        # perpetual task here
        if new_review.screening_mode in (u"single", u"double"):
            self._create_perpetual_task_for_review(new_review.review_id)
            
        # join the person administrating the review to the review.
        self._join_review(new_review.review_id)
        
        c.review = new_review
        c.num_articles = num_articles

        ###
        # here is where we'll want to thread the process of *encoding*
        # the documents comprising the review for consumption by the 
        # machine learning stuff.
        return render("/reviews/review_created.mako")
        
    @ActionProtector(not_anonymous())
    def merge_reviews(self):
        reviews_to_merge = \
            [int(review_id) for review_id in request.params.getall("merge_review")]

        merged_review = self._make_new_review()
        merged_review.name = request.params['name']
        merged_review.project_description = request.params['description']
        merged_review.sort_by = request.params['order']
        screening_mode_str = request.params['screen_mode']
        init_round_size = int(request.params['init_size']) # TODO verify
        

        # TODO make the below dictionary a global!
        merged_review.screening_mode = \
           {"Single-screen":"single", "Double-screen":"double", "Advanced":"advanced"}[screening_mode_str]
        

        model.Session.add(merged_review)
        model.Session.commit()

        # now merge the reviews
        for review_id in reviews_to_merge:
            self._move_review(review_id, merged_review.review_id)
        
        if merged_review.screening_mode in (u"single", u"double"):
            self._create_perpetual_task_for_review(merged_review.review_id)
            # now assign this perpetual task to everyone participating
            # in the merged review
            review_participants = \
               [reviewer.id for reviewer in self._get_participants_for_review(merged_review.review_id)]

            for reviewer_id in review_participants:
                self._assign_perpetual_task(reviewer_id, merged_review.review_id)
        
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
        # now the initial (pilot) round size
        new_init_round_size = int(request.params['init_size']) # TODO verify
        self._set_initial_screen_size_for_review(review, new_init_round_size)

        ###
        # re-prioritization -- BETA
        new_ordering = request.params['order']
        review.sort_by = new_ordering
        model.Session.commit()
        self._re_prioritize(id, new_ordering)

        return self.edit_review(id, message="ok -- review updated.")
        #if init_round_size == cur_init_assignment.
        

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
        priority_q = model.meta.Session.query(model.Priority)
        ranked_priorities =  priority_q.filter(\
                                    model.Priority.review_id == review_id).\
                                    order_by(model.Priority.priority).all() 
                                    
        for priority_obj in ranked_priorities:
            num_lbls = len(self._get_labels_for_citation(priority_obj.citation_id))
            priority_obj.num_times_labeled = num_lbls
            model.Session.commit()

  
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
                    model.Session.commit()
            
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
            
        review.screening_mode = new_screening_mode
        model.Session.commit()    
    
    def _delete_perpetual_assignments_for_review(self, review_id):
        assignment_q = model.meta.Session.query(model.Assignment)     
        perpetual_assignments = \
            assignment_q.filter(and_(model.Assignment.review_id == review.review_id),\
                                     model.Assignment.type == u"perpetual").all()
        for perpetual_assignment in perpetual_assignments:
            model.Session.delete(perpetual_assignment)
            model.Session.commit()

    def _get_max_priority(self, review_id):
        ''' 
        return the highest priority number for the
        specified review.
        '''
        priority_q = model.meta.Session.query(model.Priority)
        priority_objs_for_review = priority_q.filter(model.Priority.review_id == review_id).all()
        priorities = [p.priority for p in priority_objs_for_review]
        if len(priorities) == 0:
            return 0
        return max(priorities)
                
    def _citations_for_review_with_one_label(self, review_id):
        label_q = model.meta.Session.query(model.Label)
        labels = label_q.filter(model.Label.review_id == review_id).all()
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
        reviewer_project_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_projects = reviewer_project_q.filter(and_(\
                                model.ReviewerProject.review_id == old_review_id)).all()
        for reviewer_project in reviewer_projects:
            # note that this method makes sure the reviewer isn't already a
            # part of the review; if they are, then they
            self._add_user_to_review(reviewer_project.reviewer_id, new_review_id)
            # get rid of the previous entry: this review will no longer exist,
            # anyway. 
            model.Session.delete(reviewer_project)
            model.Session.commit()
        
        ###
        # NOTE: we *remove* all assignments and tasks (below) -- resolving the
        #   possible combinations of existing assignments proved
        #   too complicated -- it's assumed that new assignments
        #   will be added elsewhere.
        ###
        assignments_q = model.meta.Session.query(model.Assignment)
        assignments = assignments_q.filter(\
                    model.Assignment.review_id == old_review_id).all()
        for assignment in assignments:
            model.Session.delete(assignment)
            model.Session.commit()

        ###
        # now tasks
        tasks_q = model.meta.Session.query(model.Task)
        tasks = tasks_q.filter(\
                    model.Task.review == old_review_id).all()
        for task in tasks:
            #task.review = new_review_id
            #model.Session.commit()
            fixed_task_q = model.meta.Session.query(model.FixedTask)
            associated_fixed_tasks = fixed_task_q.filter(\
                                        model.FixedTask.task_id==task.id).all()
            for fixed_task in associated_fixed_tasks:
                model.Session.delete(fixed_task)

            model.Session.delete(task)
            model.Session.commit()

        ###
        # and citations
        citations_q = model.meta.Session.query(model.Citation)
        citations = citations_q.filter(\
                    model.Citation.review_id == old_review_id).all()
        for citation in citations:
            citation.review_id = new_review_id
            model.Session.commit()
         
        ###
        # labels
        labels_q = model.meta.Session.query(model.Label)
        labels = labels_q.filter(\
                    model.Label.review_id == old_review_id).all()
        for label in labels:
            label.review_id = new_review_id
            # we remove the associated assignment id
            # because this assignment will no longer exist
            label.assignment_id = None 
            model.Session.commit()

        
        ###
        # labeled features
        lfs_q = model.meta.Session.query(model.LabeledFeature)
        lfs = lfs_q.filter(\
                    model.LabeledFeature.review_id == old_review_id).all()
        for lf in lfs:
            lf.review_id = new_review_id
            model.Session.commit()

        
        ###
        # tags (technically, TagTypes)
        tag_types_q = model.meta.Session.query(model.TagTypes)
        tag_types_to_move = tag_types_q.filter(\
                    model.TagTypes.review_id == old_review_id).all()
        
        # issues #29/#33: need to handle duplicate tags properly
        # here -- so we pull all tags aleady associated with the
        # review were are moving old_review to.
        tag_texts_to_ids = {}
        tags_already_in_new_review = tag_types_q.filter(\
                    model.TagTypes.review_id == new_review_id).all()
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
                tag_to_move.review_id = new_review_id
                model.Session.commit()
            else:
                # then we've already got a tag with the same
                # text, so we de-dupe by moving all tags associated
                # with this type to the existing tag
                pre_existing_tag_id = tag_texts_to_ids[tag_to_move.text.lower()]

                # for actual tags, not tag types
                tags_q = model.meta.Session.query(model.Tags)
                tags_of_this_type =\
                     tags_q.filter(model.Tags.tag_id == tag_to_move.id).all()
            
                for dupe_tag in tags_of_this_type:
                    # associate these tags with the already-existing
                    # tag that has the same text -- note that
                    # this tag (pre_existing_tag_id) is already
                    # associated with the target review
                    dupe_tag.tag_id = pre_existing_tag_id
                    model.Session.commit()
                    
                # now delete the duplicate tag.
                model.Session.delete(tag_to_move)
                model.Session.commit()

        ###
        # priority
        priority_q = model.meta.Session.query(model.Priority)
        priorities = priority_q.filter(\
                    model.Priority.review_id == old_review_id).all()
        for priority in priorities:
            priority.review_id = new_review_id
            model.Session.commit()

        # ok -- that's it. now we're going to *delete* the old review!
        moved_review = self._get_review_from_id(old_review_id)        
        model.Session.delete(moved_review)
        model.Session.commit()

    def _make_new_review(self):
        new_review = model.Review()
        
        # the current_user will be the lead.
        current_user = request.environ.get('repoze.who.identity')['user']

        # we generate a random code for joining this review
        make_code = lambda N: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
        review_q = model.meta.Session.query(model.Review)
        existing_codes = [review.code for review in review_q.all()]
        code_length=10
        cur_code = make_code(code_length)
        while cur_code in existing_codes:
            cur_code = make_code(code_length)
        new_review.code = cur_code
        
        new_review.project_lead_id = current_user.id
        new_review.date_created = datetime.datetime.now()

        new_review.initial_round_size = 0
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
               "http://abstrackr.tuftscaes.org/join/%s" % project.code)

        server = smtplib.SMTP("localhost")
        to = email
        sender = "noreply@abstrackr.tuftscaes.org"
        body = string.join((
            "From: %s" % sender,
            "To: %s" % to,
            "Subject: %s" % subject,
            "",
            message
            ), "\r\n")
        
        server.sendmail(sender, [to], body)

    @ActionProtector(not_anonymous())
    def join_a_review(self):
        review_q = model.meta.Session.query(model.Review)
        c.all_reviews = review_q.all()
        return render("/reviews/join_a_review.mako")
        
    @ActionProtector(not_anonymous())
    def join(self, review_code):
        user_id = request.environ.get('repoze.who.identity')['user']
        review_q = model.meta.Session.query(model.Review)
            
        review_to_join = review_q.filter(model.Review.code==review_code).one()
        self._join_review(review_to_join.review_id)
        redirect(url(controller="account", action="welcome"))
        
    
    @ActionProtector(not_anonymous())
    def leave_review(self, id):
        current_user = request.environ.get('repoze.who.identity')['user']
        self._remove_user_from_review(current_user.id, int(id))
        redirect(url(controller="account", action="welcome"))
        
    @ActionProtector(not_anonymous())
    def remove_from_review(self, reviewer_id, review_id):
        self._remove_user_from_review(reviewer_id, review_id)
        redirect(url(controller="review", action="admin", id=review_id))
        
    def _remove_user_from_review(self, reviewer_id, review_id):
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_reviews = reviewer_review_q.filter(and_(\
                 model.ReviewerProject.review_id == review_id, 
                 model.ReviewerProject.reviewer_id==reviewer_id)).all()
                 
        for reviewer_review in reviewer_reviews:
            # note that there should only be one entry;
            # this is just in case.   
            model.Session.delete(reviewer_review)
    
        # next, we need to delete all assignments for this person and review
        assignments_q = model.meta.Session.query(model.Assignment)
        assignments = assignments_q.filter(and_(\
                    model.Assignment.review_id == review_id,
                    model.Assignment.reviewer_id == reviewer_id
        )).all()
        
        for assignment in assignments:
            model.Session.delete(assignment)
            model.Session.commit()
        
    def _add_user_to_review(self, reviewer_id, review_id):
        ###
        # make sure that this reviewer isn't already
        # associated with the review
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_reviews = reviewer_review_q.filter(and_(\
                 model.ReviewerProject.review_id == review_id, 
                 model.ReviewerProject.reviewer_id == reviewer_id)).all()
        if len(reviewer_reviews) > 0:
            return None
        
        # ok, then add them.
        reviewer_project = model.ReviewerProject()
        reviewer_project.reviewer_id = reviewer_id
        reviewer_project.review_id = review_id
        model.Session.add(reviewer_project)
        model.Session.commit()

    @ActionProtector(not_anonymous())
    def get_fields(self, review_id):
        c.review_id = review_id
        return render("/reviews/export_fragment.mako")

    @ActionProtector(not_anonymous())
    def export_labels(self, id, lbl_filter_f=None):
        # get fields
        review_q = model.meta.Session.query(model.Review)
        review = review_q.filter(model.Review.review_id == id).one()

        all_labelers = self._get_participants_for_review(review.review_id)

        # default to exporting everything
        if lbl_filter_f is None:
            lbl_filter_f = lambda label: True

        ## some helpers
        none_to_str = lambda x: "" if x is None else x
        zero_to_none = lambda x: "none" if x==0 else x

        fields_to_export = []
        for key,val in request.params.items():
            if key == "fields[]" and not val in ("", " ", "(enter new tag)"):
                fields_to_export.append(str(val))
    
       
        # map citation ids to dictionaries that, in turn, map
        # usernames to labels
        citation_to_lbls_dict = {}
        
        all_citations = [cit.citation_id for cit in self._get_citations_for_review(review.review_id)]
	citations_labeled_dict = {}
        for cit in all_citations:
          citations_labeled_dict[cit]=False

        # likewise, for notes
        citation_to_notes_dict = {}

        # we filter the citations list  (potentially)
        citations_to_export = []

        # for efficiency reasons, we keep track of whether we need
        # create a new empty dictionary for the current citation
        last_citation_id = None
        
        labeler_names = ["consensus"] # always export the consensus
        # first collect labels for all citations that pass our
        # filtering criteria
        for citation, label in model.meta.Session.query(\
            model.Citation, model.Label).filter(model.Citation.citation_id==model.Label.study_id).\
              filter(model.Label.review_id==id).order_by(model.Citation.citation_id).all():   
                # the above gives you all labeled citations for this review
                # i.e., citations that have at least one label
                citations_labeled_dict[citation.citation_id]=True

                if lbl_filter_f(label):
                    cur_citation_id = citation.citation_id
                    if last_citation_id != cur_citation_id:
                        citation_to_lbls_dict[citation.citation_id] = {}
                        citation_to_notes_dict[cur_citation_id] = {}
                        citations_to_export.append(citation)

                    # NOTE that we are assuming unique user names per-review
                    labeler = self._get_username_from_id(label.reviewer_id)
                    if not labeler in labeler_names:
                        labeler_names.append(labeler)

                    citation_to_lbls_dict[cur_citation_id][labeler] = label.label
                    last_citation_id = cur_citation_id
        
                    # note that this will only contain entries for reviews that have 
                    # been labeled! i.e., notes made on unlabeled citations are not
                    # reflected here.
                    citation_to_notes_dict[cur_citation_id][labeler] = \
                            self._get_notes_for_citation(cur_citation_id, label.reviewer_id)


        # we automatically export all labeler's labels
        for labeler in labeler_names:
            fields_to_export.append(labeler)
        
        # finally, export notes (if asked)
        notes_fields = ["general", "population", "intervention/comparator", "outcome"]
        if "notes" in  fields_to_export:
            fields_to_export.remove("notes")
            # we append all labelers notes
            for labeler in labeler_names:
                if labeler != "consensus":
                    for notes_field in notes_fields:
                        fields_to_export.append("%s notes (%s)" % (notes_field, labeler))

        labels = [",".join(fields_to_export)]
        for citation in citations_to_export:
            cur_line = []
            for field in fields_to_export:
                if field == "(internal) id":
                    cur_line.append("%s" % citation.citation_id)
                elif field == "(source) id":
                    cur_line.append("%s" % citation.refman_id)
                elif field == "pubmed id":
                    cur_line.append("%s" % zero_to_none(citation.pmid_id))
                elif field == "abstract":
                    cur_line.append('"%s"' % none_to_str(citation.abstract).replace('"', "'"))
                elif field == "title":
                    cur_line.append('"%s"' % citation.title.replace('"', "'"))
                elif field == "keywords":
                    cur_line.append('"%s"' % citation.keywords.replace('"', "'"))
                elif field == "journal":
                    cur_line.append('"%s"' % none_to_str(citation.journal))
                elif field == "authors":
                    cur_line.append('"%s"' % "".join(citation.authors))
                elif field == "tags":
                    cur_tags = self._get_tags_for_citation(citation.citation_id)
                    cur_line.append('"%s"' % ",".join(cur_tags))
                elif field in labeler_names:
                    cur_labeler = field
                    cur_lbl = "o"
                    cit_lbl_d = citation_to_lbls_dict[citation.citation_id]
                    if cur_labeler in cit_lbl_d:
                        cur_lbl = str(cit_lbl_d[cur_labeler])
                    # create a consensus label automagically in cases where
                    # there is unanimous agreement
                    elif cur_labeler == "consensus":
                        if len(set(cit_lbl_d.values()))==1:
                            if len(cit_lbl_d) > 1:
                                # if at least two people agree (and none disagree), set the 
                                # consensus label to reflect this
                                cur_lbl = str(cit_lbl_d.values()[0])
                            else:
                                # then only one person has labeled it --
                                # consensus is kind of silly
                                cur_lbl = "o"
                        else:
                            # no consensus!
                            cur_lbl = "x"

                    cur_line.append(cur_lbl)
                elif "notes" in field:
                    # notes field
                    # this is kind of hacky -- we first parse out the labeler
                    # name from the column header string assembled above and 
                    # then get a user id from this. 
                    get_labeler_name_from_str = lambda x: x.split("(")[1].split(")")[0]
                    cur_labeler = get_labeler_name_from_str(field)
                    # @TODO not sure what we should do in consensus case...
                    if cur_labeler == "consensus":
                        cur_line.append("")
                    else:
                        cur_note = None
                        cur_notes_d = citation_to_notes_dict[citation.citation_id]
                        
                        if cur_labeler in cur_notes_d:                  
                            cur_note = cur_notes_d[cur_labeler]

                        if cur_note is None:
                            cur_line.append("")
                        else:
                            notes_field = field
                            if "general" in notes_field:
                                cur_line.append(cur_note.general)
                            elif "population" in notes_field:
                                cur_line.append(cur_note.population)
                            elif "outcome" in notes_field:
                                cur_line.append(cur_note.outcome)
                            else:
                                # intervention/comparator
                                cur_line.append(cur_note.ic)

            labels.append(",".join(cur_line))
     
        # exporting *all* (including unlabeled!) citations, per Ethan's request 
        #-- may want to make this optional
        unlabeled_citations = [cit for cit in citations_labeled_dict if not citations_labeled_dict[cit]]
        labels.append("citations that are not yet labeled by anyone")
        labels.extend([str(cit_id) for cit_id in unlabeled_citations])
        
        

        fout = open(os.path.join(\
                "abstrackr", "public", "exports", "labels_%s.csv" % review.review_id), 'w')
        lbls_str = "\n".join(labels)
        lbls_str = lbls_str.encode("utf-8", "ignore")
        fout.write(lbls_str)
        fout.close()
        
        c.download_url = "http://abstrackr.tuftscaes.org/exports/labels_%s.csv" % review.review_id
        return render("/reviews/download_labels.mako")
        

    @ActionProtector(not_anonymous())
    def delete_review(self, id):
        review_q = model.meta.Session.query(model.Review)
        review = review_q.filter(model.Review.review_id == id).one()

        # make sure we're actually the project lead
        current_user = request.environ.get('repoze.who.identity')['user']
        if not review.project_lead_id == current_user.id:
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname    
    
        ###
        # should probably re-factor into routines...
        ###
        # first delete all associated citations
        citation_q = model.meta.Session.query(model.Citation)
        try:
            citations_for_review = citation_q.filter(model.Citation.review_id == review.review_id).all()        
        except:
            pdb.set_trace()
            
        for citation in citations_for_review:
            model.Session.delete(citation)
        model.Session.commit()

        # then delete the associations in the table mapping reviewers to 
        # reviews
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        entries_for_review = reviewer_review_q.filter(model.ReviewerProject.review_id == review.review_id).all()
        for reviewer_review in entries_for_review:
            model.Session.delete(reviewer_review)
        model.Session.commit()
            
        label_q = model.meta.Session.query(model.Label)
        labels = label_q.filter(model.Label.review_id == review.review_id).all()
        for l in labels:
            model.Session.delete(l)
        model.Session.commit()
            
        label_feature_q = model.meta.Session.query(model.LabeledFeature)
        labeled_features = label_feature_q.filter(model.LabeledFeature.review_id == review.review_id).all()
        for l in labeled_features:
            model.Session.delete(l)
            model.Session.commit()
            
        priority_q = model.meta.Session.query(model.Priority)
        priorities = priority_q.filter(model.Priority.review_id == review.review_id).all()
        for p in priorities:
            model.Session.delete(p)
        model.Session.commit()
            
        # remove all tasks associated with this review
        task_q = model.meta.Session.query(model.Task)
        tasks = task_q.filter(model.Task.review == review.review_id).all()
        for task in tasks:
            # and any FixedTask entries associated with these
            # tasks
            fa_q = model.meta.Session.query(model.FixedTask)
            fas = fa_q.filter(model.FixedTask.task_id == task.id).all()
            for fa in fas:
                model.Session.delete(fa)
                model.Session.commit()
            model.Session.delete(task)
            model.Session.commit()
    
            
        # ... and any assignments
        assignment_q = model.meta.Session.query(model.Assignment)     
        assignments = assignment_q.filter(model.Assignment.review_id == review.review_id).all()
        for assignment in assignments:
            model.Session.delete(assignment)
            model.Session.commit()
          
        # and the encoded status/prediction entries
        encoded_q = model.meta.Session.query(model.EncodeStatus)
        encoded_entries = encoded_q.filter(model.EncodeStatus.review_id == review.review_id).all()
        for encoded_entry in encoded_entries:
            model.Session.delete(encoded_entry)
            model.Session.commit()
        
        # predictions
        prediction_q = model.meta.Session.query(model.Prediction)
        predictions = prediction_q.filter(model.Prediction.review_id == review.review_id).all()
        for pred in predictions:
            model.Session.delete(pred)
            model.Session.commit()

        # and the prediction status objects
        pred_status_q = model.meta.Session.query(model.PredictionsStatus)
        pred_statuses = pred_status_q.filter(model.PredictionsStatus.review_id == review.review_id).all()
        for pred_stat in pred_statuses:
            model.Session.delete(pred_stat)
            model.Session.commit()

        # finally, delete the review
        model.Session.delete(review)
        model.Session.commit()
        
        redirect(url(controller="account", action="my_projects"))
       
    def get_conflict_button_fragment(self, id):
        #pdb.set_trace()
        if (controller_globals._does_a_conflict_exist(id)):
            c.display_the_button = True
        else:
            c.display_the_button = False
        c.review_id = id
        return render("/reviews/conflict_button.mako")
            #This template will determine whether the conflicts button is shown or the text is shown.
            #The template itself is then called by dashboard.mako using the load function.


    @ActionProtector(not_anonymous())
    def review_maybes(self, id):
        review_id = id
        maybe_ids = controller_globals._get_maybes(review_id)
        # TODO rename method
        self._create_conflict_task_with_ids(review_id, maybe_ids)
         
        
    @ActionProtector(not_anonymous())
    def review_conflicts(self, id):
        '''
        the basic idea here is to find all of the conflicting ids, then
        shove these into a FixedTask type task (i.e., a task with an 
        enumerated set of ids to be labeled). This task is then assigned
        to the project lead (assumed to be the current user).
        '''
        review_id = id
        conflicting_ids = controller_globals._get_conflicts(review_id)
        self._create_conflict_task_with_ids(review_id, conflicting_ids)

    def _create_conflict_task_with_ids(self, review_id, study_ids):
        task_q = model.meta.Session.query(model.Task)
        conflicts_task_for_this_review = \
            task_q.filter(and_(model.Task.review == review_id,\
                               model.Task.task_type == "conflict")).all()
        
        # we delete any existing conflict Tasks for this review
        if len(conflicts_task_for_this_review) > 0:
            # we assume there is only one such conflicts Task;
            # so if one already exists, we delete it.
            model.Session.delete(conflicts_task_for_this_review[0])
            model.Session.commit()
        
        ### now create an assignment to review these
        conflict_task = model.Task()
        conflict_task.task_type = "conflict"
        conflict_task.review_id = review_id
        conflict_task.num_assigned = len(study_ids)
        model.Session.add(conflict_task)
        model.Session.commit()
        for conflicting_id in study_ids:
            fixed_entry = model.FixedTask()
            fixed_entry.task_id = conflict_task.id
            fixed_entry.citation_id = conflicting_id
            model.Session.add(fixed_entry)
            model.Session.commit()
            
        # finally, add an assignment to (me). note that (me)
        # is the project lead.
        conflict_a = model.Assignment()
        conflict_a.review_id = review_id
        conflict_a.task_id = conflict_task.id
        conflict_a.date_assigned = datetime.datetime.now()
        conflict_a.assignment_type = conflict_task.task_type
        conflict_a.num_assigned = conflict_task.num_assigned
        conflict_a.done_so_far = 0
        model.Session.add(conflict_a)
        model.Session.commit()
        
        redirect(url(controller="review", action="screen", \
                        review_id=review_id, assignment_id=conflict_a.id))
    
    def _get_labels_for_citation(self, citation_id):
        return model.meta.Session.query(model.Label).\
            filter(model.Label.study_id==citation_id).all()
   

    @ActionProtector(not_anonymous())
    def admin(self, id, admin_msg=""):
        current_user = request.environ.get('repoze.who.identity')['user']
        # make sure we're actually the project lead
        if not self._current_user_leads_review(id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname        
            
        c.participating_reviewers = self._get_participants_for_review(id)
        # eliminate our the lead themselves from this list
        c.participating_reviewers = [reviewer for reviewer in c.participating_reviewers if \
                                        reviewer.id != current_user.id]
        
        # for the client side
        c.reviewer_ids_to_names_d = self._reviewer_ids_to_names(c.participating_reviewers)
        c.admin_msg = admin_msg
        return render("/reviews/admin.mako")
            
    def transfer_admin(self, review_id, user_id):
        '''
        sets the user specified as user_id as the lead of the
        review specified by review_id
        '''
        current_user = request.environ.get('repoze.who.identity')['user']
        # make sure we're actually the project lead
        if not self._current_user_leads_review(review_id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname        
        
        review = self._get_review_from_id(review_id)
        review.project_lead_id = user_id
        model.Session.commit()

        redirect(url(controller="account", action="my_projects"))

    @ActionProtector(not_anonymous())
    def assignments(self, id):
        # make sure we're actually the project lead (by the way, should probably
        # handle this verification in a decorator...)
        if not self._current_user_leads_review(id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname        
            
        c.participating_reviewers = self._get_participants_for_review(id)
        c.reviewer_ids_to_names_d = self._reviewer_ids_to_names(c.participating_reviewers)
        
        assignments_q = model.meta.Session.query(model.Assignment)
  
        assignments = assignments_q.filter(model.Assignment.review_id == id).all()

        # note that we don't show the 'conflict' assignments here.
        non_conflict_assignments = \
            [assignment for assignment in assignments if \
                     assignment.assignment_type != "conflict"]
   
        c.assignments = non_conflict_assignments
        return render("/reviews/assignments.mako")
    
    def _current_user_leads_review(self, review_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        c.review = self._get_review_from_id(review_id)
        return c.review.project_lead_id == current_user.id

    def _reviewer_ids_to_names(self, reviewers):
        # for the client side
        reviewer_ids_to_names_d = {}
        for reviewer in reviewers:
            reviewer_ids_to_names_d[reviewer.id] = reviewer.username
        reviewer_ids_to_names_d = reviewer_ids_to_names_d
        return reviewer_ids_to_names_d
        
    @ActionProtector(not_anonymous())    
    def participants(self, id):
        # make sure we're actually the project lead (by the way, should probably
        # handle this verification in a decorator...)
        current_user = request.environ.get('repoze.who.identity')['user']
        c.review = self._get_review_from_id(id)
        if not c.review.project_lead_id == current_user.id:
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname        
            
        c.participating_reviewers = self._get_participants_for_review(id)
    
        return render("/reviews/participants.mako")
        

    def _re_prioritize(self, review_id, sort_by_str):
        citation_ids = [cit.citation_id for cit in self._get_citations_for_review(review_id)]
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
            
        priority_q = model.meta.Session.query(model.Priority)
        priorities_for_review =  priority_q.filter(\
                                    model.Priority.review_id == review_id).all() 
        for priority_obj in priorities_for_review:
            priority_obj.priority = cit_id_to_new_priority[priority_obj.citation_id]
            model.Session.commit()

    @ActionProtector(not_anonymous())
    def show_review(self, id):
        review_q = model.meta.Session.query(model.Review)

        c.review = review_q.filter(model.Review.review_id == id).one()
        # grab all of the citations associated with this review
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == id).all()
   
        c.num_citations = len(citations_for_review)
        # and the labels provided thus far
        label_q = model.meta.Session.query(model.Label)
        ### TODO first of all, will want to differentiate between
        # unique and total (i.e., double screened citations). will
        # also likely want to pull additional information here, e.g.,
        # the participating reviewers, etc.
        labels_for_review = label_q.filter(model.Label.review_id == id).all()
        c.num_unique_labels = len(set([lbl.study_id for lbl in labels_for_review]))
        c.num_labels = len(labels_for_review)
        
        # generate a pretty plot via google charts
        chart = PieChart3D(500, 200)
        chart.add_data([c.num_citations-c.num_unique_labels, c.num_unique_labels])
        chart.set_colours(['224499', '80C65A'])
        chart.set_pie_labels(['unscreened', 'screened'])
        c.pi_url = chart.get_url()
        
        reviewer_proj_q = model.meta.Session.query(model.ReviewerProject)
        #reviewer_ids = [rp.reviewer_id for rp in reviewer_proj_q.filter(model.Citation.review_id == id).all()]

        c.participating_reviewers = reviewers = self._get_participants_for_review(id)
        user_q = model.meta.Session.query(model.User)
        c.project_lead = user_q.filter(model.User.id == c.review.project_lead_id).one()
        
        current_user = request.environ.get('repoze.who.identity')['user']
        c.is_admin = c.project_lead.id == current_user.id
        n_lbl_d = {} # map users to the number of labels they've provided
        for reviewer in reviewers:
            # @TODO problematic if two reviewers have the same fullname, which
            # isn't explicitly prohibited
            n_lbl_d[reviewer.fullname] = len([l for l in labels_for_review if l.reviewer_id == reviewer.id])
        
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
        google_url = "http://chart.apis.google.com/chart?cht=bhg&chs=%sx%s" % (width, height)
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
        term_q = model.meta.Session.query(model.LabeledFeature)
        labeled_term =  term_q.filter(model.LabeledFeature.id == term_id).one()
        labeled_term.label = new_label
        model.Session.add(labeled_term)
        model.Session.commit()
        redirect(url(controller="review", action="review_terms", \
                        id=labeled_term.review_id, assignment_id=assignment_id)) 
        
    @ActionProtector(not_anonymous())
    def delete_term(self, term_id, assignment_id):
        term_q = model.meta.Session.query(model.LabeledFeature)
        labeled_term = term_q.filter(model.LabeledFeature.id == term_id).one()
        model.Session.delete(labeled_term)
        model.Session.commit()
        redirect(url(controller="review", action="review_terms", \
                        id=labeled_term.review_id, assignment_id=assignment_id)) 
        
        
    @ActionProtector(not_anonymous())
    def label_term(self, review_id, label):
        current_user = request.environ.get('repoze.who.identity')['user']
        new_labeled_feature = model.LabeledFeature()
        new_labeled_feature.term = request.params['term']
        new_labeled_feature.review_id = review_id
        new_labeled_feature.reviewer_id = current_user.id
        new_labeled_feature.label = label
        new_labeled_feature.date_created = datetime.datetime.now()
        model.Session.add(new_labeled_feature)
        model.Session.commit()
        
    @ActionProtector(not_anonymous())
    def delete_assignment(self, review_id, assignment_id):
        if not self._current_user_leads_review(review_id):
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname        

        assignment_q = model.meta.Session.query(model.Assignment)     
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).one()
        model.Session.delete(assignment)
        model.Session.commit()

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
            model.Session.add(existing_note)

        char_limit = 999
        existing_note.general = notes["general_notes"][:char_limit]
        existing_note.population = notes["population_notes"][:char_limit]
        existing_note.ic = notes["ic_notes"][:char_limit]
        existing_note.outcome = notes["outcome_notes"][:char_limit]
        existing_note.creator_id = current_user.id
        existing_note.citation_id = citation_id
        
        model.Session.commit()


    def _get_notes_for_citation(self, citation_id, user_id):
        notes_q = model.meta.Session.query(model.Note)
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
        cur_tags = self._get_tags_for_citation(study_id, texts_only=False)
        for tag in cur_tags:
            model.Session.delete(tag)
            model.Session.commit()

        # now add all the new tags
        for tag in list(set(tags)):
            new_tag = model.Tags()
            new_tag.creator_id = current_user.id
            new_tag.tag_id = self._get_tag_id(review_id, tag)

            new_tag.citation_id = study_id
            model.Session.add(new_tag)
            model.Session.commit()



    @ActionProtector(not_anonymous())
    def add_tag(self, review_id, tag):

        current_user = request.environ.get('repoze.who.identity')['user']

        # make sure there isn't already an identical tag
        cur_tags = self._get_tag_types_for_review(review_id)

        if tag not in cur_tags:
            new_tag = model.TagTypes()
            new_tag.text = tag
            new_tag.review_id = review_id
            new_tag.creator_id = current_user.id
            model.Session.add(new_tag)
            model.Session.commit()


    @ActionProtector(not_anonymous())
    def label_citation(self, review_id, assignment_id, study_id, seconds, label):
        # unnervingly, this commit() must remain here, or sql
        # alchemy seems to get into a funk. I realize this is 
        # cargo-cult programming... @TODO further investigate
        model.meta.Session.commit()
        
        current_user = request.environ.get('repoze.who.identity')['user']
        
        # check if we've already labeled this; if so, handle
        # appropriately
        label_q = model.meta.Session.query(model.Label)
        
        # pull the associated assignment object
        assignment = self._get_assignment_from_id(assignment_id)

        existing_label = None
        if assignment.assignment_type == "conflict":
            existing_label = label_q.filter(and_(
                        model.Label.review_id == review_id, 
                        model.Label.study_id == study_id, 
                        model.Label.reviewer_id == CONSENSUS_USER)).all()
            c.consensus_review = True
        else:
            existing_label = label_q.filter(and_(
                        model.Label.review_id == review_id, 
                        model.Label.study_id == study_id, 
                        model.Label.reviewer_id == current_user.id)).all()
        

        if len(existing_label) > 0:
            # then this person has already labeled this example
            print "(RE-)labeling citation %s with label %s" % (study_id, label)
            existing_label = existing_label[0]
            existing_label.label = label
            existing_label.label_last_updated = datetime.datetime.now()
            existing_label.labeling_time += int(seconds)
            model.Session.add(existing_label)
            model.Session.commit()
            
            # if we are re-labelng, return the same abstract, reflecting the new
            # label. we put the single consensus label in a singleton list for the
            # client in the case that this is a 'conflict' assignment.
            c.cur_lbl = existing_label if assignment.assignment_type != "conflict" else [existing_label]
            c.assignment_id = assignment_id
            citation_q = model.meta.Session.query(model.Citation)
            c.assignment_type = assignment.assignment_type
            c.cur_citation = citation_q.filter(model.Citation.citation_id == study_id).one()
            c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
            c.review_id = review_id
            return render("/citation_fragment.mako")
        else:
            # either there is no existing label or this is a consens label
            # being provided (or both!)
            print "labeling citation %s with label %s" % (study_id, label)
            # first push the label to the database
            new_label = model.Label()
            new_label.label = label
            new_label.review_id = review_id
            new_label.study_id = study_id
            new_label.assignment_id = assignment_id
            new_label.labeling_time = int(seconds)
            
            if assignment.assignment_type == "conflict":
                # the 0th reviewer can be thought of as God
                # i.e., omniscient -- this is taken to be the
                # group consensus user
                new_label.reviewer_id = CONSENSUS_USER
            else:
                new_label.reviewer_id = current_user.id
            new_label.first_labeled = new_label.label_last_updated = datetime.datetime.now()
            model.Session.add(new_label)
            model.Session.commit()
            assignment.done_so_far += 1

            model.Session.commit()
            
            ###
            # for finite assignments, we need to check if we're through.
            if assignment.assignment_type != "perpetual":
                if assignment.done_so_far >= assignment.num_assigned:
                    assignment.done = True
                    model.Session.commit()
            else:
                # for `perpetual' (single, double or n-screening) case, we need to
                # keep track of the priority table. 
                #
                # update the number of times this citation has been labeled; 
                # if we have collected a sufficient number of labels, pop it from
                # the queue
                priority_obj = self._get_priority_for_citation_review(study_id, review_id)
                priority_obj.num_times_labeled += 1
                priority_obj.is_out = False
                priority_obj.locked_by = None
                model.Session.commit()
                
                # are we through with this citation/review?
                review = self._get_review_from_id(review_id)
        
                if review.screening_mode in ("single", "double"):
                    num_times_to_screen  = {"single":1, "double":2}[review.screening_mode]

                    if priority_obj.num_times_labeled >= num_times_to_screen:
                        model.Session.delete(priority_obj)
                        model.Session.commit()
        
                    # has this person already labeled everything in this review?
                    num_citations_in_review = len(self._get_citations_for_review(review_id))
                    num_screened = len(self._get_already_labeled_ids(review.review_id))
                    if num_screened >= num_citations_in_review:
                        assignment.done = True
                        model.Session.commit()
                    
                    
            return self.screen_next(review_id, assignment_id)
        
    @ActionProtector(not_anonymous())
    def markup_citation(self, id, assignment_id, citation_id):
        citation_q = model.meta.Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.citation_id == citation_id).one()
        c.review_id = id
        c.assignment_id = assignment_id

        # issue #41
        assignment = self._get_assignment_from_id(assignment_id)
        c.assignment_type = assignment.assignment_type
        c.cur_citation = self._mark_up_citation(id, c.cur_citation)
        
        current_user = request.environ.get('repoze.who.identity')['user']
        label_q = model.meta.Session.query(model.Label)
        c.cur_lbl = label_q.filter(and_(
                                     model.Label.study_id == citation_id,
                                     model.Label.reviewer_id == current_user.id)).all()
        if len(c.cur_lbl) > 0:
            c.cur_lbl = c.cur_lbl[0]
        else:
            c.cur_lbl = None
        return render("/citation_fragment.mako")
      
    @ActionProtector(not_anonymous())
    def screen(self, review_id, assignment_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        assignment = self._get_assignment_from_id(assignment_id)
        if assignment is None:
            redirect(url(controller="review", action="screen", \
                        review_id=review_id, assignment_id = assignment_id))    
            
        review = self._get_review_from_id(review_id)
        if assignment.done:
            redirect(url(controller="account", action="welcome"))    
        
    
        c.review_id = review_id
        c.review_name = review.name
        c.assignment_id = assignment_id
        c.assignment_type = assignment.assignment_type
        c.assignment = assignment 

        c.cur_citation = self._get_next_citation(assignment, review)
        
        if c.cur_citation is None:
            if assignment.assignment_type == "conflict":
                ###
                # TODO add more explanation here / return an actual page
                return "nothing to see here (i.e., not conflicting labels and/or no maybe labels). hit back?"
            else:
                assignment.done = True
                model.meta.Session.commit()
                redirect(url(controller="account", action="welcome"))

        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
        
        c.cur_lbl = None
        if assignment.assignment_type == "conflict":
            c.cur_lbl = self._get_labels_for_citation(c.cur_citation.citation_id)
            c.reviewer_ids_to_names_d =  self._labels_to_reviewer_name_d(c.cur_lbl)
        
        # now get tags for this citation
        # issue #34; only show tags that *this* user has provided
        c.tags = self._get_tags_for_citation(c.cur_citation.citation_id, \
                only_for_user_id=current_user.id)
        
        # and these are all available tags
        c.tag_types = self._get_tag_types_for_review(review_id)
        
        # now get any associated notes
        notes = self._get_notes_for_citation(c.cur_citation.citation_id, current_user.id)
        c.notes = notes

        model.meta.Session.commit()
        return render("/screen.mako")
          

    @ActionProtector(not_anonymous())
    def update_tags(self, study_id):
        # now get tags for this citation
        c.tags = self._get_tags_for_citation(study_id)
        return render("/tag_fragment.mako")

    @ActionProtector(not_anonymous())
    def update_tag_types(self, review_id, study_id):
        # now get tags for this citation
        c.tag_types = self._get_tag_types_for_review(review_id)
        c.tags = self._get_tags_for_citation(study_id)
        return render("/tag_dialog_fragment.mako")

    @ActionProtector(not_anonymous())
    def screen_next(self, review_id, assignment_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        assignment = self._get_assignment_from_id(assignment_id)
        review = self._get_review_from_id(review_id)

        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name
        c.assignment_id = assignment_id
        c.assignment_type = assignment.assignment_type
        c.assignment = assignment 

        c.cur_citation = self._get_next_citation(assignment, review)
  
        # but wait -- are we finished?
        if assignment.done or c.cur_citation is None:
            
            assignment.done = True
            model.meta.Session.commit()
            return render("/assignment_complete.mako")
            
        # mark up the labeled terms 
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)

        c.cur_lbl = None
        if assignment.assignment_type == "conflict":
            c.cur_lbl = self._get_labels_for_citation(c.cur_citation.citation_id)
            c.reviewer_ids_to_names_d =  self._labels_to_reviewer_name_d(c.cur_lbl)
         
        # now get tags for this citation
        c.tags = self._get_tags_for_citation(c.cur_citation.citation_id,\
                            only_for_user_id=current_user.id)
        
        # and these are all available tags
        c.tag_types = self._get_tag_types_for_review(review_id)

        # now get any associated notes
        notes = self._get_notes_for_citation(c.cur_citation.citation_id, current_user.id)
        c.notes = notes

        model.meta.Session.commit()
        return render("/citation_fragment.mako")
     
        
    def _labels_to_reviewer_name_d(self, labels):
        reviewer_ids_to_names_d = {}
        for label in labels:
            reviewer_ids_to_names_d[label.reviewer_id] = \
                self._get_username_from_id(label.reviewer_id)
        return reviewer_ids_to_names_d 
        
    def _get_next_citation(self, assignment, review):
        next_id = None
        
        # if the current assignment is a 'fixed' assignment (i.e.,
        # comprises a finite set of ids to be screened -- an initial round,
        # or conflicting round, e.g.) then we pull from the FixedAssignments table
        if assignment.assignment_type in ("initial", "conflict"):
            # in the case of initial assignments, we never remove the citations,
            # thus we need to ascertain that we haven't already screened it
            eligible_pool = self._get_ids_for_task(assignment.task_id)
            # a bit worried about runtime here (O(|eligible_pool| x |already_labeled|)).
            # hopefully eligible_pool shrinks as sufficient labels are acquired (and it 
            # shoudl always be pretty small for initial assignments).
            reviewer_id = None
            if assignment.assignment_type == "conflict":
                # the 0th user is the omniscient consensus reviewer,
                # by convention. in the case that we're reviewing conflicts
                # we use this special user.
                reviewer_id = 0
            already_labeled = \
                self._get_already_labeled_ids(review.review_id, reviewer_id=reviewer_id)

            eligible_pool = [xid for xid in eligible_pool if not xid in already_labeled]
            next_id = None
     
            if len(eligible_pool) > 0:
                next_id = eligible_pool[0]
        else:
            
            priority = self._get_next_priority(review)

            if priority is None:
                next_id = None
            else:
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
                    model.Session.delete(priority)
                    model.Session.commit()
                    priority = self._get_next_priority(review)


                next_id = priority.citation_id
                ## 'check out' / lock the citation
                priority.is_out = True
                priority.locked_by = request.environ.get('repoze.who.identity')['user'].id
                priority.time_requested = datetime.datetime.now()
                model.Session.commit()
 
        return None if next_id is None else self._get_citation_from_id(next_id)
      
    @ActionProtector(not_anonymous())
    def edit_tags(self, review_id, assignment_id):
        current_user = request.environ.get('repoze.who.identity')['user']

        tag_q = model.meta.Session.query(model.TagTypes)
        tags = None

        # fix for issue #35: allow admins to edit everyone's
        #   tags
        if self._current_user_leads_review(review_id):
            tags = tag_q.filter(model.TagTypes.review_id == review_id).all()
        else:
            tags = tag_q.filter(and_(\
                                model.TagTypes.review_id == review_id,\
                                model.TagTypes.creator_id == current_user.id
                         )).all()
        c.tags = tags
        c.assignment_id = assignment_id
        c.review_id = review_id
        return render("/reviews/edit_tags.mako")
    

    @ActionProtector(not_anonymous())
    def edit_tag(self, tag_id, assignment_id):
        tag_q = model.meta.Session.query(model.TagTypes)
        c.tag = tag_q.filter(model.TagTypes.id == tag_id).one()

        c.assignment_id = assignment_id
        return render("/reviews/edit_tag_fragment.mako")

    @ActionProtector(not_anonymous())
    def edit_tag_text(self, id):
        tag_q = model.meta.Session.query(model.TagTypes)
        current_user = request.environ.get('repoze.who.identity')['user']
        tag = tag_q.filter(model.TagTypes.id == id).one()
        if current_user.id == tag.creator_id or self._current_user_leads_review(tag.review_id):
            tag.text = request.params['new_text']
            model.Session.commit()
    

    @ActionProtector(not_anonymous())
    def delete_tag(self, tag_id, assignment_id):
        tag_q = model.meta.Session.query(model.TagTypes)
        current_user = request.environ.get('repoze.who.identity')['user']
        tag = tag_q.filter(model.TagTypes.id == tag_id).one()
        review_id = tag.review_id
        if current_user.id == tag.creator_id:
            model.Session.delete(tag)
            model.Session.commit()

            # also delete all the tag objects associated
            # with this TagType
            tag_obj_q = model.meta.Session.query(model.Tags)
            tags_of_this_type = tag_obj_q.filter(model.Tags.tag_id == tag_id).all()
            for tag_obj in tags_of_this_type:
                model.Session.delete(tag_obj)
            model.Session.commit()    
            
            redirect(url(controller="review", action="edit_tags", \
                            review_id=review_id, assignment_id=assignment_id))
        else:
            return "tsk, tsk."

      
    @ActionProtector(not_anonymous())
    def review_terms(self, id, assignment_id=None):
        review_id = id
        current_user = request.environ.get('repoze.who.identity')['user']
        
        term_q = model.meta.Session.query(model.LabeledFeature)
        labeled_terms =  term_q.filter(and_(\
                                model.LabeledFeature.review_id == review_id,\
                                model.LabeledFeature.reviewer_id == current_user.id
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
        
        label_q = model.meta.Session.query(model.Label)
        labels = None
        if lbl_filter in ("included", "excluded", "maybe (?)"):
            
            lbl_filter_num = {"included":1, "excluded":-1, "maybe (?)":0}[lbl_filter]

            '''
            labels = [label for label in label_q.filter(\
                                   and_(model.Label.review_id == review_id,\
                                        model.Label.reviewer_id == current_user.id),\
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

        label_q = model.meta.Session.query(model.Label)

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
                                   and_(model.Label.review_id == review_id,\
                                        model.Label.reviewer_id == current_user.id)).\
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
        c.review_name = self._get_review_from_id(review_id).name
 
        citation_q = model.meta.Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.citation_id == citation_id).one()
        # mark up the labeled terms 
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)

        # issue #36 -- making label reviewing more intuitive    
        assignment = self._get_assignment_from_id(assignment_id)
        c.assignment_type = assignment.assignment_type
        c.consensus_review = False
        label_q = model.meta.Session.query(model.Label)
        if c.assignment_type == "conflict":
            # then the assumption is that we're reviewing the labels provided
            # by the 'consensus_user'
            c.consensus_review = True       
            # we return the single result in a list to make life easier on the client
            # side; this way, the code doesn't care if it's reviewing a consensus
            # label or showing a label with conflicts (multiple labels) -- it
            # behaves the same.
            c.cur_lbl = [label_q.filter(and_(
                                     model.Label.study_id == citation_id,
                                     model.Label.reviewer_id == CONSENSUS_USER)).one()]

        else:
            # then get the label that the current user gave
            c.cur_lbl = label_q.filter(and_(
                                     model.Label.study_id == citation_id,
                                     model.Label.reviewer_id == current_user.id)).one()
                        
        # pass the assignment id back to the client
        c.assignment_id = assignment_id
 
        # grab the tags for this study
        # issue #34; blinding screeners to others' tags
        c.tag_types = self._get_tag_types_for_review(review_id)
        c.tags = None
        # ... unless we're in review conflicts mode, in which case
        # we show all tags
        if c.assignment_type == "conflict":
            c.tags = self._get_tags_for_citation(citation_id)
        else: 
            c.tags = self._get_tags_for_citation(citation_id, only_for_user_id=current_user.id)

        # also grab the notes 
        # @TODO what should we show for notes in the case of conflict mode,
        #   i.e., if multiple users have made notes..??
        c.notes = self._get_notes_for_citation(c.cur_citation.citation_id, current_user.id)

        return render("/screen.mako")
        
    @ActionProtector(not_anonymous())
    def create_assignment(self, id):
        assign_to = request.params.getall("assign_to")
        due_date = None
        try:
            m,d,y = [int(x) for x in request.params['due_date'].split("/")]
            due_date = datetime.date(y,m,d)
        except:
            pass
        p_rescreen = float(request.params['p_rescreen'])
        n = int(request.params['n'])
        assign_to_ids = [self._get_id_from_username(username) for username in assign_to]
        for reviewer_id in assign_to_ids:     
            new_assignment = model.Assignment()
            new_assignment.review_id = id
            new_assignment.reviewer_id = reviewer_id
            new_assignment.date_due = due_date
            new_assignment.done = False
            new_assignment.done_so_far = 0
            new_assignment.num_assigned = n
            new_assignment.p_rescreen = p_rescreen
            new_assignment.date_assigned = datetime.datetime.now()
            model.Session.add(new_assignment)
            model.Session.commit()
        
        redirect(url(controller="review", action="admin", id=id))     
              
        
    def _get_priority_for_citation_review(self, citation_id, review_id):
        priority_q = model.meta.Session.query(model.Priority)
        p_for_cit_review =  priority_q.filter(and_(\
                                model.Priority.review_id == review_id,\
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

        # first, make sure this person isn't already in this review.
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_reviews = reviewer_review_q.filter(and_(\
                 model.ReviewerProject.review_id == review_id, 
                 model.ReviewerProject.reviewer_id == current_user.id)).all()
        
        if len(reviewer_reviews) == 0:
            # we only add them if they aren't already a part of the review.
            reviewer_project = model.ReviewerProject()
            reviewer_project.reviewer_id = current_user.id
            reviewer_project.review_id = review_id
            model.Session.add(reviewer_project)
        
            # now we check what type of screening mode we're using
            review = self._get_review_from_id(review_id)
            if review.screening_mode in (u"single", u"double"):
                # then we automatically add a `perpetual' assignment
                self._assign_perpetual_task(current_user.id, review.review_id)
             
            # assign any initial tasks for this review to the joinee.  
            self._assign_initial_tasks(current_user.id, review.review_id)
            return True
        return False     
        
    def _get_next_priority(self, review):
        '''
        returns citation ids to be screened for the specified
        review, ordered by their priority (int he priority table).
        this is effectively how AL is implemented in our case --
        we assume the table has been sorted/ordered by some
        other process.
        
        Note: this will not return ids for instances that are 
        currently being labeled.
        '''
        review_id = review.review_id
        priority_q = model.meta.Session.query(model.Priority)
        me = request.environ.get('repoze.who.identity')['user'].id
    
        ranked_priorities =  priority_q.filter(\
                                    model.Priority.review_id == review_id).\
                                    order_by(model.Priority.priority).all() 
        
        # now filter the priorities, excluding those that are locked
        # note that we also will remove locks here if a citation has
        # been out for > 2 hours.
        filtered_ranked_priorities = []
        EXPIRE_TIME = 72000 # 72000 *seconds*: i.e., 2 hours
        
        #### Issa is complaining about speed-- and he's right
        # previously, we were walking over all priority objects
        # not once, but *twice*! once should be *worst case*
        # we should break here once we find a sufficiently good
        # good citation
        already_labeled = self._get_already_labeled_ids(review_id)
        for priority in ranked_priorities:
            if priority.is_out and not priority.locked_by == me:
                # currently locked by someone else; here we check
                # if the lock should be 'expired'
                time_locked = (datetime.datetime.now()-priority.time_requested).seconds
                if time_locked > EXPIRE_TIME:
                    priority.is_out = False
                    priority.locked_by = None
                    model.Session.commit()
                    return priority
            elif not priority.is_out or priority.locked_by == me:
                if priority.citation_id not in already_labeled:
                    return priority
                                
        
        # this person has already labeled everything -- nothing more to do!
        return None
        
    
    def _get_initial_task_for_review(self, review_id):
        task_q = model.meta.Session.query(model.Task)
        # there should only be one of these!
        
        init_task = task_q.filter(and_(\
                            model.Task.review == review_id,\
                            model.Task.task_type == "initial")).all()
        if len(init_task) == 0:
            return False # no initial task for this review
        # really there shouldonly be one!
        return init_task[0]


    def _get_tag_id(self, review_id, text):
        tag_q = model.meta.Session.query(model.TagTypes)
        
        tag_type = tag_q.filter(and_(
                model.TagTypes.review_id == review_id,
                model.TagTypes.text == text)).all()[0]
        return tag_type.id

    def _get_tags_for_citation(self, citation_id, texts_only=True, only_for_user_id=None):

        tag_q = model.meta.Session.query(model.Tags)
        tags = None
        if only_for_user_id:
            # then filter on the study and the user
            tags = tag_q.filter(and_(\
                    model.Tags.citation_id == citation_id,\
                    model.Tags.creator_id == only_for_user_id
             )).all()
        else:
            # all tags for this citation, regardless of user
            tags = tag_q.filter(model.Tags.citation_id == citation_id).all()

        if texts_only:
            return self._tag_ids_to_texts([tag.tag_id for tag in tags])
        return tags
    
    def _tag_ids_to_texts(self, tag_ids):
        return [self._text_for_tag(tag_id) for tag_id in tag_ids]
    
    def _text_for_tag(self, tag_id):
        tag_type_q = model.meta.Session.query(model.TagTypes)
        tag_obj = tag_type_q.filter(model.TagTypes.id == tag_id).one()
        return tag_obj.text


    def _get_tag_types_for_citation(self, citation_id, objects=False):
        tags = self._get_tags_for_citation(citation_id)
        # now map those types to names
        tag_type_q = model.meta.Session.query(model.TagTypes)
        tags = []
        
        for tag in tags:
            tag_obj = tag_type_q.filter(model.TagTypes.id == tag.tag_id).one()
     
            if objects:
                tags.append(tag_obj)
            else:
                tags.append(tag_obj.text)
        
        return tags

    def _get_tag_types_for_review(self, review_id):
        tag_q = model.meta.Session.query(model.TagTypes)
        tag_types = tag_q.filter(model.TagTypes.review_id == review_id).all()
        return [tag_type.text for tag_type in tag_types]


    def _get_ids_for_task(self, task_id):
        '''
        returns all the citation ids associated with the
        given task -- note that we order these by the
        citation id (somewhat arbitrarily!)
        '''
        q = model.meta.Session.query(model.FixedTask)
        eligible_ids = [fixed_task.citation_id for fixed_task in \
                                q.filter(model.FixedTask.task_id == task_id).\
                                order_by(model.FixedTask.citation_id).all()]    
        return eligible_ids
        
    def _get_already_labeled_ids(self, review_id, reviewer_id=None):
        ''' 
        returns a list of citation ids corresponding to those citations that
        the current reviewer (or the reviewer specified by user_id) has labeled 
        for the specified review.
        '''
        if reviewer_id is None:
            reviewer_id = request.environ.get('repoze.who.identity')['user'].id
        
        label_q = model.meta.Session.query(model.Label)
        already_labeled_ids = [label.study_id for label in label_q.filter(and_(\
                                                    model.Label.review_id == review_id,\
                                                    model.Label.reviewer_id == reviewer_id)).all()]
        return already_labeled_ids 
        
    def _get_participants_for_review(self, review_id):
        reviewer_proj_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_ids = \
            list(set([rp.reviewer_id for rp in reviewer_proj_q.filter(model.ReviewerProject.review_id == review_id).all()]))
        user_q = model.meta.Session.query(model.User)
        reviewers = [user_q.filter(model.User.id == reviewer_id).one() \
                    for reviewer_id in reviewer_ids]
        return reviewers
    
    def _get_username_from_id(self, id):
        if id == CONSENSUS_USER:
            return "consensus"
        user_q = model.meta.Session.query(model.User)
        return user_q.filter(model.User.id == id).one().username    
        
    def _get_id_from_username(self, username):
        user_q = model.meta.Session.query(model.User)
        return user_q.filter(model.User.username == username).one().id
        
    def _get_review_from_id(self, review_id):
        review_q = model.meta.Session.query(model.Review)
        return review_q.filter(model.Review.review_id == review_id).one()
        
    def _get_predictions_for_review(self, review_id):
        prediction_q = model.meta.Session.query(model.Prediction)
        predictions_for_review = prediction_q.filter(model.Prediction.review_id==review_id).all()
        return predictions_for_review
            
    def _do_predictions_exist_for_review(self, review_id):
        pred_status_q = model.meta.Session.query(model.PredictionsStatus)
        pred_status_of_review = \
            pred_status_q.filter(model.PredictionsStatus.review_id == review_id).all()
        if len(pred_status_of_review) > 0 and pred_status_of_review[0].predictions_exist:
            return True
        return False


    def _get_citations_for_review(self, review_id):
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == review_id).all()
        return citations_for_review
        
    def _get_citation_from_id(self, citation_id):
        citation_q = model.meta.Session.query(model.Citation)
        return citation_q.filter(model.Citation.citation_id == citation_id).one()
        
    def _get_assignment_from_id(self, assignment_id):
        assignment_q = model.meta.Session.query(model.Assignment)
        try:
            return assignment_q.filter(model.Assignment.id == assignment_id).one()
        except:
            pdb.set_trace()

        
    def _create_perpetual_task_for_review(self, review_id):
        new_task = model.Task()
        new_task.review = review_id
        new_task.task_type = u"perpetual"
        new_task.num_assigned = -1 # this is meaningless for `perpetual' assignments
        model.Session.add(new_task)
        model.Session.commit()
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
        

        cur_init_task = self._get_initial_task_for_review(review.review_id)

        if not cur_init_task:
            # if there isn't an initial task already, create one
            # here comprising 1 abstract
            self._create_initial_task_for_review(review.review_id, 0)
            cur_init_task = self._get_initial_task_for_review(review.review_id)
            # now we need to assign the task to every participant
            participants = self._get_participants_for_review(review.review_id)

            for participant in participants:
                self._assign_task(participant.id, cur_init_task, review.review_id)
            
        if n < review.initial_round_size:
            num_to_remove = review.initial_round_size - n

            # now grab the FixedTask objects associated with 
            # the initial tasks. 
            fixed_task_q = model.meta.Session.query(model.FixedTask)

            # we order these by the citation_id, since this is what
            # we do when we grab the next citation in a FixedTask.
            fixed_task_objs = fixed_task_q.filter(\
                                model.FixedTask.task_id == cur_init_task.id).\
                                order_by(model.FixedTask.citation_id).all()
            fixed_tasks_to_remove = fixed_task_objs[-num_to_remove:]

            # this is for re-inserting entries into the priority queue
            cur_max_priority = self._get_max_priority(review.review_id)+1
            if len(fixed_tasks_to_remove) > 0:
                for fixed_task in fixed_task_objs[-num_to_remove:]:
                    model.Session.delete(fixed_task)
                    model.Session.commit()
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
                                review.review_id, fixed_task.citation_id, \
                                    cur_max_priority, num_times_labeled=0)
                    cur_max_priority += 1  

        else:
            # then n > review.init_round_size: we have to add
            # citations to the fixed_task.
            fixed_task_q = model.meta.Session.query(model.FixedTask)

            # get a list of citation ids not already in the initial
            # assignment (warning -- O(n^2), though the initial round will
            # probably be << total # citations, so likely more O(n lg n).
            all_citation_ids = \
                [cit.citation_id for cit in self._get_citations_for_review(review.review_id)]

            init_citation_ids = self._get_ids_for_task(cur_init_task.id)
            citations_not_in_init = \
              [cit_id for cit_id in all_citation_ids if not cit_id in init_citation_ids]

            num_to_add = min(n-review.initial_round_size, len(citations_not_in_init))

            for i in xrange(num_to_add):
                citation_id = citations_not_in_init[i]
                fixed_task_entry = model.FixedTask()
                fixed_task_entry.task_id = cur_init_task.id
                fixed_task_entry.citation_id = citation_id
                model.Session.add(fixed_task_entry)
                model.Session.commit()  

                # and remove it from the priority queue.
                self._remove_citation_from_priority_queue(citation_id)
            
        # update the assignment objects
        init_assignments_for_tasks = \
                self._get_assignments_associated_with_task(cur_init_task.id)
        
        for assignment in init_assignments_for_tasks:
            assignment.done = (assignment.done_so_far >= n)
            assignment.num_assigned = n
            model.Session.commit()

        # update the assignment object
        initial_task = self._get_initial_task_for_review(review.review_id)
        initial_task.num_assigned = n
        model.Session.commit()
      

        # finally, update the initial round size field
        # onthe review object
        review.initial_round_size = n
        model.Session.commit()


    def _get_assignments_associated_with_task(self, task_id):
        assignment_q = model.meta.Session.query(model.Assignment)
        return assignment_q.filter(model.Assignment.task_id == task_id).all()
        

    def _remove_citation_from_priority_queue(self, citation_id):
            priority_q = model.meta.Session.query(model.Priority)
            priority_entry = priority_q.filter(model.Priority.citation_id == citation_id).one()
            model.Session.delete(priority_entry)
            model.Session.commit()

    def _create_initial_task_for_review(self, review_id, n):
        '''
        picks a random set of the citations from the specified review and 
        adds them into the FixedTask table -- participants in this 
        review should subsequently be tasked with Assignments that reference this.
        '''
        # first grab some ids at random
        init_ids = random.sample(\
                [citation.citation_id for citation in \
                    self._get_citations_for_review(review_id)], n)
        # create an entry in the Assignments table
        init_task = model.Task()
        init_task.task_type = "initial"
        init_task.review = review_id
        init_task.num_assigned = n
        model.Session.add(init_task)
        model.Session.commit()
        
        # now associate the initial ids drawn
        # with this Task
        for citation_id in init_ids:
            fixed_task_entry = model.FixedTask()
            fixed_task_entry.task_id = init_task.id
            fixed_task_entry.citation_id = citation_id
            model.Session.add(fixed_task_entry)
            model.Session.commit()
            
            # need also to remove this id from the priority queue
            priority_q = model.meta.Session.query(model.Priority)
            priority_entry = priority_q.filter(model.Priority.citation_id == citation_id).one()
            model.Session.delete(priority_entry)
            model.Session.commit()
            
    def _assign_initial_tasks(self, user_id, review_id):
        task_q = model.meta.Session.query(model.Task)
        initial_tasks_for_review = task_q.filter(and_(\
                        model.Task.review == review_id,
                        model.Task.task_type == u"initial"
                    )).all()
        
        for task in initial_tasks_for_review:
            self._assign_task(user_id, task, review_id)

 
    def _get_perpetual_assignments_for_review(self, review_id):
        assignment_q =  model.meta.Session.query(model.Assignment)
        perpetual_assignments = \
            assignment_q.filter(and_(model.Assignment.review_id == review_id,\
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
        task_q = model.meta.Session.query(model.Task)

        perpetual_tasks_for_review = task_q.filter(and_(\
                        model.Task.review == review_id,
                        model.Task.task_type == u"perpetual"
                    )).all()
        return perpetual_tasks_for_review

    def _assign_task(self, user_id, task, review_id, due_date=None):
        assignment = model.Assignment()
        assignment.review_id = review_id
        assignment.reviewer_id = user_id
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

        model.Session.add(assignment)
        model.Session.commit()
            
    def _mark_up_citation(self, review_id, citation):
        # pull the labeled terms for this review
        labeled_term_q = model.meta.Session.query(model.LabeledFeature)
        reviewer_id = request.environ.get('repoze.who.identity')['user'].id
        labeled_terms = labeled_term_q.filter(and_(\
                            model.LabeledFeature.review_id == review_id,\
                            model.LabeledFeature.reviewer_id == reviewer_id)).all()
        citation.marked_up_title = citation.title
        citation.marked_up_abstract = citation.abstract
        
        # sort the labeled terms by length (inverse)
        labeled_terms.sort(cmp=lambda x,y: len(y.term) - len(x.term))
        
        # strip these to sanitize input to RE.
        # note that this means users cannot provide REs
        # themselves.
        meta_chars = ". ^ $ * + ? { } [ ] \ | ( )".split(" ")
        for term in labeled_terms:
            # 'sanitize' the string, i.e., escape special chars
            term_text = []
            for x in term.term:
                if x in meta_chars:
                    term_text.append("\%s"%x)
                else:
                    term_text.append(x)
                    
            term_text = "".join(term_text)
            term_re = re.compile(term_text, re.IGNORECASE)
            
            # (case-insensitive) replace the term in the title text
            citation.marked_up_title = term_re.sub(\
                        "<font color='%s'>%s</font>" % (COLOR_D[term.label], term.term),\
                        citation.marked_up_title)
                  
            if citation.marked_up_abstract is not None:      
                # ... and in the abstract text
                citation.marked_up_abstract = term_re.sub(\
                            "<font color='%s'>%s</font>" % (COLOR_D[term.label], term.term),\
                            citation.marked_up_abstract)
                        
            else:
                citation.marked_up_abstract = ""
        citation.marked_up_title = literal(citation.marked_up_title)
        citation.marked_up_abstract = literal(citation.marked_up_abstract)
        return citation
   
        



