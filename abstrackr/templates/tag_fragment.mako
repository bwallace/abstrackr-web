<script>
  
  $("#selectable").selectable();


  setup_submit();

</script>


    % if len(c.tags) > 0:
        % for tag in c.tags:
            ${tag}<br/>
        % endfor
    % else:
        (no tags yet.)
    % endif
