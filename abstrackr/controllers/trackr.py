import pdb
import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from abstrackr.lib.base import BaseController, render
from abstrackr import model

log = logging.getLogger(__name__)

class TrackrController(BaseController):

    def start(self):
        """
        This is where the login form should be rendered.
        Without the login counter, we won't be able to tell if the user has
        tried to log in with wrong credentials
        """

        identity = request.environ.get('repoze.who.identity')
        came_from = str(request.GET.get('came_from', '')) or \
                    url(controller='account', action='welcome')

        if identity:
            # then we're logged in
            redirect(url(came_from))
        else:
            log_in = url(controller='account', action='login')
            redirect(log_in)

    def show_reviews(self):
        q = model.Session.query(model.Project)
        c.reviews= q.limit(5)
        return render("/index.mako")
