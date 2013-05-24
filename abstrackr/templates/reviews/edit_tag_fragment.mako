<script type="text/javascript">
function setup_js(){
    $("#edit_tag").click(function() {
            var tag_str = $("input#new_tag_text").val();
            $.post("/review/edit_tag_text/${c.tag.id}", {new_text: tag_str});
            // redirect here
            parent.location='/review/edit_tags/${c.tag.project_id}/${c.assignment_id}';
            });
}

$(document).ready(function() {
        setup_js();
        });

</script>


<form>
<center>
rename tag: <input type="text" id="new_tag_text" name="new_tag_text" value="${c.tag.text}"/>
</center>
<br/>
<div class="actions" style="text-align: right;">
<input id="edit_tag" type="button" value="ok" />
</div>

</form>
