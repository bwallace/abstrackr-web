
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

        // unbind all attached events
        $("#accept").unbind();
        $("#maybe").unbind();
        $("#reject").unbind();
        $("#pos_lbl_term").unbind();
        $("#double_pos_lbl_term").unbind();
        $("#neg_lbl_term").unbind();
        $("#double_neg_lbl_term").unbind();

        // reset the timer
        reset_timer();
                
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
    
</script>
