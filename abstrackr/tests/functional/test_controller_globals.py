from abstrackr.tests import TestController
from abstrackr import model

from nose.plugins.attrib import attr  # Decorator to mark tests
                                      # Use "nosetests -a author=jj" to
                                      # run only marked tests or
                                      # "nosetests -a '!author=jj" to
                                      # exclude marked tests

import abstrackr.controllers.controller_globals as cg

Session = model.Session


class TestControllerGlobals(TestController):

    @attr(author='jj', controller='controller_globas')
    def test_get_project_member_ids(self):
        """ Return list of member ids

        Method takes a project id and returns should returns a
        list of user ids participating in the project.

        """

        u1 = model.User()
        u2 = model.User()
        u3 = model.User()
        p1 = model.Project()

        p1.members.extend([u1, u2, u3])
        Session.add(u1)
        Session.add(u2)
        Session.add(u3)
        Session.add(p1)
        Session.commit()

        member_id_list = cg._get_project_member_ids(p1.id)
        assert member_id_list == [u1.id, u2.id, u3.id]

        # Clean up
        Session.delete(u1)
        Session.delete(u2)
        Session.delete(u3)
        Session.delete(p1)
        Session.commit()
