# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1312221473.253
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/participants.mako'
_template_uri='/reviews/participants.mako'
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
        __M_writer(u'\r\n\r\n')
        # SOURCE LINE 3
        __M_writer(u'\r\n<script language="JavaScript">\r\n    var cal = new CalendarPopup();\r\n</script>\r\n\r\n\r\n<div class="breadcrumbs">\r\n<a href="')
        # SOURCE LINE 10
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">./dashboard</a>/<a href="')
        __M_writer(escape(url(controller='review', action='show_review', id=c.review.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review.name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n\r\n<h1>')
        # SOURCE LINE 14
        __M_writer(escape(c.review.name))
        __M_writer(u': administrivia</h1>\r\n\r\n<p align="right"> \r\n<a class="tab" href="')
        # SOURCE LINE 17
        __M_writer(escape(url(controller='review', action='assignments', id=c.review.review_id)))
        __M_writer(u'">assignments</a>\r\n<a class="tab" href="')
        # SOURCE LINE 18
        __M_writer(escape(url(controller='review', action='participants', id=c.review.review_id)))
        __M_writer(u'">participants</a>\r\n</p>\r\n\r\n<div class="content">\r\nWant to invite additional reviewers? <br/>Just have them follow this link (while logged in to abstrackr): <a href="http://localhost:5000/join/')
        # SOURCE LINE 22
        __M_writer(escape(c.review.code))
        __M_writer(u'">http://localhost:5000/review/join/')
        __M_writer(escape(c.review.code))
        __M_writer(u'</a>\r\n\r\n\r\n\r\n<table class="list_table">\r\n<tr align="center"><th>person</th><th></th></tr>\r\n')
        # SOURCE LINE 28
        for participant in c.participating_reviewers:
            # SOURCE LINE 29
            __M_writer(u'       <tr>\r\n       <td>')
            # SOURCE LINE 30
            __M_writer(escape(participant.fullname))
            __M_writer(u'</td>\r\n       <td class="actions">\r\n       <a href="/review/remove_from_review/')
            # SOURCE LINE 32
            __M_writer(escape(participant.id))
            __M_writer(u'/')
            __M_writer(escape(c.review.review_id))
            __M_writer(u'")>\r\n        remove from review</a>\r\n       </tr>     \r\n       \r\n')
            pass
        # SOURCE LINE 37
        __M_writer(u'<table>\r\n\r\n</div>\r\n')
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


