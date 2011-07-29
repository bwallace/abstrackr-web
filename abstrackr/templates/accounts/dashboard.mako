<%inherit file="../site.mako" />
<%def name="title()">home</%def>


	
%if c.my_projects:
    <a class="tab" href = "${url(controller='account', action='my_work')}">my work</a>
    <a class="active_tab" href="${url(controller='account', action='my_projects')}">my projects</a>
%elif c.my_work:
    <a class="active_tab" href = "${url(controller='account', action='my_work')}">my work</a>
    <a class="tab" href="${url(controller='account', action='my_projects')}">my projects</a>
%endif
<div class="content">

<br/> 
%if c.my_projects:

    %if len(c.leading_projects) > 0:
        <h2>projects you're leading</h2> <br/><br/>
        <center>

        
        <br/>
        <table class="list_table">
        
        % for i,review in enumerate(c.leading_projects):
        <tr class="${'odd' if i%2 else 'even'}">
            <td><a href="${url(controller='review', action='show_review', id=review.review_id)}">${review.name}</td>           
            <td class="inline-actions"><a href="${url(controller='review', action='admin', id=review.review_id)}">admin 
                         <img src = "../../admin_sm.png"></a></td> 
            <td class="inline-actions"><a href="${url(controller='review', action='export_labels', id=review.review_id)}">
                      export<img src = "../../export_sm.png"></a></td>
            <td class="inline-actions"><a href="${url(controller='review', action='review_conflicts', id=review.review_id)}">
                      review conflicts<img src = "../../conflicts_sm.png"></a></td>
            <td class="inline-actions"><a href="${url(controller='review', action='delete_review', id=review.review_id)}" 
                           onclick="javascript:return confirm('are you sure you want to delete this review? all labels will be lost!')">
                      delete<img src = "../../delete.png"></a></td> 
        </tr>
        % endfor
        </table>
        <br/><br/><br/>
        </center>
    % endif 

    %if len(c.participating_projects) > 0:
        <h2>projects you're participating in</h2> <br/><br/>
        <table class="list_table">
        % for i,review in enumerate(c.participating_projects):
        <tr class="${'odd' if i%2 else 'even'}">
            <td><a href="${url(controller='review', action='show_review', id=review.review_id)}">${review.name}</td>    
            <td class="inline-actions"><a href="${url(controller='review', action='leave_review', id=review.review_id)}" 
                           onclick="javascript:return confirm('are you sure you want to leave this review?')">
            leave review</a></td>      
        </tr>
        % endfor
        </table>
    % else:
        <h2>you're not participating in any projects yet.</h2>
    % endif
    <br/>
    
    <br/><br/>

    <center>
     <div class="actions">
    <a href="${url(controller='review', action='create_new_review')}"><img src ="../../add.png">start a new project/review</a>
    </center>    
    </div>

    
%elif c.my_work:

    %if len(c.outstanding_assignments) > 0:
        <h2>work you should be doing </h2><br/><br/>
        <center>
        <table class="list_table" align="center>>
                <tr align="center">
                <th width="25%">review</th><th >number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="10%">due</th><th width="30%"></th>
                </tr>
                % for i, assignment in enumerate(c.outstanding_assignments):
                    <tr>
                    <td><a href="${url(controller='review', action='show_review', id=assignment.review_id)}">
                            ${c.review_ids_to_names_d[assignment.review_id]}</td>          
                    %if not assignment.assignment_type == "perpetual":
                        <td>${assignment.num_assigned}</td>
                    %else:
                        <td>--</td>
                    %endif
                    
                    <td>${assignment.done_so_far}</td>
                    <td>${assignment.date_assigned.month}/${assignment.date_assigned.day}/${assignment.date_assigned.year}</td>
                    %if not assignment.assignment_type == "perpetual" and assignment.date_due is not None:
                        <td>${assignment.date_due.month}/${assignment.date_due.day}/${assignment.date_due.year}</td>
                    %else:
                        <td>--</td>
                    %endif
                    <td class="inline-actions">
                    <a href="${url(controller='review', action='screen', review_id=assignment.review_id, assignment_id=assignment.id)}">
                    screen <img src="../../arrow_right.png"></img></a></td>
                    </tr>
                % endfor
        </table>
        </center>
         <br/><br/>
    %else:
        <h2>hurray, you've no outstanding assignments!</h2>
    %endif
    
    % if len(c.finished_assignments) > 0:
        <h2>assignments you've completed</h2> <br/>
        <center>
        <table width=80% class="list_table" align="center>>
                <tr align="center">
                <th width="25%">review</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th>
                </tr>
                % for i,assignment in enumerate(c.finished_assignments):
                    <tr>
                    <td><a href="${url(controller='review', action='show_review', id=assignment.review_id)}">
                            ${c.review_ids_to_names_d[assignment.review_id]}</td>          
                    %if not assignment.assignment_type == "perpetual":
                        <td>${assignment.num_assigned}</td>
                    %else:
                        <td>--</td>
                    %endif
                    <td>${assignment.done_so_far}</td>
                    <td>${assignment.date_assigned.month}/${assignment.date_assigned.day}/${assignment.date_assigned.year}</td>
                    %if not assignment.assignment_type == "perpetual" and assignment.date_due is not None:
                        <td>${assignment.date_due.month}/${assignment.date_due.day}/${assignment.date_due.year}</td>
                    %else:
                        <td>--</td>
                    %endif
                    
                    </tr>
                % endfor
        </table>
        </center>
    % endif
%endif

</div>