# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1290541592.891
_template_filename=u'C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/site.mako'
_template_uri=u'/site.mako'
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
        __M_writer(u'\r\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\r\n<html>\r\n    <head>\r\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n        <title>abstrackr: ')
        # SOURCE LINE 6
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\r\n    </head>\r\n    <body>\r\n        <img src = "../images/abstrackr.png">\r\n        <h1>')
        # SOURCE LINE 10
        __M_writer(escape(self.title()))
        __M_writer(u'</h1>\r\n\r\n<!-- *** BEGIN page content *** -->\r\n')
        # SOURCE LINE 13
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


