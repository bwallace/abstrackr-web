# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1293046591.4719999
_template_filename='C:\\dev\\abstrackr_web\\abstrackr\\abstrackr\\templates/reviews/edit_terms.mako'
_template_uri='/reviews/edit_terms.mako'
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
        c = context.get('c', UNDEFINED)
        zip = context.get('zip', UNDEFINED)
        url = context.get('url', UNDEFINED)
        len = context.get('len', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\r\n')
        # SOURCE LINE 2
        __M_writer(u'\r\n\r\n<div class="breadcrumbs">\r\n./<a href="')
        # SOURCE LINE 5
        __M_writer(escape(url(controller='account', action='welcome')))
        __M_writer(u'">dashboard</a>\r\n          /<a href="')
        # SOURCE LINE 6
        __M_writer(escape(url(controller='review', action='show_review', id=c.review_id)))
        __M_writer(u'">')
        __M_writer(escape(c.review_name))
        __M_writer(u'</a>\r\n</div>\r\n\r\n<div class="content">\r\n')
        # SOURCE LINE 10
        if len(c.terms) > 0:
            # SOURCE LINE 11
            __M_writer(u'    terms you\'ve labeled: <br/><br/>\r\n    <table class="list_table">\r\n        <th>term</th>\r\n        <th>current label</th>\r\n        <th>delete</th>\r\n        <th>re-label</th>\r\n')
            # SOURCE LINE 17
            for i,term in enumerate(c.terms):
                # SOURCE LINE 18
                __M_writer(u'            <tr class="')
                __M_writer(escape('odd' if i%2 else 'even'))
                __M_writer(u'">\r\n              <td>')
                # SOURCE LINE 19
                __M_writer(escape(term.term))
                __M_writer(u'</td>           \r\n              <td><img src="/')
                # SOURCE LINE 20
                __M_writer(escape(dict(zip([-2, -1, 1, 2],["two_thumbs_down.png", "thumbs_down.png", "thumbs_up.png", "two_thumbs_up.png"]))[term.label]))
                __M_writer(u'"></td> \r\n              <td><a href="/review/delete_term/')
                # SOURCE LINE 21
                __M_writer(escape(term.id))
                __M_writer(u'"><img src = "/reject.png"/></a> </td>\r\n              <td>\r\n                    <a href="/relabel_term/')
                # SOURCE LINE 23
                __M_writer(escape(term.id))
                __M_writer(u'/1"><img src = "/thumbs_up.png" border="2" alt="indicative of relevance"></a>\r\n                    <a href="/relabel_term/')
                # SOURCE LINE 24
                __M_writer(escape(term.id))
                __M_writer(u'/2"><img src = "/two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>\r\n                    <a href="/relabel_term/')
                # SOURCE LINE 25
                __M_writer(escape(term.id))
                __M_writer(u'/-1"><img src = "/thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>\r\n                    <a href="/relabel_term/')
                # SOURCE LINE 26
                __M_writer(escape(term.id))
                __M_writer(u'/-2"><img src = "/two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>\r\n              </td>\r\n            </tr>\r\n')
                pass
            # SOURCE LINE 30
            __M_writer(u'    </table>\r\n')
            # SOURCE LINE 31
        else:
            # SOURCE LINE 32
            __M_writer(u"   you haven't labeled any terms for this project yet. (in the future, I'll suggest some...)\r\n")
            pass
        # SOURCE LINE 34
        __M_writer(u'</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'edit terms')
        return ''
    finally:
        context.caller_stack._pop_frame()


