from abstrackr.tests import TestController, url

from nose.tools import ok_            # This is shorthand for assert

from nose.plugins.attrib import attr  # Decorator to mark tests
                                      # Use this to exclude marked
                                      # tests if you want to


class TestReviewController(TestController):

                        # run with 'nosetests -a author=jj
    @attr(author='jj')  # or to exclude run 'nosetests -a '!author=jj'
    def test_create_new_review(self):
        response = self.app.get(url(controller='review',
                                        action='create_new_review'))
        ok_('The resource was found at' in response)
        res = response.follow()
        res.showbrowser()
