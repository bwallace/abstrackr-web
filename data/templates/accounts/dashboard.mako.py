# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291062711.7249999
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/dashboard.mako'
_template_uri='/accounts/dashboard.mako'
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
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<h1>hi there, ')
        # SOURCE LINE 4
        __M_writer(escape(c.person.fullname))
        __M_writer(u'.</h1>\r\n\r\n<div class="content">\r\n\r\n\r\n<br/>\r\n\r\n<table class="list_table">\r\n\r\n')
        # SOURCE LINE 13
        if len(c.leading_projects) > 0:
            # SOURCE LINE 14
            __M_writer(u"    projects you're leading: <br/><br/>\r\n")
            # SOURCE LINE 15
            for i,review in enumerate(c.leading_projects):
                # SOURCE LINE 16
                __M_writer(u'    <tr class="')
                __M_writer(escape('odd' if i%2 else 'even'))
                __M_writer(u'">\r\n        <td><a href="')
                # SOURCE LINE 17
                __M_writer(escape(url(controller='review', action='show_review', id=review.review_id)))
                __M_writer(u'">')
                __M_writer(escape(review.name))
                __M_writer(u'</td>           \r\n    </tr>\r\n')
                pass
            # SOURCE LINE 20
            __M_writer(u'    </table>\r\n    <br/><br/>\r\n')
            pass
        # SOURCE LINE 23
        __M_writer(u'\r\n\r\n\r\n')
        # SOURCE LINE 26
        if len(c.participating_projects) > 0:
            # SOURCE LINE 27
            __M_writer(u'    projects you\'re participating in: <br/><br/>\r\n    <table class="list_table">\r\n')
            # SOURCE LINE 29
            for i,review in enumerate(c.participating_projects):
                # SOURCE LINE 30
                __M_writer(u'    <tr class="')
                __M_writer(escape('odd' if i%2 else 'even'))
                __M_writer(u'">\r\n        <td><a href="')
                # SOURCE LINE 31
                __M_writer(escape(url(controller='review', action='show_review', id=review.review_id)))
                __M_writer(u'">')
                __M_writer(escape(review.name))
                __M_writer(u'</td>          \r\n        <td><a href = "')
                # SOURCE LINE 32
                __M_writer(escape(url(controller='review', action='screen', id=review.review_id)))
                __M_writer(u'">start screening</a> </td>\r\n    </tr>\r\n')
                pass
            # SOURCE LINE 35
            __M_writer(u'    </table>\r\n')
            # SOURCE LINE 36
        else:
            # SOURCE LINE 37
            __M_writer(u"    you're not participating in any projects yet.\r\n")
            pass
        # SOURCE LINE 39
        __M_writer(u'<br/><br/>\r\nwant to <a href = "')
        # SOURCE LINE 40
        __M_writer(escape(url(controller='review', action='join_a_review')))
        __M_writer(u'">join an existing review?</a>\r\n<br/><br/>\r\nor maybe you want to <a href = "')
        # SOURCE LINE 42
        __M_writer(escape(url(controller='review', action='create_new_review')))
        __M_writer(u'">start a new review?</a>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'home')
        return ''
    finally:
        context.caller_stack._pop_frame()


