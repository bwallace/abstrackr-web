"""Setup the abstrackr application"""
import logging
import os.path

import pylons.test

from abstrackr.config.environment import load_environment
from abstrackr.model import meta
from abstrackr.model.meta import Session, Base

# for authentication
from abstrackr.model import User, Group, Permission
log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup abstrackr here"""
    load_environment(conf.global_conf, conf.local_conf)

    filename = os.path.split(conf.filename)[-1]
    if filename == 'test.ini':
        # Permanently drop any existing tables
        log.info("Dropping existing tables...")
        Base.metadata.drop_all(checkfirst=True, bind=Session.bind)
    # Create the tables if they don't already exist
    log.info("Creating database tables")
    Base.metadata.drop_all(checkfirst=True, bind=Session.bind)
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
