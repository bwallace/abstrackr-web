<%inherit file="../site.mako" />
<%def name="title()">new review</%def>

<center>


 <form action="${url(controller='review', action='upload_xml')}" method="post" multipart=True, enctype="multipart/form-data">
    <input type="file" name="myfile"/>
    <input type="submit" id="submit" value="Submit" />
 </form>

</center>