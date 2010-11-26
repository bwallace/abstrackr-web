# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1290805474.105
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/welcome.mako'
_template_uri='/accounts/welcome.mako'
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
        __M_writer(u'\r\n\r\n<h2>hi there, ')
        # SOURCE LINE 4
        __M_writer(escape(c.person.fullname))
        __M_writer(u"</h2>\r\n\r\nprojects you're participating in: <br/>\r\n")
        # SOURCE LINE 7
        for review in c.participating_projects:
            # SOURCE LINE 8
            __M_writer(u'    ')
            __M_writer(escape(review.name))
            __M_writer(u'           <a href = "')
            __M_writer(escape(url(controller='account', action='screen', id=review.review_id)))
            __M_writer(u'">screen!</a> <br/>\r\n')
            pass
        # SOURCE LINE 10
        __M_writer(u"\r\n\r\n<br/>\r\nprojects you're leading: ")
        # SOURCE LINE 13
        __M_writer(escape(c.leading_projects))
        __M_writer(u'\r\n<br/><br/>\r\nwant to <a href = "')
        # SOURCE LINE 15
        __M_writer(escape(url(controller='review', action='join_a_review')))
        __M_writer(u'">join an existing review?</a>\r\n<br/><br/>\r\nor maybe you want to <a href = "')
        # SOURCE LINE 17
        __M_writer(escape(url(controller='review', action='create_new_review')))
        __M_writer(u'">start a new review?</a>\r\n')
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


