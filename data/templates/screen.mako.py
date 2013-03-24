# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121151.661361
_enable_loop = True
_template_filename = '/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/screen.mako'
_template_uri = '/screen.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = ['write_label', 'title']


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
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def write_label(label):
            return render_write_label(context.locals_(__M_locals),label)
        c = context.get('c', UNDEFINED)
        url = context.get('url', UNDEFINED)
        h = context.get('h', UNDEFINED)
        len = context.get('len', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        dir = context.get('dir', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n<script language="javascript">\n    var seconds = 1;\n    setTimeout(update_timer, 1000);\n    \n    function reset_timer(){\n      seconds = 1; // start at one\n      setTimeout(update_timer, 1000);\n    }\n    \n    function update_timer(){\n      seconds +=1;\n      setTimeout(update_timer, 1000);\n    }\n\n  \n\n</script>\n\n\n<div id="dialog">\n   <form>\n   <center>\n    new tag: <input type="text" id="new_tag" name="new_tag" /> </input><br />\n   </center>\n   <br/>\n\n    <ul id="selectable" class="ui-selectable">\n')
        # SOURCE LINE 31
        for tag in c.tag_types:
            # SOURCE LINE 32
            if tag in c.tags:
                # SOURCE LINE 33
                __M_writer(u'            <li class="ui-selected">')
                __M_writer(escape(tag))
                __M_writer(u'</li>\n')
                # SOURCE LINE 34
            else:
                # SOURCE LINE 35
                if not c.tag_privacy:
                    # SOURCE LINE 36
                    __M_writer(u'                  <li>')
                    __M_writer(escape(tag))
                    __M_writer(u'</li>\n')
        # SOURCE LINE 40
        __M_writer(u'    </ul>\n \n\n   <div class="actions" style="text-align: right;">\n      <input id="submit_btn" type="button" value="tag" />\n   </div>\n   </form>\n</div>\n\n\n<div id="notes-dialog" >\n   <form>\n   \n    <b>general notes</b><br/> \n    <textarea id="general_notes" name="general_notes" rows="4" cols="40" /> \n    </textarea><br />\n    \n    <br>population notes</b><br/>\n    <textarea id="pop_notes" name="pop_notes" rows="1" cols="40" /></textarea><br />\n    </br>\n   \n    <br>intervention/comparator notes</b><br/>\n    <textarea id="ic_notes" name="ic_notes" rows="1" cols="40" /> \n    </textarea><br />\n    </br>\n\n    <br>outcome notes</b><br/>\n    <textarea id="outcome_notes" name="outcome_notes" rows="1" cols="40" /> </textarea><br />\n    </br>\n\n   <br/>\n    </ul>\n    <div id="notes-status"></div>\n   <div class="actions" style="text-align: right;">\n      <input id="save_notes_btn" type="button" value="save notes" />\n   </div>\n   </form>\n</div>\n\n<div class="actions">\n')
        # SOURCE LINE 80
        if c.cur_lbl is not None and c.assignment_type != "conflict":
            # SOURCE LINE 81
            if c.assignment_id is not None:
                # SOURCE LINE 82
                __M_writer(u'        <a href="')
                __M_writer(escape(url(controller='review', action='screen', review_id=c.review_id, assignment_id=c.assignment_id)))
                __M_writer(u'">back to screening <img src="/arrow_right.png"></img></a>\n        <a href="')
                # SOURCE LINE 83
                __M_writer(escape(url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)))
                __M_writer(u'">back to the list of labeled citations <img src="/arrow_right.png"></img></a>\n')
            # SOURCE LINE 85
        else:
            # SOURCE LINE 86
            __M_writer(u'    <a\n      href="')
            # SOURCE LINE 87
            __M_writer(escape(url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)))
            __M_writer(u'">review labels</a>\n    <a \n      href="')
            # SOURCE LINE 89
            __M_writer(escape(url(controller='review', action='review_terms', id=c.review_id, assignment_id=c.assignment_id)))
            __M_writer(u'">review terms</a>\n')
        # SOURCE LINE 91
        __M_writer(u'</div>\n\n<div class="container">\n\n  <div id="tags_container" class="sidebar">\n    <h2>tags &amp; notes</h2><br/>\n    <center>\n    <div id="tags" class="tags">\n    <ul>\n')
        # SOURCE LINE 100
        if len(c.tags) > 0:
            # SOURCE LINE 101
            for i,tag in enumerate(c.tags):
                # SOURCE LINE 102
                __M_writer(u'            <li class=')
                __M_writer(escape("tag%s"%(i+1)))
                __M_writer(u'><a href="#">')
                __M_writer(escape(tag))
                __M_writer(u'</a></li><br/>\n')
            # SOURCE LINE 104
            __M_writer(u'    </ul>\n')
            # SOURCE LINE 105
        else:
            # SOURCE LINE 106
            __M_writer(u'        (no tags yet.)\n')
        # SOURCE LINE 108
        __M_writer(u'    </div>\n    <br/>\n    <input type="button" style="width: 120px" id="tag_btn" value="tag study..." />\n    <br/><br/>\n\n    \n    <input type="button" style="width: 120px" id="edit_tags_btn" value="edit tags..." \n                onclick="parent.location=\'/review/edit_tags/')
        # SOURCE LINE 115
        __M_writer(escape(c.review_id))
        __M_writer(u'/')
        __M_writer(escape(c.assignment_id))
        __M_writer(u'\'"> \n   \n    <br/><br/>\n    <input type="button" style="width: 120px" id="notes_btn" value="notes..." />\n\n    </center>\n  </div>\n\n \n\n\n  <div id="citation-holder" style=\'float: right; width: 85%;\'>\n\n    <div id="citation" class="content">\n\n      <h2>')
        # SOURCE LINE 130
        __M_writer(escape(c.cur_citation.marked_up_title))
        __M_writer(u'</h2>\n\n')
        # SOURCE LINE 132
        if c.show_journal==True:
            # SOURCE LINE 133
            __M_writer(u'          <i>Journal: ')
            __M_writer(escape(c.cur_citation.journal))
            __M_writer(u'</i><br /><br />\n')
        # SOURCE LINE 135
        __M_writer(u'\n')
        # SOURCE LINE 136
        if c.show_authors==True:
            # SOURCE LINE 137
            __M_writer(u'          Authors: ')
            __M_writer(escape(c.cur_citation.authors))
            __M_writer(u'<br/><br/>\n')
        # SOURCE LINE 139
        __M_writer(u'\n      ')
        # SOURCE LINE 140
        __M_writer(escape(c.cur_citation.marked_up_abstract))
        __M_writer(u'<br/><br/>\n\n')
        # SOURCE LINE 142
        if c.show_keywords==True:
            # SOURCE LINE 143
            __M_writer(u'          <b>keywords:</b> ')
            __M_writer(escape(c.cur_citation.keywords))
            __M_writer(u'<br/><br/>\n')
        # SOURCE LINE 145
        __M_writer(u'\n      <b>ID:</b> ')
        # SOURCE LINE 146
        __M_writer(escape(c.cur_citation.citation_id))
        __M_writer(u'<br/><br/>\n\n      ')
        # SOURCE LINE 156
        __M_writer(u'\n\n')
        # SOURCE LINE 158
        if c.cur_lbl is not None:
            # SOURCE LINE 159
            if c.assignment_type == "conflict":
                # SOURCE LINE 160
                for label in c.cur_lbl:
                    # SOURCE LINE 161
                    if "consensus_review" in dir(c) and c.consensus_review:
                        # SOURCE LINE 162
                        __M_writer(u'                  a <b>consensus</b> label of ')
                        __M_writer(escape(write_label(label.label)))
                        __M_writer(u' was given for this citation on on ')
                        __M_writer(escape(label.label_last_updated))
                        __M_writer(u'<br/>\n')
                        # SOURCE LINE 163
                    else:
                        # SOURCE LINE 164
                        __M_writer(u'                  <b>')
                        __M_writer(escape(c.reviewer_ids_to_names_d[label.reviewer_id]))
                        __M_writer(u'</b> labeled this citation as ')
                        __M_writer(escape(write_label(label.label)))
                        __M_writer(u' on ')
                        __M_writer(escape(label.label_last_updated))
                        __M_writer(u'<br/>\n')
                # SOURCE LINE 167
            else:
                # SOURCE LINE 168
                __M_writer(u'          <center>\n              you labeled this citation as ')
                # SOURCE LINE 169
                __M_writer(escape(write_label(c.cur_lbl.label)))
                __M_writer(u' on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u'\n           </center>\n')
        # SOURCE LINE 173
        __M_writer(u'\n\n      <script type="text/javascript">    \n\n          var still_loading = false;\n          var waiting_for_citation = false;\n\n          function get_next_citation()\n          {\n              still_loading = true;\n              $(\'#hidden_div\').load( "')
        # SOURCE LINE 183
        __M_writer(escape('/next_citation/%s/%s' % (c.review_id, c.assignment_id)))
        __M_writer(u'", function() {\n                  still_loading = false;\n                  // were we waiting for this guy? if so, load\n                  // him in now\n                  if (waiting_for_citation){\n                    load_next_citation();\n                  }\n              });\n          }\n\n          function load_next_citation(){\n            // pull in the next citation from the hidden_div iff\n            // it has finished downloading. otherwise hide buttons,\n            // show waiting screen and flip \'waiting_for_citation\'\n            // boolean to true\n            if (still_loading) {\n              $("#wait").text("hold on to your horses..")\n              $(\'#buttons\').hide();\n              waiting_for_citation = true;\n            } else{\n              // then the next citation has been downloaded\n              // into the hidden_div\n              $(\'#citation\').html( $(\'#hidden_div\').html() );\n\n              // this is the key logic piece; we the setup_js method\n              // is defined with respect to the currently hidden\n              // citation that we just loaded into the #citation div\n              // hence when it is called it will attach calls to the\n              // buttons that label the (now currently) displayed\n              // citation that we fadein in the next line.\n              setup_js();\n              \n              $(\'#citation\').fadeIn();\n              $("#wait").text("")\n              $(\'#buttons\').show();\n              waiting_for_citation = false;\n\n\n              // once the citation \n              get_next_citation();\n            }\n          }\n\n          function we_are_reviewing_a_label(){\n            return "')
        # SOURCE LINE 227
        __M_writer(escape('assignment' not in dir(c)))
        __M_writer(u'" == "True";\n          }\n\n          function is_perpetual_assignment(){\n')
        # SOURCE LINE 231
        if not 'assignment' in dir(c):
            # SOURCE LINE 232
            __M_writer(u'              return false;\n')
            # SOURCE LINE 233
        else:
            # SOURCE LINE 234
            __M_writer(u'              return "')
            __M_writer(escape(c.assignment.assignment_type))
            __M_writer(u'" == "perpetual";\n')
        # SOURCE LINE 236
        __M_writer(u'          }\n\n          function setup_js(){\n              \n              $( "#dialog" ).dialog({\n                height: 250,\n                modal: true,\n                autoOpen: false,\n                show: "blind",\n              });\n\n              $( "#notes-dialog" ).dialog({\n                height: 300,\n                width: 400,\n                modal: true,\n                autoOpen: false,\n                position: [0,0],\n                show: "blind",\n                hide: {effect: "fadeOut", duration:2000}\n              });\n\n              function markup_current(){\n                  // reload the current citation, with markup\n                  $("#wait").text("marking up the current citation..")\n                  $("#citation").fadeOut(\'slow\', function() {\n                      $("#citation").load("')
        # SOURCE LINE 261
        __M_writer(escape('/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'", function() {\n                           $("#citation").fadeIn(\'slow\');\n                           $("#wait").text("");\n                      });\n                  });\n              }\n          \n\n              function label_cur_citation(lbl_str){\n                  $("#citation").fadeOut(\'fast\', function() {\n                        if (!(we_are_reviewing_a_label()) && is_perpetual_assignment()){\n                          // try to load the next citation\n                          // this call will in turn call get_next_citation\n                          // once loading is complete\n                          load_next_citation();\n                        }\n\n                        $.post("')
        # SOURCE LINE 278
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/" + lbl_str, function(data){\n                            if (we_are_reviewing_a_label()){\n                              // in the case that we are re-labeling a citation, \n                              // this the label method will return the citation fragment.\n                              $(\'#citation\').html(data);\n                              $(\'#citation\').fadeIn();\n                              setup_js();\n                              still_loading = false;\n                            } \n                            else if (!(is_perpetual_assignment())) {\n                              load_next_citation();\n                            }\n                            else {\n                              //alert(data);\n                              $(\'#progress\').html(data);\n                            }\n                        });\n                  });      \n              }\n\n\n              $("#accept").click(function() {\n                label_cur_citation("1");\n              });\n                     \n\n              $("#maybe").click(function() {\n                label_cur_citation("0");\n              });\n              \n               \n              $("#reject").click(function() {\n                label_cur_citation("-1");\n              });\n               \n              $("#pos_lbl_term").click(function() {\n                  // call out to the controller to label the term\n                  var term_str = $("input#term").val()\n                  if (term_str != ""){\n                      $.post("')
        # SOURCE LINE 317
        __M_writer(escape('/label_term/%s/1' % c.review_id))
        __M_writer(u'", {term: term_str});\n                      $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being indicative of relevance.")\n                      $("#label_msg").fadeIn(2000)\n                      $("input#term").val("")\n                      $("#label_msg").fadeOut(3000)\n                      markup_current();\n                  }\n               }); \n               \n              $("#double_pos_lbl_term").click(function() {\n                  // call out to the controller to label the term\n                  var term_str = $("input#term").val()\n                  if (term_str != ""){\n                      $.post("')
        # SOURCE LINE 330
        __M_writer(escape('/label_term/%s/2' % c.review_id))
        __M_writer(u'", {term: term_str});\n                      $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")\n                      $("#label_msg").fadeIn(2000)\n                      $("input#term").val("")\n                      $("#label_msg").fadeOut(3000)\n                      markup_current();\n                  }\n               }); \n              \n\n              $("#neg_lbl_term").click(function() {\n                  // call out to the controller to label the term\n                  var term_str = $("input#term").val()\n                  if (term_str != ""){\n                      $.post("')
        # SOURCE LINE 344
        __M_writer(escape('/label_term/%s/-1' % c.review_id))
        __M_writer(u'", {term: term_str});\n                      $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")\n                      $("#label_msg").fadeIn(2000)\n                      $("input#term").val("")\n                      $("#label_msg").fadeOut(3000)\n                      markup_current();\n                  }\n               }); \n               \n              $("#double_neg_lbl_term").click(function() {\n                  // call out to the controller to label the term\n                  var term_str = $("input#term").val()\n                  if (term_str != ""){\n                      $.post("')
        # SOURCE LINE 357
        __M_writer(escape('/label_term/%s/-2' % c.review_id))
        __M_writer(u'", {term: term_str});\n                      $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")\n                      $("#label_msg").fadeIn(2000)\n                      $("input#term").val("")\n                      $("#label_msg").fadeOut(3000)\n                      markup_current();\n                  }\n               }); \n\n              populate_notes();\n              setup_submit();\n          }\n\n          function populate_notes(){\n')
        # SOURCE LINE 371
        if "notes" in dir(c) and c.notes is not None:
            # SOURCE LINE 372
            __M_writer(u'              $("#pop_notes").val(\'')
            __M_writer(escape(c.notes.population))
            __M_writer(u'\'); \n              $("textarea#general_notes").val(\'')
            # SOURCE LINE 373
            __M_writer(escape(c.notes.general))
            __M_writer(u'\');\n              $("textarea#ic_notes").val(\'')
            # SOURCE LINE 374
            __M_writer(escape(c.notes.ic))
            __M_writer(u'\');\n              $("textarea#outcome_notes").val(\'')
            # SOURCE LINE 375
            __M_writer(escape(c.notes.outcome))
            __M_writer(u"');\n")
            # SOURCE LINE 376
        else:
            # SOURCE LINE 377
            __M_writer(u'              $("#pop_notes").val(\'\'); \n              $("textarea#general_notes").val(\'\');\n              $("textarea#ic_notes").val(\'\');\n              $("textarea#outcome_notes").val(\'\');\n')
        # SOURCE LINE 382
        __M_writer(u'          }\n\n          function setup_submit() {\n            $("#selectable").selectable();\n\n            $("#submit_btn").unbind();\n            $("#submit_btn").click(function()\n            {\n\n               var tag_str = $("input#new_tag").val();\n\n               // now add all selected tags to the study\n               var tags = $.map($(\'.ui-selected, this\'), function(element, i) {  \n                 return $(element).text();  \n               });\n\n               // push new tag, too (if it\'s empty, we\'ll drop it server-side)\n               tags.push(tag_str);\n\n               $.post("')
        # SOURCE LINE 401
        __M_writer(escape('/review/tag_citation/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'", {tags: tags},\n                  function()\n                  {\n                    $("#tags").fadeOut(\'slow\', function() {\n                      $("#tags").load("')
        # SOURCE LINE 405
        __M_writer(escape('/review/update_tags/%s/%s' % (c.cur_citation.citation_id, c.tag_privacy)))
        __M_writer(u'",\n                        function() {\n                          $("#tags").fadeIn(\'slow\');\n                        });\n                    });\n\n                    $("#dialog").load("')
        # SOURCE LINE 411
        __M_writer(escape('/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'");\n                  }\n               );\n\n               $( "#dialog" ).dialog( "close" );\n            });\n\n\n\n            /** adding note-taking functionality **/\n            $("#save_notes_btn").unbind();\n            $("#save_notes_btn").click(function()\n            {\n               // something like\n               var general_notes = $("#general_notes").val();\n               var pop_notes =  $("#pop_notes").val();\n               var ic_notes = $("#ic_notes").val();\n               var outcome_notes = $("#outcome_notes").val();\n\n\n               $.post("')
        # SOURCE LINE 431
        __M_writer(escape('/review/add_notes/%s' % c.cur_citation.citation_id))
        __M_writer(u'",\n                          {"general_notes": general_notes, "population_notes":pop_notes, "ic_notes":ic_notes,\n                          "outcome_notes":outcome_notes}, function() {\n                              $("#notes-status").html("<font color=\'green\'>notes added.</font>");\n                              $( "#notes-dialog" ).dialog( "close" );\n                              $("#notes-status").html("");\n                          }\n                      );\n\n\n               \n            });\n            /** end notes functionality **/\n\n            $("#tag_btn").unbind();\n            $("#tag_btn").click(function()\n            {\n               $("#dialog" ).dialog( "open" );\n            });\n\n            $("#close_btn").unbind();\n            $("#close_btn").click(function (e)\n            {\n               // I actually don\'t know where \'close_btn\' is defined...\n               // we close them both here.\n               $("#dialog" ).dialog( "close" );\n               $("#notes-dialog" ).dialog( "close" );\n            });\n\n            $("#notes_btn").unbind();\n            $("#notes_btn").click(function()\n            {\n               $("#notes-dialog" ).dialog("open");\n            });\n            \n      \n          }\n\n          $(document).ready(function() { \n              setup_js();\n              // we don\'t queue the next citation if we\'re reviewing\n              // labels!\n              if (!(we_are_reviewing_a_label())) {\n                get_next_citation(); // fetch the *next* citation\n              }\n              $("#hidden_div").hide();\n\n          });\n          \n      </script>\n    </div>\n\n    <div id="hidden_div" class="content"></div>\n\n    <center>\n    <div id="wait"></div>\n    </center>\n    \n\n    <br/><br/>\n    <center>\n    <div id="progress"> \n')
        # SOURCE LINE 493
        if 'assignment' in dir(c):
            # SOURCE LINE 494
            if c.assignment.num_assigned and c.assignment.num_assigned > 0:
                # SOURCE LINE 495
                __M_writer(u"            you've screened <b>")
                __M_writer(escape(c.assignment.done_so_far))
                __M_writer(u'</b> out of <b>')
                __M_writer(escape(c.assignment.num_assigned))
                __M_writer(u'</b> so far (nice going!)\n')
                # SOURCE LINE 496
            else:
                # SOURCE LINE 497
                __M_writer(u"            you've screened <b>")
                __M_writer(escape(c.assignment.done_so_far))
                __M_writer(u'</b> abstracts thus far (keep it up!)\n')
        # SOURCE LINE 500
        __M_writer(u'    </div>\n    </center>\n\n   \n\n\n\n    <center>\n    <br clear="all"/>\n    <div id = "buttons" >\n    <a href="#" id="accept"><img src = "/accept.png"/></a> \n    <a href="#" id="maybe"><img src = "/maybe.png"/></a> \n    <a href="#" id="reject"><img src = "/reject.png"/></a> \n    </div>\n\n\n\n  <div id="label_terms" class="summary_heading">\n  <table>\n  <tr>\n  <td>\n  <label>term: ')
        # SOURCE LINE 521
        __M_writer(escape(h.text('term')))
        __M_writer(u'</label> \n  </td>\n  <td width="10"></td>\n  <td>\n  <a href="#" id="pos_lbl_term"><img src = "/thumbs_up.png" border="2" alt="indicative of relevance"></a>\n  </td>\n  <td>\n  <a href="#" id="double_pos_lbl_term"><img src = "/two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>\n  </td>\n  <td width="10"></td>\n  <td>\n  <a href="#" id="neg_lbl_term"><img src = "/thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>\n  </td>\n  <td>\n  <a href="#" id="double_neg_lbl_term"><img src = "/two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>\n  </td>\n  </tr>\n  </table>\n  </div>\n\n  <div id="label_msg"></div>\n  </center>\n  </div>\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_write_label(context,label):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 148
        __M_writer(u'\n')
        # SOURCE LINE 149
        if label == 1:
            # SOURCE LINE 150
            __M_writer(u'              <b><font color=\'green\'>"relevant"</font></b>\n')
            # SOURCE LINE 151
        elif label == 0:
            # SOURCE LINE 152
            __M_writer(u'              <b><font color=\'light green\'>"maybe" (?)</font></b>\n')
            # SOURCE LINE 153
        else:
            # SOURCE LINE 154
            __M_writer(u'              <b><font color=\'red\'>"irrelevant"</font></b>\n')
        # SOURCE LINE 156
        __M_writer(u'      ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'screen')
        return ''
    finally:
        context.caller_stack._pop_frame()


