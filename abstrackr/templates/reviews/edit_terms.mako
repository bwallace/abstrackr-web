<%inherit file="../site.mako" />
<%def name="title()">edit terms</%def>

% if "assignment" in dir(c) and c.assignment is not None:
  <div class = "actions">
      <a href="${url(controller='review', action='screen', review_id=c.assignment.project_id, assignment_id=c.assignment.id)}">ok, get back to screening <img src="../../../arrow_right.png"></img></a>
      </div>
% endif

<div class="content">
%if len(c.terms) > 0:
    terms you've labeled: <br/><br/>
    <table class="list_table">
        <th>term</th>
        <th>current label</th>
        <th>delete</th>
        <th>re-label</th>
        % for i,term in enumerate(c.terms):
            <tr class="${'odd' if i%2 else 'even'}">
              <td>${term.term}</td>           
              <td><img src="/${dict(zip([-2, -1, 1, 2],["two_thumbs_down.png", "thumbs_down.png", "thumbs_up.png", "two_thumbs_up.png"]))[term.label]}"></td> 
              <td><a href="/review/delete_term/${term.id}/${c.assignment.id}"><img src = "/reject.png"/></a> </td>
              <td>
                    <a href="/relabel_term/${term.id}/${c.assignment.id}/1"><img src = "/thumbs_up.png" border="2" alt="indicative of relevance"></a>
                    <a href="/relabel_term/${term.id}/${c.assignment.id}/2"><img src = "/two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>
                    <a href="/relabel_term/${term.id}/${c.assignment.id}/-1"><img src = "/thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>
                    <a href="/relabel_term/${term.id}/${c.assignment.id}/-2"><img src = "/two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>
              </td>
            </tr>
        % endfor
    </table>
%else:
   you haven't labeled any terms for this project yet. (in the future, I'll suggest some...)
%endif
</div>
