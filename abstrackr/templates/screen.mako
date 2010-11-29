<%inherit file="site.mako" />
<%def name="title()">screen</%def>

<div id="citation" class="content" style='float: center'>
<h2>${c.cur_citation.title}</h2>
${c.cur_citation.authors}<br/><br/>
${c.cur_citation.abstract}


</div>

<script type="text/javascript">
    $(document).ready(function() {
        $("#accept").click(function() {
            $("#citation").load("${'/label/%s/%s/1' % (c.review_id, c.cur_citation.citation_id)}");
        });
               
        $("#maybe").click(function() {
            $("#citation").load("${'/label/%s/%s/0' % (c.review_id, c.cur_citation.citation_id)}");
        });
        
        $("#reject").click(function() {
            $("#citation").load("${'/label/%s/%s/-1' % (c.review_id, c.cur_citation.citation_id)}");
        });
    });
</script>


<br/><br/>
<center>


<a href="#" id="accept"><img src = "../../accept.png"/></a> 
<a href="#" id="maybe"><img src = "../../maybe.png"/></a> 
<a href="#" id="reject"><img src = "../../reject.png"/></a> 

</center>