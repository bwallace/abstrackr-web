
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>



<h1>${c.review.name}</h1>
	<div class="actions">
    <a
      href="${url(controller='review', action='review_labels', review_id=c.review.id)}">review labels</a>
    <a 
      href="${url(controller='review', action='review_terms', id=c.review.id)}">review terms</a>
</div>
<div class="content">
<h2>Project description</h2> 
${c.review.description}
<br/><br/>
<h2>Progress</h2>

% if float(c.num_labels)/float(c.num_citations) >= .1:
	<center><img src = "${c.pi_url}"></img></center><br/>
% endif

There are ${c.num_citations} citations in this review, so far ${c.num_labels} have been labeled.
<br/><br/>

<h2>Participants</h2>
This review is lead by
<div>
    <ul>
        % for leader in c.project_leaders:
            <li>
                ${leader.fullname}
            </li>
        % endfor
    </ul>
</div>
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
