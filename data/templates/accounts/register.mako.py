# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1290544258.6110001
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
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<center>\r\n<form action="')
        # SOURCE LINE 5
        __M_writer(escape(url(controller='account', action='create_account_handler')))
        __M_writer(u'" method="POST">\r\n\r\n<label for="first name">first name</label>\r\n<input type="text" id="first name" name="first name" /><br />\r\n\r\n<label for = "last name">last name</label>\r\n<input type="text" id="last name" name="last name" /><br />\r\n\r\n<label for = "email">email</label>\r\n<input type="text" id="email" name="email" /><br />\r\n\r\n<label for="username">username</label>\r\n<input type="text" id="username" name="username" /><br />\r\n<label for="password">password</label>\r\n<input type="password" id="password" name="password" /><br />\r\n\r\n<input type="submit" id="submit" value="Submit" />\r\n\r\n</form>\r\n\r\n\r\n</center>')
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


