<%inherit file="site.mako" />
<%def name="title()">home</%def>

% if c.login_counter > 1:
    Incorrect Username or Password
% endif

<form action="${url(controller='account', action='login_handler'
,came_from=c.came_from, __logins=c.login_counter)}" method="POST">
<label for="login">Username:</label>
<input type="text" id="login" name="login" /><br />
<label for="password">Password:</label>
<input type="password" id="password" name="password" /><br />
<input type="submit" id="submit" value="Submit" />
</form> 
