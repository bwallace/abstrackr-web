
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
            % if "consensus_review" in dir(c) and c.consensus_review and len(c.cur_lbl)==1:
              a <b>consensus</b> label of ${write_label(label.label)} was given for this citation on on ${label.label_last_updated}<br/>
            % else:
              <b>${c.reviewer_ids_to_names_d[label.reviewer_id]}</b> labeled this citation as ${write_label(label.label)} on ${label.label_last_updated}<br/>
            % endif
          % endfor
      % else:
      <center>
          you labeled this citation as ${write_label(c.cur_lbl.label)} on ${c.cur_lbl.label_last_updated}
       </center>
      % endif
  % endif



<script type="text/javascript">  

    function populate_notes(){
      % if "notes" in dir(c) and c.notes is not None:
          $("#pop_notes").val('${c.notes.population}'); 
          $("textarea#general_notes").val('${c.notes.general}');
          $("textarea#ic_notes").val('${c.notes.ic}');
          $("textarea#outcome_notes").val('${c.notes.outcome}');
      % else:
        $("#pop_notes").val(''); 
        $("textarea#general_notes").val('');
        $("textarea#ic_notes").val('');
        $("textarea#outcome_notes").val('');
      % endif
    }

    function setup_submit(){
      $("#selectable").selectable();     
      $("#submit_btn").unbind();
      $("#submit_btn").click(function()
      {
          
         var tag_str = $("input#new_tag").val();

         // now add all selected tags to the study
         var tags = $.map($('.ui-selected, this'), function(element, i) {  
           return $(element).text();  
         });

         // push new tag, too (if it's empty, we'll drop it server-side)
         tags.push(tag_str);

         $.post("${'/review/tag_citation/%s/%s' % (c.review_id, c.cur_citation.citation_id)}", {tags: tags},
            function(){
              $("#tags").fadeOut('slow', function() {
                $("#tags").load("${'/review/update_tags/%s' %  c.cur_citation.citation_id}", function() {
                  //$("#tags").load("${'/review/update_tags/%s' % c.cur_citation.citation_id}");
                  $("#tags").fadeIn('slow');
                });
              });
              
              $("#dialog").load("${'/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)}");
            }
         );

         $( "#dialog" ).dialog( "close" );
      });



      /** adding note-taking functionality **/
      $("#save_notes_btn").unbind();
      $("#save_notes_btn").click(function()
      {
        // something like
         var general_notes = $("#general_notes").val();
         var pop_notes =  $("#pop_notes").val();
         var ic_notes = $("#ic_notes").val();
         var outcome_notes = $("#outcome_notes").val();


         $.post("${'/review/add_notes/%s' % c.cur_citation.citation_id}",
                    {"general_notes": general_notes, "population_notes":pop_notes, "ic_notes":ic_notes,
                    "outcome_notes":outcome_notes}, function() {
                        $("#notes-status").html("<font color='green'>notes added.</font>");
                        $( "#notes-dialog" ).dialog( "close" );
                        $("#notes-status").html("");

                    });


         
      });
      /** end **/


      $("#tag_btn").click(function()
      {
         $("#dialog" ).dialog( "open" );
      });

      $("#close_btn").unbind();
      $("#close_btn").click(function (e)
      {
         // I actually don't know where 'close_btn' is defined...
         // we close them both here.
         $("#dialog" ).dialog( "close" );
         $("#notes-dialog" ).dialog( "close" );
      });

      $("#notes_btn").unbind();
      $("#notes_btn").click(function()
      {
         $("#notes-dialog" ).dialog("open");
      });

      $("#new_tag").val(' ');

    } 

    function setup_js(){
        
        $("#dialog").dialog({
          height: 300,
          modal: true,
          autoOpen: false,
          show: "blind",
        });

        // unbind all attached events
        $("#accept").unbind();
        $("#maybe").unbind();
        $("#reject").unbind();
        $("#pos_lbl_term").unbind();
        $("#double_pos_lbl_term").unbind();
        $("#neg_lbl_term").unbind();
        $("#double_neg_lbl_term").unbind();
        $("#submit_btn").unbind();
        $("#close_btn").unbind();
        $("#tag_btn").unbind();

        $("#dialog").load(
            "${'/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.citation_id)}",
            function() {
              setup_submit();
              populate_notes();
            }
        );

        $("#tags").load("${'/review/update_tags/%s' % c.cur_citation.citation_id}");
        
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

        
        % if 'assignment' in dir(c):
          % if c.assignment.num_assigned and c.assignment.num_assigned > 0:
            $("#progress").html("you've screened <b>${c.assignment.done_so_far}</b> out of <b>${c.assignment.num_assigned}</b> so far (nice going!)");
          % else:
            $("#progress").html("you've screened <b>${c.assignment.done_so_far}</b> abstracts thus far (keep it up!)");
          % endif
        % else:
          $("#progress").html("");
        % endif


    }   
    
</script>

