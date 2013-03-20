
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>

<script language="javascript">
    jQuery(document).ready(function(){
        
        /*$("input:submit").attr("disabled",true);

        $("input:file").change(function() {
            if ( $(this).val() && ($.trim($("#name").val()) != "") && ($("#name").val() != null) ) 
            {
                $("input:submit").attr("disabled",false);
                $("#select-file").hide();
            }
        });*/

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

        $( "#upload-help" ).dialog({
            height: 300,
            width:500, 
            modal: false,
            autoOpen: false,
            show: "blind",
        });

        jQuery("#help-link").click(function(){
            $("#upload-help" ).dialog( "open" );
        });

    });

</script>

<div class="breadcrumbs">
    ./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.id)}">${c.review.name}</a>
</div>

<div id="dialog" >
    <h2>processing your edits...</h2>
    This may take some time -- please don't navigate away from this page.<br/><br/>
    <center>
    <img src="../../loading.gif"></img>
    </center>
</div>



<h1>${c.review.name}: administrivia</h1>
<div class="actions">
    <a href="${url(controller='review', action='admin', id=c.review.id)}">Manage Participants</a>
    <a href="${url(controller='review', action='assignments', id=c.review.id)}">Manage Assignments</a>
    <a href="${url(controller='review', action='edit_review', id=c.review.id)}">Edit Settings</a>
    <a href="${url(controller='review', action='render_add_citations', id=c.review.id)}">Add Citations</a>
</div>

<div id="upload-help" class="ui-dialog">
    You can import a few different file types into <b>abstrackr</b>.<br/>

    <p>The easiest (and suggested!) file format is a list of PubMed IDs, one-per line. Such a list can be exported directly from the PubMed search results page as follows. Click <b>Send to</b>, then select <b>PMID List</b> as the <b>Format</b>. <b>abstrackr</b> will fetch the corresponding titles and abstracts for each id.</p>

    <p>Alternatively, <b>abstrackr</b> can import arbitrary tab-separated files. More specifically, this requires that you create a <b>header row</b> specifying which field each row contains. To this end, <b>abstrackr</b> recognizes special fields; it's important that you use the exact same spellings and capitalizations (all lower case) shown here.</p>

    <p>The following fields are mandatory, i.e., must be present in the header row (\t denotes a tab character):</p>
    <center><b>id</b> \t <b>title</b> \t <b>abstract</b></center>

    <p>Though the abstract for any given citation may be empty. The <b>id</b> may be anything you'd like to use to identify your citations, though it must be unique for each (i.e., no two rows may have the same <b>id</b>. Additional fields that may be optionally uploaded are:</p>

    <center><b>keywords</b> \t <b>authors</b> \t <b>journal</b></center>

    <p>Finally, you may also import XML files exported from the <b>Reference Manager</b> (Versions 11 and 12 are supported) citation software.</p>
</div>

<div class="content">

    <center>
        <table class="form_table">
            ${h.form(url(controller='review', action='add_citations', id=c.review.id), multipart=True, id="add_citations_form",  method='post')}
                
                <tr><td><label>Upload Citation-File (<a href="#" id="help-link">what can I upload?</a>):</label></td> <td>${h.file('db')} </td></tr>

                <div class="actions">
                    <tr><td></td><td></td><td class="actions"> 
                    <td class="actions">${h.submit('post', 'Add to Review')}</td></tr>
                </div>
            ${h.end_form()}
        </table>
    </center>

	% if 'msg' in dir(c):
		<div id="okay_div"><font color='green'>${c.msg}</font>
	 	</div>
	% endif

    <div id="select-file" align='right'>You must select a citation-file to upload in order to 'Add to Review' .</div>

</div>
