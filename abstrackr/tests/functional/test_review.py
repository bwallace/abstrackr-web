from abstrackr.tests import TestController, url
from abstrackr import model

from nose.plugins.attrib import attr  # Decorator to mark tests
                                      # Use "nosetests -a author=jj" to
                                      # run only marked tests or
                                      # "nosetests -a '!author=jj" to
                                      # exclude marked tests

from abstrackr.controllers.review import ReviewController

Session = model.Session


class TestReviewController(TestController):

    @attr(author='jj', controller='account')
    def test_create_account(self):
        """ Create account

        Since the database has just been rebuild it lacks any
        user to run tests with. We will test the create_account
        action in the account controller to help us create a test
        user to run further tests.

        """

        # Get the 'create_account' page.
        response = self.app.get(
            url(controller='account',
                action='create_account'),
            status=200)
        # Make sure it has the correct url.
        assert response.request.url.endswith('/account/create_account')
        # Fill out the create account form.
        form = response.form
        form['first_name'] = u'tester'
        form['last_name'] = u'bot'
        form['experience'] = u'5'
        form['email'] = u'tester_bot@brown.edu'
        form['username'] = u'tester'
        form['password'] = u'tester'
        # Submit the form and throw if status not 302.
        post_submit = form.submit(status=302)
        # Submitting the form directs us back to 'login' page. Let's follow.
        post_submit = post_submit.follow(status=302)
        # Since we are now registered, 'login' page will redirect to
        # 'welcome' page
        post_login = post_submit.follow(status=302)
        # 'Welcome' page redirects to 'my_work' page; let's follow that also
        # The 'my_work' page gets rendered based on how many outstanding
        # assignments the user has, therefore we should check that this has
        # status 200
        post_login = post_login.follow(status=200)
        # Since this is a brand new account, let's check that we get the
        # "Hurray...." message
        assert "hurray, you've no outstanding assignments" in post_login

    @attr(author='jj', controller='review')
    def test_create_new_review(self):
        """ Anonymous users should be asked to log in

        User should be redirected to login screen.
        After login, verify that the correct page was rendered.

        """

        response = self.app.get(
            url(controller='review', action='create_new_review'),
            status=302)
        response = response.follow(status=200)
        form = response.form
        form['login'] = u'tester'
        form['password'] = u'tester'
        response = form.submit(status=302)
        # Several redirects we need to navigate through
        response = response.follow(status=302)
        response = response.follow(status=200)
        # Verify path is correct
        assert response.request.url.endswith('/review/create_new_review')
        # Verify that several keywords show up on the page
        assert 'project name' in response
        assert 'project description' in response
        assert 'upload file' in response
        assert 'screening mode' in response
        assert 'order abstracts by' in response
        assert 'pilot round size' in response
        assert 'tag visibility' in response

    @attr(author='jj', controller='review')
    def test_predictions_about_remaining_citations(self):
        pass

    @attr(author='jj', controller='review')
    def test_delete_citation(self):
        """ Deleting Citation entry cascades

        Verify that entries in CitationTask table are destroyed when
        corresponding citation and/or task is deleted

        """

        # Create citation and task objects
        c1 = model.Citation()
        c2 = model.Citation()
        t1 = model.Task()
        t2 = model.Task()

        # Append tasks to citation, incidentally this verifies that
        # the relationship are properly set.
        c1.tasks.append(t1)
        c1.tasks.append(t2)
        c2.tasks.append(t2)

        # Persist the changes.
        Session.add(c1)
        Session.add(c2)
        Session.commit()

        # Verify first that the entries in table CitationTask actually exist
        assert len(Session.query(model.citations_tasks_table).all()) == 3

        # Finally remove one of the citations and check cascade
        Session.delete(c1)
        Session.commit()
        assert len(Session.query(model.citations_tasks_table).all()) == 1

        # Do the same for when the task is removed
        Session.delete(t2)
        assert len(Session.query(model.citations_tasks_table).all()) == 0

    #@attr(author='jj', controller='review')
    #def test_get_next_priority(self):
    #    """ Verify return value of _get_next_priority method

    #    Verify that _get_next_priority returns the correct type, as well as
    #    the fact that it does not query the database unnecessarily.

    ##    """

    #    review_controller = ReviewController()
    #    review = model.meta.Session.query(model.Project).\
    #        filter(model.Project.id == '1').one()
    #    priority = review_controller.\
    #        _get_next_priority(review, ignore_my_own_locks=True)
    #    assert priority == 1

    #@attr(author='jj', controller='review')
    #def test_get_ids_for_task(self):
    #    """ Verify return value of _get_ids_for_task method

    #    Verify that _get_ids_for_task method returns a list of citations
    #    associated with the given task id

    #    """

    #    review_controller = ReviewController()
    #    citations_lst = review_controller._get_ids_for_task(1)
    #    assert citations_lst == ['63L', '69L', '95L', '97L', '106L']
