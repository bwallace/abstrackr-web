<%def name="title()"></%def>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="stylesheet" href="/stylesheet.css">
        <link rel="stylesheet" href="/jquery-ui-1.8.15.custom.css">

        <script type="text/javascript" src="/scripts/jquery-1.6.2.min.js"></script>
        <script type="text/javascript" src="/scripts/jquery-ui-1.8.15.custom.min.js"></script>
        <script type="text/javascript" src="/scripts/jqModal.js"></script>
        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>
        <script type="text/javascript" src="/scripts/jquery.ui.selectable.js"></script>
  
        <title>abstrackr: ${self.title()}</title>
    </head>
    <body>

        <p align="left">
        <img src = "http://sunfire34.eecs.tufts.edu/abstrackr.png"></img>
        </p>
       
	<div id="login-header">
	 <a href="/">home</a>  || <a href="/account/my_account">my account</a> || <a href="/account/logout">sign out</a> || <a href="/help/">help</a> || <a href="/help/citing.html">citing abstrackr</a>
	</div>
	
<!-- *** BEGIN page content *** -->
${self.body()}
<!-- *** END page content *** -->

    </body>
</html>
