import os

from hashlib import sha1

from sqlalchemy import ForeignKey, Column, types, Table
from sqlalchemy.orm import relationship, backref

# imports from the model
from abstrackr.model.meta import Session, Base

# authentication
#from abstrackr.model.auth import User, Group, Permission


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)


### Association Tables
citations_tasks_table = Table('citations_tasks', Base.metadata,
        Column('citation_id', types.Integer, ForeignKey('citations.id')),
        Column('task_id', types.Integer, ForeignKey('tasks.id'))
)

users_projects_table = Table('users_projects', Base.metadata,
        Column('user_id', types.Integer, ForeignKey('user.id')),
        Column('project_id', types.Integer, ForeignKey('projects.id'))
)

projects_leaders_table = Table('projects_leaders', Base.metadata,
        Column('user_id', types.Integer, ForeignKey('user.id')),
        Column('project_id', types.Integer, ForeignKey('projects.id'))
)

### end of Association Tables

class Project(Base):
    __tablename__ = "projects"
    #__mapper_args__ = dict(order_by="date desc")

    id = Column(types.Integer, primary_key=True)
    #leader_id = Column(types.Integer, ForeignKey('user.id'))

    # If initial_round_size > 0, this will point to
    # the entry in the citations_tasks table that
    # maps to the initial assignment associated with
    # this project.
    initial_assignment_id = Column(types.Integer)

    name = Column(types.Unicode(255))
    description = Column(types.Unicode(10000))

    # This is used to identify the project when
    # the leader invites others to the project
    code = Column(types.Unicode(10), index=True, unique=True)

    # `single', `double', or `advanced'
    screening_mode = Column(types.Unicode(50))

    # True := tags are private
    # False := tags are public
    tag_privacy = Column(types.Boolean)

    # the number of labels to be procured for each abstract
    num_labels_thus_far = Column(types.Integer)

    # basically, the AI criteria (or random)
    sort_by = Column(types.Unicode(255))

    # If >0, this represents a fixed set of
    # citations that will (potentially) be
    # screened by everyone on the project
    initial_round_size = Column(types.Integer)

    # Minimum and maximum number of citations a user should screen for this project
    min_citations = Column(types.Integer)
    max_citations = Column(types.Integer)

    # Bookkeeping
    date_created = Column(types.DateTime())
    date_modified = Column(types.DateTime())

    priorities = relationship('Priority', order_by='Priority.id', backref='project')
    citations = relationship('Citation', order_by='Citation.id', backref='project')
    assignments = relationship('Assignment', order_by='Assignment.id', backref='project')
    labels = relationship('Label', order_by='Label.id', backref='project')
    members = relationship('User', secondary=users_projects_table, backref='member_of_projects')
    leaders = relationship('User', secondary=projects_leaders_table, backref='leader_of_projects')


class Citation(Base):
    __tablename__ = "citations"

    # note that this is independent of pubmed/refman/whatever id!
    id = Column(types.Integer, primary_key=True)

    # associates the citation with the project that owns it
    project_id = Column(types.Integer, ForeignKey('projects.id'))
    pmid = Column(types.Integer)
    refman = Column(types.Integer)

    title = Column(types.Unicode(500))
    # length is based on back-of-envelope calculation
    abstract = Column(types.Unicode(10000))
    authors = Column(types.Unicode(5000))
    journal = Column(types.Unicode(1000))
    publication_date = Column(types.DateTime())
    keywords = Column(types.Unicode(5000))

    tasks = relationship("Task", secondary=citations_tasks_table, backref="citations")
    priorities = relationship('Priority', backref="citation")
    labels = relationship("Label", backref="citation")

class Priority(Base):
    """
    This table stores the ordered priority for citation screening, i.e.,
    facilitates active learning. It also attempts to solve the potential
    problem of users labeling the same citation simultaneously by
    containing a `is_out` field and date.

    """

    __tablename__ = "priorities"

    id = Column(types.Integer, primary_key=True)

    # ForeignKey relationship columns
    project_id = Column(types.Integer, ForeignKey('projects.id'))
    citation_id = Column(types.Integer, ForeignKey('citations.id'))

    priority = Column(types.Integer)

    # we keep the number of times that each citation has been labeled, and
    # remove it from the queue when a sufficient number of labels have been
    # collected
    num_times_labeled = Column(types.Integer)

    # Keep a record of whether this priority item is currently being labeled
    # by a user. This is an artificial lock on the item so that users do not
    # overwrite each other's label
    is_out = Column(types.Boolean)
    locked_by = Column(types.Integer)
    time_requested = Column(types.DateTime())


class TagType(Base):
    """User added tags"""

    __tablename__ = "tagtypes"

    id = Column(types.Integer, primary_key=True)
    text = Column(types.Unicode(500))
    project_id = Column(types.Integer)
    #label = Column(types.SmallInteger)
    creator_id = Column(types.Integer)
    color = Column(types.Unicode(50))


class Tag(Base):
    """Stores study/tag pairs"""

    __tablename__ = "tags"

    id = Column(types.Integer, primary_key=True)
    tag_id = Column(types.Integer)
    creator_id = Column(types.Integer)
    citation_id = Column(types.Integer)


class Note(Base):
    """Stores notes; both structured and unstructured"""

    __tablename__ = "notes"

    id = Column(types.Integer, primary_key=True)
    creator_id = Column(types.Integer)
    citation_id = Column(types.Integer)
    general = Column(types.Unicode(1000))
    population = Column(types.Unicode(1000))
    ic = Column(types.Unicode(1000)) # intervention/comparator
    outcome = Column(types.Unicode(1000))


class LabeledFeature(Base):
    """Stores labeled features, i.e., terms"""

    __tablename__ = "labeledfeatures"

    id = Column(types.Integer, primary_key=True)
    term = Column(types.Unicode(500))
    # project for which this term applies
    project_id = Column(types.Integer)
    # person who entered the term
    user_id = Column(types.Integer)
    # label
    label = Column(types.SmallInteger)
    date_created = Column(types.DateTime())


class Label(Base):
    """Stores instances labels"""

    __tablename__ = "labels"

    id = Column(types.Integer, primary_key=True)
    # project for which this document was screened
    project_id = Column(types.Integer, ForeignKey('projects.id'))
    study_id = Column(types.Integer, ForeignKey('citations.id')) # TODO: need to rename this to citation_id
    user_id = Column(types.Integer)
    assignment_id = Column(types.Integer)
    # -1, 0, 1
    label = Column(types.SmallInteger)
    # in seconds
    labeling_time = Column(types.Integer)
    first_labeled = Column(types.DateTime())
    label_last_updated = Column(types.DateTime())


class Assignment(Base):

    __tablename__ = "assignments"

    id = Column(types.Integer, primary_key=True)
    project_id = Column(types.Integer, ForeignKey('projects.id'))
    user_id = Column(types.Integer, ForeignKey('user.id'))
    task_id = Column(types.Integer, ForeignKey('tasks.id'))
    done_so_far = Column(types.Integer)
    date_assigned = Column(types.DateTime())
    date_due = Column(types.DateTime())
    done = Column(types.Boolean)

    # both of these fields are redundant
    # with the corresponding Task entry,
    # but it is easier to keep them here, too.
    num_assigned = Column(types.Integer)
    # this is the same as `task_type'.
    assignment_type = Column(types.Unicode(50))


class Task(Base):
    """
    a Task is a unit of work. Tasks have types;
    some are `perpetual`, i.e., they basically say `allow the
    person to whom this is assigned to keep on labeling, until
    there are no more citations that have not been labeled the
    desired number of times`, and there are `finite`, in which
    assignees are to label a fixed number of citations. Tasks are
    always associated with exactly one project, but multiple
    users can be assigned the same Task (see the Assignment table).

    """

    __tablename__ = "tasks"

    id = Column(types.Integer, primary_key=True)
    project_id = Column(types.Integer)
    # this is 'perpetual', 'initial' or 'finite'; the former indicates a 'perpetual'
    # screening task -- i.e., they will continue screening
    # while abstracts remain in the Priority queue for this
    # project. The latter two are special cases; in which only n
    # citations will be screened.
    task_type = Column(types.Unicode(50))
    # both of the following are N/A for 'perpetual'
    num_assigned = Column(types.Integer)

    assignments = relationship("Assignment", order_by='Assignment.id', backref="task")


class EncodeStatus(Base):
    """
    This table contains one entry for each dataset, indicating
    its encoded (i.e., for curious_snake/machine learning stuff)
    status. That is, this table contains information regarding:
        1) if the dataset has been encoded
        2) when the labels of this encoded file were last updated
        3) the path to the encoded file

    """

    __tablename__ = "encodedstatuses"

    id = Column(types.Integer, primary_key=True)
    project_id = Column(types.Integer) # associated project
    is_encoded = Column(types.Boolean) # has it been encoded yet?
    labels_last_updated = Column(types.DateTime())
    # the location of the base directory for the encoded project
    base_path = Column(types.Unicode(100))


class PredictionsStatus(Base):
    """Status of predictions (do they exist? last update, etc.)"""

    __tablename__ = "predictionstatuses"

    id = Column(types.Integer, primary_key=True)
    project_id = Column(types.Integer) # associated project
    predictions_exist = Column(types.Boolean) # has it been encoded yet?
    predictions_last_made = Column(types.DateTime())
    train_set_size = Column(types.Integer) # how many did we train on?
    num_pos_train = Column(types.Integer) # number of positive examples we trained on


class Prediction(Base):
    """Current inclusion/exclusion predictions for studies"""

    __tablename__ = "predictions"

    id = Column(types.Integer, primary_key=True)
    study_id = Column(types.Integer) # the (internal) study id
    project_id = Column(types.Integer) # it makes life easier to have this around
    prediction = Column(types.Boolean) # true = include; false = exclude
    num_yes_votes = Column(types.Float) # number of ensemble members that voted yes
    predicted_probability = Column(types.Float) # predicted probability

    


####################################
## these tables for authentication #
####################################
class ResetPassword(Base):
    """
    This table facilitates password recovery. If someone requests to reset
    their password, we generate a random token and insert it into this db.
    We then email them this token, verifying their id.

    """

    __tablename__ = "ResetPassword"

    id = Column(types.Integer, primary_key=True)
    user_email = Column(types.Unicode(80))
    token = Column(types.Unicode(10))

class Group(Base):
    __tablename__ = "group"
    id  = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(255))

class Permission(Base):
    __tablename__ = "permission"
    id  = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(255))

class User(Base):

    __tablename__ = "user"

    id  = Column(types.Integer, primary_key=True)
    username = Column(types.Unicode(255))
    email = Column(types.Unicode(80))
    password = Column(types.Unicode(80))
    fullname = Column(types.Unicode(255))
    # Number of Systematic Reviews they've been involved with
    experience = Column(types.Integer)
    # These three columns are meant to hold user's preference
    # choices as to whether to show the corresponding information
    # on the citation screen (default=True)
    show_journal = Column(types.Boolean, default=True)
    show_authors = Column(types.Boolean, default=True)
    show_keywords = Column(types.Boolean, default=True)

    assignments = relationship("Assignment", backref=backref('user', order_by=id))

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
    id  = Column(types.Integer, primary_key=True)
    group_id = Column(types.Integer)
    permission_id = Column(types.Integer)

# This is the association table for the many-to-many relationship between
# groups and users
class UserGroup(Base):
    __tablename__ = "user_group"
    id = Column(types.Integer, primary_key=True)
    user_id = Column(types.Integer)
    group_id = Column(types.Integer)
