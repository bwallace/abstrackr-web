<%def name="title()"></%def>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>MyBlog: ${self.title()}</title>
    </head>
    <body>
        <h1>${self.title()}</h1>

<!-- *** BEGIN page content *** -->
${self.body()}
<!-- *** END page content *** -->

    </body>
</html>
