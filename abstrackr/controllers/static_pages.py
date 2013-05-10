from abstrackr.lib.base import BaseController, render

from repoze.what.plugins.pylonshq import ActionProtector
from repoze.what.predicates import not_anonymous

from pylons import tmpl_context as c, url


class StaticPagesController(BaseController):

    @ActionProtector(not_anonymous())
    def help(self):
        c.root_path = url('/', qualified=True)
        return render("/static_pages/help.mako")

    @ActionProtector(not_anonymous())
    def citing(self):
        c.root_path = url('/', qualified=True)
        return render("/static_pages/citing.mako")
