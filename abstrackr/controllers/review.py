import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from abstrackr.lib.base import BaseController, render
from abstrackr import model

import pdb

log = logging.getLogger(__name__)

class ReviewController(BaseController):

    def create_new_review(self):
        return render("/reviews/new.mako")
    
    def upload_xml(self):
        data = request.params['myfile'].file.read()
        pdb.set_trace()
        return data
