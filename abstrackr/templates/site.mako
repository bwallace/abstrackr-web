<%def name="title()"></%def>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="stylesheet" href="/stylesheet.css">
        <link rel="stylesheet" href="/jquery-ui-1.8.15.custom.css">
        <link rel="stylesheet" href="/intro.js/introjs.css">

        <script type="text/javascript" src="/scripts/jquery-1.6.2.min.js"></script>
        <script type="text/javascript" src="/scripts/jquery-ui-1.8.15.custom.min.js"></script>
        <script type="text/javascript" src="/scripts/jqModal.js"></script>
        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>
        <script type="text/javascript" src="/scripts/jquery.ui.selectable.js"></script>
        <script type="text/javascript" src="/intro.js/intro.js"></script>

        <style type="text/css">
            #flash {
                background: #ffc;
                padding: 5px;
                border: 1px dotted #000;
                margin-bottom: 20px;
            }
            #flash p { margin: 0px; padding: 0px; }
            #announcement {
                background: #FFCC00;
                padding: 5px;
                border: 1px solid #000;
                margin-bottom: 20px;
            }
        </style>
  
        <title>abstrackr: ${self.title()}</title>
    </head>
    <body>

        <p align="left">
            <img src="../../abstrackr.png"
                    data-intro='Welcome to the Abstrackr! <br><br> 
                                To navigate through the introduction, please click on the "Back" or "Next" buttons.
                                Alternatively, you may use the left and right arrow keys on your keyboard.<br><br>
                                Please enjoy this short introduction.'
                    data-step='1'></img>
        </p>

      <!-- You can place announcements here
        <div id="announcement">
        </div>
      -->

        ${self.flash()}

	<div id="login-header"
        data-intro='You may navigate the website via these controls.'
        data-step='4'>
	 <a href="/" data-intro='The home link will take you back to this page' data-step='5'>home</a>  ||
     <a href="/account/my_account" data-intro='This link will take you to your settings page. You may change your password here and set account preferences' data-step='6'>my account</a> ||
     <a href="/account/logout" data-intro='To securely sign out, please use this link' data-step='9'>sign out</a> ||
     <a href="/help/" data-intro='For more detailed help, please follow this link. Here you will find instructions and explanation to page specific items and concepts.' data-step='7'>help</a> ||
     <a href="/privacy/" data-intro='Follow this link to learn more about how we protect user data.' data-step='8'>privacy policy</a> ||
     <a href="/citing/" data-intro='If you wish to credit us, please visit this link for citation information' data-step='9'>citing abstrackr</a>
	</div>
	
<!-- *** BEGIN page content *** -->
${self.body()}
<!-- *** END page content *** -->

    </body>
</html>

<%def name="flash()">
    % if session.has_key('flash'):
    <div id="flash"><p>${session.get('flash')}</p></div>
    <%
        del session['flash']
        session.save()
    %>
    % endif
</%def>
