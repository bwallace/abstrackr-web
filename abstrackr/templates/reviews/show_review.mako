
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>



<h1>${c.review.name}</h1>


<div class="content">
<h2>Project description</h2> 
${c.review.project_description}
<br/><br/>
<h2>Progress</h2>
There are ${c.num_citations} in this review, so far ${c.num_labels} have been labeled.
<br/><br/>

<h2>Participants</h2>
This review is lead by Ethan. 
<br/><br/>
The following people are reviewing:<br/>
Stanley<br/>
Mei
</div>
