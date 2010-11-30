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
         
        $("#pos_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            $.post("${'/label_term/%s/1' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='green'>" + term_str + "</font> as being indicative of relevance.")
            $("#label_msg").fadeIn(2000)
            $("input#term").val("")
            $("#label_msg").fadeOut(3000)
         }); 
         
        $("#double_pos_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            $.post("${'/label_term/%s/2' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='green'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")
            $("#label_msg").fadeIn(2000)
            $("input#term").val("")
            $("#label_msg").fadeOut(3000)
         }); 
        

        $("#neg_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            $.post("${'/label_term/%s/-1' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")
            $("#label_msg").fadeIn(2000)
            $("input#term").val("")
            $("#label_msg").fadeOut(3000)
         }); 
         
        $("#double_neg_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            $.post("${'/label_term/%s/-2' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")
            $("#label_msg").fadeIn(2000)
            $("input#term").val("")
            $("#label_msg").fadeOut(3000)
         }); 
        
    });
</script>


<br/><br/>
<center>


<a href="#" id="accept"><img src = "../../accept.png"/></a> 
<a href="#" id="maybe"><img src = "../../maybe.png"/></a> 
<a href="#" id="reject"><img src = "../../reject.png"/></a> 

<br/><br/><br/>
<table>
<tr>
<td>
<div id="label_terms" class="summary_heading">
<label>term: ${h.text('term')}</label> 
</td>
<td width="10"></td>
<td>
<a href="#" id="pos_lbl_term"><img src = "../../thumbs_up.png" border="2" alt="indicative of relevance"></a>
</td>
<td>
<a href="#" id="double_pos_lbl_term"><img src = "../../two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>
</td>
<td width="10"></td>
<td>
<a href="#" id="neg_lbl_term"><img src = "../../thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>
</td>
<td>
<a href="#" id="double_neg_lbl_term"><img src = "../../two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>
</td>
</tr>
</div>

<div id="label_msg"></div>
</center>