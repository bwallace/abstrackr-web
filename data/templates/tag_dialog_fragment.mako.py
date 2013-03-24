# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121153.92796
_enable_loop = True
_template_filename = '/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/tag_dialog_fragment.mako'
_template_uri = '/tag_dialog_fragment.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n  \n   <form>\n   <center>\n    new tag: <input type="text" id="new_tag" name="new_tag" /><br />\n   </center>\n   <br/>\n\n    <ul id="selectable" class="ui-selectable">\n')
        # SOURCE LINE 11
        for tag in c.tag_types:
            # SOURCE LINE 12
            if tag in c.tags:
                # SOURCE LINE 13
                __M_writer(u'            <li class="ui-selected">')
                __M_writer(escape(tag))
                __M_writer(u'</li>\n')
                # SOURCE LINE 14
            else:
                # SOURCE LINE 15
                if not c.tag_privacy:
                    # SOURCE LINE 16
                    __M_writer(u'                  <li>')
                    __M_writer(escape(tag))
                    __M_writer(u'</li>\n')
        # SOURCE LINE 20
        __M_writer(u'    </ul>\n   </center>\n\n   <div class="actions" style="text-align: right;">\n      <input id="submit_btn" type="button" value="tag" />\n   </div>\n   </form>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


