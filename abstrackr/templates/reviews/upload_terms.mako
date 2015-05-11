
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
    <a href="${url(controller='review', action='render_term_upload_page', id=c.review.id)}">Upload Terms</a>
</div>

<div id="upload-help" class="ui-dialog">
    <div>You may import a tab delimited file here. Each line should consist of a term you wish to highlight as well as the rating the term is associated with.</div>
    <br />
    <div>A positive numbers indicate positive relevance, while negative numbers indicate negative relevance.</div>
    <br />
    <div>Please restrict the rating to 1's and 2's only, where a positive 1 implies 'relevant' and a positive 2 means 'very relevant', a negative 1 implies 'irrelevant' and a negative 2 means 'very irrelevant'.</div>
</div>

<div class="content">

    <center>
        <table class="form_table">
            ${h.form(url(controller='review', action='upload_terms', id=c.review.id), multipart=True, id="add_terms_form",  method='post')}
                
                <tr><td><label>Upload Terms-File (<a href="#" id="help-link">what can I upload?</a>):</label></td> <td>${h.file('db')} </td></tr>

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
