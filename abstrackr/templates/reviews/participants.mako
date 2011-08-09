<%inherit file="../site.mako" />

<%def name="title()">${c.review.name}</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>


<div class="breadcrumbs">
<a href="${url(controller='account', action='welcome')}">./dashboard</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>


<h1>${c.review.name}: administrivia</h1>

<div class="actions"> 
<a class="tab" href="${url(controller='review', action='admin', id=c.review.review_id)}">manage participants</a>
</div>

<div class="content">
Want to invite additional reviewers? <br/>Just have them follow this link (while logged in to abstrackr): <a href="http://localhost:5000/join/${c.review.code}">http://localhost:5000/review/join/${c.review.code}</a>



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

</div>
