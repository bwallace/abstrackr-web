<%inherit file="../site.mako" />
<%def name="title()">home</%def>

<h1>hi there, ${c.person.fullname}.</h1>

<div class="content">


<br/>

<table class="list_table">

%if len(c.leading_projects) > 0:
    projects you're leading: <br/><br/>
    % for i,review in enumerate(c.leading_projects):
    <tr class="${'odd' if i%2 else 'even'}">
        <td>${review.name}</td>           
    </tr>
    % endfor
    </table>
% endif 

<br/><br/>

projects you're participating in: <br/><br/>

<table class="list_table">
% for i,review in enumerate(c.participating_projects):
<tr class="${'odd' if i%2 else 'even'}">
    <td>${review.name}</td>           
    <td><a href = "${url(controller='review', action='screen', id=review.review_id)}">start screening</a> </td>
</tr>
% endfor
</table>

<br/><br/>
want to <a href = "${url(controller='review', action='join_a_review')}">join an existing review?</a>
<br/><br/>
or maybe you want to <a href = "${url(controller='review', action='create_new_review')}">start a new review?</a>
</div>