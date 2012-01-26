
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


    $( "#train-round-help" ).dialog({
        height: 200,
        width:500, 
        modal: false,
        autoOpen: false,
        show: "blind",
    });

    $( "#screen-mode-help" ).dialog({
        height: 400,
        width:500, 
        modal: false,
        autoOpen: false,
        show: "blind",
    });

    jQuery("#train-round-link").click(function(){
        $("#train-round-help" ).dialog( "open" );
    });

    jQuery("#screen-mode-link").click(function(){
        $("#screen-mode-help" ).dialog( "open" );
    });

});

</script>

<div class="breadcrumbs">
./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.review_id)}">${c.review.name}</a>
</div>

<div id="train-round-help" class="ui-dialog">
In a <b>pilot round</b>, everyone screens the same abstracts. Conflicts can then be reviewed by the project lead. The number of abstracts to be screened can be specified here. If you set this, for example, to 100, then everyone will receive the same first 100 abstracts to screen. If you don't want a training round, just leave this be at 0.
</div>


<div id="screen-mode-help" class="ui-dialog">
<p>The <b>screening mode</b> specifies how work is to be assigned to participants. </p>

<p>In the simplest case, <b>single-screen</b>, all abstracts will be screened once. In this mode, participants (reviewers) can screen all they want, until there are no remaining abstracts. If you want people to screen a certain number of abstracts in this mode, simply tell them to stop after they've screened this many. </p>

<p><b>double-screen</b> behaves analogously, with the exception that every abstract will be screened twice. Individual reviewers will <b>not</b>, however, re-screen the same abstract.</p>

<p>In <b>advanced</b> mode, you will use the <b>assignments</b> tab to manually assign work to reviewers. At current, this mode only supports single-screening; there is no way to specify that abstracts are to be re-screened.</p>

<p>Note that regardless of the screening mode, if an initial round size of <i>n</i>    &gt; 0 is specified, <b>all</b> reviewers will screen these <i>n</i> abstracts. </p>
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

    <tr><td><label>order abstracts by:</td> <td>${h.select("order", None, ["Random", "Most likely to be relevant", "Most ambiguous"])} </label></td></tr>
    
     <tr><td><label>pilot round size (<a href="#" id="train-round-link">huh?</a>):</td><td> ${h.text('init_size', c.review.initial_round_size)}</label></td></tr>
    
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
