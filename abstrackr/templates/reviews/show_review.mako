
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>


<div class="breadcrumbs">
<a href="${url(controller='account', action='welcome')}">./dashboard</a>
</div>


<h1>${c.review.name}</h1>

<div class="content">
<h2>Project description</h2> 
${c.review.project_description}
<br/><br/>
<h2>Progress</h2>
<center><img src = "${c.pi_url}"></img></center><br/>
There are ${c.num_citations} in this review, so far ${c.num_labels} have been labeled.
<br/><br/>

<h2>Participants</h2>
Number of citations screened by reviewers:
<center><img src = "${c.workload_graph_url}"></img></center><br/>
This review is lead by ${c.project_lead.fullname}.
<br/>
The following people are reviewers on the project:<br/>
${"<br/>".join([user.fullname for user in c.participating_reviewers])}
<br/>

</div>
