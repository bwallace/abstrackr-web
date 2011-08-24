

  
   <form>
   <center>
    new tag: <input type="text" id="new_tag" name="new_tag" /><br />
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
   </center>

   <div class="actions" style="text-align: right;">
      <input id="submit_btn" type="button" value="tag" />
   </div>
   </form>
