from abstrackr.tests import TestController

from abstrackr import model

Session = model.meta.Session

class TestReviewModel(TestController):
    """ Make sure db tables have the correct columns """


    def test_project(self):
        assert hasattr(model.Project, 'id')
        assert hasattr(model.Project, 'leader_id')
        assert hasattr(model.Project, 'initial_assignment_id')
        assert hasattr(model.Project, 'name')
        assert hasattr(model.Project, 'description')
        assert hasattr(model.Project, 'code')
        assert hasattr(model.Project, 'screening_mode')
        assert hasattr(model.Project, 'tag_privacy')
        assert hasattr(model.Project, 'num_labels_thus_far')
        assert hasattr(model.Project, 'sort_by')
        assert hasattr(model.Project, 'initial_round_size')
        assert hasattr(model.Project, 'date_created')
        assert hasattr(model.Project, 'date_modified')

        # This is the backref from the "user" table
        assert hasattr(model.Project, 'leader')
        assert hasattr(model.Project, 'members')

    def test_citation(self):
        assert hasattr(model.Citation, 'id')
        assert hasattr(model.Citation, 'project_id')
        assert hasattr(model.Citation, 'pmid')
        assert hasattr(model.Citation, 'refman')
        assert hasattr(model.Citation, 'title')
        assert hasattr(model.Citation, 'abstract')
        assert hasattr(model.Citation, 'authors')
        assert hasattr(model.Citation, 'journal')
        assert hasattr(model.Citation, 'publication_date')
        assert hasattr(model.Citation, 'keywords')
        assert hasattr(model.Citation, 'tasks')

    def test_priority(self):
        assert hasattr(model.Priority, 'id')
        assert hasattr(model.Priority, 'project_id')
        assert hasattr(model.Priority, 'citation_id')
        assert hasattr(model.Priority, 'priority')
        assert hasattr(model.Priority, 'num_times_labeled')
        assert hasattr(model.Priority, 'is_out')
        assert hasattr(model.Priority, 'locked_by')
        assert hasattr(model.Priority, 'time_requested')

    def test_tagtypes(self):
        pass

    def test_tags(self):
        pass

    def test_note(self):
        pass

    def test_labeledfeature(self):
        pass

    def test_label(self):
        pass

    def test_users_projects(self):
        # Create objects to test relationship (many-to-many)
        u1 = model.User()
        u2 = model.User()
        p1 = model.Project()
        p1.members.append(u1)
        p1.members.append(u2)
        Session.add(p1)
        Session.commit()

        # Get user objects now that they should have associated projects
        u1_ = Session.query(model.User).filter_by(id=u1.id).one()
        u2_ = Session.query(model.User).filter_by(id=u2.id).one()

        # Test that relationship to project exists
        assert u1_.projects == [p1]
        assert u2_.projects == [p1]

        # Now delete the project
        Session.delete(p1)
        Session.commit()

        # Verify that relationship no longer exists
        # (ie. users_projects_table entry has been removed)
        assert u1_.projects == []
        assert u2_.projects == []

        # Let's clean up
        Session.delete(u1)
        Session.delete(u2)
        Session.commit()

    def test_assignment(self):
        pass

    def test_task(self):
        # This is the backref from the "Citations" table
        assert hasattr(model.Task, 'citations')

    def test_fixedtask(self):
        pass

    def test_encodestatus(self):
        pass

    def test_predictionsstatus(self):
        pass

    def test_prediction(self):
        pass

    def test_resetpassword(self):
        pass

    def test_group(self):
        pass

    def test_permission(self):
        pass

    def test_user(self):
        assert hasattr(model.Priority, 'id')

    def test_grouppermission(self):
        pass

    def test_usergroup(self):
        pass
