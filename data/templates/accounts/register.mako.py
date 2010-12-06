# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291315627.1949999
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/register.mako'
_template_uri='/accounts/register.mako'
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
        __M_writer(u'\r\n\r\n\r\n<div class="content">\r\n    <center>\r\n    \r\n<table class="form_table">\r\n ')
        # SOURCE LINE 9
        __M_writer(escape(h.form(url(controller='account', action='create_account_handler'))))
        __M_writer(u'\r\n    <tr><td><label>first name:</td> <td>')
        # SOURCE LINE 10
        __M_writer(escape(h.text('first name')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>last name:</td> <td>')
        # SOURCE LINE 11
        __M_writer(escape(h.text('last name')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>how many SRs have you participated in?:</td> <td>')
        # SOURCE LINE 12
        __M_writer(escape(h.text('experience', size=2)))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>email:</td> <td>')
        # SOURCE LINE 13
        __M_writer(escape(h.text('email')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>username:</td> <td>')
        # SOURCE LINE 14
        __M_writer(escape(h.text('username')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>password:</td> <td>')
        # SOURCE LINE 15
        __M_writer(escape(h.text('password', type='password')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td></td><td>')
        # SOURCE LINE 16
        __M_writer(escape(h.submit('post', 'sign me up!')))
        __M_writer(u'</td></tr>\r\n  ')
        # SOURCE LINE 17
        __M_writer(escape(h.end_form()))
        __M_writer(u'\r\n  </table>\r\n  </center>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'register')
        return ''
    finally:
        context.caller_stack._pop_frame()


