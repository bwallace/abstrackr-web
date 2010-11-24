import sqlalchemy as sa
from sqlalchemy import types

# imports from the model
from abstrackr.model import meta
from abstrackr.model.meta import Session, Base
# authentication
from abstrackr.model.auth import User, Group, Permission
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, UnicodeText, Integer, Date, CHAR
from sqlalchemy import orm
from abstrackr.model.meta import metadata
import os
from hashlib import sha1

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)


class Review(Base):
    __tablename__ = "Reviews"
    #__mapper_args__ = dict(order_by="date desc")

    review_id = sa.Column(types.Integer, primary_key=True)
    project_lead_id = sa.Column(types.Integer)
    project_description = sa.Column(types.Unicode(10000))
    date_created = sa.Column(types.DateTime())
    name = sa.Column(types.Unicode(255))
    
class Citation(Base):
    __tablename__ = "Citations"
    # note that this is independent of pubmed/refman/whatever id!
    citation_id = sa.Column(types.Integer, primary_key=True)
    pmid_id = sa.Column(types.Integer)
    refman_id = sa.Column(types.Integer)
    
    title = sa.Column(types.Unicode(200))
    # length is based on back-of-envelop calculation
    abstract = sa.Column(types.Unicode(10000))
    authors = sa.Column(types.Unicode(500))
    journal = sa.Column(types.Unicode(500))
    keywords = sa.Column(types.Unicode(1000))
    
    
class LabeledFeature(Base):
    ''' Stores labeled features, i.e., terms '''
    __tablename__ = "LabelFeatures"
    id = sa.Column(types.Integer, primary_key=True)
    # review for which this term applies
    review_id = sa.Column(types.Integer)
    # person who entered the term
    reviewer_id = sa.Column(types.Integer)  
    # label
    label = sa.Column(types.SmallInteger)
    date_created = sa.Column(types.DateTime())
    
class Label(Base):
    ''' Stores instances labels '''
    __tablename__ = "Labels"
    id = sa.Column(types.Integer, primary_key=True)
    # review for which this document was screened
    review_id = sa.Column(types.Integer)
    study_id = sa.Column(types.Integer)
    reviewer_id = sa.Column(types.Integer)
    # -1, 0, 1
    label = sa.Column(types.SmallInteger)
    # in seconds
    labeling_time = sa.Column(types.Integer)
    first_labeled = sa.Column(types.DateTime())
    label_last_updated = sa.Column(types.DateTime())
    
class ReviewerProject(Base):
    '''
    junction table; maps reviewers to the projects they
    are on (and vice versa).
    '''
    __tablename__ = "ReviewersProjects"
    id = sa.Column(types.Integer, primary_key=True)
    review_id = sa.Column(types.Integer)
    reviewer_id = sa.Column(types.Integer)
    
    
####################################
## these tables for authentication #
####################################
class Group(Base):
    __tablename__ = "group"
    id  = sa.Column(types.Integer, primary_key=True)
    name = sa.Column(types.Unicode(255))
    
class Permission(Base):
    __tablename__ = "permission"
    id  = sa.Column(types.Integer, primary_key=True)
    name = sa.Column(types.Unicode(255))
    
class User(Base):
    __tablename__ = "user"
    id  = sa.Column(types.Integer, primary_key=True)
    username = sa.Column(types.Unicode(255))
    email = sa.Column(types.Unicode(80))
    password = sa.Column(types.Unicode(80))
    fullname = sa.Column(types.Unicode(255))
    
    def _set_password(self, password):
        """Hash password on the fly."""
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        # Make sure the hased password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # fields
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self.password = hashed_password

    def _get_password(self):
        """Return the password hashed"""
        return self.password

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()


'''
# This is the association table for the many-to-many relationship between
# groups and permissions.
class GroupPermission(Base):
    __tablename__ = "group_permission"
    id  = sa.Column(types.Integer, primary_key=True)
    group_id = sa.Column(types.Integer)
    permission_id = sa.Column(types.Integer)

# This is the association table for the many-to-many relationship between
# groups and users
class UserGroup(Base):
    __tablename__ = "user_group"
    id  = sa.Column(types.Integer, primary_key=True)
    user_id = sa.Column(types.Integer)
    group_id = sa.Column(types.Integer)
'''   

