import pdb
import os
import shutil
import datetime
import random
import re
import time
from operator import itemgetter
import csv

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
import logging
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector
from abstrackr.lib.base import BaseController, render
import abstrackr.model as model
from abstrackr.lib import xml_to_sql
from sqlalchemy import or_, and_, desc
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
        if xml_file.filename.endswith(".xml"):
            print "parsing uploaded xml..."
            xml_to_sql.xml_to_sql(local_file_path, new_review)
        else:
            print "assuming this is a list of pubmed ids"
            xml_to_sql.pmid_list_to_sql(local_file_path, new_review)
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
        
        # first, make sure this person isn't alerady in this review.
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_reviews = reviewer_review_q.filter(and_(\
                 model.ReviewerProject.review_id == id, 
                 model.ReviewerProject.reviewer_id==current_user.id)).all()
        if len(reviewer_reviews) == 0:
            reviewer_project = model.ReviewerProject()
            reviewer_project.reviewer_id = current_user.id
            reviewer_project.review_id = id
            model.Session.add(reviewer_project)
            model.Session.commit()
        redirect(url(controller="account", action="welcome"))  
        
    @ActionProtector(not_anonymous())
    def leave_review(self, id):
        current_user = request.environ.get('repoze.who.identity')['user']
        # for now just adding right away; may want to 
        # ask project lead for permission though.
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        reviewer_reviews = reviewer_review_q.filter(and_(\
                 model.ReviewerProject.review_id == id, 
                 model.ReviewerProject.reviewer_id==current_user.id)).all()
                 
        for reviewer_review in reviewer_reviews:  
            # note that there should only be one entry;
            # this is just in case.   
            model.Session.delete(reviewer_review)
    
        # next, we need to delete all assignments for this person and review
        assignments_q = model.meta.Session.query(model.Assignment)
        assignments = assignments_q.filter(and_(\
                    model.Assignment.review_id == id,
                    model.Assignment.reviewer_id == current_user.id
        )).all()
        
        for assignment in assignments:
            model.Session.delete(assignment)
            
        model.Session.commit()
        redirect(url(controller="account", action="welcome"))
        
        
    @ActionProtector(not_anonymous())
    def export_labels(self, id):
        review_q = model.meta.Session.query(model.Review)
        review = review_q.filter(model.Review.review_id == id).one()
        labels = [",".join(["(internal) id", "pubmed id", "refman id", "labeler", "label"])]
        for citation, label in model.meta.Session.query(\
            model.Citation, model.Label).filter(model.Citation.citation_id==model.Label.study_id).\
            filter(model.Label.review_id==id).all():   
                user_name = self._get_username_from_id(label.reviewer_id)
                labels.append(",".join(\
                   [str(x) for x in [citation.citation_id, citation.pmid_id, citation.refman_id, user_name, label.label]]))
        
        response.headers['Content-type'] = 'text/csv'
        response.headers['Content-disposition'] = 'attachment; filename=labels_%s.csv' % id
        return "\n".join(labels)
        

    @ActionProtector(not_anonymous())
    def delete_review(self, id):
        review_q = model.meta.Session.query(model.Review)
        review = review_q.filter(model.Review.review_id == id).one()

        # make sure we're actually the project lead
        current_user = request.environ.get('repoze.who.identity')['user']
        if not review.project_lead_id == current_user.id:
            return "<font color='red'>tsk, tsk. you're not the project lead, %s.</font>" % current_user.fullname    
    
        # first delete all associated citations
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == review.review_id).all()        
        for citation in citations_for_review:
            model.Session.delete(citation)
        
        # then delete the associations in the table mapping reviewers to 
        # reviews
        reviewer_review_q = model.meta.Session.query(model.ReviewerProject)
        entries_for_review = reviewer_review_q.filter(model.ReviewerProject.review_id == review.review_id).all()
        for reviewer_review in entries_for_review:
            model.Session.delete(reviewer_review)
        
        # next delete all assignments associated with this review
        assignments_q = model.meta.Session.query(model.Assignment)
        assignments = assignments_q.filter(model.Assignment.review_id == review.review_id)
        for assignment in assignments:
            model.Session.delete(assignment)
                    
        # finally, delete the review
        model.Session.delete(review)

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
    def relabel_term(self, term_id, new_label):
        term_q = model.meta.Session.query(model.LabeledFeature)
        labeled_term =  term_q.filter(model.LabeledFeature.id == term_id).one()
        labeled_term.label = new_label
        model.Session.add(labeled_term)
        model.Session.commit()
        redirect(url(controller="review", action="review_terms", id=labeled_term.review_id)) 
        
    @ActionProtector(not_anonymous())
    def delete_term(self, id):
        term_id = id
        term_q = model.meta.Session.query(model.LabeledFeature)
        labeled_term = term_q.filter(model.LabeledFeature.id == term_id).one()
        model.Session.delete(labeled_term)
        model.Session.commit()
        redirect(url(controller="review", action="review_terms", id=labeled_term.review_id)) 
        
        
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
        current_user = request.environ.get('repoze.who.identity')['user']
        # check if we've already labeled this; if so, handle
        # appropriately
        label_q = model.meta.Session.query(model.Label)
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
            # label.
            c.cur_lbl = existing_label
            c.assignment_id = c.cur_lbl.assignment_id
            citation_q = model.meta.Session.query(model.Citation)
            c.cur_citation = citation_q.filter(model.Citation.citation_id == study_id).one()
            c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
            c.review_id = review_id
            return render("/citation_fragment.mako")
            
        else:
            print "labeling citation %s with label %s" % (study_id, label)
            # first push the label to the database
            new_label = model.Label()
            new_label.label = label
            new_label.review_id = review_id
            new_label.study_id = study_id
            new_label.assignment_id = assignment_id
            new_label.labeling_time = int(seconds)
            new_label.reviewer_id = current_user.id
            new_label.first_labeled = new_label.label_last_updated = datetime.datetime.now()
            model.Session.add(new_label)
            model.Session.commit()
            # pull the associated assignment object
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
        # but wait, are we finished?
        assignment_q = model.meta.Session.query(model.Assignment)
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).one()
        if assignment.done:
            redirect(url(controller="account", action="welcome"))    
        
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == review_id).all()
        
        label_q = model.meta.Session.query(model.Label)
        already_labeled_ids = [label.study_id for label in label_q.filter(model.Label.review_id == review_id).all()] 
        filtered = \
           [citation for citation in citations_for_review if not citation.citation_id in already_labeled_ids]
           
        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name
        c.assignment_id = assignment_id
        c.cur_citation = random.choice(filtered)
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
        c.cur_lbl = None
        return render("/screen.mako")
     
       
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
    
        # if an assignment id is given, it allows us to provide a 'get back to work'
        # link.
        c.assignment = assignment_id
        if assignment_id is not None:
            c.assignment = self._get_assignment_from_id(assignment_id)
            
        return render("/reviews/edit_terms.mako")
                         
    @ActionProtector(not_anonymous())
    def review_labels(self, review_id, assignment_id=None):
        current_user = request.environ.get('repoze.who.identity')['user']
        
        label_q = model.meta.Session.query(model.Label)
        already_labeled_by_me = [label for label in label_q.filter(\
                                   and_(model.Label.review_id == review_id,\
                                        model.Label.reviewer_id == current_user.id)).\
                                            order_by(desc(model.Label.label_last_updated)).all()] 
        
        c.given_labels = already_labeled_by_me
        
        # now get the citation objects associated with the given labels
        c.citations_d = {}
        for label in c.given_labels:
            c.citations_d[label.study_id] = self._get_citation_from_id(label.study_id)
        
        # if an assignment id is given, it allows us to provide a 'get back to work'
        # link.
        c.assignment = assignment_id
        if assignment_id is not None:
            c.assignment = self._get_assignment_from_id(assignment_id)
     
        return render("/reviews/review_labels.mako")
            
    @ActionProtector(not_anonymous())
    def show_labeled_citation(self, review_id, citation_id):
        current_user = request.environ.get('repoze.who.identity')['user']
        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name
 
        citation_q = model.meta.Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.citation_id == citation_id).one()
        # mark up the labeled terms 
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
        
        label_q = model.meta.Session.query(model.Label)
        c.cur_lbl = label_q.filter(and_(
                                     model.Label.study_id == citation_id,
                                     model.Label.reviewer_id == current_user.id)).one()
        c.assignment_id = c.cur_lbl.assignment_id
        return render("/screen.mako")
        
    @ActionProtector(not_anonymous())
    def screen_next(self, review_id, assignment_id):
        # but wait -- are we finished?
        assignment_q = model.meta.Session.query(model.Assignment)
        assignment = assignment_q.filter(model.Assignment.id == assignment_id).one()
        if assignment.done:
            redirect(url(controller="account", action="welcome"))

        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == review_id).all()

        # filter out examples already screened
        label_q = model.meta.Session.query(model.Label)
        already_labeled_ids = [label.study_id for label in label_q.filter(model.Label.review_id == review_id).all()] 

        filtered = \
           [citation for citation in citations_for_review if not citation.citation_id in already_labeled_ids]

        c.review_id = review_id
        c.review_name = self._get_review_from_id(review_id).name
        c.assignment_id = assignment_id
 
        c.cur_citation = random.choice(filtered)
        # mark up the labeled terms 
        c.cur_citation = self._mark_up_citation(review_id, c.cur_citation)
        c.cur_lbl = None
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
    
    def _get_username_from_id(self, id):
        user_q = model.meta.Session.query(model.User)
        return user_q.filter(model.User.id == id).one().username    
        
    def _get_id_from_username(self, username):
        user_q = model.meta.Session.query(model.User)
        return user_q.filter(model.User.username == username).one().id
        
    def _get_review_from_id(self, review_id):
        review_q = model.meta.Session.query(model.Review)
        return review_q.filter(model.Review.review_id == review_id).one()
        
    def _get_citation_from_id(self, citation_id):
        citation_q = model.meta.Session.query(model.Citation)
        return citation_q.filter(model.Citation.citation_id == citation_id).one()
        
    def _get_assignment_from_id(self, assignment_id):
        assignment_q = model.meta.Session.query(model.Assignment)
        return assignment_q.filter(model.Assignment.id == assignment_id).one()
        
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
        