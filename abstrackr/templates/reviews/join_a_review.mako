<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<center>

<h2>existing reviews</h2>
click the link to join.<br/>
% for review in c.all_reviews:
    <a href = "${url(controller='review', action='join_review', id=review.review_id)}">${review.name}</a> <br/>
% endfor

</center>