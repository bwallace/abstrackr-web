from abstrackr.tests import *

class TestTrackrController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='trackr', action='index'))
        # Test response...
