<%inherit file="../site.mako" />
<%def name="title()">home</%def>

hi there, ${c.person.fullname}
<br/><br/>
want to <a href = "${url(controller='review', action='create_new_review')}">start a new review?</a>
