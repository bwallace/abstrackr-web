# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1312911922.25
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/admin.mako'
_template_uri='/reviews/admin.mako'
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
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n')
        # SOURCE LINE 3
        __M_writer(u'\r\n<script language="JavaScript">\r\n    var cal = new CalendarPopup();\r\n</script>\r\n\r\n<script language="javascript">\r\njQuery(document).ready(function(){\r\n    jQuery("#submit").click(function(){\r\n        $("#okay_div").fadeIn(2000)\r\n    });\r\n});\r\n\r\n</script>\r\n\r\n<div class="breadcrumbs">\r\n./<a href="')
        # SOURCE LINE 18
        __M_writer(escape(url(controller='account', action='my_projects')))
        __M_writer(u'">my projects</a>/<a href="')
        __M_writer(escape(url(controller='review', action='show_review', id=c.review.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review.name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n\r\n<h1>')
        # SOURCE LINE 22
        __M_writer(escape(c.review.name))
        __M_writer(u': administrivia</h1>\r\n<div class="actions">\r\n<a href="')
        # SOURCE LINE 24
        __M_writer(escape(url(controller='review', action='assignments', id=c.review.review_id)))
        __M_writer(u'">manage assignments</a>\r\n</div>\r\n\r\n<div class="content">\r\n\r\n')
        # SOURCE LINE 29
        if len(c.participating_reviewers)>0:
            # SOURCE LINE 30
            __M_writer(u'\t<h2>Participants</h2>\r\n\t<table class="list_table">\r\n\t<tr align="center"><th>person</th><th></th></tr>\r\n')
            # SOURCE LINE 33
            for participant in c.participating_reviewers:
                # SOURCE LINE 34
                __M_writer(u'\t       <tr>\r\n\t       <td>')
                # SOURCE LINE 35
                __M_writer(escape(participant.fullname))
                __M_writer(u'</td>\r\n\t       <td class="actions">\r\n\t       <a href="/review/remove_from_review/')
                # SOURCE LINE 37
                __M_writer(escape(participant.id))
                __M_writer(u'/')
                __M_writer(escape(c.review.review_id))
                __M_writer(u'")>\r\n\t        remove from review</a>\r\n\t       </tr>     \r\n\t       \r\n')
                pass
            # SOURCE LINE 42
            __M_writer(u'\t<table>\r\n\r\n\t<br/>\r\n')
            # SOURCE LINE 45
        elif c.admin_msg == "":
            # SOURCE LINE 46
            __M_writer(u"\t<H2>Hrmm... You're the only person participating in this review. </h2><h2>But don't despair: you can invite people below! </H2>\r\n\t<br/><br/>\r\n")
            pass
        # SOURCE LINE 49
        __M_writer(u'\r\n')
        # SOURCE LINE 50
        if c.admin_msg != "":
            # SOURCE LINE 51
            __M_writer(u'\t<H2>')
            __M_writer(escape(c.admin_msg))
            __M_writer(u'</H2>\r\n')
            pass
        # SOURCE LINE 53
        __M_writer(u'\r\n<div align="right">\r\n<form action = "/review/invite_reviewers/')
        # SOURCE LINE 55
        __M_writer(escape(c.review.review_id))
        __M_writer(u'">\r\n<div class="actions">\r\n<label for="emails">Want to invite additional reviewers? Enter their emails (comma-separated).</label>\r\n<input type="text" id="emails" name="emails" /><br />\r\n<input type="submit" id="submit" value="invite them" />\r\n</div>\r\n</form>\r\n    <div class="loading" id="okay_div">\r\n        okay! emails have been sent!\r\n    </div>\r\n</div>\r\n\r\n\r\n    <div class="loading" id="okay_div">\r\n        okay! emails have been sent!\r\n    </div>\r\n\r\n<p align="right">\r\nAlternatively, they can join the review themselves using this code: <b>')
        # SOURCE LINE 73
        __M_writer(escape(c.review.code))
        __M_writer(u'</b>\r\n</p>\r\n\r\n\r\n\r\n\r\n\r\n</div>\r\n')
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


