<script type="text/javascript">
	$(document).ready(function() { 
		$("#export_btn").unbind();

	    $("#export_btn").click(function()
	    {
	       
	       // now add all selected tags to the study
	       var fields = $.map($('.ui-selected, this'), function(element, i) {  
	         return $(element).text();  
	       });


		   $("#export").load('/exporting.html', function(){
	       		$("#export").load("${'/review/export_labels/%s' % c.review_id}", {fields: fields});
	       });
	       
	       
	    });
	 });
</script>

<h1>export labels</h1>

select the fields you'd like to export:<br/>

<center>
<ul id="selectable" class="ui-selectable">
% for field in ["(internal) id", "(source) id", "pubmed id"]:
 	<li class="ui-selected">${field}</li>
% endfor

% for field in ["keywords", "abstract", "title", "journal", "authors", "tags", "notes"]:
	<li class="ui-selectee">${field}</li>
% endfor
</ul>

</center>
<br/>
<div class="actions">
<input id="export_btn" type="button" value="export" />
</div>

