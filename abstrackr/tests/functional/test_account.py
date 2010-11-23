from abstrackr.tests import *

class TestAccountController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='account', action='index'))
        # Test response...
