<%inherit file="../site.mako" />
<%def name="title()">register</%def>

<center>
<form action="${url(controller='account', action='create_account_handler')}" method="POST">

<label for="first name">first name</label>
<input type="text" id="first name" name="first name" /><br />

<label for = "last name">last name</label>
<input type="text" id="last name" name="last name" /><br />

<label for = "email">email</label>
<input type="text" id="email" name="email" /><br />

<label for="username">username</label>
<input type="text" id="username" name="username" /><br />
<label for="password">password</label>
<input type="password" id="password" name="password" /><br />

<input type="submit" id="submit" value="Submit" />

</form>


</center>