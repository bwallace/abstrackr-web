<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<div class="breadcrumbs">
  ./<a href="${url(controller='account', action='welcome')}">dashboard</a>
</div>

<h1>existing reviews</h1>
<center>
<div class="content">
click the link to join.<br/>
% for review in c.all_reviews:
    <a href = "${url(controller='review', action='join_review', id=review.review_id)}">${review.name}</a> <br/>
% endfor
</div>

</center>