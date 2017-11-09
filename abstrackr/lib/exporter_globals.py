from pylons import config

## GLOBALS
ROOT_PATH = config['pylons.paths']['root']
STATIC_FILES_PATH = config['pylons.paths']['static_files']

# this is the path where uploaded databases will be written to
PERMANENT_STORE = STATIC_FILES_PATH + "/uploads"
