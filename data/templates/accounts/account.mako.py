# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1312920292.227
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/account.mako'
_template_uri='/accounts/account.mako'
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
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n\r\n')
        # SOURCE LINE 3
        __M_writer(u'\r\n\r\n<div class="content">\r\n\r\n\r\n<h2>')
        # SOURCE LINE 8
        __M_writer(escape(c.account_msg))
        __M_writer(u'</h2>\r\n\r\nto change your password:\r\n    \r\n<table class="form_table">\r\n ')
        # SOURCE LINE 13
        __M_writer(escape(h.form(url(controller='account', action='change_password'))))
        __M_writer(u'\r\n    <tr><td><label>new password:</td> <td>')
        # SOURCE LINE 14
        __M_writer(escape(h.text('password', type='password')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td><label>confirm new password:</td> <td>')
        # SOURCE LINE 15
        __M_writer(escape(h.text('password_confirm', type='password')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td></td><td>')
        # SOURCE LINE 16
        __M_writer(escape(h.submit('post', 'change password')))
        __M_writer(u'</td></tr>\r\n  ')
        # SOURCE LINE 17
        __M_writer(escape(h.end_form()))
        __M_writer(u'\r\n  </table>\r\n  </center>\r\n</div>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'my account')
        return ''
    finally:
        context.caller_stack._pop_frame()


