import os
import sqlalchemy as sa

from hashlib import sha1

from sqlalchemy import Table, ForeignKey,\
    Column, types, orm

from sqlalchemy.types import Unicode, UnicodeText,\
    Integer, Date, CHAR, Float

# imports from the model
from abstrackr.model import meta
from abstrackr.model.meta import Session, Base, metadata

# authentication
from abstrackr.model.auth import User, Group, Permission


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)


class Project(Base):
    __tablename__ = "project"
    #__mapper_args__ = dict(order_by="date desc")

    id = sa.Column(types.Integer, primary_key=True)
    project_lead_id = sa.Column(types.Integer)
    project_description = sa.Column(types.Unicode(10000))
    
    # this is for joining the project
    code = sa.Column(types.Unicode(10))
    
    # `single', `double', or `advanced'
    screening_mode = sa.Column(types.Unicode(50))

    # True (i.e. tags are private)
    #  or 
    # False (i.e. tags are public)
    tag_privacy = sa.Column(types.Boolean)
    
    # the number of labels to be procured for each abstract
    num_labels_thus_far = sa.Column(types.Integer)
    # basically, the AI criteria (or random)
    sort_by = sa.Column(types.Unicode(255))
    
    # If >0, this represents a fixed set of
    # citations that will (potentially) be
    # screened by everyone on the project
    initial_round_size = sa.Column(types.Integer)
    # under the same condition, this will point to
    # the entry in the FixedAssignment table that
    # maps to the initial assignment associated with
    # this project.
    initial_assignment_id = sa.Column(types.Integer)
    
    date_created = sa.Column(types.DateTime())
    name = sa.Column(types.Unicode(255))
    
    
class Citation(Base):
    __tablename__ = "Citations"
    # note that this is independent of pubmed/refman/whatever id!
    citation_id = sa.Column(types.Integer, primary_key=True)
    # associates the citation with the project that owns it
    project_id = sa.Column(types.Integer)
    pmid = sa.Column(types.Integer)
    refman = sa.Column(types.Integer)
    
    title = sa.Column(types.Unicode(500))
    # length is based on back-of-envelope calculation
    abstract = sa.Column(types.Unicode(10000))
    authors = sa.Column(types.Unicode(5000))
    journal = sa.Column(types.Unicode(1000))
    keywords = sa.Column(types.Unicode(5000))
    
class Priority(Base):
    '''
    This table stores the ordered priority for citation screening, i.e.,
    facilitates active learning. It also attempts to solve the potential
    problem of users labeling the same citation simultaneously by 
    containing a `is_out` field and date.
    '''
    __tablename__ = "Priority"
    id = sa.Column(types.Integer, primary_key=True) 
    # project to which this ordering applies
    project_id = sa.Column(types.Integer)
    citation_id = sa.Column(types.Integer)
    priority = sa.Column(types.Integer)
    
    # we keep the number of times that each citation has been
    # labeled, and remove it from the queue when a sufficient
    # number of labels have been collected
    num_times_labeled = sa.Column(types.Integer)
    
    # here we do some bookkeeping to lock citations
    # while they are being labeled to prevent tandem
    # labelings
    is_out = sa.Column(types.Boolean)
    locked_by = sa.Column(types.Integer)
    time_requested = sa.Column(types.DateTime())
    
    
class TagTypes(Base):
    ''' User added tags '''
    __tablename__ = "TagTypes"
    id = sa.Column(types.Integer, primary_key=True)
    text = sa.Column(types.Unicode(500))
    # project for which tag was generated
    project_id = sa.Column(types.Integer)
    label = sa.Column(types.SmallInteger)
    # who invented this?
    creator_id = sa.Column(types.Integer)
    color = sa.Column(types.Unicode(50))

class Tags(Base):
    ''' Stores study/tag pairs '''
    __tablename__ = "Tags"
    id = sa.Column(types.Integer, primary_key=True)
    tag_id = sa.Column(types.Integer)
    creator_id = sa.Column(types.Integer)
    citation_id = sa.Column(types.Integer) 


class Note(Base):
    ''' Stores notes; both structured and unstructured '''
    __tablename__ = "Notes"
    id = sa.Column(types.Integer, primary_key=True)
    creator_id = sa.Column(types.Integer)
    citation_id = sa.Column(types.Integer) 
    general = sa.Column(types.Unicode(1000))
    population = sa.Column(types.Unicode(1000))
    ic = sa.Column(types.Unicode(1000)) # intervention/comparator
    outcome = sa.Column(types.Unicode(1000))

class LabeledFeature(Base):
    ''' Stores labeled features, i.e., terms '''
    __tablename__ = "LabelFeatures"
    id = sa.Column(types.Integer, primary_key=True)
    term = sa.Column(types.Unicode(500))
    # project for which this term applies
    project_id = sa.Column(types.Integer)
    # person who entered the term
    user_id = sa.Column(types.Integer)  
    # label
    label = sa.Column(types.SmallInteger)
    date_created = sa.Column(types.DateTime())
    
class Label(Base):
    ''' Stores instances labels '''
    __tablename__ = "Labels"
    id = sa.Column(types.Integer, primary_key=True)
    # project for which this document was screened
    project_id = sa.Column(types.Integer)
    study_id = sa.Column(types.Integer)
    user_id = sa.Column(types.Integer)
    assignment_id = sa.Column(types.Integer)
    # -1, 0, 1
    label = sa.Column(types.SmallInteger)
    # in seconds
    labeling_time = sa.Column(types.Integer)
    first_labeled = sa.Column(types.DateTime())
    label_last_updated = sa.Column(types.DateTime())
    
class ReviewerProject(Base):
    '''
    junction table; maps users to the projects they
    are on (and vice versa).
    '''
    __tablename__ = "ReviewersProjects"
    id = sa.Column(types.Integer, primary_key=True)
    project_id = sa.Column(types.Integer)
    user_id = sa.Column(types.Integer)
    
class Assignment(Base):
    __tablename__ = "Assignments"
    id = sa.Column(types.Integer, primary_key=True)
    project_id = sa.Column(types.Integer)
    user_id = sa.Column(types.Integer)
    task_id = sa.Column(types.Integer)
    done_so_far = sa.Column(types.Integer)
    date_assigned = sa.Column(types.DateTime())
    date_due = sa.Column(types.DateTime())
    done = sa.Column(types.Boolean)
    
    # both of these fields are redundant
    # with the corresponding Task entry,
    # but it is easier to keep them here, too.
    num_assigned = sa.Column(types.Integer)
    # this is the same as `task_type'. 
    assignment_type = sa.Column(types.Unicode(50))
    
    
class Task(Base):
    '''
    a Task is a unit of work. Tasks have types; 
    some are `perpetual`, i.e., they basically say `allow the
    person to whom this is assigned to keep on labeling, until
    there are no more citations that have not been labeled the
    desired number of times`, and there are `finite`, in which
    assignees are to label a fixed number of citations. Tasks are 
    always associated with exactly one project, but multiple
    users can be assigned the same Task (see the Assignment table).
    '''
    __tablename__ = "Tasks"
    id = sa.Column(types.Integer, primary_key=True)
    project_id = sa.Column(types.Integer)
    # this is 'perpetual', 'initial' or 'finite'; the former indicates a 'perpetual'
    # screening task -- i.e., they will continue screening
    # while abstracts remain in the Priority queue for this
    # project. The latter two are special cases; in which only n
    # citations will be screened.  
    task_type = sa.Column(types.Unicode(50))
    # both of the following are N/A for 'perpetual'
    num_assigned = sa.Column(types.Integer)
    
class FixedTask(Base):
    __tablename__ = "FixedTasks"
    # the id is meaningless, but we want a primary key to make SQL 
    # happy, so...
    id = sa.Column(types.Integer, primary_key=True) 
    task_id = sa.Column(types.Integer)
    citation_id = sa.Column(types.Integer)
 
 
class EncodeStatus(Base):
    '''
    This table contains one entry for each dataset, indicating
    its encoded (i.e., for curious_snake/machine learning stuff)
    status. That is, this table contains information regarding:
        1) if the dataset has been encoded
        2) when the labels of this encoded file were last updated
        3) the path to the encoded file
    '''
    __tablename__ = "EncodedStatuses" # sticking with the pluralized convention here
    id = sa.Column(types.Integer, primary_key=True)
    project_id = sa.Column(types.Integer) # associated project
    is_encoded = sa.Column(types.Boolean) # has it been encoded yet?
    labels_last_updated = sa.Column(types.DateTime())
    # the location of the base directory for the encoded project
    base_path = sa.Column(types.Unicode(100)) 


class PredictionsStatus(Base):
    '''
    Status of predictions (do they exist? last update, etc.)
    '''
    __tablename__ = "PredictionStatuses" 
    id = sa.Column(types.Integer, primary_key=True)
    project_id = sa.Column(types.Integer) # associated project
    predictions_exist = sa.Column(types.Boolean) # has it been encoded yet?
    predictions_last_made = sa.Column(types.DateTime())
    train_set_size = sa.Column(types.Integer) # how many did we train on?
    num_pos_train = sa.Column(types.Integer) # number of positive examples we trained on
    

class Prediction(Base):
    '''
    Current inclusion/exclusion predictions for studies
    '''
    __tablename__ = "Predictions" 
    id = sa.Column(types.Integer, primary_key=True)
    study_id = sa.Column(types.Integer) # the (internal) study id
    project_id = sa.Column(types.Integer) # it makes life easier to have this around
    prediction = sa.Column(types.Boolean) # true = include; false = exclude
    num_yes_votes = sa.Column(types.Float) # number of ensemble members that voted yes
    predicted_probability = sa.Column(types.Float) # predicted probability
    
####################################
## these tables for authentication #
####################################
class ResetPassword(Base):
    '''
    This table facilitates password recovery. If someone requests to reset
    their password, we generate a random token and insert it into this db. 
    We then email them this token, verifying their id.
    '''
    __tablename__ = "ResetPassword"
    id = sa.Column(types.Integer, primary_key=True)
    user_email = sa.Column(types.Unicode(80))
    token = sa.Column(types.Unicode(10))

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
    # Number of Systematic Reviews they've been involved with
    experience = sa.Column(types.Integer)
    # These three columns are meant to hold user's preference
    # choices as to whether to show the corresponding information
    # on the citation screen (default=True)
    show_journal = sa.Column(types.Boolean, default=True)
    show_authors = sa.Column(types.Boolean, default=True)
    show_keywords = sa.Column(types.Boolean, default=True)
    

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
   

