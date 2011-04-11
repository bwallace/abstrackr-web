<%inherit file="../site.mako" />
<%def name="title()">home</%def>

<h1>hi there, ${c.person.fullname}.</h1>

<p align="right"> 
<a class="tab" href = "${url(controller='review', action='join_a_review')}">join an existing review</a>
<a class="tab" href="${url(controller='review', action='create_new_review')}">start a new review</a>
</p>

<div class="content">

<br/>

%if len(c.leading_projects) > 0:
    projects you're leading: <br/><br/>
    <center>
    <div>
    <img style="vertical-align:middle" src = "../../admin.png"><span style="">= go to the administration page</span>
    <img style="vertical-align:middle"  src = "../../export_sm.png"><span style="">= export labels</span>
    <img style="vertical-align:middle" src = "../../delete.png"><span style="">= delete review</span>
    <div>
    
    <br/>
    <table class="list_table">
    % for i,review in enumerate(c.leading_projects):
    <tr class="${'odd' if i%2 else 'even'}">
        <td><a href="${url(controller='review', action='show_review', id=review.review_id)}">${review.name}</td>           
        <td><a href="${url(controller='review', action='admin', id=review.review_id)}">
                     <img src = "../../admin.png"></a></td> 
        <td><a href="${url(controller='review', action='export_labels', id=review.review_id)}">
                  <img src = "../../export_sm.png"></a></td>
        <td><a href="${url(controller='review', action='delete_review', id=review.review_id)}" 
                       onclick="javascript:return confirm('are you sure you want to delete this review?\nall labels will be lost.')">
                  <img src = "../../delete.png"></a></td> 
    </tr>
    % endfor
    </table>
    <br/><br/>
% endif 

%if len(c.participating_projects) > 0:
    projects you're participating in: <br/><br/>
    <table class="list_table">
    % for i,review in enumerate(c.participating_projects):
    <tr class="${'odd' if i%2 else 'even'}">
        <td><a href="${url(controller='review', action='show_review', id=review.review_id)}">${review.name}</td>    
        <td><a href="${url(controller='review', action='leave_review', id=review.review_id)}" 
                       onclick="javascript:return confirm('are you sure you want to leave this review?')">
        leave review</a></td>      
    </tr>
    % endfor
    </table>
% else:
    you're not participating in any projects yet.
% endif


<br/><br/>
%if len(c.outstanding_assignments) > 0:
    work you should be doing: <br/><br/>
    <center>
    <table width=80% class="list_table" align="center>>
            <tr align="center">
            <th width="25%">review</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th><th width="20%"></th>
            </tr>
            % for i,assignment in enumerate(c.outstanding_assignments):
                <tr>
                <td><a href="${url(controller='review', action='show_review', id=assignment.review_id)}">
                        ${c.review_ids_to_names_d[assignment.review_id]}</td>          
                <td>${assignment.num_assigned}</td>
                <td>${assignment.done_so_far}</td>
                <td>${assignment.date_assigned.month}/${assignment.date_assigned.day}/${assignment.date_assigned.year}</td>
                <td>${assignment.date_due.month}/${assignment.date_due.day}/${assignment.date_due.year}</td>
                <td width=30>
                <a href="${url(controller='review', action='screen', review_id=assignment.review_id, assignment_id=assignment.id)}">
                get to work!</a></td>
                </tr>
            % endfor
    </table>
    </center>
%else:
    hurray, you've no outstanding assignments!    
%endif

<br/><br/>

% if len(c.finished_assignments) > 0:
    assignments you've completed: <br/>
    <center>
    <table width=80% class="list_table" align="center>>
            <tr align="center">
            <th width="25%">review</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th>
            </tr>
            % for i,assignment in enumerate(c.finished_assignments):
                <tr>
                <td><a href="${url(controller='review', action='show_review', id=assignment.review_id)}">
                        ${c.review_ids_to_names_d[assignment.review_id]}</td>          
                <td>${assignment.num_assigned}</td>
                <td>${assignment.done_so_far}</td>
                <td>${assignment.date_assigned.month}/${assignment.date_assigned.day}/${assignment.date_assigned.year}</td>
                <td>${assignment.date_due.month}/${assignment.date_due.day}/${assignment.date_due.year}</td>
                </tr>
            % endfor
    </table>
    </center>
% endif


</div>