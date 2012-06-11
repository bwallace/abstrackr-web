<%inherit file="../site.mako" />

<%def name="title()">my account</%def>

<script type='text/javascript'>

	$(document).ready( function() {

	    $( "#citation-settings-help" ).dialog({
	        height: 200,
	        width:300, 
	        modal: false,
	        autoOpen: false,
	        show: "blind",
	    });

	    jQuery("#citation-settings-help-link").click(function(){
	        $("#citation-settings-help" ).dialog( "open" );
	    });
	
	});

</script>


<div class="content">
	<h3>${c.account_msg}</h3>
	<center>
		<table class="form_table">
			${h.form(url(controller='account', action='change_password'))}
				<tr><td><h3>Password Change:</h3></td><td></td></tr>
				<tr><td><label>new password:</td> <td>${h.text('password', type='password')}</label></td></tr>
				<tr><td><label>confirm new password:</td> <td>${h.text('password_confirm', type='password')}</label></td></tr>
				<tr><td></td><td>${h.submit('post', 'change password')}</td></tr>
			${h.end_form()}
		</table>
	</center>
</div>


<div class="content">
	<h3>${c.account_msg_citation_settings}</h3>
	<center>
		<table class="form_table">
			${h.form(url(controller='account', action='customize_citations'))}

				<tr><td><h3>Citation Settings (<a href="#" id="citation-settings-help-link">need help?</a>):</h3></td><td></td></tr>
				<tr>
					<td><label>Journal:</td>
					<td>${h.select("toggle_journal", None, ["Show", "Hide"])} </label></td>
				</tr>
				<tr>
					<td><label>Authors:</td>
					<td>${h.select("toggle_authors", None, ["Show", "Hide"])} </label></td>
				</tr>
				<tr>
					<td><label>Keywords:</td>
					<td>${h.select("toggle_keywords", None, ["Show", "Hide"])} </label></td>
				</tr>

				<tr><td></td><td>${h.submit('post', 'Apply Settings')}</td></tr>

			${h.end_form()}
		</table>
	</center>
</div>


<div id="citation-settings-help" class="ui-dialog">
    <p>The <b>Citation Settings</b> section gives you the option to customize the content of the abstracts you will see during screening.</p>
    <p>You have the option to <i>show</i> or <i>hide</i> the <b>title</b> of the paper, the name of the <b>journal</b>, the <b>authors</b> of the paper, and/or the <b>keywords</b> associated with the abstract.</p>
    <p>Just make your selections and click on 'Apply Settings'.</p>
</div>