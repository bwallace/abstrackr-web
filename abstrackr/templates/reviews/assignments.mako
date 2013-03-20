
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>


<div class="breadcrumbs">
<a href="${url(controller='account', action='welcome')}">./dashboard</a>/<a href="${url(controller='review', action='show_review', id=c.review.id)}">${c.review.name}</a>
</div>


<h1>${c.review.name}: administrivia</h1>

<div class="actions">
    <a href="${url(controller='review', action='admin', id=c.review.id)}">Manage Participants</a>
    <a href="${url(controller='review', action='assignments', id=c.review.id)}">Manage Assignments</a>
    <a href="${url(controller='review', action='edit_review', id=c.review.id)}">Edit Settings</a>
    <a href="${url(controller='review', action='render_add_citations', id=c.review.id)}">Add Citations</a>
</div>

<div class="content">

<h2>existing assignments</h2> 
    <center>
    <table width=80% class="list_table" align="center>>
            <tr align="center">
            <th width="25%">reviewer</th><th span=20>number to screen</th><th>screened so far</th><th width="20%">assigned</th><th width="20%">due</th><th>delete</th>
            </tr>
            % for i,assignment in enumerate(c.assignments):
                <tr>
                <td>${c.reviewer_ids_to_names_d[assignment.user_id]}</td>     
                % if assignment.num_assigned < 0:
                    <td>--</td>
                % else:
                    <td>${assignment.num_assigned}</td>
                % endif     
                <td>${assignment.done_so_far}</td>
                % if assignment.date_assigned is not None:
                    <td>${assignment.date_assigned.month}/${assignment.date_assigned.day}/${assignment.date_assigned.year}</td>
                % endif
                % if assignment.date_due is not None:
                    <td>${assignment.date_due.month}/${assignment.date_due.day}/${assignment.date_due.year}</td>
                % else:
                    <td>N/A</td>
                % endif
                <td><a href=
                       "${url(controller='review', action='delete_assignment', review_id=c.review.id, assignment_id=assignment.id)}">
                       <img src="/delete_sm.png"></img></a>
                </tr>
            % endfor
    </table>
    </center>
<br/><br/>

<h2>create new assignment</h2>
<center>
<br/>
<form name="new_assignment" action="${url(controller='review', action='create_assignment', id=c.review.id)}">
assign to: <br/><br/>
% for reviewer in c.participating_reviewers:
    <input type="checkbox" name="assign_to" value="${reviewer.username}" checked="yes"/> ${reviewer.username}<br/>
% endfor
<br/><br/>
<table>
<tr><td>number of citations for each assignee to screen:</td><td> <INPUT TYPE="text" NAME="n" SIZE=10></td></tr>
<tr><td>percent of these that should be re-screens:</td><td> <INPUT TYPE="text" NAME="p_rescreen" VALUE="0" SIZE=10>
</td>
</tr>
<tr>
<td>
due date:</td><td> 
<INPUT TYPE="text" NAME="due_date" VALUE="" SIZE=10>
<a href="#"
   onClick="cal.select(document.forms['new_assignment'].due_date,'anchor1','MM/dd/yyyy'); return false;"
   NAME="anchor1" ID="anchor1">select</A> </td></tr>
  <tr><td></td><td class="actions"><INPUT TYPE=SUBMIT VALUE="create assignment"></td></tr>
</table>
</form>
</center>


</div>
