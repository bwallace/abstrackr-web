import os

import abstrackr.model as model
from abstrackr.model.meta import Session
from abstrackr.config.environment import load_environment
from paste.deploy import appconfig
from pylons import config, url
from abstrackr.controllers.controller_globals import *
from exporter_globals import *
from sqlalchemy import and_

class CsvBuilder:
    def __init__(self, p_id, labeled_only):
        self.fields = ["(internal) id", "(source) id", "pubmed id", "keywords",
                        "abstract", "title", "journal", "authors", "tags", "notes"]
        self.project_id = p_id
        self.lbl_filter_f = lambda label: True
        self.user_dict = {}
        self.citation_to_notes_dict = {}
        self.citation_to_tags_dict = {}
        self.all_citations = []
        self.all_labelers = []
        return

    def write_labels(self):
        # get fields
        review_q = Session.query(model.Project)
        review = review_q.filter(model.Project.id == self.project_id).one()

        self.all_labelers = self._get_participants_for_review(self.project_id)

        ## some helpers
        none_to_str = lambda x: "" if x is None else x
        zero_to_none = lambda x: "none" if x==0 else x

        fields_to_export = self.fields

        # map citation ids to dictionaries that, in turn, map
        # usernames to labels
        citation_to_lbls_dict = {}

        self.all_citations = [cit.id for cit in self._get_citations_for_review(self.project_id)]

        citations_labeled_dict = {}
        for cit in self.all_citations:
          citations_labeled_dict[cit]=False

        # likewise, for notes
        # citation_to_notes_dict = {}
        if "notes" in fields_to_export:
            self._build_notes_dict()

        if "tags" in fields_to_export:
            self._build_tags_dict()

        # we filter the citations list  (potentially)
        citations_to_export = []

        # for efficiency reasons, we keep track of whether we need
        # create a new empty dictionary for the current citation
        last_citation_id = None

        labeler_names = ["consensus"] # always export the consensus
        # first collect labels for all citations that pass our
        # filtering criteria
        for citation, label in Session.query(\
            model.Citation, model.Label).filter(model.Citation.id==model.Label.study_id).\
              filter(model.Label.project_id==self.project_id).order_by(model.Citation.id).all():
                # the above gives you all labeled citations for this review
                # i.e., citations that have at least one label
                citations_labeled_dict[citation.id]=True

                if self.lbl_filter_f(label):
                    cur_citation_id = citation.id
                    if last_citation_id != cur_citation_id:
                        citation_to_lbls_dict[citation.id] = {}
                        # citation_to_notes_dict[cur_citation_id] = {}
                        citations_to_export.append(citation)

                    # NOTE that we are assuming unique user names per-review
                    labeler = self._get_username_from_id(label.user_id)
                    if not labeler in labeler_names:
                        labeler_names.append(labeler)

                    citation_to_lbls_dict[cur_citation_id][labeler] = label.label
                    last_citation_id = cur_citation_id

                    # note that this will only contain entries for reviews that have
                    # been labeled! i.e., notes made on unlabeled citations are not
                    # reflected here.
                    # if "notes" in fields_to_export
                    # citation_to_notes_dict[cur_citation_id][labeler] = \
                    #         self._get_notes_for_citation(cur_citation_id, label.user_id)


        # we automatically export all labeler's labels
        for labeler in labeler_names:
            fields_to_export.append(labeler)

        # finally, export notes (if asked)
        notes_fields = ["general", "population", "intervention/comparator", "outcome"]
        if "notes" in  fields_to_export:
            fields_to_export.remove("notes")
            # we append all labelers notes
            for labeler in labeler_names:
                if labeler != "consensus":
                    for notes_field in notes_fields:
                        fields_to_export.append("%s notes (%s)" % (notes_field, labeler))

        self.write_buffer = [",".join(fields_to_export)]
        for citation in citations_to_export:
            cur_line = []
            for field in fields_to_export:
                if field == "(internal) id":
                    cur_line.append("%s" % citation.id)
                elif field == "(source) id":
                    cur_line.append("%s" % citation.refman)
                elif field == "pubmed id":
                    cur_line.append("%s" % zero_to_none(citation.pmid))
                elif field == "abstract":
                    cur_line.append('"%s"' % none_to_str(citation.abstract).replace('"', "'"))
                elif field == "title":
                    cur_line.append('"%s"' % citation.title.replace('"', "'"))
                elif field == "keywords":
                    cur_line.append('"%s"' % citation.keywords.replace('"', "'"))
                elif field == "journal":
                    cur_line.append('"%s"' % none_to_str(citation.journal))
                elif field == "authors":
                    cur_line.append('"%s"' % "".join(citation.authors))
                elif field == "tags":
                    #cur_tags = self._get_tags_for_citation(citation.id)
                    cur_tags = self.citation_to_tags_dict[citation.id]
                    cur_line.append('"%s"' % ",".join(cur_tags))
                elif field in labeler_names:
                    cur_labeler = field
                    cur_lbl = "o"
                    cit_lbl_d = citation_to_lbls_dict[citation.id]
                    if cur_labeler in cit_lbl_d:
                        cur_lbl = str(cit_lbl_d[cur_labeler])
                    # create a consensus label automagically in cases where
                    # there is unanimous agreement
                    elif cur_labeler == "consensus":
                        if len(set(cit_lbl_d.values()))==1:
                            if len(cit_lbl_d) > 1:
                                # if at least two people agree (and none disagree), set the
                                # consensus label to reflect this
                                cur_lbl = str(cit_lbl_d.values()[0])
                            else:
                                # then only one person has labeled it --
                                # consensus is kind of silly
                                cur_lbl = "o"
                        else:
                            # no consensus!
                            cur_lbl = "x"

                    cur_line.append(cur_lbl)
                elif "notes" in field:
                    # notes field
                    # this is kind of hacky -- we first parse out the labeler
                    # name from the column header string assembled above and
                    # then get a user id from this.
                    get_labeler_name_from_str = lambda x: x.split("(")[1].split(")")[0]
                    cur_labeler = get_labeler_name_from_str(field)
                    # @TODO not sure what we should do in consensus case...
                    if cur_labeler == "consensus":
                        cur_line.append("")
                    else:
                        cur_note = None
                        cur_notes_d = self.citation_to_notes_dict[citation.id]

                        if cur_labeler in cur_notes_d:
                            cur_note = cur_notes_d[cur_labeler]

                        if cur_note is None:
                            cur_line.append("")
                        else:
                            notes_field = field
                            if "general" in notes_field:
                                cur_line.append("\"%s\"" % cur_note.general.replace('"', "'"))
                            elif "population" in notes_field:
                                cur_line.append("\"%s\"" % cur_note.population.replace('"', "'"))
                            elif "outcome" in notes_field:
                                cur_line.append("\"%s\"" % cur_note.outcome.replace('"', "'"))
                            else:
                                # intervention/comparator
                                cur_line.append("\"%s\"" % cur_note.ic.replace('"', "'"))

            self.write_buffer.append(",".join(cur_line))

        # exporting *all* (including unlabeled!) citations, per Ethan's request
        #-- may want to make this optional

        self.write_buffer.append("citations that are not yet labeled by anyone")

        # jj 2014-08-20: Request to include citation information even for those citations that have not
        #                been labeled yet.
        unlabeled_citation_ids = [cit for cit in citations_labeled_dict if not citations_labeled_dict[cit]]
        unlabeled_citations = Session.query(model.Citation).filter(model.Citation.id.in_(unlabeled_citation_ids)).all()

        for citation in unlabeled_citations:
            cur_line = []
            for field in fields_to_export:
                if field == "(internal) id":
                    cur_line.append("%s" % citation.id)
                elif field == "(source) id":
                    cur_line.append("%s" % citation.refman)
                elif field == "pubmed id":
                    cur_line.append("%s" % zero_to_none(citation.pmid))
                elif field == "abstract":
                    cur_line.append('"%s"' % none_to_str(citation.abstract).replace('"', "'"))
                elif field == "title":
                    cur_line.append('"%s"' % citation.title.replace('"', "'"))
                elif field == "keywords":
                    cur_line.append('"%s"' % citation.keywords.replace('"', "'"))
                elif field == "journal":
                    cur_line.append('"%s"' % none_to_str(citation.journal))
                elif field == "authors":
                    cur_line.append('"%s"' % "".join(citation.authors))
            self.write_buffer.append(",".join(cur_line))

        path_to_export = os.path.join(STATIC_FILES_PATH, "exports", "labels_%s.csv" % self.project_id)
        try:
            fout = open(path_to_export, 'w')
        except IOError:
            os.makedirs(os.path.dirname(path_to_export))
            fout = open(path_to_export, 'w')
        lbls_str = "\n".join(self.write_buffer)
        lbls_str = lbls_str.encode("utf-8", "ignore")
        fout.write(lbls_str)
        fout.close()
        return "%sexports/labels_%s.csv" % (url('/', qualified=True), self.project_id)

    def set_fields(self, new_fields):
        self.fields = new_fields

    def set_filter(self, new_filter):
        self.filter = new_filter

    def _get_participants_for_review(self, project_id):
        project = Session.query(model.Project).filter(model.Project.id == project_id).one()
        members = project.members
        return members

    def _get_citations_for_review(self, review_id):
        citation_q = Session.query(model.Citation)
        citations_for_review = citation_q.filter(model.Citation.project_id == review_id).all()
        return citations_for_review

    def _get_username_from_id(self, id):
        if id == CONSENSUS_USER:
            return "consensus"
        if id not in self.user_dict:
            user_q = Session.query(model.User)
            self.user_dict[id] = user_q.filter(model.User.id == id).one().username
        return self.user_dict[id]

    def _build_notes_dict(self):
        notes = Session.query(model.Note).filter(model.Note.citation_id.in_(self.all_citations)).all()
        for citation_id in self.all_citations:
            if citation_id not in self.citation_to_notes_dict:
                self.citation_to_notes_dict[citation_id] = {}
                for labeler in self.all_labelers:
                    self.citation_to_notes_dict[citation_id][labeler.username] = None

        for note in notes:
            self.citation_to_notes_dict[note.citation_id][self._get_username_from_id(note.creator_id)] = note

    def _build_tags_dict(self):
        tags = Session.query(model.Tag, model.TagType).filter(model.Tag.citation_id.in_(self.all_citations)).join(model.TagType, model.Tag.tag_id == model.TagType.id).all()
        for citation_id in self.all_citations:
            if citation_id not in self.citation_to_tags_dict:
                self.citation_to_tags_dict[citation_id] = []
        for tag in tags:
            self.citation_to_tags_dict[tag[0].citation_id].append(tag[1].text)

    def _get_notes_for_citation(self, citation_id, user_id):
        notes_q = Session.query(model.Note)
        notes = notes_q.filter(and_(\
                model.Note.citation_id == citation_id,
                model.Note.creator_id == user_id)).all()
        if len(notes) > 0:
            return notes[0]
        return None

    def _get_tags_for_citation(self, citation_id, texts_only=True, only_for_user_id=None):

        tag_q = Session.query(model.Tag)
        tags = None
        if only_for_user_id:
            # then filter on the study and the user
            tags = tag_q.filter(and_(\
                    model.Tag.citation_id == citation_id,\
                    model.Tag.creator_id == only_for_user_id)).all()
        else:
            # all tags for this citation, regardless of user
            tags = tag_q.filter(model.Tag.citation_id == citation_id).all()

        if texts_only:
            return self._tag_ids_to_texts([tag.tag_id for tag in tags])
        return tags

    def _tag_ids_to_texts(self, tag_ids):
        return [self._text_for_tag(tag_id) for tag_id in tag_ids]

    def _text_for_tag(self, tag_id):
        tag_type_q = Session.query(model.TagType)
        tag_obj = tag_type_q.filter(model.TagType.id == tag_id).one()
        return tag_obj.text

    def _get_tag_types_for_citation(self, citation_id, objects=False):
        tags = self._get_tags_for_citation(citation_id)
        # now map those types to names
        tag_type_q = Session.query(model.TagType)
        tags = []

        for tag in tags:
            tag_obj = tag_type_q.filter(model.TagType.id == tag.tag_id).one()

            if objects:
                tags.append(tag_obj)
            else:
                tags.append(tag_obj.text)

        return tags

    def _get_tag_types_for_review(self, review_id, only_for_user_id=None):
        tag_q = Session.query(model.TagType)

        if only_for_user_id:
            tag_types = tag_q.filter(and_(\
                        model.TagType.project_id == review_id,\
                        model.TagType.creator_id == only_for_user_id
                )).all()
        else:
            tag_types = tag_q.filter(model.TagType.project_id == review_id).all()
        return [tag_type.text for tag_type in tag_types]
