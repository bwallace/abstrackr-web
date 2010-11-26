
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>

<center>

<h2>${c.review.name}</h2>
Project description: ${c.review.project_description}
<br/><br/>
There are ${c.num_citations} in this review, so far ${c.num_labels} have been labeled.

</center>