# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291403915.9170001
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/admin.mako'
_template_uri='/reviews/admin.mako'
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
    return runtime._inherit_from(context, u'../site.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n')
        # SOURCE LINE 3
        __M_writer(u'\r\n<script language="JavaScript">\r\n    var cal = new CalendarPopup();\r\n</script>\r\n\r\n\r\n<div class="breadcrumbs">\r\n<a href="')
        # SOURCE LINE 10
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">./dashboard</a>/<a href="')
        __M_writer(escape(url(controller='review', action='show_review', id=c.review.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review.name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n\r\n<h1>')
        # SOURCE LINE 14
        __M_writer(escape(c.review.name))
        __M_writer(u': administrivia</h1>\r\n\r\n<div class="content">\r\n<h2>Assignments</h2> \r\n    <center>\r\n    <table width=80% class="list_table" align="center>>\r\n            <tr align="center">\r\n            <th width="25%">reviewer</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th>\r\n            </tr>\r\n')
        # SOURCE LINE 23
        for i,assignment in enumerate(c.assignments):
            # SOURCE LINE 24
            __M_writer(u'                <tr>\r\n                <td>')
            # SOURCE LINE 25
            __M_writer(escape(c.reviewer_ids_to_names_d[assignment.reviewer_id]))
            __M_writer(u'</td>          \r\n                <td>')
            # SOURCE LINE 26
            __M_writer(escape(assignment.num_assigned))
            __M_writer(u'</td>\r\n                <td>')
            # SOURCE LINE 27
            __M_writer(escape(assignment.done_so_far))
            __M_writer(u'</td>\r\n                <td>')
            # SOURCE LINE 28
            __M_writer(escape(assignment.date_assigned.month))
            __M_writer(u'/')
            __M_writer(escape(assignment.date_assigned.day))
            __M_writer(u'/')
            __M_writer(escape(assignment.date_assigned.year))
            __M_writer(u'</td>\r\n                <td>')
            # SOURCE LINE 29
            __M_writer(escape(assignment.date_due.month))
            __M_writer(u'/')
            __M_writer(escape(assignment.date_due.day))
            __M_writer(u'/')
            __M_writer(escape(assignment.date_due.year))
            __M_writer(u'</td>\r\n                </tr>\r\n')
            pass
        # SOURCE LINE 32
        __M_writer(u'    </table>\r\n    </center>\r\n<br/><br/>\r\n\r\n<h2>Create new assignment</h2>\r\n\r\n<br/>\r\n<form name="new_assignment" action="')
        # SOURCE LINE 39
        __M_writer(escape(url(controller='review', action='create_assignment', id=c.review.review_id)))
        __M_writer(u'">\r\nassign to: <br/><br/>\r\n')
        # SOURCE LINE 41
        for reviewer in c.participating_reviewers:
            # SOURCE LINE 42
            __M_writer(u'    <input type="checkbox" name="assign_to" value="')
            __M_writer(escape(reviewer.username))
            __M_writer(u'" checked="yes"/> ')
            __M_writer(escape(reviewer.username))
            __M_writer(u'<br/>\r\n')
            pass
        # SOURCE LINE 44
        __M_writer(u'<br/><br/>\r\n<table>\r\n<tr><td>number of citations for each assignee to screen:</td><td> <INPUT TYPE="text" NAME="n" SIZE=10></td></tr>\r\n<tr><td>percent of these that should be re-screens:</td><td> <INPUT TYPE="text" NAME="p_rescreen" VALUE="0" SIZE=10>\r\n</td>\r\n</tr>\r\n<tr>\r\n<td>\r\ndue date:</td><td> \r\n<INPUT TYPE="text" NAME="due_date" VALUE="" SIZE=10>\r\n<a href="#"\r\n   onClick="cal.select(document.forms[\'new_assignment\'].due_date,\'anchor1\',\'MM/dd/yyyy\'); return false;"\r\n   NAME="anchor1" ID="anchor1">select</A> </td></tr>\r\n  <tr><td><INPUT TYPE=SUBMIT VALUE="Create assignment"></td></tr>\r\n</table>\r\n</form>\r\n\r\n\r\n\r\n</div>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(escape(c.review.name))
        return ''
    finally:
        context.caller_stack._pop_frame()


