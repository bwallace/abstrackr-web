
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>

<script language="javascript">
jQuery(document).ready(function(){
    jQuery("#submit").click(function(){
        $("#okay_div").fadeIn(2000)
    });
});

</script>

<div class="breadcrumbs">
./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>


<h1>${c.review.name}: administrivia</h1>
<div class="actions">
<a href="${url(controller='review', action='assignments', id=c.review.review_id)}">manage assignments</a>
</div>

<div class="content">


<center>
<table class="form_table">
 ${h.form(url(controller='review', action='edit_review_settings', id=c.review.review_id), multipart=True, id="edit_project_form",  method='post')}

    <tr><td><label>screening mode (<a href="#" id="screen-mode-link">what?</a>):</td> <td>${h.select("screen_mode", None, ["Single-screen", "Double-screen", "Advanced"])} </label></td></tr>


    <tr><td></td><td></td><td class="actions"> 
    <td class="actions">${h.submit('post', 'Apply to review')}</td></tr>
    </div>
  ${h.end_form()} 
</table>
</center>

    <div class="loading" id="okay_div">
       ok, settings applied to review!
    </div>

</div>
