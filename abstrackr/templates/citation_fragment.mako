<h2>${c.cur_citation.marked_up_title}</h2>
% if c.show_journal==True:
    <i>Journal: ${c.cur_citation.journal}</i><br><br>
% endif

% if c.show_authors==True:
    Authors: ${c.cur_citation.authors}<br><br>
% endif

${c.cur_citation.marked_up_abstract}<br><br>

% if c.show_keywords==True:
    <b>keywords:</b> ${c.cur_citation.keywords}<br><br>
% endif

<b>ID:</b> <span id="cur_citation_id" data-cur_citation_id="${c.cur_citation.id}">${c.cur_citation.id}</span><br><br>

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
                a <b>consensus</b> label of ${write_label(label.label)} was given for this citation on on ${label.label_last_updated}<br>
            % else:
                <b>${c.reviewer_ids_to_names_d[label.user_id]}</b> labeled this citation as ${write_label(label.label)} on ${label.label_last_updated}<br>
            % endif
        % endfor
    % else:
        <center>you labeled this citation as ${write_label(c.cur_lbl.label)} on ${c.cur_lbl.label_last_updated}</center>
    % endif
% endif



<script type="text/javascript">

function populate_notes() {
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
};

function setup_submit(){
    $("#selectable").selectable();

    $("#submit_btn").unbind();
    $("#submit_btn").click(function() {
        var tag_str = $("input#new_tag").val();
        var cur_citation_id = $('#citation.content span#cur_citation_id').text();

        // now add all selected tags to the study
        var tags = $.map($('.ui-selected, this'), function(element, i) {
            return $(element).text();
        });

        // push new tag, too (if it's empty, we'll drop it server-side)
        tags.push(tag_str);

        $.post("${'/review/tag_citation/%s/' % (c.review_id)}" + cur_citation_id, {tags: tags}, function() {
            $("#tags").fadeOut('slow', function() {
                $("#tags").load("/review/update_tags/" + cur_citation_id + "/${'%s' % (c.tag_privacy)}", function() {
                    $("#tags").fadeIn('slow');
                });
            });

            $("#dialog").load("${'/review/update_tag_types/%s/' % (c.review_id)}" + cur_citation_id);
        });
        $( "#dialog" ).dialog( "close" );
    });

    $("#save_notes_btn").unbind();
    $("#save_notes_btn").click(function() {
        var general_notes = $("#general_notes").val();
        var pop_notes =  $("#pop_notes").val();
        var ic_notes = $("#ic_notes").val();
        var outcome_notes = $("#outcome_notes").val();
        var cur_citation_id = $('#citation.content span#cur_citation_id').text();

        ##$.post("${'/review/add_notes/%s' % c.cur_citation.id}", {"general_notes": general_notes, "population_notes":pop_notes, "ic_notes":ic_notes, "outcome_notes":outcome_notes}, function() {
        $.post("/review/add_notes/" + cur_citation_id, {"general_notes": general_notes, "population_notes":pop_notes, "ic_notes":ic_notes, "outcome_notes":outcome_notes}, function() {
            $("#notes-status").html("<font color='green'>notes added.</font>");
            $("#notes-dialog" ).dialog( "close" );
            $("#notes-status").html("");
        });
    });

    $("#tag_btn").unbind();
    $("#tag_btn").click(function() {
        $("#dialog" ).dialog( "open" );
    });

    $("#close_btn").unbind();
    $("#close_btn").click(function (e) {
        // I actually don't know where 'close_btn' is defined...
        // we close them both here.
        $("#dialog" ).dialog( "close" );
        $("#notes-dialog" ).dialog( "close" );
    });

    $("#notes_btn").unbind();
    $("#notes_btn").click(function() {
        $("#notes-dialog" ).dialog("open");
    });
    $("#new_tag").val(' ');
};

function setup_js(){
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

    ##alert("About to cache: ${'/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.id)}");
    ##$("#dialog").load("${'/review/update_tag_types/%s/%s' % (c.review_id, c.cur_citation.id)}", function() {
    ##    setup_submit();
    ##    populate_notes();
    ##});

    $("#tags").load("${'/review/update_tags/%s/%s' % (c.cur_citation.id, c.tag_privacy)}");

    // reset the timer
    reset_timer();

    function markup_current() {
        var cur_citation_id = $('#citation.content span#cur_citation_id').text();
        var next_citation_id = $('#hidden_div.content span#cur_citation_id').text();
        // reload the current citation, with markup
        ##alert("${'/markup/%s/%s/' % (c.review_id, c.assignment_id)}" + cur_citation_id);
        $("#wait").text("marking up the current citation..")
        $("#citation").fadeOut('slow', function() {
            $("#citation").load("${'/markup/%s/%s/' % (c.review_id, c.assignment_id)}" + cur_citation_id, function() {
                $("#citation").fadeIn('slow');
                $("#wait").text("");
            });
        });
        ##alert("${'/markup/%s/%s/' % (c.review_id, c.assignment_id)}" + next_citation_id);
        $("#citation").fadeOut('fast', function() {
            $("#hidden_div").load("${'/markup/%s/%s/' % (c.review_id, c.assignment_id)}" + next_citation_id, function() {
                $("#citation").fadeIn('slow');
                $("#wait").text("");
            });
        });
    };

    function label_cur_citation(lbl_str){
        var cur_citation_id = $('#citation.content span#cur_citation_id').text();

        $("#citation").fadeOut('fast', function() {
            if (!(we_are_reviewing_a_label()) && is_perpetual_assignment()){
                // try to load the next citation
                // this call will in turn call get_next_citation
                // once loading is complete
                load_next_citation();
            };
            $.post("${'/label/%s/%s/' % (c.review_id, c.assignment_id)}" + cur_citation_id + "/" + seconds + "/" + lbl_str, function(data) {
                if (we_are_reviewing_a_label()){
                    // in the case that we are re-labeling a citation,
                    // this the label method will return the citation fragment.
                    $('#citation').html(data);
                    $('#citation').fadeIn();
                    setup_js();
                    still_loading = false;
                }
                else if (!(is_perpetual_assignment())) {
                    load_next_citation();
                }
                else {
                    ##alert('fragment: ' + data);
                    $('#progress').html(data);
                };
            });
        });
    };

    $("#accept").click(function() {
        label_cur_citation("1");
    });

    $("#maybe").click(function() {
        label_cur_citation("0");
    });

    $("#reject").click(function() {
        label_cur_citation("-1");
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
        };
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
        };
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
            $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.");
            $("#label_msg").fadeIn(2000);
            $("input#term").val("");
            $("#label_msg").fadeOut(3000);
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
};

</script>

