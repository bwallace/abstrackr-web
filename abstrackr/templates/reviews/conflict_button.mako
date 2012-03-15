% if c.display_the_button:
    <td class="inline-actions"><a href="${url(controller='review', action='review_conflicts', id=c.review_id)}">
        conflicts<img src = "../../conflicts_sm.png"></a></td>    
% else:
    <td class="inline-actions"><i>no conflicts yet</i></td>
% endif