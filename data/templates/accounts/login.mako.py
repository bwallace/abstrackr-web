# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1311799904.5009999
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/login.mako'
_template_uri='/accounts/login.mako'
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
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n')
        # SOURCE LINE 4
        if c.login_counter > 1:
            # SOURCE LINE 5
            __M_writer(u'    Incorrect Username or Password\r\n')
            pass
        # SOURCE LINE 7
        __M_writer(u'\r\n<center>\r\n<div class="content">\r\n<form action="')
        # SOURCE LINE 10
        __M_writer(escape(url(controller='account', action='login_handler'
,came_from=c.came_from, __logins=c.login_counter)))
        # SOURCE LINE 11
        __M_writer(u'" method="POST">\r\n<label for="login">username</label>\r\n<input type="text" id="login" name="login" /><br />\r\n<label for="password">password</label>\r\n<input type="password" id="password" name="password" /><br />\r\n<input type="submit" id="submit" value="Submit" />\r\n</form>\r\n</div>\r\n\r\ndon\'t have an account yet? <a href="')
        # SOURCE LINE 20
        __M_writer(escape(url(controller='account', action='create_account')))
        __M_writer(u'">register here</a>.<br/>\r\nor maybe you forget your password? <a href="')
        # SOURCE LINE 21
        __M_writer(escape(url(controller='account', action='recover_password')))
        __M_writer(u'">recover it</a>.\r\n</center>')
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


