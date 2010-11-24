import pdb
import os
import shutil

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
import logging

from abstrackr.lib.base import BaseController, render
from abstrackr import model

permanent_store = "/uploads/"

log = logging.getLogger(__name__)

class ReviewController(BaseController):

    def create_new_review(self):
        return render("/reviews/new.mako")
    
    def upload_xml(self):
        xml_file = request.params['db']#.file.read()
        permanent_file = open("." + os.path.join(permanent_store, 
                              xml_file.filename.lstrip(os.sep)), 'w')
        
        shutil.copyfileobj(xml_file.file, permanent_file)
        xml_file.file.close()
        permanent_file.close()
        return "OK!"
