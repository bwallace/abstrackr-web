<%inherit file="site.mako" />
<%def name="title()">screen</%def>

<script language="javascript">
    var seconds = 1;
    setTimeout(update_timer, 1000);
    
    function reset_timer(){
      seconds = 1; // start at one
      setTimeout(update_timer, 1000);
    }
    
    function update_timer(){
      seconds +=1;
      setTimeout(update_timer, 1000);
    }


</script>

<div class="breadcrumbs">
./<a href="${url(controller='account', action='welcome')}">dashboard</a>
          /<a href="${url(controller='review', action='show_review', id=c.review_id)}">${c.review_name}</a>
</div>



<div class="actions">
% if c.cur_lbl is not None and c.assignment_type != "conflict":
  <a href="${url(controller='review', action='screen', review_id=c.review_id, assignment_id=c.assignment_id)}">ok, get back to screening <img src="../../arrow_right.png"></img></a>
% else:
  <a
    href="${url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)}">review labels</a>
  <a 
    href="${url(controller='review', action='review_terms', id=c.review_id, assignment_id=c.assignment_id)}">review terms</a>
% endif

</div>



<div id="citation" class="content" style='float: center'>
<h2>${c.cur_citation.marked_up_title}</h2>
${c.cur_citation.authors}<br/><br/>
${c.cur_citation.marked_up_abstract}<br/><br/>
<b>keywords:</b> ${c.cur_citation.keywords}<br/><br/>
<b>ID:</b> ${c.cur_citation.citation_id}<br/><br/>

<%def name="write_label(label)">
    % if label == 1:
        <b><font color='green'>"relevant"</font></b>
    % elif label == 0:
        <b><font color='light green'>"maybe" (?)</font></b>
    % else:
        <b><font color='red'>"irrelevant"</font></b>
    % endif
</%def>

% if c.cur_lbl is not None:
    % if c.assignment_type == "conflict":
        % for label in c.cur_lbl:
            <b>${c.reviewer_ids_to_names_d[label.reviewer_id]}</b> labeled this citation as ${write_label(label.label)} on ${label.label_last_updated}<br/>
        % endfor
    % else:
    <center>
        you labeled this citation as ${write_label(c.cur_lbl.label)} on ${c.cur_lbl.label_last_updated}
     </center>
    % endif
% endif


<script type="text/javascript">    
    function setup_js(){
    
        function markup_current(){
            // reload the current citation, with markup
            $("#wait").text("marking up the current citation..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/markup/%s/%s/%s' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)}", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                });
            });
        }
    
    
        $("#accept").click(function() {
            $('#buttons').hide();
            $("#wait").text("hold on to your horses..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)}" + seconds + "/1", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                     $('#buttons').show();
                     setup_js();
                });
            });
         });   
               
        $("#maybe").click(function() {
            $('#buttons').hide();
            $("#wait").text("hold on to your horses..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)}" + seconds + "/0", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                     $('#buttons').show();
                     setup_js();
                });
            });
         });   
        
         
        $("#reject").click(function() {
            $('#buttons').hide();
            $("#wait").text("hold on to your horses..")
            $("#citation").fadeOut('slow', function() {
                $("#citation").load("${'/label/%s/%s/%s/' % (c.review_id, c.assignment_id, c.cur_citation.citation_id)}" + seconds + "/-1", function() {
                     $("#citation").fadeIn('slow');
                     $("#wait").text("");
                     $('#buttons').show();
                     setup_js();
                });
            });
         });  
         
        $("#pos_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            if (term_str != ""){
                $.post("${'/label_term/%s/1' % c.review_id}", {term: term_str});
                $("#label_msg").html("ok. labeled <font color='green'>" + term_str + "</font> as being indicative of relevance.")
                $("#label_msg").fadeIn(2000)
                $("input#term").val("")
                $("#label_msg").fadeOut(3000)
                markup_current();
            }
            
            
         }); 
         
        $("#double_pos_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            if (term_str != ""){
                $.post("${'/label_term/%s/2' % c.review_id}", {term: term_str});
                $("#label_msg").html("ok. labeled <font color='green'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.")
                $("#label_msg").fadeIn(2000)
                $("input#term").val("")
                $("#label_msg").fadeOut(3000)
                markup_current();
            }
         }); 
        

        $("#neg_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            if (term_str != ""){
                $.post("${'/label_term/%s/-1' % c.review_id}", {term: term_str});
                $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.")
                $("#label_msg").fadeIn(2000)
                $("input#term").val("")
                $("#label_msg").fadeOut(3000)
                markup_current();
            }
         }); 
         
        $("#double_neg_lbl_term").click(function() {
            // call out to the controller to label the term
            var term_str = $("input#term").val()
            if (term_str != ""){
                $.post("${'/label_term/%s/-2' % c.review_id}", {term: term_str});
                $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.")
                $("#label_msg").fadeIn(2000)
                $("input#term").val("")
                $("#label_msg").fadeOut(3000)
                markup_current();
            }
         }); 
    }    

    $(document).ready(function() { 
        setup_js();
    });
    
</script>
</div>

<center>
<div id="wait"></div>
</center>

<br/><br/>
<center>

<div id = "buttons">
<a href="#" id="accept"><img src = "../../accept.png"/></a> 
<a href="#" id="maybe"><img src = "../../maybe.png"/></a> 
<a href="#" id="reject"><img src = "../../reject.png"/></a> 
</div>

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
