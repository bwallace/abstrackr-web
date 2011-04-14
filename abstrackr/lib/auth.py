from repoze.what.plugins.quickstart import setup_sql_auth
from abstrackr.model import meta
from abstrackr.model.auth import User, Group, Permission

def add_auth(app, config):
    """
    Add authentication and authorization middleware to the ``app``.

    We're going to define post-login and post-logout pages
    to do some cool things.

    """
    # we need to provide repoze.what with translations as described here:
    # http://what.repoze.org/docs/plugins/quickstart/
    return setup_sql_auth(app, User, Group, Permission, meta.Session,
                login_url='/account/login',
                post_login_url='/account/login',
                post_logout_url='/account/welcome',
                login_handler='/account/login_handler',
                logout_handler='/account/logout',
                cookie_secret=config.get('cookie_secret'),
                translations={
                    'user_name': 'username',
                    'group_name': 'name',
                    'permission_name': 'name',
                })
