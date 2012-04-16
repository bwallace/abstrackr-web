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


<div id="dialog" >
   <form>
   <center>
    new tag: <input type="text" id="new_tag" name="new_tag" /> </input><br />
   </center>
   <br/>

    <ul id="selectable" class="ui-selectable">
      % for tag in c.tag_types:
          % if tag in c.tags:
            <li class="ui-selected">${tag}</li>
          % else:
            <li>${tag}</li>
          % endif
      % endfor
    </ul>
 

   <div class="actions" style="text-align: right;">
      <input id="submit_btn" type="button" value="tag" />
   </div>
   </form>
</div>


<div id="notes-dialog" >
   <form>
   
    <b>general notes</b><br/> 
    <textarea id="general_notes" name="general_notes" rows="4" cols="40" /> 
    </textarea><br />
    
    <br>population notes</b><br/>
    <textarea id="pop_notes" name="pop_notes" rows="1" cols="40" /></textarea><br />
    </br>
   
    <br>intervention/comparator notes</b><br/>
    <textarea id="ic_notes" name="ic_notes" rows="1" cols="40" /> 
    </textarea><br />
    </br>

    <br>outcome notes</b><br/>
    <textarea id="outcome_notes" name="outcome_notes" rows="1" cols="40" /> </textarea><br />
    </br>

   <br/>
    </ul>
    <div id="notes-status"></div>
   <div class="actions" style="text-align: right;">
      <input id="save_notes_btn" type="button" value="save notes" />
   </div>
   </form>
</div>

<div class="actions">
  % if c.cur_lbl is not None and c.assignment_type != "conflict":
      % if c.assignment_id is not None:
        <a href="${url(controller='review', action='screen', review_id=c.review_id, assignment_id=c.assignment_id)}">ok, get back to screening <img src="/arrow_right.png"></img></a>
      % endif
  % else:
    <a
      href="${url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)}">review labels</a>
    <a 
      href="${url(controller='review', action='review_terms', id=c.review_id, assignment_id=c.assignment_id)}">review terms</a>
  % endif
</div>

<div class="container">

  <div id="tags_container" class="sidebar">
    <h2>tags &amp; notes</h2><br/>
    <center>
    <div id="tags" class="tags">
    <ul>
    % if len(c.tags) > 0:
        % for i,tag in enumerate(c.tags):
            <li class=${"tag%s"%(i+1)}><a href="#">${tag}</a></li><br/>
        % endfor
    </ul>
    % else:
        (no tags yet.)
    % endif
    </div>
    <br/>
    <input type="button" style="width: 120px" id="tag_btn" value="tag study..." />
    <br/><br/>

    
    <input type="button" style="width: 120px" id="edit_tags_btn" value="edit tags..." 
                onclick="parent.location='/review/edit_tags/${c.review_id}/${c.assignment_id}'"> 
   
    <br/><br/>
    <input type="button" style="width: 120px" id="notes_btn" value="notes..." />

    </center>
  </div>

 


  <div id="citation-holder" style='float: right; width: 85%;'>

    <div id="citation" class="content">

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
                % if "consensus_review" in dir(c) and c.consensus_review:
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
          function setup_js(){
              
              $( "#dialog" ).dialog({
                height: 250,
                modal: true,
                autoOpen: false,
                show: "blind",
              });

              $( "#notes-dialog" ).dialog({
                height: 300,
                width: 400,
                modal: true,
                autoOpen: false,
                position: [0,0],
                show: "blind",
                hide: {effect: "fadeOut", duration:2000}
              });



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

              populate_notes();
              setup_submit();
          }

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
                      $("#tags").load("${'/review/update_tags/%s' % c.cur_citation.citation_id}", function() {
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

            $("#tag_btn").unbind();
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
    <div id="progress"> 
    % if 'assignment' in dir(c):
        % if c.assignment.num_assigned and c.assignment.num_assigned > 0:
            you've screened <b>${c.assignment.done_so_far}</b> out of <b>${c.assignment.num_assigned}</b> so far (nice going!)
        % else:
            you've screened <b>${c.assignment.done_so_far}</b> abstracts thus far (keep it up!)
        % endif
    % endif
    </div>
    </center>

   



    <center>
    <br clear="all"/>
    <div id = "buttons" >
    <a href="#" id="accept"><img src = "/accept.png"/></a> 
    <a href="#" id="maybe"><img src = "/maybe.png"/></a> 
    <a href="#" id="reject"><img src = "/reject.png"/></a> 
  </div>



  <table>
  <tr>
  <td>
  <div id="label_terms" class="summary_heading">
  <label>term: ${h.text('term')}</label> 
  </td>
  <td width="10"></td>
  <td>
  <a href="#" id="pos_lbl_term"><img src = "/thumbs_up.png" border="2" alt="indicative of relevance"></a>
  </td>
  <td>
  <a href="#" id="double_pos_lbl_term"><img src = "/two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a>
  </td>
  <td width="10"></td>
  <td>
  <a href="#" id="neg_lbl_term"><img src = "/thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a>
  </td>
  <td>
  <a href="#" id="double_neg_lbl_term"><img src = "/two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a>
  </td>
  </tr>
  </div>

  <div id="label_msg"></div>
  </center>
  </div>
</div>