import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from abstrackr.lib.base import BaseController, render
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector
from pylons.controllers.util import redirect
import abstrackr.controllers.controller_globals as controller_globals # shared querying routines
from controller_globals import * 

import turbomail
import abstrackr.model as model
import pdb
import smtplib
import string
import random

# validation stuff
from pylons.decorators import validate
import abstrackr.model.form as form

log = logging.getLogger(__name__)

class AccountController(BaseController):

    def login(self):
        """
        This is where the login form should be rendered.
        Without the login counter, we won't be able to tell if the user has
        tried to log in with wrong credentials.
        """
        identity = request.environ.get('repoze.who.identity')
        came_from = str(request.GET.get('came_from', '')) or \
                     url(controller='account', action='welcome')
        if identity:
            redirect(url(came_from))
        else:
            c.came_from = came_from
            c.login_counter = request.environ['repoze.who.logins'] + 1
            return render('/accounts/login.mako')

    def email_test(self):
        from turbomail import Message
        msg = Message('byron.wallace@gmail.com', 'byron.wallace@gmail.com', 'Subject')
        msg.plain = "Foo Bar"
        try:
            msg.send()   # Message will be sent through the configured manager/transport.
        except Exception, err:
            print err
        
    def recover_password(self):
        c.pwd_msg = ""
        return render('/accounts/recover.mako')
        
    def reset_password(self):
        user_email = request.params['email']
        user_for_email = self._get_user_from_email(user_email)
        if user_for_email:
            token = self.gen_token_to_reset_pwd(user_for_email)
            message = """
                        Hi, %s. \n
                        Someone (hopefully you!) asked to reset your abstrackr password. 
                        To do so, follow this link:\n
                        \t http://abstrackr.tuftscaes.org/account/confirm_password_reset/%s.\n 
                        Note that your password will be temporarily changed if you follow this link!
                        If you didn't request to reset your password, just ignore this email. 
                      """ % (user_for_email.fullname, token)
                    
            print token
            self.send_email_to_user(user_for_email, "resetting your abstrackr password", message)
            c.pwd_msg = "OK -- check your email (and your spam folder!)"
            return render('/accounts/recover.mako')
        else:
            c.pwd_msg = """
                Well, this is awkward. 
                We don't have a user in our database with email: %s. 
                Try again?""" % user_email
            return render('/accounts/recover.mako')
        
    
    def confirm_password_reset(self, id):
        token = str(id)
        reset_pwd_q = model.meta.Session.query(model.ResetPassword)
        # we pull all in case they've tried to reset their pwd a few times
        # by the way, these should time-expire...
        matches = reset_pwd_q.filter(model.ResetPassword.token == token).all()
        if len(matches) == 0:
            return """ 
                Hrmm... It looks like you're trying to reset your password, but I can't match the provided token. 
                Please go back to the email that was sent to you and make sure you've copied the URL correctly. 
                """
        user = self._get_user_from_email(matches[0].user_email)
        for match in matches:
            model.Session.delete(match)
        user._set_password(token)
        model.Session.commit()
        return '''
          ok! your password has been set to %s (you can change it once you've logged in).\n 
          <a href="http://sunfire34.eecs.tufts.edu">log in here</a>.''' % token
        
    def gen_token_to_reset_pwd(self, user):
        # generate a random token for the user to reset their password; stick
        # it in the database
        make_token = lambda N: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
        reset_pwd_q = model.meta.Session.query(model.ResetPassword)
        existing_tokens = [entry.token for entry in reset_pwd_q.all()]
        token_length=10
        cur_token = make_token(token_length)
        while cur_token in existing_tokens:
            cur_token = make_code(token_length)
        
        reset = model.ResetPassword()
        reset.token = cur_token
        reset.user_email = user.email
        model.Session.add(reset)
        model.Session.commit()
        return cur_token
            
    def send_email_to_user(self, user, subject, message):
        server = smtplib.SMTP("localhost")
        to = user.email
        sender = "noreply@abstrackr.tuftscaes.org"
        body = string.join((
            "From: %s" % sender,
            "To: %s" % to,
            "Subject: %s" % subject,
            "",
            message
            ), "\r\n")
        
        server.sendmail(sender, [to], body)
        
    
    def my_account(self):
        c.current_user = request.environ.get('repoze.who.identity')['user']
        c.account_msg = ""
        return render("/accounts/account.mako")

    def change_password(self):
        current_user = request.environ.get('repoze.who.identity')['user']
        if request.params["password"] == request.params["password_confirm"]:
            current_user._set_password(request.params['password'])
            model.Session.commit()
            c.account_msg = "ok, your password has been changed."
        else:
            c.account_msg = "whoops -- the passwords didn't match! try again."

        return render("/accounts/account.mako")
      

    def create_account(self):
        if 'then_join' in request.params:
            c.then_join = request.params['then_join']
        
        return render('/accounts/register.mako')
        
    @validate(schema=form.RegisterForm(), form='create_account')
    def create_account_handler(self):
        '''
        Note that the verification goes on in model/form.py.
        '''
        # create the new user; post to db via sqlalchemy
        new_user = model.User()
        new_user.username = request.params['username']
        new_user.fullname = " ".join([request.params['first_name'], request.params['last_name']])
        new_user.experience = request.params['experience']
        new_user._set_password(request.params['password'])
        new_user.email = request.params['email']
        model.Session.add(new_user)
        model.Session.commit()
        
        # send out an email
        greeting_message = """
            Hi, %s.\n
            
            Thanks for signing up at abstrackr (http://abstrackr.tuftscaes.org). You
            should be able to sign up now with username %s (only you know your password).
            
            This is just a welcome email to say hello, and that we've got your email.
            Should you ever need to reset your password, we'll send you instructions 
            to this email. In the meantime, happy screening!
            
            -- The Tufts EPC.
        """ % (new_user.fullname, new_user.username)
        
        try:
            self.send_email_to_user(new_user, "welcome to abstrackr", greeting_message)
        except:
            # this almost certainly means we're on our Windows dev box :)
            pass
        
        ###
        # log this user in programmatically (issue #28)
        rememberer = request.environ['repoze.who.plugins']['cookie']
        identity = {'repoze.who.userid': new_user.username}
        response.headerlist = response.headerlist + \
            rememberer.remember(request.environ, identity) 
        rememberer.remember(request.environ, identity) 


        # if they were originally trying to join a review prior to 
        # registering, then join them now. (issue #8).
        if 'then_join' in request.params and request.params['then_join'] != '':
            redirect(url(controller="review", action="join", review_code=request.params['then_join']))
        else:
            redirect(url(controller="account", action="login"))
        

    def _get_user_from_email(self, email):
        '''
        If a user with the provided email exists in the database, their
        object is returned; otherwise this method returns False. 
        '''
        user_q = model.meta.Session.query(model.User)
        try:
            return user_q.filter(model.User.email == email).one()
        except:
            # (naively, I guess) assuming that this implies that we've
            # no user with the provided email.
            return False
        
        
    '''
    The following methods are protected, i.e., the user must be logged in.
    '''
    @ActionProtector(not_anonymous())
    def welcome(self):
        redirect(url(controller="account", action="my_work"))
        
    @ActionProtector(not_anonymous())
    def my_work(self):
        person = request.environ.get('repoze.who.identity')['user']
        c.person = person
        
        # pull all assignments for this person
        assignment_q = model.meta.Session.query(model.Assignment)
        all_assignments = assignment_q.filter(model.Assignment.reviewer_id == person.id).all()

        c.outstanding_assignments = [a for a in all_assignments if not a.done]
        # if there's an initial assignment, we'll only show that.
        assignment_types = [assignment.assignment_type for assignment in \
                                                    c.outstanding_assignments]
                                
        #####
        # for any review that has an initial assignment, we will show
        # *only* that assignment, thereby forcining participants to 
        # finish initial assignments before moving on to other 
        # assignments. fix for issue #5.
        ####
        # which reviews have (outstanding) initial assigments?
        reviews_with_initial_assignments = []
        for assignment in c.outstanding_assignments:
            if assignment.assignment_type == "initial":
                reviews_with_initial_assignments.append(assignment.review_id)
        

        # now remove other (non-initial) assignments for reviews
        # that have an initial assignment
        filtered_assigments = [assignment for assignment in c.outstanding_assignments if \
                                assignment.review_id not in reviews_with_initial_assignments or \
                                assignment.assignment_type == "initial"]
        c.outstanding_assignments = filtered_assigments
                           
        c.finished_assignments = [a for a in all_assignments if a.done]   
        
        

        project_q = model.meta.Session.query(model.Review)   
        junction_q = model.meta.Session.query(model.ReviewerProject)
        participating_project_ids = \
            [p.review_id for p in junction_q.filter(model.ReviewerProject.reviewer_id == person.id).all()]
        c.participating_projects = [p for p in project_q.all() if p.review_id in participating_project_ids]
        c.review_ids_to_names_d = self._get_review_ids_to_names_d(c.participating_projects )
        
        c.my_work = True
        c.my_projects = False
        return render('/accounts/dashboard.mako')
        
        
    @ActionProtector(not_anonymous())
    def show_merge_review_screen(self):
        person = request.environ.get('repoze.who.identity')['user']
        c.person = person 

        projects_person_leads = self._get_projects_person_leads(person)
        c.reviews = projects_person_leads

        return render('/reviews/merge_reviews.mako')

    @ActionProtector(not_anonymous())
    def my_projects(self):
        person = request.environ.get('repoze.who.identity')['user']
        c.person = person
        
        project_q = model.meta.Session.query(model.Review)       
        c.leading_projects = project_q.filter(model.Review.project_lead_id == person.id).all()     
        leading_project_ids = [proj.review_id for proj in c.leading_projects]
         
        # pull the reviews that this person is participating in
        junction_q = model.meta.Session.query(model.ReviewerProject)
        participating_project_ids = \
            [p.review_id for p in junction_q.filter(model.ReviewerProject.reviewer_id == person.id).all()]
        c.participating_projects = [p for p in project_q.all() if p.review_id in participating_project_ids and \
                                                not p.review_id in leading_project_ids]
        
        c.review_ids_to_names_d = self._get_review_ids_to_names_d(c.participating_projects)
        
        statuses_q = model.meta.Session.query(model.PredictionsStatus)
        c.statuses = {}
        #c.conflicts = {}
        c.do_we_have_a_maybe = {}
        for project_id in leading_project_ids:
            
            predictions_for_review = statuses_q.filter(model.PredictionsStatus.review_id==project_id).all()
            if len(predictions_for_review) > 0 and predictions_for_review[0].predictions_exist:
                c.statuses[project_id] = True
            else:
                c.statuses[project_id] = False
            
            #c.statuses[project_id] = False
            
            import time
            start_time = time.time()
            #c.conflicts[project_id] = controller_globals._does_a_conflict_exist(project_id)
            end_time = time.time() 
            elapsed = end_time-start_time
            #pdb.set_trace()
            #len(controller_globals._get_conflicts(project_id)) > 0 
                                        # conflicting labels for this review?

            c.do_we_have_a_maybe[project_id] = False#= len(controller_globals._get_maybes(project_id)) > 0
                                        # Do we have maybes for this project?
            
        c.my_work = False
        c.my_projects = True
        
        return render('/accounts/dashboard.mako')
        
    def _get_projects_person_leads(self, person):
        project_q = model.meta.Session.query(model.Review)       
        leading_projects = project_q.filter(model.Review.project_lead_id == person.id).all()
        return leading_projects

    def _get_review_ids_to_names_d(self, reviews):
        # make life easier on client side
        review_ids_to_names_d = {}
        for review in reviews:
            review_ids_to_names_d[review.review_id] = review.name
        return review_ids_to_names_d
        
        
    @ActionProtector(not_anonymous())
    def test_user_access(self):
        return 'You are inside user section'

    @ActionProtector(has_permission('admin'))
    def test_admin_access(self):
        return 'You are inside admin section'
