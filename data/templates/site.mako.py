# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121142.770538
_enable_loop = True
_template_filename = u'/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/site.mako'
_template_uri = u'/accounts/../site.mako'
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
        __M_writer(u'\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n        <link rel="stylesheet" href="/stylesheet.css">\n        <link rel="stylesheet" href="/jquery-ui-1.8.15.custom.css">\n\n        <script type="text/javascript" src="/scripts/jquery-1.6.2.min.js"></script>\n        <script type="text/javascript" src="/scripts/jquery-ui-1.8.15.custom.min.js"></script>\n        <script type="text/javascript" src="/scripts/jqModal.js"></script>\n        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>\n        <script type="text/javascript" src="/scripts/jquery.ui.selectable.js"></script>\n  \n        <title>abstrackr: ')
        # SOURCE LINE 15
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\n    </head>\n    <body>\n\n        <p align="left">\n        <img src = "http://sunfire34.eecs.tufts.edu/abstrackr.png"></img>\n        </p>\n       \n\t<div id="login-header">\n\t <a href="/">home</a>  || <a href="/account/my_account">my account</a> || <a href="/account/logout">sign out</a> || <a href="/help/">help</a> || <a href="/help/citing.html">citing abstrackr</a>\n\t</div>\n\t\n<!-- *** BEGIN page content *** -->\n')
        # SOURCE LINE 28
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


