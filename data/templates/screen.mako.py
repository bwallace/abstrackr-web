# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1292624379.1459999
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
        url = context.get('url', UNDEFINED)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<script language="javascript">\r\nvar seconds = 1;\r\nsetTimeout(update_timer, 1000);\r\n\r\nfunction reset_timer(){\r\n  seconds = 1; // start at one\r\n  setTimeout(update_timer, 1000);\r\n}\r\n\r\nfunction update_timer(){\r\n  seconds +=1;\r\n  setTimeout(update_timer, 1000);\r\n}\r\n\r\nfunction awesome(){\r\n  alert("eggs");\r\n  alert(eval("\'')
        # SOURCE LINE 20
        __M_writer(escape(c.cur_citation.title))
        __M_writer(u'\'"));\r\n}\r\n  \r\n</script>\r\n\r\n<div class="breadcrumbs">\r\n./<a href="')
        # SOURCE LINE 26
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">dashboard</a>\r\n          /<a href="')
        # SOURCE LINE 27
        __M_writer(escape(url(controller='review', action='show_review', id=c.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review_name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n')
        # SOURCE LINE 30
        if c.cur_lbl is not None:
            # SOURCE LINE 31
            __M_writer(u'  ALREADY LABELED ')
            __M_writer(escape(c.cur_lbl.label))
            __M_writer(u'\r\n')
            pass
        # SOURCE LINE 33
        __M_writer(u'\r\n\r\n<div id="citation" class="content" style=\'float: center\'>\r\n<h2>')
        # SOURCE LINE 36
        __M_writer(escape(c.cur_citation.marked_up_title))
        __M_writer(u'</h2>\r\n')
        # SOURCE LINE 37
        __M_writer(escape(c.cur_citation.authors))
        __M_writer(u'<br/><br/>\r\n')
        # SOURCE LINE 38
        __M_writer(escape(c.cur_citation.marked_up_abstract))
        __M_writer(u'<br/><br/>\r\n<b>keywords:</b> ')
        # SOURCE LINE 39
        __M_writer(escape(c.cur_citation.keywords))
        __M_writer(u'<br/><br/>\r\n<b>refman ID:</b> ')
        # SOURCE LINE 40
        __M_writer(escape(c.cur_citation.refman_id))
        __M_writer(u'<br/><br/>\r\n\r\n\r\n<script type="text/javascript">    \r\n    function setup_js(){\r\n    \r\n        function markup_current(){\r\n            // reload the current citation, with markup\r\n            $("#wait").text("marking up the current citation..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 50
        __M_writer(escape('/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                });\r\n            });\r\n        }\r\n    \r\n    \r\n        $("#accept").click(function() {\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 61
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/1", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     setup_js();\r\n                });\r\n            });\r\n         });   \r\n               \r\n        $("#maybe").click(function() {\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 72
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/0", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     setup_js();\r\n                });\r\n            });\r\n         });   \r\n        \r\n         \r\n        $("#reject").click(function() {\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 84
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/-1", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     setup_js();\r\n                });\r\n            });\r\n         });  \r\n         \r\n        $("#pos_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 96
        __M_writer(escape('/label_term/%s/1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being indicative of relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n            \r\n            \r\n         }); \r\n         \r\n        $("#double_pos_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 111
        __M_writer(escape('/label_term/%s/2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n        \r\n\r\n        $("#neg_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 125
        __M_writer(escape('/label_term/%s/-1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n         \r\n        $("#double_neg_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 138
        __M_writer(escape('/label_term/%s/-2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n    }    \r\n\r\n    $(document).ready(function() { \r\n        setup_js();\r\n    });\r\n    \r\n</script>\r\n</div>\r\n\r\n<center>\r\n<div id="wait"></div>\r\n</center>\r\n\r\n<br/><br/>\r\n<center>\r\n\r\n\r\n<a href="#" id="accept"><img src = "../../accept.png"/></a> \r\n<a href="#" id="maybe"><img src = "../../maybe.png"/></a> \r\n<a href="#" id="reject"><img src = "../../reject.png"/></a> \r\n\r\n<br/><br/><br/>\r\n<table>\r\n<tr>\r\n<td>\r\n<div id="label_terms" class="summary_heading">\r\n<label>term: ')
        # SOURCE LINE 172
        __M_writer(escape(h.text('term')))
        __M_writer(u'</label> \r\n</td>\r\n<td width="10"></td>\r\n<td>\r\n<a href="#" id="pos_lbl_term"><img src = "../../thumbs_up.png" border="2" alt="indicative of relevance"></a>\r\n</td>\r\n<td>\r\n<a href="#" id="double_pos_lbl_term"><img src = "../../two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>\r\n</td>\r\n<td width="10"></td>\r\n<td>\r\n<a href="#" id="neg_lbl_term"><img src = "../../thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>\r\n</td>\r\n<td>\r\n<a href="#" id="double_neg_lbl_term"><img src = "../../two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>\r\n</td>\r\n</tr>\r\n</div>\r\n\r\n<div id="label_msg"></div>\r\n</center>')
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


