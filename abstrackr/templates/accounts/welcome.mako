<%inherit file="../site.mako" />
<%def name="title()">home</%def>

<h2>hi there, ${c.person.fullname}</h2>

projects you're participating in: <br/>
% for review in c.participating_projects:
    ${review.name}           <a href = "${url(controller='review', action='screen', id=review.review_id)}">screen!</a> <br/>
% endfor


<br/>
projects you're leading: ${c.leading_projects}
<br/><br/>
want to <a href = "${url(controller='review', action='join_a_review')}">join an existing review?</a>
<br/><br/>
or maybe you want to <a href = "${url(controller='review', action='create_new_review')}">start a new review?</a>
