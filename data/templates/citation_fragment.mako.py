# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1313525454.283
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/citation_fragment.mako'
_template_uri='/citation_fragment.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['write_label']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def write_label(label):
            return render_write_label(context.locals_(__M_locals),label)
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
        __M_writer(u'<br/><br/>\r\n<b>ID:</b> ')
        # SOURCE LINE 6
        __M_writer(escape(c.cur_citation.citation_id))
        __M_writer(u'<br/><br/>\r\n\r\n')
        # SOURCE LINE 16
        __M_writer(u'\r\n\r\n\r\n')
        # SOURCE LINE 19
        if c.cur_lbl is not None:
            # SOURCE LINE 20
            if c.assignment_type == "conflict":
                # SOURCE LINE 21
                for label in c.cur_lbl:
                    # SOURCE LINE 22
                    __M_writer(u'            <b>')
                    __M_writer(escape(c.reviewer_ids_to_names_d[label.reviewer_id]))
                    __M_writer(u'</b> labeled this citation as ')
                    __M_writer(escape(write_label(label.label)))
                    __M_writer(u' on ')
                    __M_writer(escape(label.label_last_updated))
                    __M_writer(u'<br/>\r\n')
                    pass
                # SOURCE LINE 24
            else:
                # SOURCE LINE 25
                __M_writer(u'    <center>\r\n        you labeled this citation as ')
                # SOURCE LINE 26
                __M_writer(escape(write_label(c.cur_lbl.label)))
                __M_writer(u' on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u'\r\n     </center>\r\n   \r\n')
                pass
            pass
        # SOURCE LINE 31
        __M_writer(u'\r\n\r\n\r\n<script type="text/javascript">  \r\n    function setup_js(){\r\n\r\n        $("#selectable").selectable();\r\n      \r\n        $("#dialog").dialog({\r\n          height: 300,\r\n          modal: true,\r\n          autoOpen: false,\r\n          show: "blind",\r\n        });\r\n\r\n        // unbind all attached events\r\n        $("#accept").unbind();\r\n        $("#maybe").unbind();\r\n        $("#reject").unbind();\r\n        $("#pos_lbl_term").unbind();\r\n        $("#double_pos_lbl_term").unbind();\r\n        $("#neg_lbl_term").unbind();\r\n        $("#double_neg_lbl_term").unbind();\r\n        $("#submit_btn").unbind();\r\n        $("#close_btn").unbind();\r\n        $("#tag_btn").unbind();\r\n\r\n        $("#dialog").load("')
        # SOURCE LINE 58
        __M_writer(escape('/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'");\r\n        $("#tags").load("')
        # SOURCE LINE 59
        __M_writer(escape('/review/update_tags/%s' % c.cur_citation.citation_id))
        __M_writer(u'");\r\n        \r\n        // reset the timer\r\n        reset_timer();\r\n                \r\n        function markup_current(){\r\n            // reload the current citation, with markup\r\n            $("#wait").text("marking up the current citation..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 68
        __M_writer(escape('/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                });\r\n            });\r\n        }\r\n    \r\n        $("#accept").click(function() {\r\n            $(\'#buttons\').hide();\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 79
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/1", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     $(\'#buttons\').show();\r\n                     setup_js();\r\n                });\r\n            });\r\n         });   \r\n               \r\n        $("#maybe").click(function() {\r\n            $(\'#buttons\').hide();\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 92
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/0", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     $(\'#buttons\').show();\r\n                     setup_js();\r\n                });\r\n            });\r\n         });   \r\n        \r\n        $("#reject").click(function() {\r\n            $(\'#buttons\').hide();\r\n            $("#wait").text("hold on to your horses..")\r\n            $("#citation").fadeOut(\'slow\', function() {\r\n                $("#citation").load("')
        # SOURCE LINE 105
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/-1", function() {\r\n                     $("#citation").fadeIn(\'slow\');\r\n                     $("#wait").text("");\r\n                     $(\'#buttons\').show();\r\n                     setup_js();\r\n                });\r\n            });\r\n         });  \r\n         \r\n        $("#pos_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 118
        __M_writer(escape('/label_term/%s/1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being indicative of relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n            \r\n            \r\n         }); \r\n         \r\n        $("#double_pos_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 133
        __M_writer(escape('/label_term/%s/2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n        \r\n        \r\n        $("#neg_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 147
        __M_writer(escape('/label_term/%s/-1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         }); \r\n         \r\n        $("#double_neg_lbl_term").click(function() {\r\n            // call out to the controller to label the term\r\n            var term_str = $("input#term").val()\r\n            if (term_str != ""){\r\n                $.post("')
        # SOURCE LINE 160
        __M_writer(escape('/label_term/%s/-2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")\r\n                $("#label_msg").fadeIn(2000)\r\n                $("input#term").val("")\r\n                $("#label_msg").fadeOut(3000)\r\n                markup_current();\r\n            }\r\n         });\r\n         \r\n        $("#tag_btn").click(function()\r\n        {\r\n           $("#dialog" ).dialog( "open" );\r\n        });\r\n\r\n        $("#close_btn").click(function (e)\r\n        {\r\n           $("#dialog" ).dialog( "close" );\r\n        });\r\n\r\n        $("#submit_btn").click(function()\r\n        {\r\n           var tag_str = $("input#new_tag").val();\r\n\r\n           // now add all selected tags to the study\r\n           var tags = $.map($(\'.ui-selected, this\'), function(element, i) {  \r\n             return $(element).text();  \r\n           });\r\n\r\n           // push new tag, too (if it\'s empty, we\'ll drop it server-side)\r\n           tags.push(tag_str);\r\n\r\n           $.post("')
        # SOURCE LINE 191
        __M_writer(escape('/review/tag_citation/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'", {tags: tags},\r\n              function(){\r\n                $("#tags").fadeOut(\'slow\', function() {\r\n                  $("#tags").load("')
        # SOURCE LINE 194
        __M_writer(escape('/review/update_tags/%s' % c.review_id))
        __M_writer(u'", function() {\r\n                    $("#tags").load("')
        # SOURCE LINE 195
        __M_writer(escape('/review/update_tags/%s' % c.cur_citation.citation_id))
        __M_writer(u'");\r\n                    $("#tags").fadeIn(\'slow\');\r\n                  });\r\n                });\r\n\r\n                $("#dialog").load("')
        # SOURCE LINE 200
        __M_writer(escape('/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'");\r\n                }\r\n            );\r\n\r\n            $( "#dialog" ).dialog( "close" );\r\n        });\r\n\r\n        $("#new_tag").val(\'\');\r\n    }    \r\n    \r\n</script>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_write_label(context,label):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'\r\n')
        # SOURCE LINE 9
        if label == 1:
            # SOURCE LINE 10
            __M_writer(u'        <b><font color=\'green\'>"relevant"</font></b>\r\n')
            # SOURCE LINE 11
        elif label == 0:
            # SOURCE LINE 12
            __M_writer(u'        <b><font color=\'light green\'>"maybe" (?)</font></b>\r\n')
            # SOURCE LINE 13
        else:
            # SOURCE LINE 14
            __M_writer(u'        <b><font color=\'red\'>"irrelevant"</font></b>\r\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


