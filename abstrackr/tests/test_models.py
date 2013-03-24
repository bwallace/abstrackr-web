from abstrackr.tests import TestController

from abstrackr import model

class TestReviewModel(TestController):
    """ Make sure db tables have the correct columns """

    def test_project(self):
        assert hasattr(model.Project, 'id')
        assert hasattr(model.Project, 'name')
        assert hasattr(model.Project, 'leader_id')
        assert hasattr(model.Project, 'initial_assignment_id')
        assert hasattr(model.Project, 'description')
        assert hasattr(model.Project, 'code')
        assert hasattr(model.Project, 'screening_mode')
        assert hasattr(model.Project, 'tag_privacy')
        assert hasattr(model.Project, 'num_labels_thus_far')
        assert hasattr(model.Project, 'sort_by')
        assert hasattr(model.Project, 'initial_round_size')
        assert hasattr(model.Project, 'created')
        assert hasattr(model.Project, 'modified')
        assert hasattr(model.Project, 'fullname')

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

    def test_priority(self):
        pass

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

    def test_reviewerproject(self):
        pass

    def test_assignment(self):
        pass

    def test_task(self):
        pass

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
        pass

    def test_grouppermission(self):
        pass

    def test_usergroup(self):
        pass
