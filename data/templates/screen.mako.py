# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1313528080.6900001
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/screen.mako'
_template_uri='/screen.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
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
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        def write_label(label):
            return render_write_label(context.locals_(__M_locals),label)
        c = context.get('c', UNDEFINED)
        len = context.get('len', UNDEFINED)
        h = context.get('h', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<script language="javascript">\r\n    var seconds = 1;\r\n    setTimeout(update_timer, 1000);\r\n    \r\n    function reset_timer(){\r\n      seconds = 1; // start at one\r\n      setTimeout(update_timer, 1000);\r\n    }\r\n    \r\n    function update_timer(){\r\n      seconds +=1;\r\n      setTimeout(update_timer, 1000);\r\n    }\r\n\r\n  \r\n\r\n</script>\r\n\r\n<div class="breadcrumbs">\r\n./<a href="')
        # SOURCE LINE 23
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">dashboard</a>\r\n          /<a href="')
        # SOURCE LINE 24
        __M_writer(escape(url(controller='review', action='show_review', id=c.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review_name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n<div id="dialog" >\r\n   <form>\r\n   <center>\r\n    new tag: <input type="text" id="new_tag" name="new_tag" /><br />\r\n   </center>\r\n   <br/>\r\n\r\n    <ul id="selectable" class="ui-selectable">\r\n')
        # SOURCE LINE 35
        for tag in c.tag_types:
            # SOURCE LINE 36
            if tag in c.tags:
                # SOURCE LINE 37
                __M_writer(u'            <li class="ui-selected">')
                __M_writer(escape(tag))
                __M_writer(u'</li>\r\n')
                # SOURCE LINE 38
            else:
                # SOURCE LINE 39
                __M_writer(u'            <li>')
                __M_writer(escape(tag))
                __M_writer(u'</li>\r\n')
                pass
            pass
        # SOURCE LINE 42
        __M_writer(u'    </ul>\r\n   </center>\r\n\r\n   <div class="actions" style="text-align: right;">\r\n      <input id="submit_btn" type="button" value="tag" />\r\n   </div>\r\n   </form>\r\n</div>\r\n\r\n\r\n<div class="actions">\r\n')
        # SOURCE LINE 53
        if c.cur_lbl is not None and c.assignment_type != "conflict":
            # SOURCE LINE 54
            __M_writer(u'    <a href="')
            __M_writer(escape(url(controller='review', action='screen', review_id=c.review_id, assignment_id=c.assignment_id)))
            __M_writer(u'">ok, get back to screening <img src="../../arrow_right.png"></img></a>\r\n')
            # SOURCE LINE 55
        else:
            # SOURCE LINE 56
            __M_writer(u'    <a\r\n      href="')
            # SOURCE LINE 57
            __M_writer(escape(url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)))
            __M_writer(u'">review labels</a>\r\n    <a \r\n      href="')
            # SOURCE LINE 59
            __M_writer(escape(url(controller='review', action='review_terms', id=c.review_id, assignment_id=c.assignment_id)))
            __M_writer(u'">review terms</a>\r\n')
            pass
        # SOURCE LINE 61
        __M_writer(u'</div>\r\n\r\n<div class="container">\r\n\r\n  <div id="tags_container" class="sidebar">\r\n    <h2>tags</h2><br/><br/>\r\n    <center>\r\n    <div id="tags">\r\n')
        # SOURCE LINE 69
        if len(c.tags) > 0:
            # SOURCE LINE 70
            for tag in c.tags:
                # SOURCE LINE 71
                __M_writer(u'            ')
                __M_writer(escape(tag))
                __M_writer(u'<br/>\r\n')
                pass
            # SOURCE LINE 73
        else:
            # SOURCE LINE 74
            __M_writer(u'        (no tags yet.)\r\n')
            pass
        # SOURCE LINE 76
        __M_writer(u'    </div>\r\n    <br/><br/>\r\n    <input type="button" id="tag_btn" value="tag study..." />\r\n    </center>\r\n  </div>\r\n\r\n \r\n\r\n  <div id="citation-holder" style=\'float: right; width: 85%;\'>\r\n\r\n    <div id="citation" class="content">\r\n\r\n      <h2>')
        # SOURCE LINE 88
        __M_writer(escape(c.cur_citation.marked_up_title))
        __M_writer(u'</h2>\r\n      ')
        # SOURCE LINE 89
        __M_writer(escape(c.cur_citation.authors))
        __M_writer(u'<br/><br/>\r\n      ')
        # SOURCE LINE 90
        __M_writer(escape(c.cur_citation.marked_up_abstract))
        __M_writer(u'<br/><br/>\r\n      <b>keywords:</b> ')
        # SOURCE LINE 91
        __M_writer(escape(c.cur_citation.keywords))
        __M_writer(u'<br/><br/>\r\n      <b>ID:</b> ')
        # SOURCE LINE 92
        __M_writer(escape(c.cur_citation.citation_id))
        __M_writer(u'<br/><br/>\r\n\r\n      ')
        # SOURCE LINE 102
        __M_writer(u'\r\n\r\n')
        # SOURCE LINE 104
        if c.cur_lbl is not None:
            # SOURCE LINE 105
            if c.assignment_type == "conflict":
                # SOURCE LINE 106
                for label in c.cur_lbl:
                    # SOURCE LINE 107
                    __M_writer(u'                  <b>')
                    __M_writer(escape(c.reviewer_ids_to_names_d[label.reviewer_id]))
                    __M_writer(u'</b> labeled this citation as ')
                    __M_writer(escape(write_label(label.label)))
                    __M_writer(u' on ')
                    __M_writer(escape(label.label_last_updated))
                    __M_writer(u'<br/>\r\n')
                    pass
                # SOURCE LINE 109
            else:
                # SOURCE LINE 110
                __M_writer(u'          <center>\r\n              you labeled this citation as ')
                # SOURCE LINE 111
                __M_writer(escape(write_label(c.cur_lbl.label)))
                __M_writer(u' on ')
                __M_writer(escape(c.cur_lbl.label_last_updated))
                __M_writer(u'\r\n           </center>\r\n')
                pass
            pass
        # SOURCE LINE 115
        __M_writer(u'\r\n\r\n      <script type="text/javascript">    \r\n          function setup_js(){\r\n              $("#selectable").selectable();\r\n              \r\n              $( "#dialog" ).dialog({\r\n                height: 250,\r\n                modal: true,\r\n                autoOpen: false,\r\n                show: "blind",\r\n              });\r\n\r\n\r\n              function markup_current(){\r\n                  // reload the current citation, with markup\r\n                  $("#wait").text("marking up the current citation..")\r\n                  $("#citation").fadeOut(\'slow\', function() {\r\n                      $("#citation").load("')
        # SOURCE LINE 133
        __M_writer(escape('/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'", function() {\r\n                           $("#citation").fadeIn(\'slow\');\r\n                           $("#wait").text("");\r\n                      });\r\n                  });\r\n              }\r\n          \r\n          \r\n              $("#accept").click(function() {\r\n                  $(\'#buttons\').hide();\r\n                  $("#wait").text("hold on to your horses..")\r\n                  $("#citation").fadeOut(\'slow\', function() {\r\n                      $("#citation").load("')
        # SOURCE LINE 145
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/1", function() {\r\n                           $("#citation").fadeIn(\'slow\');\r\n                           $("#wait").text("");\r\n                           $(\'#buttons\').show();\r\n                           setup_js();\r\n                      });\r\n                  });\r\n               });   \r\n                     \r\n              $("#maybe").click(function() {\r\n                  $(\'#buttons\').hide();\r\n                  $("#wait").text("hold on to your horses..")\r\n                  $("#citation").fadeOut(\'slow\', function() {\r\n                      $("#citation").load("')
        # SOURCE LINE 158
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/0", function() {\r\n                           $("#citation").fadeIn(\'slow\');\r\n                           $("#wait").text("");\r\n                           $(\'#buttons\').show();\r\n                           setup_js();\r\n                      });\r\n                  });\r\n               });   \r\n              \r\n               \r\n              $("#reject").click(function() {\r\n                  $(\'#buttons\').hide();\r\n                  $("#wait").text("hold on to your horses..")\r\n                  $("#citation").fadeOut(\'slow\', function() {\r\n                      $("#citation").load("')
        # SOURCE LINE 172
        __M_writer(escape('/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)))
        __M_writer(u'" + seconds + "/-1", function() {\r\n                           $("#citation").fadeIn(\'slow\');\r\n                           $("#wait").text("");\r\n                           $(\'#buttons\').show();\r\n                           setup_js();\r\n                      });\r\n                  });\r\n               });  \r\n               \r\n              $("#pos_lbl_term").click(function() {\r\n                  // call out to the controller to label the term\r\n                  var term_str = $("input#term").val()\r\n                  if (term_str != ""){\r\n                      $.post("')
        # SOURCE LINE 185
        __M_writer(escape('/label_term/%s/1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                      $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being indicative of relevance.")\r\n                      $("#label_msg").fadeIn(2000)\r\n                      $("input#term").val("")\r\n                      $("#label_msg").fadeOut(3000)\r\n                      markup_current();\r\n                  }\r\n               }); \r\n               \r\n              $("#double_pos_lbl_term").click(function() {\r\n                  // call out to the controller to label the term\r\n                  var term_str = $("input#term").val()\r\n                  if (term_str != ""){\r\n                      $.post("')
        # SOURCE LINE 198
        __M_writer(escape('/label_term/%s/2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                      $("#label_msg").html("ok. labeled <font color=\'green\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")\r\n                      $("#label_msg").fadeIn(2000)\r\n                      $("input#term").val("")\r\n                      $("#label_msg").fadeOut(3000)\r\n                      markup_current();\r\n                  }\r\n               }); \r\n              \r\n\r\n              $("#neg_lbl_term").click(function() {\r\n                  // call out to the controller to label the term\r\n                  var term_str = $("input#term").val()\r\n                  if (term_str != ""){\r\n                      $.post("')
        # SOURCE LINE 212
        __M_writer(escape('/label_term/%s/-1' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                      $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")\r\n                      $("#label_msg").fadeIn(2000)\r\n                      $("input#term").val("")\r\n                      $("#label_msg").fadeOut(3000)\r\n                      markup_current();\r\n                  }\r\n               }); \r\n               \r\n              $("#double_neg_lbl_term").click(function() {\r\n                  // call out to the controller to label the term\r\n                  var term_str = $("input#term").val()\r\n                  if (term_str != ""){\r\n                      $.post("')
        # SOURCE LINE 225
        __M_writer(escape('/label_term/%s/-2' % c.review_id))
        __M_writer(u'", {term: term_str});\r\n                      $("#label_msg").html("ok. labeled <font color=\'red\'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")\r\n                      $("#label_msg").fadeIn(2000)\r\n                      $("input#term").val("")\r\n                      $("#label_msg").fadeOut(3000)\r\n                      markup_current();\r\n                  }\r\n               }); \r\n\r\n              setup_submit();\r\n          }\r\n\r\n\r\n          function setup_submit(){\r\n            \r\n            $("#selectable").selectable();\r\n              \r\n            $("#submit_btn").unbind();\r\n            $("#submit_btn").click(function()\r\n            {\r\n              \r\n               var tag_str = $("input#new_tag").val();\r\n\r\n               // now add all selected tags to the study\r\n               var tags = $.map($(\'.ui-selected, this\'), function(element, i) {  \r\n                 return $(element).text();  \r\n               });\r\n\r\n               // push new tag, too (if it\'s empty, we\'ll drop it server-side)\r\n               tags.push(tag_str);\r\n\r\n               $.post("')
        # SOURCE LINE 256
        __M_writer(escape('/review/tag_citation/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'", {tags: tags},\r\n                  function(){\r\n                    $("#tags").fadeOut(\'slow\', function() {\r\n                      $("#tags").load("')
        # SOURCE LINE 259
        __M_writer(escape('/review/update_tags/%s' % c.review_id))
        __M_writer(u'", function() {\r\n                        $("#tags").load("')
        # SOURCE LINE 260
        __M_writer(escape('/review/update_tags/%s' % c.cur_citation.citation_id))
        __M_writer(u'");\r\n                        $("#tags").fadeIn(\'slow\');\r\n                      });\r\n                    });\r\n                    \r\n                    $("#dialog").load("')
        # SOURCE LINE 265
        __M_writer(escape('/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)))
        __M_writer(u'");\r\n                    alert("ok!");\r\n                  }\r\n               );\r\n\r\n               $( "#dialog" ).dialog( "close" );\r\n            });\r\n\r\n            $("#tag_btn").click(function()\r\n            {\r\n               $("#dialog" ).dialog( "open" );\r\n            });\r\n\r\n            $("#close_btn").click(function (e)\r\n            {\r\n               $("#dialog" ).dialog( "close" );\r\n            });\r\n\r\n            $("#new_tag").val(\'\');\r\n          }\r\n\r\n\r\n          $(document).ready(function() { \r\n              setup_js();\r\n          });\r\n          \r\n      </script>\r\n    </div>\r\n\r\n\r\n    <center>\r\n    <div id="wait"></div>\r\n    </center>\r\n\r\n\r\n\r\n    <center>\r\n    <br clear="all"/>\r\n    <div id = "buttons" >\r\n    <a href="#" id="accept"><img src = "../../accept.png"/></a> \r\n    <a href="#" id="maybe"><img src = "../../maybe.png"/></a> \r\n    <a href="#" id="reject"><img src = "../../reject.png"/></a> \r\n  </div>\r\n\r\n\r\n\r\n  <table>\r\n  <tr>\r\n  <td>\r\n  <div id="label_terms" class="summary_heading">\r\n  <label>term: ')
        # SOURCE LINE 315
        __M_writer(escape(h.text('term')))
        __M_writer(u'</label> \r\n  </td>\r\n  <td width="10"></td>\r\n  <td>\r\n  <a href="#" id="pos_lbl_term"><img src = "../../thumbs_up.png" border="2" alt="indicative of relevance"></a>\r\n  </td>\r\n  <td>\r\n  <a href="#" id="double_pos_lbl_term"><img src = "../../two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>\r\n  </td>\r\n  <td width="10"></td>\r\n  <td>\r\n  <a href="#" id="neg_lbl_term"><img src = "../../thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>\r\n  </td>\r\n  <td>\r\n  <a href="#" id="double_neg_lbl_term"><img src = "../../two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>\r\n  </td>\r\n  </tr>\r\n  </div>\r\n\r\n  <div id="label_msg"></div>\r\n  </center>\r\n  </div>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_write_label(context,label):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 94
        __M_writer(u'\r\n')
        # SOURCE LINE 95
        if label == 1:
            # SOURCE LINE 96
            __M_writer(u'              <b><font color=\'green\'>"relevant"</font></b>\r\n')
            # SOURCE LINE 97
        elif label == 0:
            # SOURCE LINE 98
            __M_writer(u'              <b><font color=\'light green\'>"maybe" (?)</font></b>\r\n')
            # SOURCE LINE 99
        else:
            # SOURCE LINE 100
            __M_writer(u'              <b><font color=\'red\'>"irrelevant"</font></b>\r\n')
            pass
        # SOURCE LINE 102
        __M_writer(u'      ')
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


