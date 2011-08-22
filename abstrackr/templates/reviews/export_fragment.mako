<h1>export labels</h1>

select the fields you'd like:
<center>

<ul id="selectable" class="ui-selectable">
% for field in ["(internal) id", "pubmed id", "labeler", "label"]:
 	<li class="ui-selected">${field}</li>
% endfor

% for field in ["mesh", "abstract", "journal", "authors"]:
	<li class="ui-selectee">${field}</li>
% endfor
</ul>

</center>
<br/>
<div class="actions">
<a href="${url(controller='review', action='export_labels', id=c.review_id)}">export</a>
</div>


