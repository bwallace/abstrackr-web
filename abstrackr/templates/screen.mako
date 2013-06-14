<%inherit file="site.mako" />
<%def name="title()">screen</%def>


<script type="text/javascript">
    var seconds = 1;
    setTimeout(update_timer, 1000);

    function reset_timer() {
        seconds = 1; // start at one
        setTimeout(update_timer, 1000);
    }

    function update_timer() {
        seconds +=1;
        setTimeout(update_timer, 1000);
    }
</script>


<div id="dialog">
    <form>
        <center>
            new tag: <input type="text" id="new_tag" name="new_tag" /> </input><br>
        </center><br>

        <ul id="selectable" class="ui-selectable">
            % for tag in c.tag_types:
                % if tag in c.tags:
                    <li class="ui-selected">${tag}</li>
                % else:
                    % if not c.tag_privacy:
                        <li>${tag}</li>
                    % endif
                % endif
            % endfor
        </ul>

        <div class="actions" style="text-align: right;">
            <input id="submit_btn" type="button" value="tag" />
        </div>
    </form>
</div>


<div id="notes-dialog">
    <form>
        <b>general notes</b><br>
        <textarea id="general_notes" name="general_notes" rows="4" cols="40" /></textarea><br><br>

        <b>population notes</b><br>
        <textarea id="pop_notes" name="pop_notes" rows="1" cols="40" /></textarea><br><br>

        <b>intervention/comparator notes</b><br>
        <textarea id="ic_notes" name="ic_notes" rows="1" cols="40" /></textarea><br><br>

        <b>outcome notes</b><br>
        <textarea id="outcome_notes" name="outcome_notes" rows="1" cols="40" /> </textarea><br><br>

        <div id="notes-status"></div>

        <div class="actions" style="text-align: right;">
            <input id="save_notes_btn" type="button" value="save notes" />
        </div>
    </form>
</div>


<div class="actions">
    % if c.cur_lbl is not None and c.assignment_type != "conflict":
        % if c.assignment_id is not None:
            <a href="${url(controller='review', action='screen', review_id=c.review_id, assignment_id=c.assignment_id)}">back to screening <img src="/arrow_right.png"></img></a>
            <a href="${url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)}">back to the list of labeled citations <img src="/arrow_right.png"></img></a>
        % endif
    % else:
        <a href="${url(controller='review', action='review_labels', review_id=c.review_id, assignment_id=c.assignment_id)}">review labels</a>
        <a href="${url(controller='review', action='review_terms', id=c.review_id, assignment_id=c.assignment_id)}">review terms</a>
    % endif
</div>


<div class="container">
    <div id="tags_container" class="sidebar">
        <h2>tags &amp; notes</h2><br>
        <center>
            <div id="tags" class="tags">
                <ul>
                % if len(c.tags) > 0:
                    % for i,tag in enumerate(c.tags):
                        <li class=${"tag%s"%(i+1)}><a href="#">${tag}</a></li><br>
                    % endfor
                </ul>
                % else:
                    (no tags yet.)
                % endif
            </div><br>
            <input type="button" style="width: 120px" id="tag_btn" value="tag study..." /><br><br>
            <input type="button" style="width: 120px" id="edit_tags_btn" value="edit tags..." onclick="parent.location='/review/edit_tags/${c.review_id}/${c.assignment_id}'"><br><br>
            <input type="button" style="width: 120px" id="notes_btn" value="notes..." /><br><br>
        </center>
    </div>

    <div id="citation-holder" style='float: right; width: 85%;'>
        <div id="citation" class="content">
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
        </div> <!-- <div id="citation" class="content"> -->

        <div id="hidden_div" class="content"></div>

        <center><div id="wait"></div></center><br><br>

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
            <div id="label_terms" class="summary_heading">
                <table>
                    <tr>
                        <td><label>term: ${h.text('term')}</label></td>
                        <td width="10"></td>
                        <td><a href="#" id="pos_lbl_term"><img src = "/thumbs_up.png" border="2" alt="indicative of relevance"></a></td>
                        <td><a href="#" id="double_pos_lbl_term"><img src = "/two_thumbs_up.png" border="2" alt="strongly indicative of relevance"></a></td>
                        <td width="10"></td>
                        <td><a href="#" id="neg_lbl_term"><img src = "/thumbs_down.png"/ border="2" alt="indicative of irrelevance" ></a></td>
                        <td><a href="#" id="double_neg_lbl_term"><img src = "/two_thumbs_down.png"/ border="2" alt="strongly indicative of irrelevance"></a></td>
                    </tr>
                </table>
            </div>
            <div id="label_msg"></div>
        </center>
    </div>
</div>


<script type="text/javascript">

var still_loading = false;
var waiting_for_citation = false;

function get_next_citation() {
    still_loading = true;
    $('#hidden_div').load( "${'/next_citation/%s/%s' % (c.review_id, c.assignment_id)}", function() {
        still_loading = false;
        // were we waiting for this guy? if so, load
        // him in now
        if (waiting_for_citation) {
            load_next_citation();
        };
    });
};

function load_next_citation() {
    // pull in the next citation from the hidden_div iff
    // it has finished downloading. otherwise hide buttons,
    // show waiting screen and flip 'waiting_for_citation'
    // boolean to true
    if (still_loading) {
        $("#wait").text("hold on to your horses..");
        $('#buttons').hide();
        waiting_for_citation = true;
    } else {
        // then the next citation has been downloaded
        // into the hidden_div
        $('#citation').html( $('#hidden_div').html() );

        // this is the key logic piece; we the setup_js method
        // is defined with respect to the currently hidden
        // citation that we just loaded into the #citation div
        // hence when it is called it will attach calls to the
        // buttons that label the (now currently) displayed
        // citation that we fadein in the next line.
        setup_js();

        $('#citation').fadeIn();
        $("#wait").text("");
        $('#buttons').show();
        waiting_for_citation = false;

        // once the citation
        get_next_citation();
    };
};

function we_are_reviewing_a_label() {
    return "${'assignment' not in dir(c)}" == "True";
};

function is_perpetual_assignment() {
    % if not 'assignment' in dir(c):
        return false;
    % else:
        return "${c.assignment.assignment_type}" == "perpetual";
    % endif
};

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

function setup_submit() {
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
    $("#close_btn").click(function(e) {
        // I actually don't know where 'close_btn' is defined...
        // we close them both here.
        $("#dialog" ).dialog( "close" );
        $("#notes-dialog" ).dialog( "close" );
    });

    $("#notes_btn").unbind();
    $("#notes_btn").click(function() {
        $("#notes-dialog" ).dialog("open");
    });
};

function setup_js() {

    $( "#dialog" ).dialog({
        height: 250,
        modal: true,
        autoOpen: false,
        show: "blind",
    });

    $( "#notes-dialog" ).dialog({
        height: 500,
        width: 400,
        modal: true,
        autoOpen: false,
        position: [0,0],
        show: "blind",
        hide: {effect: "fadeOut", duration:2000}
    });

    function markup_current() {
        var cur_citation_id = $('#citation.content span#cur_citation_id').text();
        var next_citation_id = $('#hidden_div.content span#cur_citation_id').text();
        // reload the current citation, with markup
        $("#wait").text("marking up the current citation..")
        $("#citation").fadeOut('slow', function() {
            $("#citation").load("${'/markup/%s/%s/' % (c.review_id, c.assignment_id)}" + cur_citation_id, function() {
                $("#citation").fadeIn('slow');
                $("#wait").text("");
            });
        });
        $("#citation").fadeOut('fast', function() {
            $("#hidden_div").load("${'/markup/%s/%s/' % (c.review_id, c.assignment_id)}" + next_citation_id, function() {
                $("#citation").fadeIn('slow');
                $("#wait").text("");
            });
        });
    };

    function label_cur_citation(lbl_str) {
        var cur_citation_id = $('#citation.content span#cur_citation_id').text();

        $("#citation").fadeOut('fast', function() {
            if (!(we_are_reviewing_a_label()) && is_perpetual_assignment()) {
                // try to load the next citation
                // this call will in turn call get_next_citation
                // once loading is complete
                load_next_citation();
            };
            $.post("${'/label/%s/%s/' % (c.review_id, c.assignment_id)}" + cur_citation_id + "/" + seconds + "/" + lbl_str, function(data) {
                if (we_are_reviewing_a_label()) {
                    // in the case that we are re-labeling a citation,
                    // this the label method will return the citation fragment.
                    $('#citation').html(data);
                    $('#citation').fadeIn();
                    setup_js();
                    still_loading = false;
                } else if (!(is_perpetual_assignment())) {
                    load_next_citation();
                } else {
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
        var term_str = $("input#term").val();
        if (term_str != "") {
            $.post("${'/label_term/%s/1' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='green'>" + term_str + "</font> as being indicative of relevance.");
            $("#label_msg").fadeIn(2000);
            $("input#term").val("");
            $("#label_msg").fadeOut(3000);
            markup_current();
        };
    });

    $("#double_pos_lbl_term").click(function() {
        // call out to the controller to label the term
        var term_str = $("input#term").val();
        if (term_str != "") {
            $.post("${'/label_term/%s/2' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='green'>" + term_str + "</font> as being <bold>strongly</bold> indicative of relevance.");
            $("#label_msg").fadeIn(2000);
            $("input#term").val("");
            $("#label_msg").fadeOut(3000);
            markup_current();
        };
    });

    $("#neg_lbl_term").click(function() {
        // call out to the controller to label the term
        var term_str = $("input#term").val()
        if (term_str != "") {
            $.post("${'/label_term/%s/-1' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being indicative of <i>ir</i>relevance.");
            $("#label_msg").fadeIn(2000);
            $("input#term").val("");
            $("#label_msg").fadeOut(3000);
            markup_current();
        };
    });

    $("#double_neg_lbl_term").click(function() {
        // call out to the controller to label the term
        var term_str = $("input#term").val()
        if (term_str != "") {
            $.post("${'/label_term/%s/-2' % c.review_id}", {term: term_str});
            $("#label_msg").html("ok. labeled <font color='red'>" + term_str + "</font> as being <bold>strongly</bold> indicative of <i>ir</i>relevance.");
            $("#label_msg").fadeIn(2000);
            $("input#term").val("");
            $("#label_msg").fadeOut(3000);
            markup_current();
        };
    });

    populate_notes();
    setup_submit();
};

$(document).ready(function() {
    setup_js();
    // we don't queue the next citation if we're reviewing
    // labels!
    if (!(we_are_reviewing_a_label())) {
        get_next_citation(); // fetch the *next* citation
    }
    $("#hidden_div").hide();
});
</script>
