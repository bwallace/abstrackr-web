# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364121144.933707
_enable_loop = True
_template_filename = '/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/reviews/show_review.mako'
_template_uri = '/reviews/show_review.mako'
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
        float = context.get('float', UNDEFINED)
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3
        __M_writer(u'\n\n\n\n<h1>')
        # SOURCE LINE 7
        __M_writer(escape(c.review.name))
        __M_writer(u'</h1>\n\t<div class="actions">\n    <a\n      href="')
        # SOURCE LINE 10
        __M_writer(escape(url(controller='review', action='review_labels', review_id=c.review.id)))
        __M_writer(u'">review labels</a>\n    <a \n      href="')
        # SOURCE LINE 12
        __M_writer(escape(url(controller='review', action='review_terms', id=c.review.id)))
        __M_writer(u'">review terms</a>\n</div>\n<div class="content">\n<h2>Project description</h2> \n')
        # SOURCE LINE 16
        __M_writer(escape(c.review.description))
        __M_writer(u'\n<br/><br/>\n<h2>Progress</h2>\n\n')
        # SOURCE LINE 20
        if float(c.num_labels)/float(c.num_citations) >= .1:
            # SOURCE LINE 21
            __M_writer(u'\t<center><img src = "')
            __M_writer(escape(c.pi_url))
            __M_writer(u'"></img></center><br/>\n')
        # SOURCE LINE 23
        __M_writer(u'\nThere are ')
        # SOURCE LINE 24
        __M_writer(escape(c.num_citations))
        __M_writer(u' citations in this review, so far ')
        __M_writer(escape(c.num_labels))
        __M_writer(u' have been labeled.\n<br/><br/>\n\n<h2>Participants</h2>\nThis review is lead by ')
        # SOURCE LINE 28
        __M_writer(escape(c.project_lead.fullname))
        __M_writer(u'.<br/>\n<br/>\n')
        # SOURCE LINE 30
        if len(c.participating_reviewers) > 1:
            # SOURCE LINE 31
            __M_writer(u'    The following people are reviewers on the project: \n')
            # SOURCE LINE 32
            for user in c.participating_reviewers[:-1]:
                # SOURCE LINE 33
                __M_writer(u'        ')
                __M_writer(escape(user.fullname))
                __M_writer(u',\n')
            # SOURCE LINE 35
            __M_writer(u'    and ')
            __M_writer(escape(c.participating_reviewers[-1].fullname))
            __M_writer(u'.\n')
            # SOURCE LINE 36
        else:
            # SOURCE LINE 37
            __M_writer(u'    This project is a lonely undertaking by ')
            __M_writer(escape(c.participating_reviewers[0].fullname))
            __M_writer(u'.\n')
        # SOURCE LINE 39
        __M_writer(u'<br/><br/>\nNumber of citations screened by reviewers:\n<center>\n<img src= "')
        # SOURCE LINE 42
        __M_writer(escape(c.workload_graph_url))
        __M_writer(u'">\n</center>\n</div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(escape(c.review.name))
        return ''
    finally:
        context.caller_stack._pop_frame()


