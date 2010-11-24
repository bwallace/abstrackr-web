<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<center>

 <form action="${url(controller='review', action='upload_xml')}" method="post" multipart=True, enctype="multipart/form-data">
    <label for="project name">project name</label>
    <input type="text" id="project name" name="project name" /><br />
    
    <input type="file" name="db"/><br/>
    <input type="submit" id="submit" value="Submit" />
 </form>

</center>