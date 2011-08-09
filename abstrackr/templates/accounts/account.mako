<%inherit file="../site.mako" />

<%def name="title()">my account</%def>

<div class="content">


<h2>${c.account_msg}</h2>

to change your password:
    
<table class="form_table">
 ${h.form(url(controller='account', action='change_password'))}
    <tr><td><label>new password:</td> <td>${h.text('password', type='password')}</label></td></tr>
    <tr><td><label>confirm new password:</td> <td>${h.text('password_confirm', type='password')}</label></td></tr>
    <tr><td></td><td>${h.submit('post', 'change password')}</td></tr>
  ${h.end_form()}
  </table>
  </center>
</div>
