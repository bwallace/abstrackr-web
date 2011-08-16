# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1313527367.1719999
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/tag_dialog_fragment.mako'
_template_uri='/tag_dialog_fragment.mako'
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
        __M_writer(u'\r\n\r\n   <form>\r\n   <center>\r\n    new tag: <input type="text" id="new_tag" name="new_tag" /><br />\r\n   </center>\r\n   <br/>\r\n\r\n    <ul id="selectable" class="ui-selectable">\r\n')
        # SOURCE LINE 10
        for tag in c.tag_types:
            # SOURCE LINE 11
            if tag in c.tags:
                # SOURCE LINE 12
                __M_writer(u'            <li class="ui-selected">')
                __M_writer(escape(tag))
                __M_writer(u'</li>\r\n')
                # SOURCE LINE 13
            else:
                # SOURCE LINE 14
                __M_writer(u'            <li>')
                __M_writer(escape(tag))
                __M_writer(u'</li>\r\n')
                pass
            pass
        # SOURCE LINE 17
        __M_writer(u'    </ul>\r\n   </center>\r\n\r\n   <div class="actions" style="text-align: right;">\r\n      <input id="submit_btn" type="button" value="tag" />\r\n   </div>\r\n   </form>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


