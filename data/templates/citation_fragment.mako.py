# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291053630.9530001
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/citation_fragment.mako'
_template_uri='/citation_fragment.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n<h2>')
        # SOURCE LINE 2
        __M_writer(escape(c.cur_citation.title))
        __M_writer(u'</h2>\r\n')
        # SOURCE LINE 3
        __M_writer(escape(c.cur_citation.authors))
        __M_writer(u'<br/><br/>\r\n')
        # SOURCE LINE 4
        __M_writer(escape(c.cur_citation.abstract))
        __M_writer(u'\r\n\r\n\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


