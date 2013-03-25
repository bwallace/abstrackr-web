# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1364208212.041385
_enable_loop = True
_template_filename = u'/home/sunya7a/Hive/abstrackr-web/abstrackr/templates/site.mako'
_template_uri = u'/accounts/../site.mako'
_source_encoding = 'utf-8'
from webhelpers.html import escape
_exports = ['title']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n        <link rel="stylesheet" href="/stylesheet.css">\n        <link rel="stylesheet" href="/jquery-ui-1.8.15.custom.css">\n        <link rel="stylesheet" href="/intro.js/introjs.css">\n        <link rel="stylesheet" href="/intro.js/introjs-ie.css">\n\n        <script type="text/javascript" src="/scripts/jquery-1.6.2.min.js"></script>\n        <script type="text/javascript" src="/scripts/jquery-ui-1.8.15.custom.min.js"></script>\n        <script type="text/javascript" src="/scripts/jqModal.js"></script>\n        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>\n        <script type="text/javascript" src="/scripts/jquery.ui.selectable.js"></script>\n        <script type="text/javascript" src="/intro.js/intro.js"></script>\n  \n        <title>abstrackr: ')
        # SOURCE LINE 18
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\n    </head>\n    <body>\n\n        <p align="left">\n            <img src="http://sunfire34.eecs.tufts.edu/abstrackr.png"\n                    data-intro=\'Welcome to the Abstrackr! <br><br> \n                                To navigate through the introduction, please click on the "Back" or "Next" buttons.\n                                Alternatively, you may use the left and right arrow keys on your keyboard.<br><br>\n                                Please enjoy this short introduction.\'\n                    data-step=\'1\'></img>\n        </p>\n       \n\t<div id="login-header"\n        data-intro=\'You may navigate the website via these controls.\'\n        data-step=\'4\'>\n\t <a href="/" data-intro=\'The home link will take you back to this page\' data-step=\'5\'>home</a>  ||\n     <a href="/account/my_account" data-intro=\'This link will take you to your settings page. You may change your password here and set account preferences\' data-step=\'6\'>my account</a> ||\n     <a href="/account/logout" data-intro=\'To securely sign out, please use this link\' data-step=\'9\'>sign out</a> ||\n     <a href="/help/" data-intro=\'For more detailed help, please follow this link. Here you will find instructions and explanation to page specific items and concepts.\' data-step=\'7\'>help</a> ||\n     <a href="/help/citing.html" data-intro=\'If you wish to credit us, please visit this link for citation information\' data-step=\'8\'>citing abstrackr</a>\n\t</div>\n\t\n<!-- *** BEGIN page content *** -->\n')
        # SOURCE LINE 42
        __M_writer(escape(self.body()))
        __M_writer(u'\n<!-- *** END page content *** -->\n\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


