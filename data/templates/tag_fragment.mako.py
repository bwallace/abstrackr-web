# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1313526545.744
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/tag_fragment.mako'
_template_uri='/tag_fragment.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<script>\r\n  \r\n  $("#selectable").selectable();\r\n\r\n\r\n  setup_submit();\r\n\r\n</script>\r\n\r\n\r\n')
        # SOURCE LINE 11
        if len(c.tags) > 0:
            # SOURCE LINE 12
            for tag in c.tags:
                # SOURCE LINE 13
                __M_writer(u'            ')
                __M_writer(escape(tag))
                __M_writer(u'<br/>\r\n')
                pass
            # SOURCE LINE 15
        else:
            # SOURCE LINE 16
            __M_writer(u'        (no tags yet.)\r\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


