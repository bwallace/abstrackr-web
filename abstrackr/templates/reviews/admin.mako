
<%inherit file="../site.mako" />
<%def name="title()">${c.review.name}</%def>
<script language="JavaScript">
    var cal = new CalendarPopup();
</script>

<script language="javascript">
    jQuery(document).ready(function(){
        jQuery("#submit").click(function(){
            $("#okay_div").fadeIn(2000)
        });
    });
</script>

<div class="breadcrumbs">
    ./<a href="${url(controller='account', action='my_projects')}">my projects</a>/<a href="${url(controller='review', action='show_review', id=c.review.id)}">${c.review.name}</a>
</div>

<h1>${c.review.name}: administrivia</h1>

<div class="actions">
    <a href="${url(controller='review', action='admin', project_id=c.review.id)}">Manage Participants</a>
    <a href="${url(controller='review', action='assignments', id=c.review.id)}">Manage Assignments</a>
    <a href="${url(controller='review', action='edit_review', id=c.review.id)}">Edit Settings</a>
    <a href="${url(controller='review', action='render_add_citations', id=c.review.id)}">Add Citations</a>
</div>


<div class="content">

    % if len(c.participating_reviewers)>0:
        <h2>Participants</h2>
        <table class="list_table">
        <tr align="center"><th>person</th><th></th></tr>
        % for participant in c.participating_reviewers:
            <tr>
                <td>${participant.fullname}</td>
                <td class="actions">
                    <a href="/review/remove_from_review/${participant.id}/${c.review.id}">remove from review</a>
                    % if participant in c.project_leader_list:
                        <a href="/review/remove_admin/${c.review.id}/${participant.id}">remove user from project leader group</a>
                    % else:
                        <a href="/review/add_admin/${c.review.id}/${participant.id}">add user to the project leader group</a></td>
                    % endif
                </td>
            </tr>
        % endfor
        </table>
        <br/>
    % elif c.admin_msg == "":
        <H2>Hrmm... You're the only person participating in this review. </h2><h2>But don't despair: you can invite people below! </H2>
        <br/><br/>
    % endif

    % if c.admin_msg != "":
        <H2>${c.admin_msg}</H2>
    % endif

    <div align="right">
        <form action = "/review/invite_reviewers/${c.review.id}">
            <div class="actions">
                <label for="emails">Want to invite additional reviewers? Enter their emails (comma-separated).</label>
                <input type="text" id="emails" name="emails" /><br />
                <input type="submit" id="submit" value="invite them" />
            </div>
        </form>
        <div class="loading" id="okay_div">
            okay! emails have been sent!
        </div>
    </div>

    <div class="loading" id="okay_div">
        okay! emails have been sent!
    </div>

    <p align="right">
        Alternatively, they can join the review themselves by following this link: <b>${c.root_path}join/${c.review.code}</b>
    </p>

</div>
