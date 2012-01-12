<%inherit file="../site_out.mako" />
<%def name="title()">register</%def>


<div class="content">
    <center>
    
<table class="form_table">
  

 ${h.form(url(controller='account', action='create_account_handler', then_join=c.then_join if 'then_join' in dir(c) else ''))}
    <tr><td><label>first name:</td> <td>${h.text('first_name')}</label></td></tr>
    <tr><td><label>last name:</td> <td>${h.text('last_name')}</label></td></tr>
    <tr><td><label>how many SRs have you participated in?:</td> <td>${h.text('experience', size=2)}</label></td></tr>
    <tr><td><label>email:</td> <td>${h.text('email')}</label></td></tr>
    <tr><td><label>username:</td> <td>${h.text('username')}</label></td></tr>
    <tr><td><label>password:</td> <td>${h.text('password', type='password')}</label></td></tr>
    <tr><td></td><td>${h.submit('post', 'sign me up!')}</td></tr>
  ${h.end_form()}
  </table>
  </center>
</div>