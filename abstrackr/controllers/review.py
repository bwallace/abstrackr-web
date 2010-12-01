import pdb
import os
import shutil
import datetime
import random
import re

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
        c.num_labels = len(labels_for_review)
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
    def label_citation(self, review_id, study_id, label):
        print "\n\n----------------------------------"
        print "labeling citation %s with label %s" % (study_id, label)
       # pdb.set_trace()
        # first push the label to the database
        new_label = model.Label()
        new_label.label = label
        new_label.review_id = review_id
        new_label.study_id = study_id
        current_user = request.environ.get('repoze.who.identity')['user']
        new_label.reviewer_id = current_user.id
        model.Session.add(new_label)
        model.Session.commit()
        
        return self.screen_next(review_id)
        
    @ActionProtector(not_anonymous())
    def screen(self, id):
        citation_q = model.meta.Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.review_id == id).all()
        c.review_id = id
        c.cur_citation = citations_for_review[0]
        c.cur_citation = self._mark_up_citation(id, c.cur_citation)
        return render("/screen.mako")
        
    @ActionProtector(not_anonymous())
    def markup_citation(self, id, citation_id):
        citation_q = model.meta.Session.query(model.Citation)
        c.cur_citation = citation_q.filter(model.Citation.citation_id == citation_id).one()
        c.review_id = id
        c.cur_citation = self._mark_up_citation(id, c.cur_citation)
        return render("/citation_fragment.mako")
        
    @ActionProtector(not_anonymous())
    def screen_next(self, id):
        citation_q = model.meta.Session.query(model.Citation)
        print "\n\n\nquerying for all citations"
        citations_for_review = citation_q.filter(model.Citation.review_id == id).all()
        print "done\n\n\n"
        
        # filter out examples already screened
        label_q = model.meta.Session.query(model.Label)
        print "\n\nquerying for citations already labeled"
        already_labeled_ids = [label.study_id for label in label_q.filter(model.Citation.review_id == id).all()] 
        filtered = \
           [citation for citation in citations_for_review if not citation.citation_id in already_labeled_ids]
        print "done\n\n\n"
        
        c.review_id = id
        c.cur_citation = random.choice(filtered)
        # mark up the labeled terms 
        #pdb.set_trace()
        
        print "\n\nrendering"
        c.cur_citation = self._mark_up_citation(id, c.cur_citation)
        #pdb.set_trace()
        print "done\n\n\n"

        return render("/citation_fragment.mako")
        
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
            
            abstract_matches = list(set(re.findall(term.term, citation.marked_up_abstract)))
            for match in abstract_matches:
                citation.marked_up_abstract = citation.marked_up_abstract.replace(match, "<font color='%s'>%s</font>" % (COLOR_D[term.label], match))
                
        citation.marked_up_title = literal(citation.marked_up_title)
        citation.marked_up_abstract = literal(citation.marked_up_abstract)
        return citation
        