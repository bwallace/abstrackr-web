"""Setup the abstrackr application"""
import logging

import pylons.test

from abstrackr.config.environment import load_environment
from abstrackr.model import meta
from abstrackr.model.meta import Session, Base

# for authentication
from abstrackr.model import User, Group, Permission
log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup abstrackr here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    log.info("Creating database tables")
    Base.metadata.create_all(bind=Session.bind)
    log.info("Finished setting up")

    g = Group()
    g.name = u'admin'
    meta.Session.add(g)
    
    p = Permission()
    p.name = u'admin'
    meta.Session.add(p)

    # give myslf a login. 
    u = User()
    u.username = u'byron'
    u.fullname = u'byron wallace'
    u.experience = 2
    u._set_password('pignic')
    u.email = u'byron.wallace@gmail.com'
    meta.Session.add(u)

    meta.Session.commit()