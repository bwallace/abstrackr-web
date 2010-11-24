<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<center>

 ${h.form(url(controller='review', action='create_review_handler'), multipart=True)}
    <label>project name: ${h.text('name')}</label><br/>
    <label>project description: ${h.textarea('description', rows="10", cols="40")}</label><br/>
    <label>upload file: ${h.file('db')} </label><br />
    ${h.submit('post', 'create new review')}
  ${h.end_form()}

</center>