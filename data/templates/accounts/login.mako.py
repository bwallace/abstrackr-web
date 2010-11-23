# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1290533976.641
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/login.mako'
_template_uri='/accounts/login.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        if c.login_counter > 1:
            # SOURCE LINE 2
            __M_writer(u'    Incorrect Username or Password\r\n')
            pass
        # SOURCE LINE 4
        __M_writer(u'\r\n<form action="')
        # SOURCE LINE 5
        __M_writer(escape(url(controller='account', action='login_handler'
,came_from=c.came_from, __logins=c.login_counter)))
        # SOURCE LINE 6
        __M_writer(u'" method="POST">\r\n<label for="login">Username:</label>\r\n<input type="text" id="login" name="login" /><br />\r\n<label for="password">Password:</label>\r\n<input type="password" id="password" name="password" /><br />\r\n<input type="submit" id="submit" value="Submit" />\r\n</form>')
        return ''
    finally:
        context.caller_stack._pop_frame()


