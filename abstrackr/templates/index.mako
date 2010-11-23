<%inherit file="site.mako" />
<%def name="title()">abstrackr Home</%def>

<p>reviews </p>

% for review in c.reviews:
<p class="content" style="border-style:solid; border-width:1px">
        <span class="h3"> ${review.name} </span>
</p>
% endfor
