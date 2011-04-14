import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from abstrackr.lib.base import BaseController, render
from repoze.what.predicates import not_anonymous, has_permission
from repoze.what.plugins.pylonshq import ActionProtector
from pylons.controllers.util import redirect
import turbomail
import abstrackr.model as model
import pdb

log = logging.getLogger(__name__)

class AccountController(BaseController):

    def login(self):
        """
        This is where the login form should be rendered.
        Without the login counter, we won't be able to tell if the user has
        tried to log in with wrong credentials
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
        
    def create_account(self):
        return render('/accounts/register.mako')
        
    def create_account_handler(self):
        '''
        TODO need to ascertain user doesn't already exist!
        See: http://pylonshq.com/docs/en/1.0/controllers/
        in particular,
            user = model.User.get_by(name=request.params['name'])
        If user exists here, abort
        '''
        # create the new user; post to db via sqlalchemy
        new_user = model.User()
        new_user.username = request.params['username']
        new_user.fullname = " ".join([request.params['first name'], request.params['last name']])
        new_user.experience = request.params['experience']
        new_user._set_password(request.params['password'])
        new_user.email = request.params['email']
        model.Session.add(new_user)
        model.Session.commit()
        redirect(url(controller="account", action="login"))
        
    @ActionProtector(not_anonymous())
    def welcome(self):
        """
        Greet the user if she logged in successfully or redirect back
        to the login form otherwise(using ActionProtector decorator).
        """
        person = request.environ.get('repoze.who.identity')['user']
        c.person = person
        
        project_q = model.meta.Session.query(model.Review)       
        c.leading_projects = project_q.filter(model.Review.project_lead_id == person.id).all()
        
        # pull the reviews that this person is participating in
        junction_q = model.meta.Session.query(model.ReviewerProject)
        participating_project_ids = \
            [p.review_id for p in junction_q.filter(model.ReviewerProject.reviewer_id == person.id).all()]
        c.participating_projects = [p for p in project_q.all() if p.review_id in participating_project_ids]
        
        # pull all assignments for this person
        assignment_q = model.meta.Session.query(model.Assignment)
        all_assignments = assignment_q.filter(model.Assignment.reviewer_id == person.id).all()
        
        # make life easier on client side
        review_ids_to_names_d = {}
        for review in c.participating_projects:
            review_ids_to_names_d[review.review_id] = review.name
        c.review_ids_to_names_d = review_ids_to_names_d
        
        c.outstanding_assignments = [a for a in all_assignments if not a.done]
        c.finished_assignments = [a for a in all_assignments if a.done]
        
        return render('/accounts/dashboard.mako')
        
    @ActionProtector(not_anonymous())
    def test_user_access(self):
        return 'You are inside user section'

    @ActionProtector(has_permission('admin'))
    def test_admin_access(self):
        return 'You are inside admin section'
