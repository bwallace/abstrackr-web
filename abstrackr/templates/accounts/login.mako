<%inherit file="../site.mako" />
<%def name="title()">home</%def>

% if c.login_counter > 1:
    Incorrect Username or Password
% endif

<center>
<form action="${url(controller='account', action='login_handler'
,came_from=c.came_from, __logins=c.login_counter)}" method="POST">
<label for="login">username</label>
<input type="text" id="login" name="login" /><br />
<label for="password">password</label>
<input type="password" id="password" name="password" /><br />
<input type="submit" id="submit" value="Submit" />
</form>

don't have an account yet? <a href="${url(controller='account', action='create_account')}">register here</a>.
</center>