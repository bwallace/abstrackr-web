"""
SQLAlchemy-powered model definitions for repoze.what SQL plugin.
Sets up Users, Groups and Permissions
"""
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, UnicodeText, Integer, Date, CHAR
from sqlalchemy import orm
from abstrackr.model.meta import metadata
import os
from hashlib import sha1

group_table = Table('group', metadata,
    Column('id', Integer(), primary_key=True),
    Column('name', Unicode(255), unique=True, nullable=False),
)

permission_table = Table('permission', metadata,
    Column('id', Integer(), primary_key=True),
    Column('name', Unicode(255), unique=True, nullable=False),
)

user_table = Table('user', metadata,
    Column('id', Integer(), primary_key=True),
    Column('username', Unicode(255), unique=True, nullable=False),
    Column('email', Unicode(255), unique=True, nullable=False),
    Column('password', Unicode(80), nullable=False),
    Column('fullname', Unicode(255), nullable=False),
)

# This is the association table for the many-to-many relationship between
# groups and permissions.
group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('group.id')),
    Column('permission_id', Integer, ForeignKey('permission.id')),
)

# This is the association table for the many-to-many relationship between
# groups and users
user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('group_id', Integer, ForeignKey('group.id')),
)

class Group(object):
    pass

class Permission(object):
    pass

class User(object):

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

# Map SQLAlchemy table definitions to python classes
orm.mapper(Group, group_table, properties={
    'permissions':orm.relation(Permission, secondary=group_permission_table),
    'users':orm.relation(User, secondary=user_group_table),
})
orm.mapper(Permission, permission_table, properties={
    'groups':orm.relation(Group, secondary=group_permission_table),
})
orm.mapper(User, user_table, properties={
    'groups':orm.relation(Group, secondary=user_group_table),
})
