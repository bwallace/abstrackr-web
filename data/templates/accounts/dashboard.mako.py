# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1291403926.464
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/accounts/dashboard.mako'
_template_uri='/accounts/dashboard.mako'
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
        len = context.get('len', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<h1>hi there, ')
        # SOURCE LINE 4
        __M_writer(escape(c.person.fullname))
        __M_writer(u'.</h1>\r\n\r\n<div class="content">\r\n\r\n<br/>\r\n\r\n')
        # SOURCE LINE 10
        if len(c.leading_projects) > 0:
            # SOURCE LINE 11
            __M_writer(u'    projects you\'re leading: <br/><br/>\r\n    <table class="list_table">\r\n')
            # SOURCE LINE 13
            for i,review in enumerate(c.leading_projects):
                # SOURCE LINE 14
                __M_writer(u'    <tr class="')
                __M_writer(escape('odd' if i%2 else 'even'))
                __M_writer(u'">\r\n        <td><a href="')
                # SOURCE LINE 15
                __M_writer(escape(url(controller='review', action='show_review', id=review.review_id)))
                __M_writer(u'">')
                __M_writer(escape(review.name))
                __M_writer(u'</td>           \r\n        <td><a href="')
                # SOURCE LINE 16
                __M_writer(escape(url(controller='review', action='admin', id=review.review_id)))
                __M_writer(u'">administrate!</td> \r\n    </tr>\r\n')
                pass
            # SOURCE LINE 19
            __M_writer(u'    </table>\r\n    <br/><br/>\r\n')
            pass
        # SOURCE LINE 22
        __M_writer(u'\r\n')
        # SOURCE LINE 23
        if len(c.participating_projects) > 0:
            # SOURCE LINE 24
            __M_writer(u'    projects you\'re participating in: <br/><br/>\r\n    <table class="list_table">\r\n')
            # SOURCE LINE 26
            for i,review in enumerate(c.participating_projects):
                # SOURCE LINE 27
                __M_writer(u'    <tr class="')
                __M_writer(escape('odd' if i%2 else 'even'))
                __M_writer(u'">\r\n        <td><a href="')
                # SOURCE LINE 28
                __M_writer(escape(url(controller='review', action='show_review', id=review.review_id)))
                __M_writer(u'">')
                __M_writer(escape(review.name))
                __M_writer(u'</td>          \r\n    </tr>\r\n')
                pass
            # SOURCE LINE 31
            __M_writer(u'    </table>\r\n')
            # SOURCE LINE 32
        else:
            # SOURCE LINE 33
            __M_writer(u"    you're not participating in any projects yet.\r\n")
            pass
        # SOURCE LINE 35
        __M_writer(u'\r\n\r\n<br/><br/>\r\n')
        # SOURCE LINE 38
        if len(c.outstanding_assignments) > 0:
            # SOURCE LINE 39
            __M_writer(u'    work you should be doing: <br/><br/>\r\n    <center>\r\n    <table width=80% class="list_table" align="center>>\r\n            <tr align="center">\r\n            <th width="25%">review</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th><th width="20%"></th>\r\n            </tr>\r\n')
            # SOURCE LINE 45
            for i,assignment in enumerate(c.outstanding_assignments):
                # SOURCE LINE 46
                __M_writer(u'                <tr>\r\n                <td><a href="')
                # SOURCE LINE 47
                __M_writer(escape(url(controller='review', action='show_review', id=assignment.review_id)))
                __M_writer(u'">\r\n                        ')
                # SOURCE LINE 48
                __M_writer(escape(c.review_ids_to_names_d[assignment.review_id]))
                __M_writer(u'</td>          \r\n                <td>')
                # SOURCE LINE 49
                __M_writer(escape(assignment.num_assigned))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 50
                __M_writer(escape(assignment.done_so_far))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 51
                __M_writer(escape(assignment.date_assigned.month))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_assigned.day))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_assigned.year))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 52
                __M_writer(escape(assignment.date_due.month))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_due.day))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_due.year))
                __M_writer(u'</td>\r\n                <td width=30>\r\n                <a href="')
                # SOURCE LINE 54
                __M_writer(escape(url(controller='review', action='screen', review_id=assignment.review_id, assignment_id=assignment.id)))
                __M_writer(u'">\r\n                get to work!</a></td>\r\n                </tr>\r\n')
                pass
            # SOURCE LINE 58
            __M_writer(u'    </table>\r\n    </center>\r\n')
            # SOURCE LINE 60
        else:
            # SOURCE LINE 61
            __M_writer(u"    hurray, you've no outstanding assignments!    \r\n")
            pass
        # SOURCE LINE 63
        __M_writer(u'\r\n<br/><br/>\r\n\r\n')
        # SOURCE LINE 66
        if len(c.finished_assignments) > 0:
            # SOURCE LINE 67
            __M_writer(u'    assignments you\'ve completed: <br/>\r\n    <center>\r\n    <table width=80% class="list_table" align="center>>\r\n            <tr align="center">\r\n            <th width="25%">review</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th>\r\n            </tr>\r\n')
            # SOURCE LINE 73
            for i,assignment in enumerate(c.finished_assignments):
                # SOURCE LINE 74
                __M_writer(u'                <tr>\r\n                <td><a href="')
                # SOURCE LINE 75
                __M_writer(escape(url(controller='review', action='show_review', id=assignment.review_id)))
                __M_writer(u'">\r\n                        ')
                # SOURCE LINE 76
                __M_writer(escape(c.review_ids_to_names_d[assignment.review_id]))
                __M_writer(u'</td>          \r\n                <td>')
                # SOURCE LINE 77
                __M_writer(escape(assignment.num_assigned))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 78
                __M_writer(escape(assignment.done_so_far))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 79
                __M_writer(escape(assignment.date_assigned.month))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_assigned.day))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_assigned.year))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 80
                __M_writer(escape(assignment.date_due.month))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_due.day))
                __M_writer(u'/')
                __M_writer(escape(assignment.date_due.year))
                __M_writer(u'</td>\r\n                </tr>\r\n')
                pass
            # SOURCE LINE 83
            __M_writer(u'    </table>\r\n    </center>\r\n')
            pass
        # SOURCE LINE 86
        __M_writer(u'\r\nwant to <a href = "')
        # SOURCE LINE 87
        __M_writer(escape(url(controller='review', action='join_a_review')))
        __M_writer(u'">join an existing review?</a>\r\n<br/><br/>\r\nor maybe you want to <a href = "')
        # SOURCE LINE 89
        __M_writer(escape(url(controller='review', action='create_new_review')))
        __M_writer(u'">start a new review?</a>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'home')
        return ''
    finally:
        context.caller_stack._pop_frame()


