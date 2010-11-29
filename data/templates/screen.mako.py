# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291053628.984
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/screen.mako'
_template_uri='/screen.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['title']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'site.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<div id="citation" style=\'float: center\'>\r\n<h2>')
        # SOURCE LINE 5
        __M_writer(escape(c.cur_citation.title))
        __M_writer(u'</h2>\r\n')
        # SOURCE LINE 6
        __M_writer(escape(c.cur_citation.authors))
        __M_writer(u'<br/><br/>\r\n')
        # SOURCE LINE 7
        __M_writer(escape(c.cur_citation.abstract))
        __M_writer(u'\r\n\r\n\r\n</div>\r\n\r\n<script type="text/javascript">\r\n    $(document).ready(function() {\r\n        $("#labelCitation").click(function() {\r\n            $("#citation").load("')
        # SOURCE LINE 15
        __M_writer(escape('/review/screen_next/%s' % c.review_id))
        __M_writer(u'");\r\n        });\r\n    });\r\n</script>\r\n\r\n\r\n<br/><br/>\r\n<center>\r\n\r\n\r\n<a id="labelCitation">Change my text</a>\r\n\r\n\r\n<a href =   "#", onclick="new Ajax.Updater(\r\n            \'citation\',\r\n            \'/review/screen_next/\',\r\n            {\r\n                onComplete:function(){ new Effect.Highlight(\'citation\', duration=4);},\r\n                asynchronous:true,\r\n                evalScripts:true\r\n            }\r\n        );"><img src = "../../accept.png"/></a> <img src = "../../reject.png"/>\r\n</center>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'screen')
        return ''
    finally:
        context.caller_stack._pop_frame()


