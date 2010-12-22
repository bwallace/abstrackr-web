# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1293039538.2179999
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/show_review.mako'
_template_uri='/reviews/show_review.mako'
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
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n')
        # SOURCE LINE 3
        __M_writer(u'\r\n\r\n\r\n<div class="breadcrumbs">\r\n<a href="')
        # SOURCE LINE 7
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">./dashboard</a>\r\n</div>\r\n\r\n\r\n<h1>')
        # SOURCE LINE 11
        __M_writer(escape(c.review.name))
        __M_writer(u'</h1>\r\n\r\n<p align="right">\r\n')
        # SOURCE LINE 14
        if c.is_admin:
            # SOURCE LINE 15
            __M_writer(u'    <a class="tab" href="')
            __M_writer(escape(url(controller='review', action='admin', id=c.review.review_id)))
            __M_writer(u'">admin</a>\r\n')
            pass
        # SOURCE LINE 17
        __M_writer(u'<a class="tab" href="')
        __M_writer(escape(url(controller='review', action='review_labels', review_id=c.review.review_id)))
        __M_writer(u'">review labels</a>\r\n<a class="tab" href="')
        # SOURCE LINE 18
        __M_writer(escape(url(controller='review', action='review_terms', id=c.review.review_id)))
        __M_writer(u'">review terms</a>\r\n</p>\r\n\r\n<div class="content">\r\n<h2>Project description</h2> \r\n')
        # SOURCE LINE 23
        __M_writer(escape(c.review.project_description))
        __M_writer(u'\r\n<br/><br/>\r\n<h2>Progress</h2>\r\n<center><img src = "')
        # SOURCE LINE 26
        __M_writer(escape(c.pi_url))
        __M_writer(u'"></img></center><br/>\r\nThere are ')
        # SOURCE LINE 27
        __M_writer(escape(c.num_citations))
        __M_writer(u' citations in this review, so far ')
        __M_writer(escape(c.num_labels))
        __M_writer(u' have been labeled.\r\n<br/><br/>\r\n\r\n<h2>Participants</h2>\r\nThis review is lead by ')
        # SOURCE LINE 31
        __M_writer(escape(c.project_lead.fullname))
        __M_writer(u'.<br/>\r\n<br/>\r\n')
        # SOURCE LINE 33
        if len(c.participating_reviewers) > 1:
            # SOURCE LINE 34
            __M_writer(u'    The following people are reviewers on the project: \r\n')
            # SOURCE LINE 35
            for user in c.participating_reviewers[:-1]:
                # SOURCE LINE 36
                __M_writer(u'        ')
                __M_writer(escape(user.fullname))
                __M_writer(u',\r\n')
                pass
            # SOURCE LINE 38
            __M_writer(u'    and ')
            __M_writer(escape(c.participating_reviewers[-1].fullname))
            __M_writer(u'.\r\n')
            # SOURCE LINE 39
        else:
            # SOURCE LINE 40
            __M_writer(u'    This project is a lonely undertaking by ')
            __M_writer(escape(c.participating_reviewers[0].fullname))
            __M_writer(u'.\r\n')
            pass
        # SOURCE LINE 42
        __M_writer(u'<br/><br/>\r\nNumber of citations screened by reviewers:\r\n<center>\r\n<img src= "')
        # SOURCE LINE 45
        __M_writer(escape(c.workload_graph_url))
        __M_writer(u'">\r\n</center>\r\n</div>\r\n')
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


