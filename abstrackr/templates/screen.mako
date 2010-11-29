<%inherit file="site.mako" />
<%def name="title()">screen</%def>

<div class="breadcrumbs">
./<a href="${url(controller='account', action='welcome')}">dashboard</a>
          /<a href="${url(controller='review', action='show_review', id=c.review_id)}">show_review</a>
</div>

<div id="citation" class="content" style='float: center'>
<h2>${c.cur_citation.title}</h2>
${c.cur_citation.authors}<br/><br/>
${c.cur_citation.abstract}
</div>

<center>
<div id="wait"></div>
</center>

<script type="text/javascript">
    $(document).ready(function() {

        $("#accept").click(function() {
            $("#wait").text("hold on to your horses..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/label/%s/%s/1' % (c.review_id, c.cur_citation.citation_id)}", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                });
            });
         });   
               
        $("#maybe").click(function() {
            $("#wait").text("hold on to your horses..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/label/%s/%s/0' % (c.review_id, c.cur_citation.citation_id)}", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                });
            });
         });   
        
        $("#reject").click(function() {
            $("#wait").text("hold on to your horses..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/label/%s/%s/-1' % (c.review_id, c.cur_citation.citation_id)}", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                });
            });
         });  
        
    });
</script>


<br/><br/>
<center>


<a href="#" id="accept"><img src = "../../accept.png"/></a> 
<a href="#" id="maybe"><img src = "../../maybe.png"/></a> 
<a href="#" id="reject"><img src = "../../reject.png"/></a> 

</center>