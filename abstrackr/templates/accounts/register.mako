<%inherit file="../site.mako" />
<%def name="title()">register</%def>


<center>


 ${h.form(url(controller='account', action='create_account_handler'))}
    <label>first name: ${h.text('first name')}</label><br/>
    <label>last name: ${h.text('last name')}</label><br/>
    <label>email: ${h.text('email')}</label><br/>
    <label>username: ${h.text('username')}</label><br/>
    <label>password: ${h.text('password', type='password')}</label><br/>
    ${h.submit('post', 'sign me up!')}
  ${h.end_form()}
  
</center>