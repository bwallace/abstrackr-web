# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1292875740.8929999
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
        __M_writer(escape(c.cur_citation.marked_up_title))
        __M_writer(u'</h2>\r\n')
        # SOURCE LINE 3
        __M_writer(escape(c.cur_citation.authors))
        __M_writer(u'<br/><br/>\r\n')
        # SOURCE LINE 4
        __M_writer(escape(c.cur_citation.marked_up_abstract))
        __M_writer(u'<br/><br/>\r\n<b>keywords:</b> ')
        # SOURCE LINE 5
        __M_writer(escape(c.cur_citation.keywords))
        __M_writer(u'<br/><br/>\r\n<b>refman ID:</b> ')
        # SOURCE LINE 6
        __M_writer(escape(c.cur_citation.refman_id))
        __M_writer(u'<br/><br/>\r\n\r\n')
        # SOURCE LINE 8
        if c.cur_lbl is not None:
            # SOURCE LINE 9
            __M_writer(u'<center>\r\n')
            # SOURCE LINE 10
            if c.cur_lbl.label == 1:
                # SOURCE LINE 11
                __M_writer(u'        you labeled this citation as <b><font color=\'green\'>"relevant"</font></b> on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u'\r\n')
                # SOURCE LINE 12
            elif c.cur_lbl.label == 0:
                # SOURCE LINE 13
                __M_writer(u'        you labeled this citation as <b><font color=\'light green\'>"maybe" (?)</font></b> on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u'\r\n')
                # SOURCE LINE 14
            else:
                # SOURCE LINE 15
                __M_writer(u'        you labeled this citation as <b><font color=\'red\'>"irrelevant"</font></b> on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u' \r\n')
                pass
            # SOURCE LINE 17
            __M_writer(u' </center>\r\n')
            pass
        # SOURCE LINE 19
        __M_writer(u'\r\n<script type="text/javascript">  \r\n    function setup_js(){\r\n\r\n        // unbind all attached events\r\n        $("#accept").unbind();\r\n        $("#maybe").unbind();\r\n        $("#reject").unbind();\r\n        $("#pos_lbl_term").unbind();\r\n        $("#double_pos_lbl_term").unbind();\r\n        $("#neg_lbl_term").unbind();\r\n        $("#double_neg_lbl_term").unbind();\r\n\r\n        // reset the timer\r\n        reset_timer();\r\n                \r\n        function markup_current(){\r\n            // reload the current citation, with markup\r\n            $("#wait").text("marking up the current citation..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 39
        __M_writer(escape('/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                });\r\n            });\r\n        }\r\n    \r\n    \r\n        $("#accept").click(function() {\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 50
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/1", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     setup_js();\r\n                });\r\n            });\r\n         });   \r\n               \r\n        $("#maybe").click(function() {\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 61
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/0", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     setup_js();\r\n                });\r\n            });\r\n         });   \r\n        \r\n        $("#reject").click(function() {\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 72
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/-1", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     setup_js();\r\n                });\r\n            });\r\n         });  \r\n         \r\n        $("#pos_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 84
        __M_writer(escape('/label_term/%s/1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being indicative of relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n            \r\n            \r\n         }); \r\n         \r\n        $("#double_pos_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 99
        __M_writer(escape('/label_term/%s/2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n        \r\n\r\n        $("#neg_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 113
        __M_writer(escape('/label_term/%s/-1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n         \r\n        $("#double_neg_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 126
        __M_writer(escape('/label_term/%s/-2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n    }    \r\n    \r\n</script>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


