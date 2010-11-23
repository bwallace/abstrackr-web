import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from abstrackr.lib.base import BaseController, render
from abstrackr import model

log = logging.getLogger(__name__)

class TrackrController(BaseController):

    def index(self):
        # Return a rendered template
        #return render('/trackr.mako')
        # or, return a string
        q = model.Session.query(model.Review)
        c.reviews= q.limit(5)
        return render("/index.mako")