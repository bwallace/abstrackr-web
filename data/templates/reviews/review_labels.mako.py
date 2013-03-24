# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121146.715918
_enable_loop = True
_template_filename = '/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/reviews/review_labels.mako'
_template_uri = '/reviews/review_labels.mako'
_source_encoding = 'utf-8'
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
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        c = context.get('c', UNDEFINED)
        len = context.get('len', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n\n\n')
        # SOURCE LINE 6
        if c.assignment is not None:
            # SOURCE LINE 7
            __M_writer(u'<div class = "actions">\n    <a href="')
            # SOURCE LINE 8
            __M_writer(escape(url(controller='review', action='screen', review_id=c.assignment.project_id, assignment_id=c.assignment.id)))
            __M_writer(u'">ok, get back to screening <img src="../../arrow_right.png"></img></a>\n    </div>\n')
        # SOURCE LINE 11
        __M_writer(u'\n\n<div class="content">\n<div id="labels_fragment">\n')
        # SOURCE LINE 15
        if len(c.given_labels) > 0:
            # SOURCE LINE 16
            __M_writer(u'    labels you\'ve provided: <br/><br/>\n    <center>\n    <table width=100% class="list_table" align="center>>\n            <tr align="center">\n            \n            <th span=20>doc id</th>\n            <th span=20>refman id</th>\n            <th span=20>pubmed id</th>\n            <th width="30%">title</th>\n            <th>label</th>\n            <th>first labeled</th>\n            <th>last updated</th>\n            \n            </tr>\n')
            # SOURCE LINE 30
            for i, label in enumerate(c.given_labels):
                # SOURCE LINE 31
                __M_writer(u'                <tr>\n                <td>')
                # SOURCE LINE 32
                __M_writer(escape(label.study_id))
                __M_writer(u'</td>\n                <td>')
                # SOURCE LINE 33
                __M_writer(escape(c.citations_d[label.study_id].refman))
                __M_writer(u'</td>\n                <td>')
                # SOURCE LINE 34
                __M_writer(escape(c.citations_d[label.study_id].pmid))
                __M_writer(u'</td>\n                <td>\n               \n                <a href="')
                # SOURCE LINE 37
                __M_writer(escape(url(controller='review', action='show_labeled_citation', review_id=label.project_id, citation_id=label.study_id, assignment_id=label.assignment_id)))
                __M_writer(u'">')
                __M_writer(escape(c.citations_d[label.study_id].title))
                __M_writer(u'</a></td>\n\n                <td>')
                # SOURCE LINE 39
                __M_writer(escape(label.label))
                __M_writer(u'</td>\n                <td>')
                # SOURCE LINE 40
                __M_writer(escape(label.first_labeled.month))
                __M_writer(u'/')
                __M_writer(escape(label.first_labeled.day))
                __M_writer(u'/')
                __M_writer(escape(label.first_labeled.year))
                __M_writer(u'</td>\n                <td>')
                # SOURCE LINE 41
                __M_writer(escape(label.label_last_updated.month))
                __M_writer(u'/')
                __M_writer(escape(label.label_last_updated.day))
                __M_writer(u'/')
                __M_writer(escape(label.label_last_updated.year))
                __M_writer(u'</td>\n                <td></td>\n                </tr>\n')
            # SOURCE LINE 45
            __M_writer(u'    </table>\n    </center>\n')
            # SOURCE LINE 47
        else:
            # SOURCE LINE 48
            __M_writer(u"    whoops, you've not labeled anything yet. \n")
        # SOURCE LINE 50
        __M_writer(u'</div>\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'review labels')
        return ''
    finally:
        context.caller_stack._pop_frame()


