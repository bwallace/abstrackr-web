"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import atexit
from turbomail import interface
from turbomail.adapters import tm_pylons

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = CacheManager(**parse_cache_config_options(config))
        #from turbomail.adapters import tm_pylons 
        #tm_pylons.start_extension() 
    
        atexit.register(tm_pylons.shutdown_extension)
        interface.start(tm_pylons.FakeConfigObj(config))
