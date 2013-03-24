# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121152.071898
_enable_loop = True
_template_filename = '/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/citation_fragment.mako'
_template_uri = '/citation_fragment.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = ['write_label']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def write_label(label):
            return render_write_label(context.locals_(__M_locals),label)
        c = context.get('c', UNDEFINED)
        dir = context.get('dir', UNDEFINED)
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<h2>')
        __M_writer(escape(c.cur_citation.marked_up_title))
        __M_writer(u'</h2>\n\n')
        # SOURCE LINE 3
        if c.show_journal==True:
            # SOURCE LINE 4
            __M_writer(u'    <i>Journal: ')
            __M_writer(escape(c.cur_citation.journal))
            __M_writer(u'</i><br /><br />\n')
        # SOURCE LINE 6
        __M_writer(u'\n')
        # SOURCE LINE 7
        if c.show_authors==True:
            # SOURCE LINE 8
            __M_writer(u'    Authors: ')
            __M_writer(escape(c.cur_citation.authors))
            __M_writer(u'<br/><br/>\n')
        # SOURCE LINE 10
        __M_writer(u'\n')
        # SOURCE LINE 11
        __M_writer(escape(c.cur_citation.marked_up_abstract))
        __M_writer(u'<br/><br/>\n\n')
        # SOURCE LINE 13
        if c.show_keywords==True:
            # SOURCE LINE 14
            __M_writer(u'    <b>keywords:</b> ')
            __M_writer(escape(c.cur_citation.keywords))
            __M_writer(u'<br/><br/>\n')
        # SOURCE LINE 16
        __M_writer(u'\n<b>ID:</b> ')
        # SOURCE LINE 17
        __M_writer(escape(c.cur_citation.citation_id))
        __M_writer(u'<br/><br/>\n\n\n')
        # SOURCE LINE 28
        __M_writer(u'\n\n')
        # SOURCE LINE 30
        if c.cur_lbl is not None:
            # SOURCE LINE 31
            if c.assignment_type == "conflict":
                # SOURCE LINE 32
                for label in c.cur_lbl:
                    # SOURCE LINE 33
                    if "consensus_review" in dir(c) and c.consensus_review and len(c.cur_lbl)==1:
                        # SOURCE LINE 34
                        __M_writer(u'              a <b>consensus</b> label of ')
                        __M_writer(escape(write_label(label.label)))
                        __M_writer(u' was given for this citation on on ')
                        __M_writer(escape(label.label_last_updated))
                        __M_writer(u'<br/>\n')
                        # SOURCE LINE 35
                    else:
                        # SOURCE LINE 36
                        __M_writer(u'              <b>')
                        __M_writer(escape(c.reviewer_ids_to_names_d[label.reviewer_id]))
                        __M_writer(u'</b> labeled this citation as ')
                        __M_writer(escape(write_label(label.label)))
                        __M_writer(u' on ')
                        __M_writer(escape(label.label_last_updated))
                        __M_writer(u'<br/>\n')
                # SOURCE LINE 39
            else:
                # SOURCE LINE 40
                __M_writer(u'      <center>\n          you labeled this citation as ')
                # SOURCE LINE 41
                __M_writer(escape(write_label(c.cur_lbl.label)))
                __M_writer(u' on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u'\n       </center>\n')
        # SOURCE LINE 45
        __M_writer(u'\n\n\n<script type="text/javascript">  \n\n    function populate_notes(){\n')
        # SOURCE LINE 51
        if "notes" in dir(c) and c.notes is not None:
            # SOURCE LINE 52
            __M_writer(u'          $("#pop_notes").val(\'')
            __M_writer(escape(c.notes.population))
            __M_writer(u'\'); \n          $("textarea#general_notes").val(\'')
            # SOURCE LINE 53
            __M_writer(escape(c.notes.general))
            __M_writer(u'\');\n          $("textarea#ic_notes").val(\'')
            # SOURCE LINE 54
            __M_writer(escape(c.notes.ic))
            __M_writer(u'\');\n          $("textarea#outcome_notes").val(\'')
            # SOURCE LINE 55
            __M_writer(escape(c.notes.outcome))
            __M_writer(u"');\n")
            # SOURCE LINE 56
        else:
            # SOURCE LINE 57
            __M_writer(u'          $("#pop_notes").val(\'\'); \n          $("textarea#general_notes").val(\'\');\n          $("textarea#ic_notes").val(\'\');\n          $("textarea#outcome_notes").val(\'\');\n')
        # SOURCE LINE 62
        __M_writer(u'    }\n\n    function setup_submit(){\n      $("#selectable").selectable();     \n      $("#submit_btn").unbind();\n      $("#submit_btn").click(function()\n      {\n          \n         var tag_str = $("input#new_tag").val();\n\n         // now add all selected tags to the study\n         var tags = $.map($(\'.ui-selected, this\'), function(element, i) {  \n           return $(element).text();  \n         });\n\n         // push new tag, too (if it\'s empty, we\'ll drop it server-side)\n         tags.push(tag_str);\n\n         $.post("')
        # SOURCE LINE 80
        __M_writer(escape('/review/tag_citation/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'", {tags: tags},\n            function()\n            {\n              $("#tags").fadeOut(\'slow\', function() {\n                $("#tags").load("')
        # SOURCE LINE 84
        __M_writer(escape('/review/update_tags/%s/%s' % (c.cur_citation.citation_id, c.tag_privacy)))
        __M_writer(u'", \n                function() {\n                  $("#tags").fadeIn(\'slow\');\n                });\n              });\n              \n              $("#dialog").load("')
        # SOURCE LINE 90
        __M_writer(escape('/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'");\n            }\n         );\n\n         $( "#dialog" ).dialog( "close" );\n      });\n\n\n\n      /** adding note-taking functionality **/\n\n      $("#save_notes_btn").unbind();\n      $("#save_notes_btn").click(function()\n      {\n        // something like\n         var general_notes = $("#general_notes").val();\n         var pop_notes =  $("#pop_notes").val();\n         var ic_notes = $("#ic_notes").val();\n         var outcome_notes = $("#outcome_notes").val();\n\n\n         $.post("')
        # SOURCE LINE 111
        __M_writer(escape('/review/add_notes/%s' % c.cur_citation.citation_id))
        __M_writer(u'",\n                    {"general_notes": general_notes, "population_notes":pop_notes, "ic_notes":ic_notes,\n                    "outcome_notes":outcome_notes}, function() {\n                        $("#notes-status").html("<font color=\'green\'>notes added.</font>");\n                        $( "#notes-dialog" ).dialog( "close" );\n                        $("#notes-status").html("");\n                    });\n\n      });\n\n      /** end notes functionality **/\n\n\n\n      $("#tag_btn").click(function()\n      {\n         $("#dialog" ).dialog( "open" );\n      });\n\n      $("#close_btn").unbind();\n      $("#close_btn").click(function (e)\n      {\n         // I actually don\'t know where \'close_btn\' is defined...\n         // we close them both here.\n         $("#dialog" ).dialog( "close" );\n         $("#notes-dialog" ).dialog( "close" );\n      });\n\n      $("#notes_btn").unbind();\n      $("#notes_btn").click(function()\n      {\n         $("#notes-dialog" ).dialog("open");\n      });\n\n      $("#new_tag").val(\' \');\n\n    } \n\n    function setup_js(){\n      \n        $("#dialog").dialog({\n          height: 300,\n          modal: true,\n          autoOpen: false,\n          show: "blind",\n        });\n\n        // unbind all attached events\n        $("#accept").unbind();\n        $("#maybe").unbind();\n        $("#reject").unbind();\n        $("#pos_lbl_term").unbind();\n        $("#double_pos_lbl_term").unbind();\n        $("#neg_lbl_term").unbind();\n        $("#double_neg_lbl_term").unbind();\n        $("#submit_btn").unbind();\n        $("#close_btn").unbind();\n        $("#tag_btn").unbind();\n\n        $("#dialog").load(\n            "')
        # SOURCE LINE 171
        __M_writer(escape('/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'",\n            function() {\n              setup_submit();\n              populate_notes();\n            }\n        );\n\n        $("#tags").load("')
        # SOURCE LINE 178
        __M_writer(escape('/review/update_tags/%s/%s' % (c.cur_citation.citation_id, c.tag_privacy)))
        __M_writer(u'");\n        \n        // reset the timer\n        reset_timer();\n                \n        function markup_current(){\n            // reload the current citation, with markup\n            $("#wait").text("marking up the current citation..")\n            $("#citation").fadeOut(\'slow\', function() {\n                $("#citation").load("')
        # SOURCE LINE 187
        __M_writer(escape('/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'", function() {\n                     $("#citation").fadeIn(\'slow\');\n                     $("#wait").text("");\n                });\n            });\n        }\n\n\n        function label_cur_citation(lbl_str){\n            $("#citation").fadeOut(\'fast\', function() {\n                  if (!(we_are_reviewing_a_label()) && is_perpetual_assignment()){\n                    // try to load the next citation\n                    // this call will in turn call get_next_citation\n                    // once loading is complete\n                    load_next_citation();\n                  }\n\n                  $.post("')
        # SOURCE LINE 204
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/" + lbl_str, function(data){\n                      if (we_are_reviewing_a_label()){\n                        // in the case that we are re-labeling a citation, \n                        // this the label method will return the citation fragment.\n                        $(\'#citation\').html(data);\n                        $(\'#citation\').fadeIn();\n                        setup_js();\n                        still_loading = false;\n                      } \n                      else if (!(is_perpetual_assignment())) {\n                        load_next_citation();\n                      }\n                      else {\n                        //alert(data);\n                        $(\'#progress\').html(data);\n                      }\n                  });\n            });      \n        }\n\n\n        $("#accept").click(function() {\n          label_cur_citation("1");\n        });\n               \n\n        $("#maybe").click(function() {\n          label_cur_citation("0");\n        });\n        \n         \n        $("#reject").click(function() {\n          label_cur_citation("-1");\n        });\n\n        $("#pos_lbl_term").click(function() {\n            // call out to the controller to label the term\n            var term_str = $("input#term").val()\n            if (term_str != ""){\n                $.post("')
        # SOURCE LINE 243
        __M_writer(escape('/label_term/%s/1' % c.review_id))
        __M_writer(u'", {term: term_str});\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being indicative of relevance.")\n                $("#label_msg").fadeIn(2000)\n                $("input#term").val("")\n                $("#label_msg").fadeOut(3000)\n                markup_current();\n            }\n            \n            \n         }); \n         \n        $("#double_pos_lbl_term").click(function() {\n            // call out to the controller to label the term\n            var term_str = $("input#term").val()\n            if (term_str != ""){\n                $.post("')
        # SOURCE LINE 258
        __M_writer(escape('/label_term/%s/2' % c.review_id))
        __M_writer(u'", {term: term_str});\n                $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")\n                $("#label_msg").fadeIn(2000)\n                $("input#term").val("")\n                $("#label_msg").fadeOut(3000)\n                markup_current();\n            }\n         }); \n        \n        \n        $("#neg_lbl_term").click(function() {\n            // call out to the controller to label the term\n            var term_str = $("input#term").val()\n            if (term_str != ""){\n                $.post("')
        # SOURCE LINE 272
        __M_writer(escape('/label_term/%s/-1' % c.review_id))
        __M_writer(u'", {term: term_str});\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")\n                $("#label_msg").fadeIn(2000)\n                $("input#term").val("")\n                $("#label_msg").fadeOut(3000)\n                markup_current();\n            }\n         }); \n         \n        $("#double_neg_lbl_term").click(function() {\n            // call out to the controller to label the term\n            var term_str = $("input#term").val()\n            if (term_str != ""){\n                $.post("')
        # SOURCE LINE 285
        __M_writer(escape('/label_term/%s/-2' % c.review_id))
        __M_writer(u'", {term: term_str});\n                $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")\n                $("#label_msg").fadeIn(2000)\n                $("input#term").val("")\n                $("#label_msg").fadeOut(3000)\n                markup_current();\n            }\n         });\n\n\n')
        # SOURCE LINE 295
        if 'assignment' in dir(c):
            # SOURCE LINE 296
            if c.assignment.num_assigned and c.assignment.num_assigned > 0:
                # SOURCE LINE 297
                __M_writer(u'            $("#progress").html("you\'ve screened <b>')
                __M_writer(escape(c.assignment.done_so_far))
                __M_writer(u'</b> out of <b>')
                __M_writer(escape(c.assignment.num_assigned))
                __M_writer(u'</b> so far (nice going!)");\n')
                # SOURCE LINE 298
            else:
                # SOURCE LINE 299
                __M_writer(u'            $("#progress").html("you\'ve screened <b>')
                __M_writer(escape(c.assignment.done_so_far))
                __M_writer(u'</b> abstracts thus far (keep it up!)");\n')
            # SOURCE LINE 301
        else:
            # SOURCE LINE 302
            __M_writer(u'          $("#progress").html("");\n')
        # SOURCE LINE 304
        __M_writer(u'\n\n    }   \n    \n</script>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_write_label(context,label):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 20
        __M_writer(u'\n')
        # SOURCE LINE 21
        if label == 1:
            # SOURCE LINE 22
            __M_writer(u'        <b><font color=\'green\'>"relevant"</font></b>\n')
            # SOURCE LINE 23
        elif label == 0:
            # SOURCE LINE 24
            __M_writer(u'        <b><font color=\'light green\'>"maybe" (?)</font></b>\n')
            # SOURCE LINE 25
        else:
            # SOURCE LINE 26
            __M_writer(u'        <b><font color=\'red\'>"irrelevant"</font></b>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


