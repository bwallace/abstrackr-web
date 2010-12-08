import pdb
import os
import shutil
import datetime
import random
import re
from operator import itemgetter

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
import logging
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector
from abstrackr.lib.base import BaseController, render
import abstrackr.model as model
from pylons import request, response, session, tmpl_context as c, url
from abstrackr.lib import xml_to_sql
from sqlalchemy import or_, and_
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

class ReviewController(BaseController):

    @ActionProtector(not_anonymous())
    def create_new_review(self):
        return render("/reviews/new.mako")
    
    @ActionProtector(not_anonymous())
    def create_review_handler(self):
        # first upload the xml file
        xml_file = request.params['db']
        local_file_path = "." + os.path.join(permanent_store, 
                          xml_file.filename.lstrip(os.sep))
        local_file = open(local_file_path, 'w')
        
        shutil.copyfileobj(xml_file.file, local_file)
        xml_file.file.close()
        local_file.close()
        
        current_user = request.environ.get('repoze.who.identity')['user']
        new_review = model.Review()
        new_review.name = request.params['name']
        new_review.project_lead_id = current_user.id
        new_review.project_description = request.params['description']
        new_review.date_created = datetime.datetime.now()
        model.Session.add(new_review)
        model.Session.commit()
        
        # now parse the uploaded file
        print "parsing uploaded xml..."
        xml_to_sql.xml_to_sql(local_file_path, new_review)
        print "done."
        
        redirect(url(controller="review", action="join_review", id=new_review.review_id))       
        
    @ActionProtector(not_anonymous())
    def join_a_review(self):
        review_q = model.meta.Session.query(model.Review)
        c.all_reviews = review_q.all()
        return render("/reviews/join_a_review.mako")
        
    @ActionProtector(not_anonymous())
    def join_review(self, id):
        current_user = request.environ.get('repoze.who.identity')['user']
        # for now just adding right away; may want to 
        # ask project lead for permission though.
        reviewer_project = model.ReviewerProject()
        reviewer_project.reviewer_id = current_user.id
        reviewer_project.review_id = id
        model.Session.add(reviewer_project)
        model.Session.commit()
        redirect(url(controller="account", action="welcome"))  
        
    @ActionProtector(not_anonymous())
    def admin(self, id):
        review_q = model.meta.Session.query(model.Review)
        review = review_q.filter(model.Review.review_id == id).one()
        c.review = review
        c.participating_reviewers = self._get_participants_for_review(id)
        
        # make sure we're actually the project lead
        current_user = request.environ.get('repoze.who.identity')['user']
        if not review.project_lead_id == current_user.id:
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname

        # for the client side
        reviewer_ids_to_names_d = {}
        for reviewer in c.participating_reviewers:
            reviewer_ids_to_names_d[reviewer.id] = reviewer.username
        c.reviewer_ids_to_names_d = reviewer_ids_to_names_d
        
        assignments_q = model.meta.Session.query(model.Assignment)
        assignments = assignments_q.filter(model.Assignment.review_id == id)
        c.assignments = assignments
        return render("/reviews/admin.mako")
            
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
        reviewer_ids = [rp.reviewer_id for rp in reviewer_proj_q.filter(model.Citation.review_id == id).all()]

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
    def label_citation(self, review_id, assignment_id, study_id, seconds, label):
        # TODO need to differentiate between first and subsequent labels
        # should check db here to see if this study has already been labeled
        # by this reviewer and handle accordingly
        print "labeling citation %s with label %s" % (study_id, label)
        # first push the label to the database
        new_label = model.Label()
        new_label.label = label
        new_label.review_id = review_id
        new_label.study_id = study_id
        new_label.labeling_time = int(seconds)
        current_user = request.environ.get('repoze.who.identity')['user']
        new_label.reviewer_id = current_user.id
        new_label.first_labeled = datetime.datetime.now()
        model.Session.add(new_label)
        model.Session.commit()
        
        # update the assignment
        assignment_q = model.meta.Session.query(model.Assignment)
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).one()
        assignment.done_so_far += 1
        if assignment.done_so_far >= assignment.num_assigned:
            assignment.done = True
        model.Session.commit()
        
        return self.screen_next(review_id, assignment_id)
        
    @ActionProtector(not_anonymous())
    def markup_citation(self, id, assignment_id, citation_id):
        citation_q = model.meta.Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.citation_id == citation_id).one()
        c.review_id = id
        c.assignment_id = assignment_id
        c.cur_citation = self._mark_up_citation(id, c.cur_citation)
        return render("/citation_fragment.mako")
        
    @ActionProtector(not_anonymous())
    def screen(self, review_id, assignment_id):
        # but wait, are we finished?
        assignment_q = model.meta.Session.query(model.Assignment)
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).one()
        if assignment.done:
            redirect(url(controller="account", action="welcome"))    
        
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == review_id).all()
        
        label_q = model.meta.Session.query(model.Label)
        already_labeled_ids = [label.study_id for label in label_q.filter(model.Citation.review_id == review_id).all()] 
        filtered = \
           [citation for citation in citations_for_review if not citation.citation_id in already_labeled_ids]
           
        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name
        c.assignment_id = assignment_id
        c.cur_citation = random.choice(filtered)
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
        return render("/screen.mako")
     
        
    @ActionProtector(not_anonymous())
    def screen_next(self, review_id, assignment_id):
        # but wait, are we finished?
        assignment_q = model.meta.Session.query(model.Assignment)
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).one()
        if assignment.done:
            redirect(url(controller="account", action="welcome"))
            
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == review_id).all()
        
        # filter out examples already screened
        label_q = model.meta.Session.query(model.Label)
        already_labeled_ids = [label.study_id for label in label_q.filter(model.Citation.review_id == review_id).all()] 
        filtered = \
           [citation for citation in citations_for_review if not citation.citation_id in already_labeled_ids]

        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name
        c.assignment_id = assignment_id
        
        c.cur_citation = random.choice(filtered)
        # mark up the labeled terms 
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
        return render("/citation_fragment.mako")
        
    @ActionProtector(not_anonymous())
    def create_assignment(self, id):
        assign_to = request.params.getall("assign_to")
        m,d,y = [int(x) for x in request.params['due_date'].split("/")]
        due_date = datetime.date(y,m,d)
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
        
        redirect(url(controller="review", action="join_review", id=id))     
                    
            
    def _get_participants_for_review(self, review_id):
        reviewer_proj_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_ids = \
            list(set([rp.reviewer_id for rp in reviewer_proj_q.filter(model.ReviewerProject.review_id == review_id).all()]))
        user_q = model.meta.Session.query(model.User)
        reviewers = [user_q.filter(model.User.id == reviewer_id).one() for reviewer_id in reviewer_ids]
        return reviewers
    
    def _get_id_from_username(self, username):
        user_q = model.meta.Session.query(model.User)
        return user_q.filter(model.User.username == username).one().id
        
    def _get_review_from_id(self, review_id):
        review_q = model.meta.Session.query(model.Review)
        return review_q.filter(model.Review.review_id == review_id).one()
        
    def _mark_up_citation(self, review_id, citation):
        # pull the labeled terms for this review
        labeled_term_q = model.meta.Session.query(model.LabeledFeature)
        reviewer_id = request.environ.get('repoze.who.identity')['user'].id
        labeled_terms = labeled_term_q.filter(and_(\
                            model.LabeledFeature.review_id == review_id,\
                            model.LabeledFeature.reviewer_id == reviewer_id)).all()
        citation.marked_up_title = citation.title
        citation.marked_up_abstract = citation.abstract
        for term in labeled_terms:
            title_matches = list(set(re.findall(term.term, citation.marked_up_title)))

            for match in title_matches:
                citation.marked_up_title = citation.marked_up_title.replace(match, "<font color='%s'>%s</font>" % (COLOR_D[term.label], match))
            
            if citation.marked_up_abstract is not None:
                abstract_matches = list(set(re.findall(term.term, citation.marked_up_abstract)))
                for match in abstract_matches:
                    citation.marked_up_abstract = \
                       citation.marked_up_abstract.replace(match, "<font color='%s'>%s</font>" % (COLOR_D[term.label], match))
            else:
                citation.marked_up_abstract = ""
        citation.marked_up_title = literal(citation.marked_up_title)
        citation.marked_up_abstract = literal(citation.marked_up_abstract)
        return citation
        