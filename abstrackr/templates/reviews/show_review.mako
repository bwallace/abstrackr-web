
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>


<div class="breadcrumbs">
<a href="${url(controller='account', action='welcome')}">./dashboard</a>
</div>


<h1>${c.review.name}</h1>

% if c.is_admin:
    <p align="right"><a class="tab" href="${url(controller='review', action='admin', id=c.review.review_id)}">admin</a></p>
% endif
<div class="content">
<h2>Project description</h2> 
${c.review.project_description}
<br/><br/>
<h2>Progress</h2>
<center><img src = "${c.pi_url}"></img></center><br/>
There are ${c.num_citations} in this review, so far ${c.num_labels} have been labeled.
<br/><br/>

<h2>Participants</h2>
This review is lead by ${c.project_lead.fullname}.<br/>
<br/>
% if len(c.participating_reviewers) > 1:
    The following people are reviewers on the project: 
    % for user in c.participating_reviewers[:-1]:
        ${user.fullname},
    % endfor
    and ${c.participating_reviewers[-1].fullname}.
% else:
    This project is a lonely undertaking by ${c.participating_reviewers[0].fullname}.
% endif
<br/><br/>
Number of citations screened by reviewers:
<center>
<img src= "${c.workload_graph_url}">
</center>
</div>
