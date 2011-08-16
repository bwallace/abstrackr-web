# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1311799909.5480001
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/recover.mako'
_template_uri='/accounts/recover.mako'
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
    return runtime._inherit_from(context, u'../site_out.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n\r\n<div class="content">\r\n\r\nForgot your password, huh? tsk, tsk. <br/><br/>\r\nEnter your email below and we\'ll send you instructions to reset it. \r\n<br/><br/>\r\n    <center>\r\n\r\n<table class="form_table">\r\n ')
        # SOURCE LINE 13
        __M_writer(escape(h.form(url(controller='account', action='reset_password'))))
        __M_writer(u'\r\n    <tr><td><label>your email:</td> <td>')
        # SOURCE LINE 14
        __M_writer(escape(h.text('email')))
        __M_writer(u'</label></td></tr>\r\n    <tr><td></td><td>')
        # SOURCE LINE 15
        __M_writer(escape(h.submit('post', 'reset my password!')))
        __M_writer(u'</td></tr>\r\n  ')
        # SOURCE LINE 16
        __M_writer(escape(h.end_form()))
        __M_writer(u'\r\n  </table>\r\n  <font color="black">')
        # SOURCE LINE 18
        __M_writer(escape(c.pwd_msg))
        __M_writer(u'</font>\r\n  </center>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'recover password')
        return ''
    finally:
        context.caller_stack._pop_frame()


