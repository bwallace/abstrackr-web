<%inherit file="../site.mako" />
<%def name="title()">home</%def>


<script type="text/javascript" src="/scripts/jquery.alerts.js"></script>

<link href="/scripts/jquery.alerts.css"  rel="stylesheet" type="text/css" media="screen" />

<script language="javascript">

    $(document).ready(function() { 
  

        $("#export").dialog({
            height: 500,
            width:500, 
            modal: true,
            autoOpen: false,
            show: "blind",
        });
        
        
    });

</script>


<div id="export" class="dialog">
</div>

<button type="button" onclick="introJs().start()">Quick Tour!</button>
	
%if c.my_work:
    <a class="active_tab" href="${url(controller='account', action='my_work')}"
            data-intro='You will find all of your projects summarized on this tab'
            data-step='2'>my work</a>
    <a class="tab" href="${url(controller='account', action='my_projects')}"
            data-intro='On this tab you will find all the projects you are leading'
            data-step='3'>my projects</a>
%elif c.my_projects:
    <a class="tab" href="${url(controller='account', action='my_work')}"
            data-intro='You will find all of your projects summarized on this tab'
            data-step='2'>my work</a>
    <a class="active_tab" href="${url(controller='account', action='my_projects')}"
            data-intro='On this tab you will find all the projects you are leading'
            data-step='3'>my projects</a>
%endif
<div class="content">

<br/> 
%if c.my_projects:

    %if len(c.leading_projects) > 0:
        <h1>projects you're leading</h1>
        <center>

        <br/>
        <table class="list_table">
        
        % for i,review in enumerate(c.leading_projects):
        <tr class="${'odd' if i%2 else 'even'}">
            <td><a href="${url(controller='review', action='show_review', id=review.id)}">${review.name}</td>           
            <td class="inline-actions"><a href="${url(controller='review', action='admin', id=review.id)}">admin 
                         <img src = "../../admin_sm.png"></a></td> 
            <td class="inline-actions">
            <a href="#" onclick="javascript:    
                      $('#export').load('${url(controller="review", action="get_fields", review_id=review.id)}', 
                        function() {
                            $('#export').dialog('open');
                            $('#selectable').selectable();
                      });
                      ">
                      export<img src = "../../export_sm.png"></a></td>
                    
            % if c.statuses[review.id]:
                <td class="inline-actions"><a href="${url(controller='review', action='predictions_about_remaining_citations', id=review.id)}">predictions
                            <img src = "../../Robot-icon.png"></a></td>
            % else:
                <td class="inline-actions"><i>no predictions yet</i></td>
            % endif
            
            <td id="conflict_button_${review.id}">loading...</td>
            <script language="javascript">
                $("#conflict_button_${review.id}").load("/review/get_conflict_button_fragment/${review.id}");
            </script>
            
            % if c.do_we_have_a_maybe:
                <td class="inline-actions"><a href="${url(controller='review', action='review_maybes', id=review.id)}">
                    maybes<img src = "../../maybe_sm.png"></a></td>
            % else:
                <td class="inline-actions"><i>no maybes yet</i></td>
            % endif
            
            <td class="inline-actions">
                <a href="#" onclick="javascript:jConfirm('are you sure you want to delete this review? all labels will be lost!', 
                     'delete review?', function(r) {
                        if(r) window.location = '${url(controller='review', action='delete_review', id=review.id)}'; 
                   });">delete<img src = "../../delete.png"></a></td> 
        </tr>
        % endfor
        </table>
        <br/><br/><br/>
        </center>
    % endif 
 
    %if len(c.participating_projects) > 0:
        <h1>projects in which you're participating</h1>
        <table class="list_table">
        % for i,review in enumerate(c.participating_projects):
        <tr class="${'odd' if i%2 else 'even'}">
            <td><a href="${url(controller='review', action='show_review', id=review.id)}">${review.name}</td>    
            <td class="inline-actions"><a href="${url(controller='review', action='review_labels', review_id=review.id)}">review my labels</td>  
            <td class="inline-actions"><a href="${url(controller='review', action='leave_review', id=review.id)}" 
                           onclick="javascript:return confirm('are you sure you want to leave this review?')">
            leave review</a></td>      
        </tr>
        % endfor
        </table>
    % else:
        % if len(c.leading_projects) > 0:
            <h2>you're not participating in any projects yet (aside from those you're leading).</h2>
        % else:
            <h2>you're not participating in any projects yet.</h2>
        % endif
    % endif
    <br/>
    
    <br/><br/>

    <center>
     <div class="actions">

     % if len(c.leading_projects) > 1:
        <a href="${url(controller='account', action='show_merge_review_screen')}"><img src ="../../merge_sm.png">merge reviews ...</a>
     % endif
    <a href="${url(controller='review', action='create_new_review')}"><img src ="../../add.png">start a new project/review</a>
    </center>    
    </div>

    
%elif c.my_work:

    %if len(c.outstanding_assignments) > 0:
        <h1>work you should be doing </h1>
        <center>
        <table class="list_table" align="center>>
                <tr align="center">
                <th width="25%">review</th><th >number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="10%">due</th><th width="30%">actions</th>
                </tr>
                % for i, assignment in enumerate(c.outstanding_assignments):
                    <tr>
                    <td><a href="${url(controller='review', action='show_review', id=assignment.project_id)}">
                            ${c.review_ids_to_names_d[assignment.project_id]}</td>          
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
                    <a href="${url(controller='review', action='screen', review_id=assignment.project_id, assignment_id=assignment.id)}">
                    screen <img src="../../arrow_right.png"></img></a>
                    <a href="${url(controller='review', action='review_labels', review_id=assignment.project_id, assignment_id=assignment.id)}">review labels <img src="../../arrow_right.png"></a>
                    </td>
                    </tr>
                % endfor
        </table>
        </center>
         <br/><br/>
    %else:
        <h2>hurray, you've no outstanding assignments!</h2><br/><br/>
    %endif
    
    % if len(c.finished_assignments) > 0:
        <h1>assignments you've completed</h1>
        <center>
        <table width=80% class="list_table" align="center>>
                <tr align="center">
<th width="25%">review</th><th >number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="10%">due</th><th width="30%">actions</th>
                </tr>
                % for i,assignment in enumerate(c.finished_assignments):
                    <tr>
                    <td><a href="${url(controller='review', action='show_review', id=assignment.project_id)}">
                            ${c.review_ids_to_names_d[assignment.project_id]}</td>          
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
                                      <a href="${url(controller='review', action='review_labels', review_id=assignment.project_id, assignment_id=assignment.id)}">review labels <img src="../../arrow_right.png"></a>
                        </td>
                    </td>
                    </tr>
                % endfor
        </table>
        </center>
    % endif
%endif

</div>
