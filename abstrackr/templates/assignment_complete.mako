
<h2>Huzzah! You've completed this assignment.</h2> <br/></br><h2> Nice work.</h2>

<script type="text/javascript">    
    function setup_js(){
        % if 'assignment' in dir(c):
          % if c.assignment.num_assigned and c.assignment.num_assigned > 0:
            $("#progress").html("you've screened <b>${c.assignment.done_so_far}</b> out of <b>${c.assignment.num_assigned}</b> so far (nice going!)");
          % else:
            $("#progress").html("you've screened <b>${c.assignment.done_so_far}</b> abstracts thus far, and, regrettably, there are no more for you to screen.");
          % endif
        % else:
          $("#progress").html("");
        % endif


        $('#buttons').html("");
        //alert("???");
        $('#buttons').remove()
        $('#tags_container').remove();
        $('#label_terms').remove();
        
    }
</script>