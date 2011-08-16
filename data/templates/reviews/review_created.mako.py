# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1312911418.575
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/review_created.mako'
_template_uri='/reviews/review_created.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['title']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'../site.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n')
        # SOURCE LINE 3
        __M_writer(u'\r\n<script language="JavaScript">\r\n    var cal = new CalendarPopup();\r\n</script>\r\n\r\n<script language="javascript">\r\njQuery(document).ready(function(){\r\n    jQuery("#submit").click(function(){\r\n        $("#okay_div").fadeIn(2000)\r\n    });\r\n});\r\n</script>\r\n\r\n<div class="breadcrumbs">\r\n<a href="')
        # SOURCE LINE 17
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">./dashboard</a>/<a href="')
        __M_writer(escape(url(controller='review', action='show_review', id=c.review.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review.name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n\r\n<h1>Your review (')
        # SOURCE LINE 21
        __M_writer(escape(c.review.name))
        __M_writer(u') has been succesfully created!</h1>\r\n\r\n<div class="content">\r\n\r\nAwesome, you\'re ready to start screening.\r\n\r\n<br/><br/>\r\n<b>What now?</b>, you ask. You can invite additional reviewers, if you\'d like.<br/><br/>\r\n\r\n<div align="right">\r\n<form action = "/review/invite_reviewers/')
        # SOURCE LINE 31
        __M_writer(escape(c.review.review_id))
        __M_writer(u'">\r\n<div class="actions">\r\n<label for="emails">Enter their emails (comma-separated).</label>\r\n<input type="text" id="emails" name="emails" /><br />\r\n<input type="submit" id="submit" value="invite them!" />\r\n</div>\r\n</form>\r\n    <div class="loading" id="okay_div">\r\n        okay! emails have been sent!\r\n    </div>\r\n</div>\r\n\r\n<br/><br/>\r\nOr, send this link directly to participants:\r\n\r\n<center>\r\n<h2><a href="http://abstrackr.tuftscaes.org/join/')
        # SOURCE LINE 47
        __M_writer(escape(c.review.code))
        __M_writer(u'">http://abstrackr.tuftscaes.org/join/')
        __M_writer(escape(c.review.code))
        __M_writer(u'</a></h2>\r\n</center>\r\n\r\n\r\n</div>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(escape(c.review.name))
        return ''
    finally:
        context.caller_stack._pop_frame()


