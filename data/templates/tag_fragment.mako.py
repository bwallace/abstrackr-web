# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121153.884976
_enable_loop = True
_template_filename = '/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/tag_fragment.mako'
_template_uri = '/tag_fragment.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        len = context.get('len', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<script>\n  \n  $("#selectable").selectable();\n\n\n  setup_submit();\n\n</script>\n\n')
        # SOURCE LINE 10
        if len(c.tags) > 0:
            # SOURCE LINE 11
            for i,tag in enumerate(c.tags):
                # SOURCE LINE 12
                __M_writer(u'            <li class=')
                __M_writer(escape("tag%s"%(i+1)))
                __M_writer(u'><a href="#">')
                __M_writer(escape(tag))
                __M_writer(u'</a></li><br/>\n')
            # SOURCE LINE 14
            __M_writer(u'        \n    </ul>\n')
            # SOURCE LINE 16
        else:
            # SOURCE LINE 17
            __M_writer(u'        (no tags yet.)\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


