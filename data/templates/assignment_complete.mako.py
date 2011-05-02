# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1303136275.3
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/assignment_complete.mako'
_template_uri='/assignment_complete.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u"\r\n<h2>Huzzah! You've completed this assignment.</h2> <br/></br><h2> Nice work.</h2>\r\n\r\n\r\n")
        return ''
    finally:
        context.caller_stack._pop_frame()


