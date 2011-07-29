
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>


<div class="breadcrumbs">
./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>


<h1>${c.review.name}: administrivia</h1>

<p align="right"> 
<a class="tab" href="${url(controller='review', action='assignments', id=c.review.review_id)}">assignments</a>
<a class="tab" href="${url(controller='review', action='participants', id=c.review.review_id)}">participants</a>
</p>

<div class="content">
Review conflicts

</div>
