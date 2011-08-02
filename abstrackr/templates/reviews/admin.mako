
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>


<div class="breadcrumbs">
./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>


<h1>${c.review.name}: administrivia</h1>
<div class="actions">
<a href="${url(controller='review', action='assignments', id=c.review.review_id)}">manage assignments</a>
</div>

<div class="content">

<h2>Participants</h2>
<table class="list_table">
<tr align="center"><th>person</th><th></th></tr>
%for participant in c.participating_reviewers:
       <tr>
       <td>${participant.fullname}</td>
       <td class="actions">
       <a href="/review/remove_from_review/${participant.id}/${c.review.review_id}")>
        remove from review</a>
       </tr>     
       
%endfor
<table>

<br/>

<div align="right">
<form action="${url(controller='review', action='invite_reviewers')}" method="POST">

<div class="actions">
<label for="emails">Want to invite additional reviewers? Enter their emails (comma-separated).</label>
<input type="text" id="emails" name="emails" /><br />
<input type="submit" id="submit" value="invite them" />
</div>
</form>
</div>

<p align="right">
Alternatively, they can join the review themselves using this code: <b>${c.review.code}</b>
</p>


</div>


</div>
