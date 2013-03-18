<%inherit file="../site.mako" />
<%def name="title()">review labels</%def>



%if c.assignment is not None:
<div class = "actions">
    <a href="${url(controller='review', action='screen', review_id=c.assignment.project_id, assignment_id=c.assignment.id)}">ok, get back to screening <img src="../../arrow_right.png"></img></a>
    </div>
%endif


<div class="content">
<div id="labels_fragment">
%if len(c.given_labels) > 0:
    labels you've provided: <br/><br/>
    <center>
    <table width=100% class="list_table" align="center>>
            <tr align="center">
            
            <th span=20>doc id</th>
            <th span=20>refman id</th>
            <th span=20>pubmed id</th>
            <th width="30%">title</th>
            <th>label</th>
            <th>first labeled</th>
            <th>last updated</th>
            
            </tr>
            % for i, label in enumerate(c.given_labels):
                <tr>
                <td>${label.study_id}</td>
                <td>${c.citations_d[label.study_id].refman}</td>
                <td>${c.citations_d[label.study_id].pmid}</td>
                <td>
               
                <a href="${url(controller='review', action='show_labeled_citation', review_id=label.project_id, citation_id=label.study_id, assignment_id=label.assignment_id)}">${c.citations_d[label.study_id].title}</a></td>

                <td>${label.label}</td>
                <td>${label.first_labeled.month}/${label.first_labeled.day}/${label.first_labeled.year}</td>
                <td>${label.label_last_updated.month}/${label.label_last_updated.day}/${label.label_last_updated.year}</td>
                <td></td>
                </tr>
            % endfor
    </table>
    </center>
%else:
    whoops, you've not labeled anything yet. 
%endif
</div>
</div>
