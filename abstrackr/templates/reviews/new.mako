<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<script language="javascript">
jQuery(document).ready(function(){
    jQuery("#post").click(function(){
        $("#loading_div").fadeIn(2000)
    });
});

</script>


<div class="content">
<center>
<table class="form_table">
 ${h.form(url(controller='review', action='create_review_handler'), multipart=True, id="new_project_form")}
    <tr><td><label>project name:</td><td> ${h.text('name')}</label></td></tr>
    <tr><td><label>project description:</td> <td>${h.textarea('description', rows="10", cols="40")}</label></td></tr>
    <tr><td><label>upload file (list of PMIDs or refman XML):</td> <td>${h.file('db')} </label></td></tr>
    <tr><td><label>screening mode:</td> <td>${h.select("screen_mode", None, ["Single-screen", "Double-screen", "Advanced"])} </label></td></tr>
    <tr><td><label>order abstracts by:</td> <td>${h.select("order", None, ["Random", "Most likely to be relevant", "Most ambiguous"])} </label></td></tr>
    <tr><td><label>initial round size:</td><td> ${h.text('init_size', '100')}</label></td></tr>
    <div class="actions">
    

		
    <tr><td></td><td></td><td class="actions"> <a href="${url(controller='account', action='welcome')}">Cancel</a></td><td class="actions">${h.submit('post', 'Create new review')}</td></tr>
    </div>
  ${h.end_form()} 
</table>

    <div class="loading" id="loading_div">
        <img src="../../loading.gif"></img><br/>working on it...
    </div>
</center>


</div>