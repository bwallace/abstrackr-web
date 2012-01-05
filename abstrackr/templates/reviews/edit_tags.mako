<%inherit file="../site.mako" />
<%def name="title()">edit tags</%def>


<script type="text/javascript">    

$(document).ready(function() {
    $( "#dialog" ).dialog({
      height: 120,
      modal: true,
      autoOpen: false,
      show: "blind",
    });


    % for tag in c.tags:
      $("#edit_button_${tag.id}").click(function()
      {

         $("#dialog").load('/review/edit_tag/${tag.id}/${c.assignment_id}',
           function(){
                $("#dialog").dialog("open");
           });
      });
    % endfor 

    $("#close_btn").click(function (e)
    {
       $("#dialog" ).dialog( "close" );
    });
});

</script>
          
  


<div id="dialog"></div>

% if "assignment_id" in dir(c):
  <div class = "actions">
      <a href="${url(controller='review', action='screen', review_id=c.review_id, assignment_id=c.assignment_id)}">ok, get back to screening <img src="../../../arrow_right.png"></img></a>
      </div>
% endif

<div class="content">

%if len(c.tags) > 0:
    your tags: <br/><br/>
    <table class="list_table">
        <th>tag</th>
        <th>edit</th>
        <th>delete</th>
        % for i,tag in enumerate(c.tags):
            <tr class="${'odd' if i%2 else 'even'}">
              <td>${tag.text}</td>           
              <td class="actions" align="left"><input type="button" id="edit_button_${tag.id}" value="re-name tag..."/></td>
                <td><a href="/review/delete_tag/${tag.id}/${c.assignment_id}"><img src = "/reject.png"/>
                </a>
            </tr>
        % endfor
    </table>
%endif

</div>
