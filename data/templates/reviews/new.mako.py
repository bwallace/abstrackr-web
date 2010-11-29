# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291063013.0880001
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/new.mako'
_template_uri='/reviews/new.mako'
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
        h = context.get('h', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<div class="content">\r\n<center>\r\n<table class="form_table">\r\n ')
        # SOURCE LINE 7
        __M_writer(escape(h.form(url(controller='review', action='create_review_handler'), multipart=True)))
        __M_writer(u'\r\n    <tr><td><label>project name:</td><td> ')
        # SOURCE LINE 8
        __M_writer(escape(h.text('name')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>project description:</td> <td>')
        # SOURCE LINE 9
        __M_writer(escape(h.textarea('description', rows="10", cols="40")))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>upload file:</td> <td>')
        # SOURCE LINE 10
        __M_writer(escape(h.file('db')))
        __M_writer(u' </label></td></tr>\r\n    \r\n    <tr><td></td><td>')
        # SOURCE LINE 12
        __M_writer(escape(h.submit('post', 'Create new review')))
        __M_writer(u'</td></tr>\r\n    \r\n  ')
        # SOURCE LINE 14
        __M_writer(escape(h.end_form()))
        __M_writer(u'\r\n</table>\r\n</center>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'new review')
        return ''
    finally:
        context.caller_stack._pop_frame()


