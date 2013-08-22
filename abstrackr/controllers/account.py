import logging

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.controllers.util import redirect

import abstrackr.model as model
from abstrackr.model.meta import Session
from abstrackr.lib.base import BaseController, render
import abstrackr.controllers.controller_globals as controller_globals # shared querying routines

from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector

import turbomail
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
        user_for_email = controller_globals._get_user_from_email(user_email)
        if user_for_email:
            token = self.gen_token_to_reset_pwd(user_for_email)
            message = """
                        Hi, %s. \n
                        Someone (hopefully you!) asked to reset your abstrackr password.
                        To do so, follow this link:\n
                        \t %saccount/confirm_password_reset/%s.\n
                        Note that your password will be temporarily changed if you follow this link!
                        If you didn't request to reset your password, just ignore this email.
                      """ % (user_for_email.fullname, url('/', qualified=True), token)
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
        reset_pwd_q = Session.query(model.ResetPassword)
        # we pull all in case they've tried to reset their pwd a few times
        # by the way, these should time-expire...
        matches = reset_pwd_q.filter(model.ResetPassword.token == token).all()
        if len(matches) == 0:
            return """
                Hrmm... It looks like you're trying to reset your password, but I can't match the provided token.
                Please go back to the email that was sent to you and make sure you've copied the URL correctly.
                """
        user = controller_globals._get_user_from_email(matches[0].user_email)
        for match in matches:
            Session.delete(match)
        user._set_password(token)
        Session.commit()
        return '''
          ok! your password has been set to %s (you can change it once you've logged in).\n
          <a href="%s">log in here</a>.''' % (token, url('/', qualified=True))

    def gen_token_to_reset_pwd(self, user):
        # generate a random token for the user to reset their password; stick
        # it in the database
        make_token = lambda N: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))
        reset_pwd_q = Session.query(model.ResetPassword)
        existing_tokens = [entry.token for entry in reset_pwd_q.all()]
        token_length=10
        cur_token = make_token(token_length)
        while cur_token in existing_tokens:
            cur_token = make_code(token_length)

        reset = model.ResetPassword()
        reset.token = cur_token
        reset.user_email = user.email
        Session.add(reset)
        Session.commit()
        return cur_token

    def send_email_to_user(self, user, subject, message):
        host = config['smtp_host']
        port = config['smtp_port']
        sender = config['sender']
        server = smtplib.SMTP(host=host, port=port)
        to = user.email
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
        c.account_msg_citation_settings = ""
        return render("/accounts/account.mako")

    def change_password(self):
        current_user = request.environ.get('repoze.who.identity')['user']
        if request.params["password"] == request.params["password_confirm"]:
            current_user._set_password(request.params['password'])
            Session.commit()
            c.account_msg = "ok, your password has been changed."
        else:
            c.account_msg = "whoops -- the passwords didn't match! try again."

        c.account_msg_citation_settings = ""

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

        # These are for citation settings,
        # initialized to True to make everything in the citation visible by default.
        new_user.show_journal = True
        new_user.show_authors = True
        new_user.show_keywords = True

        Session.add(new_user)
        Session.commit()

        # send out an email
        greeting_message = """
            Hi, %s.\n

            Thanks for signing up at abstrackr (%s). You
            should be able to sign up now with username %s (only you know your password).

            This is just a welcome email to say hello, and that we've got your email.
            Should you ever need to reset your password, we'll send you instructions
            to this email. In the meantime, happy screening!

            -- The Brown EPC.
        """ % (new_user.fullname, url('/', qualified=True), new_user.username)

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



    '''
    The following methods are protected, i.e., the user must be logged in.
    '''
    @ActionProtector(not_anonymous())
    def welcome(self):
        redirect(url(controller="account", action="my_work"))

    @ActionProtector(not_anonymous())
    def back_to_projects(self):
        redirect(url(controller="account", action="my_projects"))


    @ActionProtector(not_anonymous())
    def my_work(self):

        person = request.environ.get('repoze.who.identity')['user']
        c.person = person
        user = controller_globals._get_user_from_email(c.person.email)
        if not user:
            log.error('''\
Hum...fetching user from the database returned False.
We need to investigate. Go remove the catch all in
controller_globals.py, method _get_user_from_email()
to see which OperationalError is being raised ''')

        # If somehow the user's citation settings variables don't get initialized yet,
        # then the following 3 if-else blocks should take care of it in order to avoid
        # any errors due to the values of the variables being null:
        c.show_journal = user.show_journal if not user.show_journal is None else True

        if (user.show_authors==True or user.show_authors==False):
            c.show_authors = user.show_authors
        else:
            user.show_authors = True

        if (user.show_keywords==True or user.show_keywords==False):
            c.show_keywords = user.show_keywords
        else:
            user.show_keywords = True


        # pull all assignments for this person
        assignment_q = Session.query(model.Assignment)
        all_assignments = assignment_q.filter(model.Assignment.user_id == person.id).all()

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
                reviews_with_initial_assignments.append(assignment.project_id)


        # now remove other (non-initial) assignments for reviews
        # that have an initial assignment
        filtered_assignments = [assignment for assignment in c.outstanding_assignments if \
                                assignment.project_id not in reviews_with_initial_assignments or \
                                assignment.assignment_type == "initial"]

        c.outstanding_assignments = filtered_assignments

        c.finished_assignments = [a for a in all_assignments if a.done]


        project_q = Session.query(model.Project)
        c.participating_projects = user.member_of_projects
        c.review_ids_to_names_d = self._get_review_ids_to_names_d(c.participating_projects)

        c.my_work = True
        c.my_projects = False
        return render('/accounts/dashboard.mako')


    @ActionProtector(not_anonymous())
    def show_merge_review_screen(self):
        person = request.environ.get('repoze.who.identity')['user']
        c.person = person
        user = controller_globals._get_user_from_email(person.email)

        projects_person_leads = self._get_projects_person_leads(user)
        c.reviews = projects_person_leads

        return render('/reviews/merge_reviews.mako')


    @ActionProtector(not_anonymous())
    def my_projects(self):
        person = request.environ.get('repoze.who.identity')['user']
        c.person = person

        # Get user object from db.
        user = controller_globals._get_user_from_email(person.email)

        # Set user's show preference defaults in case they weren't set.
        if (user.show_journal==True or user.show_journal==False):
            c.show_journal = user.show_journal
        else:
            user.show_journal = True

        if (user.show_authors==True or user.show_authors==False):
            c.show_authors = user.show_authors
        else:
            user.show_authors = True

        if (user.show_keywords==True or user.show_keywords==False):
            c.show_keywords = user.show_keywords
        else:
            user.show_keywords = True

        project_q = Session.query(model.Project)
        #c.leading_projects = project_q.filter(model.Project.leader_id == person.id).all()
        c.leading_projects = user.leader_of_projects
        leading_project_ids = [proj.id for proj in c.leading_projects]

        c.participating_projects = [p for p in user.member_of_projects if p.id not in leading_project_ids]

        c.review_ids_to_names_d = self._get_review_ids_to_names_d(c.participating_projects)

        statuses_q = Session.query(model.PredictionsStatus)
        c.statuses = {}

        c.do_we_have_a_maybe = {}
        for project_id in leading_project_ids:

            predictions_for_review = statuses_q.filter(model.PredictionsStatus.project_id==project_id).all()
            if len(predictions_for_review) > 0 and predictions_for_review[0].predictions_exist:
                c.statuses[project_id] = True
            else:
                c.statuses[project_id] = False

            c.do_we_have_a_maybe[project_id] = False

        c.my_work = False
        c.my_projects = True

        return render('/accounts/dashboard.mako')


    def _get_projects_person_leads(self, person):
        #project_q = Session.query(model.Project)
        #leading_projects = project_q.filter(model.Project.leader_id == person.id).all()
        leading_projects = person.leader_of_projects
        return leading_projects

    def _get_review_ids_to_names_d(self, reviews):
        # make life easier on client side
        review_ids_to_names_d = {}
        for review in reviews:
            review_ids_to_names_d[review.id] = review.name
        return review_ids_to_names_d


    @ActionProtector(not_anonymous())
    def test_user_access(self):
        return 'You are inside user section'

    @ActionProtector(has_permission('admin'))
    def test_admin_access(self):
        return 'You are inside admin section'


    # This is what gets executed when the user attempts to customize the 'citation settings'.
    @ActionProtector(not_anonymous())
    def customize_citations(self):

        # Obtain the parameters.
        show_journal_str = request.params['toggle_journal']
        show_authors_str = request.params['toggle_authors']
        show_keywords_str = request.params['toggle_keywords']

        # Obtain the User object (as opposed to the auth.User object).
        cur_user = controller_globals._get_user_from_email(request.environ.get('repoze.who.identity')['user'].email)

        # Make changes to the booleans of the user object.
        cur_user.show_journal = {"Show":True, "Hide":False}[show_journal_str]
        cur_user.show_authors = {"Show":True, "Hide":False}[show_authors_str]
        cur_user.show_keywords = {"Show":True, "Hide":False}[show_keywords_str]

        # Add the changes to the database.
        Session.commit()

        # These messages appear in their designated separate locations,
        #   i.e. on the top left corner of the div that corresponds to this function.
        # This is more appropriate than having a general message on some part of the screen.
        c.account_msg = ""
        c.account_msg_citation_settings = "Citation Settings changes have been applied."

        return render("/accounts/account.mako")
