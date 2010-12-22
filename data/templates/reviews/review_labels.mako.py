# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1293044319.382
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/review_labels.mako'
_template_uri='/reviews/review_labels.mako'
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
        __M_writer(u'\r\n\r\n')
        # SOURCE LINE 4
        if c.assignment is not None:
            # SOURCE LINE 5
            __M_writer(u'    <p align="right">\r\n    \r\n    <a class="tab" href="')
            # SOURCE LINE 7
            __M_writer(escape(url(controller='review', action='screen', review_id=c.assignment.review_id, assignment_id=c.assignment.id)))
            __M_writer(u'">get back to work!</a>\r\n    </p>\r\n')
            pass
        # SOURCE LINE 10
        __M_writer(u'\r\n\r\n<div class="content">\r\n\r\n')
        # SOURCE LINE 14
        if len(c.given_labels) > 0:
            # SOURCE LINE 15
            __M_writer(u'    labels you\'ve provided: <br/><br/>\r\n    <center>\r\n    <table width=100% class="list_table" align="center>>\r\n            <tr align="center">\r\n            \r\n            <th span=20>doc id</th>\r\n            <th span=20>refman id</th>\r\n            <th width="30%">title</th>\r\n            <th>label</th>\r\n            <th>first labeled</th>\r\n            <th>last updated</th>\r\n            \r\n            </tr>\r\n')
            # SOURCE LINE 28
            for i, label in enumerate(c.given_labels):
                # SOURCE LINE 29
                __M_writer(u'                <tr>\r\n                <td>')
                # SOURCE LINE 30
                __M_writer(escape(label.study_id))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 31
                __M_writer(escape(c.citations_d[label.study_id].refman_id))
                __M_writer(u'</td>\r\n                <td>\r\n                <a href="')
                # SOURCE LINE 33
                __M_writer(escape(url(controller='review', action='show_labeled_citation', review_id=label.review_id, citation_id=label.study_id)))
                __M_writer(u'">\r\n                ')
                # SOURCE LINE 34
                __M_writer(escape(c.citations_d[label.study_id].title))
                __M_writer(u'</a></td>\r\n                <td>')
                # SOURCE LINE 35
                __M_writer(escape(label.label))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 36
                __M_writer(escape(label.first_labeled.month))
                __M_writer(u'/')
                __M_writer(escape(label.first_labeled.day))
                __M_writer(u'/')
                __M_writer(escape(label.first_labeled.year))
                __M_writer(u'</td>\r\n                <td>')
                # SOURCE LINE 37
                __M_writer(escape(label.label_last_updated.month))
                __M_writer(u'/')
                __M_writer(escape(label.label_last_updated.day))
                __M_writer(u'/')
                __M_writer(escape(label.label_last_updated.year))
                __M_writer(u'</td>\r\n                <td></td>\r\n                </tr>\r\n')
                pass
            # SOURCE LINE 41
            __M_writer(u'    </table>\r\n    </center>\r\n')
            # SOURCE LINE 43
        else:
            # SOURCE LINE 44
            __M_writer(u"    whoops, you've not labeled anything yet. \r\n")
            pass
        # SOURCE LINE 46
        __M_writer(u'\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'review labels')
        return ''
    finally:
        context.caller_stack._pop_frame()


