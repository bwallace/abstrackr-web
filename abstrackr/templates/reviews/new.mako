<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<script language="javascript">

    $(document).ready(function() { 

        // fix for issue #4
        $("input:submit").attr("disabled",true);

        $("input:file").change(function() {
            if ( $(this).val() && ($.trim($("#name").val()) != "") && ($("#name").val() != null) ) {
                $("input:submit").attr("disabled",false);
                $("#select-file").hide();
            }
            else
            {
                $("input:submit").attr("disabled","disabled");
                $("#select-file").show();
            }
        });

        // Enable the 'Create New Review' button after the user enters a project name and a file to upload
        $("#name").keyup(function() {
            if ( ($.trim($(this).val()) != "") && ($(this).val() != null) && $("input:file").val() ) {
                $("input:submit").attr("disabled",false);
                $("#select-file").hide();
            }
            else
            {
                $("input:submit").attr("disabled","disabled");
                $("#select-file").show();
            }
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

        $( "#tag-visibility-help" ).dialog({
            height: 200,
            width:300, 
            modal: false,
            autoOpen: false,
            show: "blind",
        });


        $("#post").click(function(){
            $("#dialog").dialog( "open" );
        });

        jQuery("#help-link").click(function(){
            $("#upload-help" ).dialog( "open" );
        });

        jQuery("#train-round-link").click(function(){
            $("#train-round-help" ).dialog( "open" );
        });

        jQuery("#screen-mode-link").click(function(){
            $("#screen-mode-help" ).dialog( "open" );
        });

        jQuery("#tag-visibility-link").click(function(){
            $("#tag-visibility-help" ).dialog( "open" );
        });

    });

</script>


<div id="dialog" >
    <h2>processing your abstracts. </h2>
    This may take a while -- please don't navigate away from this page.<br/><br/>
    <center>
    <img src="/loading.gif"></img>
    </center>
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

<div id="tag-visibility-help" class="ui-dialog">
    <p>By default, the tags are set to be visible <i>only</i> to the project leader.  They are <b>private</b> to the other members of the project, i.e. only project lead and the user himself, if the tag was introduced by a non-leading member, can see the tag.</p>
    <p>This <b>tag visibility</b> option lets you change the visibility of tags to <b>public</b> or keep it <b>private</b>.  If the tags are public, everyone can see each other's tags for any given citation.
</div>


<div class="content">
    <center>
        <table class="form_table">

            ${h.form(url(controller='review', action='create_review_handler'), multipart=True, id="new_project_form",  method='post')}

            <tr><td><label>project name:</td><td> ${h.text('name', "Review " + c.review_count)}</label></td></tr>

            <tr><td><label>project description:</td> <td>${h.textarea('description', rows="10", cols="40")}</label></td></tr>

            <tr><td><label>upload file (<a href="#" id="help-link">what can I import?</a>):</label></td> <td>${h.file('db')} </td></tr>

            <tr><td><label>screening mode (<a href="#" id="screen-mode-link">what?</a>):</td> <td>${h.select("screen_mode", None, ["Single-screen", "Double-screen", "Advanced"])} </label></td></tr>

            <tr><td><label>order abstracts by:</td> <td>${h.select("order", None, ["Most likely to be relevant", "Random", "Most ambiguous"])} </label></td></tr>            

            <tr><td><label>pilot round size (<a href="#" id="train-round-link">huh?</a>):</td><td> ${h.text('init_size', '0')}</label></td></tr>

            <tr><td><label>tag visibility (<a href="#" id="tag-visibility-link">what?</a>):</td> <td>${h.select("tag_visibility", None, ["Private", "Public"])} </label></td></tr>

            <tr><td><label>minimum number of abstracts to screen:</td><td> ${h.text('min_citations', '0')}</label></td></tr>

            <tr><td><label>maximum number of abstracts to screen:</td><td> ${h.text('max_citations', '0')}</label></td></tr>

            <div id='create' class="actions">
                <tr><td></td><td></td><td class="actions">
                <a href="${url(controller='account', action='back_to_projects')}">Cancel</a></td>
                <td id='submit-td' class="actions">${h.submit('post', 'Create new review')}</td></tr>
            </div>

            ${h.end_form()} 

        </table>
    </center>

    <div id="select-file" align='right'>Before creating a review, you'll have to select a file to upload and make sure the project has a name.</div>
</div>
