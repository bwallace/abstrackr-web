# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121159.243081
_enable_loop = True
_template_filename = u'/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/site_out.mako'
_template_uri = u'/accounts/../site_out.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = ['title']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n        <link rel="stylesheet" href="/stylesheet.css">\n        <script type="text/javascript" src="/scripts/jquery-1.4.4.js"></script>\n        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>\n        <title>abstrackr: ')
        # SOURCE LINE 9
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\n    </head>\n    <body>\n\n        <p align="left">\n        <img src = "../../abstrackr.png"></img>\n        </p>\n       \n\t\n<!-- *** BEGIN page content *** -->\n')
        # SOURCE LINE 19
        __M_writer(escape(self.body()))
        __M_writer(u'\n<!-- *** END page content *** -->\n\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


