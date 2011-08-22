<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<script language="javascript">

    $(document).ready(function() { 
        $( "#dialog" ).dialog({
            height: 250,
            width: 400,
            modal: true,
            autoOpen: false,   
            show: "blind",
        });

        $( "#upload-help" ).dialog({
            height: 300,
            width:500, 
            modal: false,
            autoOpen: false,
            show: "blind",
        });

        jQuery("#post").click(function(){
            $("#dialog" ).dialog( "open" );
        });

        jQuery("#help-link").click(function(){
            $("#upload-help" ).dialog( "open" );
        });
    });

    


</script>

<div id="dialog" >
  
    <h2>processing your abstracts. </h2>
    This may take awhile -- please don't navigate away from this page.<br/><br/>
    <center>
    <img src="../../loading.gif"></img>
    </center>
</div>

<div id="upload-help" class="ui-dialog">
You can import a few different file types into <b>abstrackr</b>.<br/>

<p>The easiest (and suggested!) file format is a list of PubMed IDs, one-per line. Such a list can be exported directly from the PubMed search results page as follows. Click <b>Send to</b>, then select <b>PMID List</b> as the <b>Format</b>. <b>abstrackr</b> will fetch the corresponding titles and abstracts for each id.</p>

<p>Alternatively, <b>abstrackr</b> can import arbitrary tab-separated files. More specifically, this requires that you create a <b>header row</b> specifying which field each row contains. To this end, <b>abstrackr</b> recognizes special fields; it's important that you use the exact same spellings and capitalizations (all lower case) shown here.</p>

<p>The following fields are mandatory, i.e., must be present in the header row (\t denotes a tab character):</p>
<center><b>id</b> \t <b>title</b> \t <b>abstract</b></center>

<p>Though the abstract for any given citation may be empty. The <b>id</b> may be anything you'd like to use to identify your citations, though it must be unique for each (i.e., no two rows may have the same <b>id</b>. Additional fields that may be optionally uploaded are:</p>

<center><b>keywords</b> \t <b>authors</b> \t <b>journal</b></center>

<p>Finally, you may also import XML files exported from the <b>Reference Manager</b> citation software.</p>


</div>

<div class="content">
<center>
<table class="form_table">
 ${h.form(url(controller='review', action='create_review_handler'), multipart=True, id="new_project_form")}
    <tr><td><label>project name:</td><td> ${h.text('name')}</label></td></tr>
    <tr><td><label>project description:</td> <td>${h.textarea('description', rows="10", cols="40")}</label></td></tr>
    <tr><td><label>upload file (<a href="#" id="help-link">what can I import?</a>):</label></td> <td>${h.file('db')} </td></tr>
    <tr><td><label>screening mode:</td> <td>${h.select("screen_mode", None, ["Single-screen", "Double-screen", "Advanced"])} </label></td></tr>
    <tr><td><label>order abstracts by:</td> <td>${h.select("order", None, ["Random", "Most likely to be relevant", "Most ambiguous"])} </label></td></tr>
    <tr><td><label>initial round size:</td><td> ${h.text('init_size', '100')}</label></td></tr>
    <div class="actions">
    

		
    <tr><td></td><td></td><td class="actions"> <a href="${url(controller='account', action='welcome')}">Cancel</a></td><td class="actions">${h.submit('post', 'Create new review')}</td></tr>
    </div>
  ${h.end_form()} 
</table>

</center>


</div>