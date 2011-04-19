
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>


<div class="breadcrumbs">
<a href="${url(controller='account', action='welcome')}">./dashboard</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>


<h1>Your review (${c.review.name}) has been succesfully created!</h1>

<div class="content">

Awesome, you're ready to start screening.

<br/><br/>
<b>What now?</b>, you ask. 
<br/><br/>
Have any other reviewers that will be screening abstracts register on abstrackr, if they have not. They can then join this review by following this link (send it to them):

<center>
<h2><a href="http://localhost:5000/join/${c.review.code}">http://localhost:5000/join/${c.review.code}</a></h2>
</center>


</div>
