# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1312992985.8929999
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
        __M_writer(u'\r\n\r\n\r\n\t\r\n')
        # SOURCE LINE 6
        if c.my_projects:
            # SOURCE LINE 7
            __M_writer(u'    <a class="tab" href = "')
            __M_writer(escape(url(controller='account', action='my_work')))
            __M_writer(u'">my work</a>\r\n    <a class="active_tab" href="')
            # SOURCE LINE 8
            __M_writer(escape(url(controller='account', action='my_projects')))
            __M_writer(u'">my projects</a>\r\n')
            # SOURCE LINE 9
        elif c.my_work:
            # SOURCE LINE 10
            __M_writer(u'    <a class="active_tab" href = "')
            __M_writer(escape(url(controller='account', action='my_work')))
            __M_writer(u'">my work</a>\r\n    <a class="tab" href="')
            # SOURCE LINE 11
            __M_writer(escape(url(controller='account', action='my_projects')))
            __M_writer(u'">my projects</a>\r\n')
            pass
        # SOURCE LINE 13
        __M_writer(u'<div class="content">\r\n\r\n<br/> \r\n')
        # SOURCE LINE 16
        if c.my_projects:
            # SOURCE LINE 17
            __M_writer(u'\r\n')
            # SOURCE LINE 18
            if len(c.leading_projects) > 0:
                # SOURCE LINE 19
                __M_writer(u'        <h2>projects you\'re leading</h2> <br/><br/>\r\n        <center>\r\n\r\n        \r\n        <br/>\r\n        <table class="list_table">\r\n        \r\n')
                # SOURCE LINE 26
                for i,review in enumerate(c.leading_projects):
                    # SOURCE LINE 27
                    __M_writer(u'        <tr class="')
                    __M_writer(escape('odd' if i%2 else 'even'))
                    __M_writer(u'">\r\n            <td><a href="')
                    # SOURCE LINE 28
                    __M_writer(escape(url(controller='review', action='show_review', id=review.review_id)))
                    __M_writer(u'">')
                    __M_writer(escape(review.name))
                    __M_writer(u'</td>           \r\n            <td class="inline-actions"><a href="')
                    # SOURCE LINE 29
                    __M_writer(escape(url(controller='review', action='admin', id=review.review_id)))
                    __M_writer(u'">admin \r\n                         <img src = "../../admin_sm.png"></a></td> \r\n            <td class="inline-actions"><a href="')
                    # SOURCE LINE 31
                    __M_writer(escape(url(controller='review', action='export_labels', id=review.review_id)))
                    __M_writer(u'">\r\n                      export<img src = "../../export_sm.png"></a></td>\r\n            <td class="inline-actions"><a href="')
                    # SOURCE LINE 33
                    __M_writer(escape(url(controller='review', action='review_conflicts', id=review.review_id)))
                    __M_writer(u'">\r\n                      review conflicts<img src = "../../conflicts_sm.png"></a></td>\r\n            <td class="inline-actions"><a href="')
                    # SOURCE LINE 35
                    __M_writer(escape(url(controller='review', action='delete_review', id=review.review_id)))
                    __M_writer(u'" \r\n                           onclick="javascript:return confirm(\'are you sure you want to delete this review? all labels will be lost!\')">\r\n                      delete<img src = "../../delete.png"></a></td> \r\n        </tr>\r\n')
                    pass
                # SOURCE LINE 40
                __M_writer(u'        </table>\r\n        <br/><br/><br/>\r\n        </center>\r\n')
                pass
            # SOURCE LINE 44
            __M_writer(u'\r\n')
            # SOURCE LINE 45
            if len(c.participating_projects) > 0:
                # SOURCE LINE 46
                __M_writer(u'        <h2>projects you\'re participating in</h2> <br/><br/>\r\n        <table class="list_table">\r\n')
                # SOURCE LINE 48
                for i,review in enumerate(c.participating_projects):
                    # SOURCE LINE 49
                    __M_writer(u'        <tr class="')
                    __M_writer(escape('odd' if i%2 else 'even'))
                    __M_writer(u'">\r\n            <td><a href="')
                    # SOURCE LINE 50
                    __M_writer(escape(url(controller='review', action='show_review', id=review.review_id)))
                    __M_writer(u'">')
                    __M_writer(escape(review.name))
                    __M_writer(u'</td>    \r\n            <td class="inline-actions"><a href="')
                    # SOURCE LINE 51
                    __M_writer(escape(url(controller='review', action='leave_review', id=review.review_id)))
                    __M_writer(u'" \r\n                           onclick="javascript:return confirm(\'are you sure you want to leave this review?\')">\r\n            leave review</a></td>      \r\n        </tr>\r\n')
                    pass
                # SOURCE LINE 56
                __M_writer(u'        </table>\r\n')
                # SOURCE LINE 57
            else:
                # SOURCE LINE 58
                if len(c.leading_projects) > 0:
                    # SOURCE LINE 59
                    __M_writer(u"            <h2>you're not participating in any projects yet (aside from those you're leading).</h2>\r\n")
                    # SOURCE LINE 60
                else:
                    # SOURCE LINE 61
                    __M_writer(u"            <h2>you're not participating in any projects yet.</h2>\r\n")
                    pass
                pass
            # SOURCE LINE 64
            __M_writer(u'    <br/>\r\n    \r\n    <br/><br/>\r\n\r\n    <center>\r\n     <div class="actions">\r\n    <a href="')
            # SOURCE LINE 70
            __M_writer(escape(url(controller='review', action='create_new_review')))
            __M_writer(u'"><img src ="../../add.png">start a new project/review</a>\r\n    </center>    \r\n    </div>\r\n\r\n    \r\n')
            # SOURCE LINE 75
        elif c.my_work:
            # SOURCE LINE 76
            __M_writer(u'\r\n')
            # SOURCE LINE 77
            if len(c.outstanding_assignments) > 0:
                # SOURCE LINE 78
                __M_writer(u'        <h2>work you should be doing </h2><br/><br/>\r\n        <center>\r\n        <table class="list_table" align="center>>\r\n                <tr align="center">\r\n                <th width="25%">review</th><th >number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="10%">due</th><th width="30%"></th>\r\n                </tr>\r\n')
                # SOURCE LINE 84
                for i, assignment in enumerate(c.outstanding_assignments):
                    # SOURCE LINE 85
                    __M_writer(u'                    <tr>\r\n                    <td><a href="')
                    # SOURCE LINE 86
                    __M_writer(escape(url(controller='review', action='show_review', id=assignment.review_id)))
                    __M_writer(u'">\r\n                            ')
                    # SOURCE LINE 87
                    __M_writer(escape(c.review_ids_to_names_d[assignment.review_id]))
                    __M_writer(u'</td>          \r\n')
                    # SOURCE LINE 88
                    if not assignment.assignment_type == "perpetual":
                        # SOURCE LINE 89
                        __M_writer(u'                        <td>')
                        __M_writer(escape(assignment.num_assigned))
                        __M_writer(u'</td>\r\n')
                        # SOURCE LINE 90
                    else:
                        # SOURCE LINE 91
                        __M_writer(u'                        <td>--</td>\r\n')
                        pass
                    # SOURCE LINE 93
                    __M_writer(u'                    \r\n                    <td>')
                    # SOURCE LINE 94
                    __M_writer(escape(assignment.done_so_far))
                    __M_writer(u'</td>\r\n                    <td>')
                    # SOURCE LINE 95
                    __M_writer(escape(assignment.date_assigned.month))
                    __M_writer(u'/')
                    __M_writer(escape(assignment.date_assigned.day))
                    __M_writer(u'/')
                    __M_writer(escape(assignment.date_assigned.year))
                    __M_writer(u'</td>\r\n')
                    # SOURCE LINE 96
                    if not assignment.assignment_type == "perpetual" and assignment.date_due is not None:
                        # SOURCE LINE 97
                        __M_writer(u'                        <td>')
                        __M_writer(escape(assignment.date_due.month))
                        __M_writer(u'/')
                        __M_writer(escape(assignment.date_due.day))
                        __M_writer(u'/')
                        __M_writer(escape(assignment.date_due.year))
                        __M_writer(u'</td>\r\n')
                        # SOURCE LINE 98
                    else:
                        # SOURCE LINE 99
                        __M_writer(u'                        <td>--</td>\r\n')
                        pass
                    # SOURCE LINE 101
                    __M_writer(u'                    <td class="inline-actions">\r\n                    <a href="')
                    # SOURCE LINE 102
                    __M_writer(escape(url(controller='review', action='screen', review_id=assignment.review_id, assignment_id=assignment.id)))
                    __M_writer(u'">\r\n                    screen <img src="../../arrow_right.png"></img></a></td>\r\n                    </tr>\r\n')
                    pass
                # SOURCE LINE 106
                __M_writer(u'        </table>\r\n        </center>\r\n         <br/><br/>\r\n')
                # SOURCE LINE 109
            else:
                # SOURCE LINE 110
                __M_writer(u"        <h2>hurray, you've no outstanding assignments!</h2>\r\n")
                pass
            # SOURCE LINE 112
            __M_writer(u'    \r\n')
            # SOURCE LINE 113
            if len(c.finished_assignments) > 0:
                # SOURCE LINE 114
                __M_writer(u'        <h2>assignments you\'ve completed</h2> <br/>\r\n        <center>\r\n        <table width=80% class="list_table" align="center>>\r\n                <tr align="center">\r\n                <th width="25%">review</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th>\r\n                </tr>\r\n')
                # SOURCE LINE 120
                for i,assignment in enumerate(c.finished_assignments):
                    # SOURCE LINE 121
                    __M_writer(u'                    <tr>\r\n                    <td><a href="')
                    # SOURCE LINE 122
                    __M_writer(escape(url(controller='review', action='show_review', id=assignment.review_id)))
                    __M_writer(u'">\r\n                            ')
                    # SOURCE LINE 123
                    __M_writer(escape(c.review_ids_to_names_d[assignment.review_id]))
                    __M_writer(u'</td>          \r\n')
                    # SOURCE LINE 124
                    if not assignment.assignment_type == "perpetual":
                        # SOURCE LINE 125
                        __M_writer(u'                        <td>')
                        __M_writer(escape(assignment.num_assigned))
                        __M_writer(u'</td>\r\n')
                        # SOURCE LINE 126
                    else:
                        # SOURCE LINE 127
                        __M_writer(u'                        <td>--</td>\r\n')
                        pass
                    # SOURCE LINE 129
                    __M_writer(u'                    <td>')
                    __M_writer(escape(assignment.done_so_far))
                    __M_writer(u'</td>\r\n                    <td>')
                    # SOURCE LINE 130
                    __M_writer(escape(assignment.date_assigned.month))
                    __M_writer(u'/')
                    __M_writer(escape(assignment.date_assigned.day))
                    __M_writer(u'/')
                    __M_writer(escape(assignment.date_assigned.year))
                    __M_writer(u'</td>\r\n')
                    # SOURCE LINE 131
                    if not assignment.assignment_type == "perpetual" and assignment.date_due is not None:
                        # SOURCE LINE 132
                        __M_writer(u'                        <td>')
                        __M_writer(escape(assignment.date_due.month))
                        __M_writer(u'/')
                        __M_writer(escape(assignment.date_due.day))
                        __M_writer(u'/')
                        __M_writer(escape(assignment.date_due.year))
                        __M_writer(u'</td>\r\n')
                        # SOURCE LINE 133
                    else:
                        # SOURCE LINE 134
                        __M_writer(u'                        <td>--</td>\r\n')
                        pass
                    # SOURCE LINE 136
                    __M_writer(u'                    \r\n                    </tr>\r\n')
                    pass
                # SOURCE LINE 139
                __M_writer(u'        </table>\r\n        </center>\r\n')
                pass
            pass
        # SOURCE LINE 143
        __M_writer(u'\r\n</div>')
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


