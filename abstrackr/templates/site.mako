<%def name="title()"></%def>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="stylesheet" href="/stylesheet.css">
        <link rel="stylesheet" href="/jquery-ui-1.8.15.custom.css">
        <link rel="stylesheet" href="/intro.js/introjs.css">
        <link rel="stylesheet" href="/intro.js/introjs-ie.css">

        <script type="text/javascript" src="/scripts/jquery-1.6.2.min.js"></script>
        <script type="text/javascript" src="/scripts/jquery-ui-1.8.15.custom.min.js"></script>
        <script type="text/javascript" src="/scripts/jqModal.js"></script>
        <script type="text/javascript" src="/scripts/CalendarPopup.js"></script>
        <script type="text/javascript" src="/scripts/jquery.ui.selectable.js"></script>
        <script type="text/javascript" src="/intro.js/intro.js"></script>
  
        <title>abstrackr: ${self.title()}</title>
    </head>
    <body>

        <p align="left">
            <img src="http://sunfire34.eecs.tufts.edu/abstrackr.png"
                    data-intro='Welcome to the Abstrackr! <br><br> 
                                To navigate through the introduction, please click on the "Back" or "Next" buttons.
                                Alternatively, you may use the left and right arrow keys on your keyboard.<br><br>
                                Please enjoy this short introduction.'
                    data-step='1'></img>
        </p>
       
	<div id="login-header"
        data-intro='You may navigate the website via these controls.'
        data-step='4'>
	 <a href="/" data-intro='The home link will take you back to this page' data-step='5'>home</a>  ||
     <a href="/account/my_account" data-intro='This link will take you to your settings page. You may change your password here and set account preferences' data-step='6'>my account</a> ||
     <a href="/account/logout" data-intro='To securely sign out, please use this link' data-step='9'>sign out</a> ||
     <a href="/help/" data-intro='For more detailed help, please follow this link. Here you will find instructions and explanation to page specific items and concepts.' data-step='7'>help</a> ||
     <a href="/citing/" data-intro='If you wish to credit us, please visit this link for citation information' data-step='8'>citing abstrackr</a>
	</div>
	
<!-- *** BEGIN page content *** -->
${self.body()}
<!-- *** END page content *** -->

    </body>
</html>
