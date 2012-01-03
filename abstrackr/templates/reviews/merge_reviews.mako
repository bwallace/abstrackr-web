<%inherit file="../site.mako" />
<%def name="title()">abstrackr: merge reviews</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>


<h1>merge reviews</h1>

<div class="content">

<h2>projects to merge:</h2>

<center>
<table class="form_table">

 ${h.form(url(controller='review', action='merge_reviews'), multipart=True, id="merge_review_form",  method='post')}
    
    % for review in c.reviews:
        <tr><td><input type="checkbox" name="merge_review" value="${review.review_id}" checked="no"/> ${review.name}</td></tr>
    % endfor
    
    <tr><td><label>merged project name:</td><td> ${h.text('name')}</label></td></tr>

    <tr><td><label>merged project description:</td> <td>${h.textarea('description', rows="10", cols="40")}</label></td></tr>


    <tr><td><label>merged screening mode (<a href="#" id="screen-mode-link">what?</a>):</td> <td>${h.select("screen_mode", None, ["Single-screen", "Double-screen", "Advanced"])} </label></td></tr>

    <tr><td><label>order abstracts by:</td> <td>${h.select("order", None, ["Random", "Most likely to be relevant", "Most ambiguous"])} </label></td></tr>
    

    <div class="actions">

    <tr></tr>

    <tr><td></td><td class="actions"> 
    ${h.submit('post', 'merge reviews')}</td></tr>
    </div>
  ${h.end_form()} 
</table>
</center>