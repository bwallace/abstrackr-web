<script type="text/javascript">
	$(document).ready(function() {
		$("#export_btn").unbind();

	    $("#export_btn").click(function()
	    {

	       // now add all selected tags to the study
	       var fields = $.map($('.ui-selected, this'), function(element, i) {
	         return $(element).text();
	       });

				 var export_type = $('input[name=export_type]:checked').val();
		   	 $("#export").load('/exporting.html', function(){
	       		$("#export").load("${'/review/export_labels/%s' % c.review_id}", {fields: fields, export_type: export_type});
				 });


	    });
	 });
</script>

<h1>export labels</h1>

<span> select the export type: </span>
<div id="export_type_radio_group">
	<input type="radio" name="export_type" value="xml" checked> XML<br>
  <input type="radio" name="export_type" value="ris-citations"> RIS (citations)<br>
	<input type="radio" name="export_type" value="ris-labels"> RIS (labels)<br>
  <input type="radio" name="export_type" value="csv"> CSV
</div>


select the fields you'd like to export:<br/>

<center>
<ul id="selectable" class="ui-selectable">
% for field in ["(internal) id", "(source) id", "pubmed id", "keywords", "abstract", "title", "journal", "authors", "tags", "notes"]:
 	<li class="ui-selected">${field}</li>
% endfor

% for field in []:
	<li class="ui-selectee">${field}</li>
% endfor
</ul>

</center>
<br/>
<div class="actions">
<input id="export_btn" type="button" value="export" />
</div>
