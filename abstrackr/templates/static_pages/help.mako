<html>
<head>
<title>abstrackr help</title>
<LINK href="../stylesheet.css" rel="stylesheet" type="text/css">
 <STYLE type="text/css" media="screen">
#floating_link {
     position: fixed;
     left: 0;
     top: 20px;
     display: block;
     width: 170px;
     height: 20px;
     text-indent: 0px;
     border: 1px solid black;
     background-color: white;
     font-color: white;
}
</STYLE>

</head>

<body>


<a id="floating_link" href="${c.root_path}">&larr; go back to <b>abstrackr</b></a>

<div class="content">
<h1>welcome to abstrackr help.</h1>
<h1>Table of Contents</h1>
<ul>
<li> <a href="#big_pic">The Big Picture</a> 
  <br/><br/>
<li> <a href="#joining">Joining a Review</a>
<li> <a href="#working">Getting to Work</a>
<li> <a href="#screening">Screening</a>
  <ul>
    <li><a href="#basic_screening">Basic screening</a></li>
    <li><a href="#labeled_terms">Labeling terms</a></li>
    <li><a href="#tags">Tags</a></li>
    <li><a href="#notes">Notes</a></li>
  </ul>
</li><br/>
<li> <a href="#leading">Leading a Review</a></a>
  <ul>
    <li><a href="#creating_new">Starting a Review</a></li>
    <li><a href="#conflicts">Reviewing Conflicts</a></li>
    <li><a href="#export">Exporting your Screening Decisions</a></li>
  </ul>
</li>
</ul>


<br/>
<h1><a name="big_pic">The Big Picture</a></h1>
<p><b>abstrackr</b> is a web-application that makes citation-screening process of systematic reviews easier (or, we hope it does, anyway). It is a collaborative tool that facilitates screening of citations by multiple reviewers in tandem. Citations are imported and then screened by participants. The screening decisions (or, 'labels') can subsequently be exported. We'll now define some abstractions that are used within <b>abstrackr</b>, to help you understand how best to work with the system.</p>

<p>There are two main types of things in <b>abstrackr</b>: <i>reviewers</i> and <i>reviews</i>. The former are people like yourself, and the latter (sometimes referred to as projects), are collections of citations to be screened by reviewers. Each reviews is lead by a special reviewer; the associated <i>project lead</i>. All other reviewers associated with a given projects are participants. </p>

<p>The work-flow in <b>abstrackr</b> is centered around <i>assignments</i>, which are created by project leads. In the simplest case, the same assignment is tasked to all participants in a review (including the lead): this assignment is, essentially, to screen until all abstracts have been labeled. More advanced types of assignments exist, but we'll cover these later.</p>

<h1><a name="joining">Joining a Review</a></h1>
<p>To join a review in <b>abstrackr</b>, you'll need a join link (URL). This URL should have been sent to your e-mail, either by the <b>abstrackr</b> system or by your project lead. The URL will look like this: 

<center>https://abstrackr.cebm.brown.edu/join/IQT1KAI0LJ</center><br/>

Where the last part of the URL will depend on the review. Simply follow this link in your web browser and you will be automatically joined to the corresponding review.</p>

<h1><a name="working">Getting to Work</a></h1>
 
 <center><img src="images/tabs.png" width=800/></center>

 <p>The main screen with which you're greeted upon joining a review is shown above. There are two tabs: My Work and My Projects: for now, we'll focus on the former. The My Work tab shows your assignments. Outstanding (unfinished) assignments will be at the top of the page; any completed assignments will be displayed below these. If you are participating in multiple reviews, you may see multiple assignments from them; the 'review' column of the table specifies to which review the corresponding assignment belongs.</p>

 <p>To get screening, you'll want to click the  <img height=25 src="images/screen.png" /> button in the actions column of the assignments table. You can also review the labels (screening decisions) you have given thus far to the abstracts comprising the corresponding assignment, via the <img height=25 src="images/review_labels.png" />.

<h1><a name="screening">Screening</a></h1>
<p>We now explain how to screen abstracts in <b>abstrackr</b>. You will likely spend the majority of your time in the system screening, so we will go over the functionality available here in detail. The screening view is shown below.</p>

<center>
<img src="images/screen_screen.png" /><br/>
<b>Figure 1</b>. The main screening interface. The main functional components are circled and labeled (<b>A</b>, <b>B</b>, <b>C</b>): their functionality is described below.
</center>

<h2><a name="basic_screening">Screening abstracts</a></h2>
<p>In <b>abstrackr</b> you screen an abstract by pushing a button that communicates the <i>label</i> you want to give it. The available labels for abstracts are: <b>relevant</b>, <b>borderline</b> and <b>irrelevant</b>, and correspond to the three buttons in the <b>A</b> panel of the above screen-shot, respectively. The first and last of these are likely self-explanatory: they correspond to accepting and rejecting the abstract. The <b>borderline</b> label, to which the button with the "?" in the screenshot corresponds, implies that you are uncertain about whether or not the abstract should be included or not. Abstracts labeled as maybe can be reviewed at a later time.</p>

<p>Once you screen an article, the label you provided will be saved and <b>abstrackr</b> will immediately fetch a new abstract for you to screen from the database. You can review your labels at any time via the <img height=25 src="images/review_labels.png" /> button (located to the upper-right of the abstract), which will take you to the following screen

 <center><img src="images/review_labels_screen.png" width=800/></center><br/>
 
Here you can review all of the labels you've assigned to the abstracts comprising the associated assignment (thus far). You can re-label an abstract by clicking on its title. You will then be shown the corresponding abstract within the screening page (Figure 1). From here you can re-label the abstract however you'd like: the label will be updated. When you've finished, you can click the  <img height=25 src="images/ok.png" /> button from either the review labels page or from the re-labeling screening view: this will bring you back to normal screening mode.</p>

<h2><a name="labeled_terms">Labeling terms</a></h2>
<p>In addition to screening (labeling) abstracts, you may also wish to indicate that certain terms are indicative that the abstract containing them is more likely to be either relevant or irrelevant to your question (e.g., 'mouse', 'randomized control') than it would be if the corresponding term were not present. <b>abstrackr</b> can remember such terms and highlight them for you in abstracts as you screen. To label terms in the system, use panel <b>B</b> as follows. First, enter the term you would like to highlight in the text box. Next, press the button that corresponds to what you deem appropriate for said term.</p>

<center>
<img src="images/thumbs.png" />
</center>

<p>There are four options here. A term may be (strongly) associated with relevant articles, i.e. its presence in an abstract (greatly) increases the likelihood that said abstract ought to be included; or the reverse may be true, in which case its presence in abstracts (weakly or strongly) correlates with studies to be excluded from the review. These four options -- indicative of relevance, strongly indicative of relevance, indicative of irrelevance, strongly indicative of irrelevance -- are captured by the four `thumbed' buttons to the right of the term text-field in panel <b>B</b> (also shown above), respectively: one thumb up designates a term as indicative of inclusion, two thumbs as strongly indicative of inclusion, etc. Once a term is labeled, it will be highlighted in abstracts with a color corresponding to its label. You can review your terms via the <img height=25 src="images/review_terms.png" /> button, which will take you to a screen that includes this table:

 <center><img src="images/review_terms_screen.png" width=800 /></center>


From here, you can delete or re-label terms, using the respective buttons. As usual, you can get back to work via the <img height=25 src="images/ok.png" /> button.

</p>



<h2><a name="tags">Tags</a></h2>

<p>Another form of annotation available in <b>abstrackr</b> is <i>tagging</i>. Tags are managed in panel <b>C</b> (Figure 1). They are intended to be used flexibly, and can be thought of as additional 'labels' that can be assigned to abstracts. Abstracts may have multiple tags. Tags can be exported with your labels, and in the future you will be able to review all abstracts with a given tag.</p>

<p>As an example, suppose you want to tag certain abstracts as being randomized control trials (RCTs). To do so, click the <img height=25 src="images/tag_study.png" /> button. A window will pop-up, in which you may enter "RCT". This is shown below.

<center>
<img src="images/new_tag.png" />
</center><br/>

Click the 'tag' button. The tags panel will then be updated so that it appears like this:<br/>

<center>
<img src="images/tagged.png" />
</center><br/>

If you change your mind about the tag, click <img height=25 src="images/tag_study.png" /> again. You will then see<br/>

<center>
<img src="images/tagged_rct.png" />
</center><br/>

You can toggle this tag on/off by clicking it. When the tag is highlighted (yellow), this means that it applies to the current abstract, otherwise it does not. The same applies to new abstracts; when they first appear, they are by default 'untagged', so that all tags will be de-selected (i.e., not highlighted). You can toggle on all appropriate tags by clicking the <img height=25 src="images/tag_study.png" /> button, and then clicking on those that apply.</p>
</p>

<h2><a name="notes">Notes</a></h2>

<p>Tags are meant to designate studies as belonging to some auxilary category (e.g., RCT or not). For more general notes regarding studies, you'll want to use the <i>notes</i> funcitonality. Notes allow you to enter both unstructured/general notes about a study and/or PICO-structured notes.</p>

<p>To create a note, simply click the <img height=25 src="images/notes_btn.png" /> button. This will bring up the following dialog:<br/>

 <center>
<img src="images/notes.png" />
</center><br/>

Enter whatever notes you'd like in the corresponding, then click the 'save notes' button to save them. The note-taking dialog can be manipulated as indicated. It can also be dragged around (just click on the grey header and move it!).</p>

<p>You can export your notes as a field when you  <a href="#export">export labels</a>, and you can also see them when you review your labels. When you click the notes button for a study for which you've already entered notes, these will be shown in the notes dialog.</p>

<br/><br/>
<h1><a name="leading">Leading a Review/Project</a></h1>

<p>This section of the help discusses how to <i>lead</i> a review in <b>abstrackr</b>; this includes importing your data, dealing with assignments, reviewing conflicts and exporting labels. At present, each review (inter-changeably referred to as projects) has exactly one project lead. By default, this is the person that started the review (i.e., uploaded the abstracts). The project lead role can be transferred after the review begins, however.</p>

<h2><a name="creating_new">Starting a new Review</a></h2>

<p>To start a new review, you'll first need to get your citation data into a format that <b>abstrackr</b> can understand. <b>abstrackr</b> supports a number of file formats, which we'll now briefly review. The easiest (and suggested!) format is a list of PubMed IDs, one-per line. Such a list can be exported directly from the PubMed search results page as follows. Click <b>Send to</b>, then select <b>PMID List</b> as the <b>Format</b>. Then click the 'Create file' button (an image is shown below). <b>abstrackr</b> will fetch the corresponding titles and abstracts for each id.</p>

<center>
<img src="images/export_from_pubmed.png" />
</center><br/>


<p>Alternatively, <b>abstrackr</b> can import arbitrary tab-separated files. More specifically, this requires that you create a <b>header row</b> specifying which field each row contains. To this end, <b>abstrackr</b> recognizes special fields; it's important that you use the exact same spellings and capitalizations (all lower case) shown here.</p>

<p>The following fields are mandatory, i.e., must be present in the header row (\t denotes a tab character):</p>
<center><b>id</b> \t <b>title</b> \t <b>abstract</b></center>

<p>Though the abstract for any given citation may be empty. The <b>id</b> may be anything you'd like to use to identify your citations, though it must be unique for each (i.e., no two rows may have the same <b>id</b>. Additional fields that may be optionally uploaded are:</p>

<center><b>keywords</b> \t <b>authors</b> \t <b>journal</b></center>

<p>Finally, you may also import XML files exported from the <b>Reference Manager</b> (Versions 11 and 12 are supported) citation software.</p>

<p>Once you've got a file ready to upload, you're ready to start a new review. To do so, first navigate to the 'my projects' tab. Then click the 'start new project/review' button, as seen below.</p>

<center>
<img src="images/start_new_review.png" />
</center>

<p>You'll be shown a form with various fields. The first is the title, or name, of your review: it's best to give a descriptive name, but you can leave this blank if you'd like. Next is the project description. This, too, is optional, but consider adding details about your project. The 'upload file' field is where you will, obviously, upload the file containing your citations (see above). Click the 'browse...' button to locate the file on your local computer.</p>

<center>
<img src="images/new_review.png" />
</center>

<p>The <b>screening mode</b> dictates whether abstracts will be single- or double- screened. You may also choose 'advanced', which will result in your having to manually assign work to participating reviewers. Presently, the latter mode allows only single-screening of abstracts. The <b>order abstracts by</b> option specifies the order in which the system will select citations to be screened. The default, 'most likely to be relevant', will order abstracts by their likelihood of meeting the review's inclusion criteria (likelihood of being relevant), according to the machine learning methods. The predictions will get better as you screen more abstracts.</p>

<p>Finally, the <b>pilot round size</b> specifies the number of abstracts to be screened by all reviewers before everyone begins individually screening; these abstracts comprise the <b>pilot round</b>. The thought is that this will allow the team to work out any issues that may arise with respect to the inclusion criteria. In this pilot round, everyone screens the same abstracts. Conflicts can then be reviewed by the project lead. The number of abstracts to be screened can be specified here. If you set this, for example, to 100, then everyone will receive the same first 100 abstracts to screen. If you don't want a training round, just leave this be at 0.</p>

<p>Once you've selected your options for the above fields, click 'Create new review'; the system will import your abstracts. You'll see a waiting screening while this is happening. If successfully completed, you'll eventually see the screen below. Here you may invite additional reviewers by entering their e-mails, separated by commas, and clicking the 'invite them!' button. You may also do this later, or you may send them the unique join URL directly. 
</p>

<center>
<img src="images/invite.png" />
</center>


<h2><a name="conflicts">Reviewing Conflicting (and Borderline) Decisions</a></h2>

<p>In cases in which the same set of abstracts has been screened by multiple reviewers, it is often useful to review any abstracts that have received conflicting labels, e.g., one person may have marked a given study as 'irrelevant', whereas another may have thought it 'relevant'. This may happen during the pilot round, for example.</p>

<p>In <b>abstrackr</b>, the project lead can screen abstracts that have been given conflicting labels, and assign a 'consensus' label that resolves the conflict. To enter this mode for a review, first navigate to the 'my projects' tab. Then click the 'review conflicts' button (circled below) for the review of interest.</p>


<center>
<img src="images/conflicts.png" />
</center>

<p>This will bring you to a screening mode in which only conflict abstracts are shown. The respective labels (screening decisions) assigned to each of the abstracts by reviewers will be shown. The label assigned in this mode is recorded as the 'consensus' label when screening decisions are exported (see below), but a record is kept of the pre-existing decisions, too. </p>

<p>An analogous mode is available for screening abstracts with a designation of 'maybe'. This mode is accessible by clicking the 'review maybes' button adjacent to the 'review conflicts' button.</p>


<h2><a name="export">Exporting Screening Decisions (Labels)</a></h2>

<p>Once you've finished screening abstracts for your projects, you'll no doubt want to export your labels. To do so, again navigate to the 'my projects' tab. Then click the 'export' button (circled below).
</p>


<center>
<img src="images/export.png" />
</center>

<p>You'll see a pop-up (below) that allows you to (de-) select the fields you'd like exported for each abstract. Hopefully most of these are self-explanatory. The '(internal) id', '(source) id' and 'pubmed id' fields correspond to different index numbers for a given abstract. The pubmed id may or may not be present; the source id reflects the id with which an abstract was imported (e.g,. the RefMan id) -- these two ids may very well be the same. The internal id is a globally unique identifier used internally by the system. </p>

<center>
<img src="images/export_fields.png" />
</center>

<p>Once you select the fields to export, <b>abstrackr</b> will generate a spreadsheet for you. You will receive a link to download this spreadsheet when it's ready. This file can then be opened in Excel (or any program capable of handling tab-delimited data). Of course, in addition to the above fields, <b>abstrackr</b> will export the labels (screening decisions) given for each abstract. Currently, this is done as follows. Each abstract is a row in the spreadsheet. Each reviewer on the project gets a column in the spreadsheet. In addition, a 'consensus' column is included. For each of these, a '-1' stands for 'exclude', '1' for 'include', '0' for 'borderline' (i.e., 'maybe') and 'o' for missing. The spreadsheet looks like this:</p> 

<center>
<img src="images/exported_labels.png" />
</center>

<p>The rules for forming a consensus are as follows. If a consensus label was explicitly provided, e.g., in <a href="#conflicts">review conflicts</a> mode, then this label is used. Alternatively, if <b>at least two</b> reviewers have labeled an abstract and their is unanimous agreement, this is taken as the consensus label. If the labels conflict, however, the consensus label is 'x'. Finally, if only one reviewer has screened an abstract, the consensus label is considered missing, i.e., 'o'.</p>

</div>
</body>
</html>
