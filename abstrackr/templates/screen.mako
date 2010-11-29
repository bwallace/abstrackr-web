<%inherit file="site.mako" />
<%def name="title()">screen</%def>

<div id="citation" style='float: center'>
<h2>${c.cur_citation.title}</h2>
${c.cur_citation.authors}<br/><br/>
${c.cur_citation.abstract}


</div>

<script type="text/javascript">
    $(document).ready(function() {
        $("#labelCitation").click(function() {
            $("#citation").load("${'/review/screen_next/%s' % c.review_id}");
        });
    });
</script>


<br/><br/>
<center>


<a id="labelCitation">Change my text</a>


<a href =   "#", onclick="new Ajax.Updater(
            'citation',
            '/review/screen_next/',
            {
                onComplete:function(){ new Effect.Highlight('citation', duration=4);},
                asynchronous:true,
                evalScripts:true
            }
        );"><img src = "../../accept.png"/></a> <img src = "../../reject.png"/>
</center>