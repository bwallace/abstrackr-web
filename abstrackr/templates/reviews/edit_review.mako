
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>

<script language="javascript">
jQuery(document).ready(function(){
    jQuery("#post").click(function(){
    	$("#dialog" ).dialog( "open" );
        $("#okay_div").fadeIn(2000)

    });

    $( "#dialog" ).dialog({
            height: 250,
            width: 400,
            modal: true,
            autoOpen: false,   
            show: "blind",
        });

});

</script>

<div class="breadcrumbs">
./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>


<div id="dialog" >
  
    <h2>processing your edits. </h2>
    This may take awhile -- please don't navigate away from this page.<br/><br/>
    <center>
    <img src="../../loading.gif"></img>
    </center>
</div>



<h1>${c.review.name}: administrivia</h1>
<div class="actions">
<a href="${url(controller='review', action='admin', id=c.review.review_id)}">manage participants</a>
<a href="${url(controller='review', action='assignments', id=c.review.review_id)}">manage assignments</a>
</div>

<div class="content">


<center>
<table class="form_table">
 ${h.form(url(controller='review', action='edit_review_settings', id=c.review.review_id), multipart=True, id="edit_project_form",  method='post')}

    <tr><td><label>screening mode (<a href="#" id="screen-mode-link">what?</a>):</td> <td>${h.select("screen_mode", None, ["Single-screen", "Double-screen", "Advanced"])} </label></td></tr>

     <tr><td><label>pilot round size (<a href="#" id="pilot-round-size">huh?</a>):</td><td> ${h.text('init_size', c.review.initial_round_size)}</label></td></tr>
    
    <div class="actions">
    <tr><td></td><td></td><td class="actions"> 
    <td class="actions">${h.submit('post', 'Apply to review')}</td></tr>
    </div>
  ${h.end_form()} 
</table>
</center>

	% if 'msg' in dir(c):
		<div id="okay_div"><font color='green'>${c.msg}</font>
	 	</div>
	% endif

</div>
