# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1311799904.5639999
_template_filename=u'C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/site_out.mako'
_template_uri=u'/accounts/../site_out.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['title']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\r\n<html>\r\n    <head>\r\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n        <link rel="stylesheet" href="/stylesheet.css">\r\n        <script type="text/javascript" src="/scripts/jquery-1.4.4.js"></script>\r\n        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>\r\n        <title>abstrackr: ')
        # SOURCE LINE 9
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\r\n    </head>\r\n    <body>\r\n\r\n        <p align="left">\r\n        <img src = "../../abstrackr.png"></img>\r\n        </p>\r\n       \r\n\t\r\n<!-- *** BEGIN page content *** -->\r\n')
        # SOURCE LINE 19
        __M_writer(escape(self.body()))
        __M_writer(u'\r\n<!-- *** END page content *** -->\r\n\r\n    </body>\r\n</html>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


