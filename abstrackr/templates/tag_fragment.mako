<script>
    $("#selectable").selectable();
    setup_submit();
</script>

% if len(c.tags) > 0:
    % for i,tag in enumerate(c.tags):
        <li class=${"tag%s"%(i+1)}><a href="#">${tag}</a></li>
    % endfor
</ul>
    % else:
        (no tags yet.)
    % endif
