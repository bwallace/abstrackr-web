import os
from exporter_globals import *

import xml.etree.ElementTree as ET
import abstrackr.model as model
from abstrackr.model.meta import Session
from paste.deploy import appconfig
from pylons import url

class XmlBuilder:
    def __init__(self, id, lbl_filter_f = None):
        """
        id => id of the abstrackr project
        filter => filter function for labels
        """

        self.project_id = id

        # default to exporting everything
        if lbl_filter_f is None:
            lbl_filter_f = lambda label: True

        # get fields
        conf = appconfig('config:development.ini', relative_to='.')
        #load_environment(conf.global_conf, conf.local_conf)

        review_q = Session.query(model.Project)
        review = review_q.filter(model.Project.id == id).one()

        """ create XML root and add meta information
            -Birol
        """
        self.root = ET.Element('project')
        et_project_name = ET.SubElement(self.root, 'name')
        et_project_name.text = review.name
        et_project_id = ET.SubElement(self.root, 'id')
        et_project_id.text = str(review.id)

        labeler_dict = {}
        member_list = review.members
        leader_list = review.leaders

        et_project_member_list = ET.SubElement(self.root, 'member_list')

        for user in  member_list + leader_list:
            et_project_member = ET.SubElement(et_project_member_list, 'member')
            et_project_member_id = ET.SubElement(et_project_member, 'id')
            et_project_member_id.text = str(user.id)
            et_project_member_username = ET.SubElement(et_project_member, 'username')
            et_project_member_username.text = user.username
            et_project_member_email = ET.SubElement(et_project_member, 'email')
            et_project_member_email.text = user.email


        """ create an ET subelement to hold the citations
            -Birol
        """
        et_citation_list = ET.SubElement(self.root, "citation_list")

        citations_to_export = Session.query(model.Citation).filter_by(project_id = id).all()

        for citation in citations_to_export:
            """ create ET subelement for each citation, then add the relevant fields
                -Birol
            """
            ## some helpers
            none_to_str = lambda x: "" if x is None else x
            zero_to_none = lambda x: "none" if x==0 else str(x)

            et_citation = ET.SubElement(et_citation_list, "citation")

            et_citation_internal = ET.SubElement(et_citation, "internal_id")
            et_citation_internal.text = zero_to_none(citation.id)

            et_citation_source = ET.SubElement(et_citation, "source_id")
            et_citation_source.text = zero_to_none(citation.refman)

            et_citation_pubmed = ET.SubElement(et_citation, "pubmed_id")
            et_citation_pubmed.text = zero_to_none(citation.pmid)

            """ We replace double quotes with single quotes here, so we do not
                have to do it later.
                -Birol
            """
            et_citation_abstract = ET.SubElement(et_citation, "abstract")
            et_citation_abstract.text = none_to_str(citation.abstract).replace('"', "'")

            et_citation_title = ET.SubElement(et_citation, "title")
            et_citation_title.text = citation.title.replace('"', "'")

            """ Not sure if all the keywords are separated by commas. If not, this
                would cause problems.
                -Birol
            """
            kw_list = citation.keywords.replace('"', "'").split(',')
            et_citation_keyword_list = ET.SubElement(et_citation, "keyword_list")
            for kw in kw_list:
                if kw == "":
                    continue
                et_citation_keyword = ET.SubElement(et_citation_keyword_list, "keyword")
                et_citation_keyword.text = kw

            et_citation_journal = ET.SubElement(et_citation, "journal")
            et_citation_journal.text = none_to_str(citation.journal)

            """ Also not sure if all the authors are separated by " and ". If not,
                there will be suffering.
                -Birol
            """
            auth_list = citation.authors.split(' and ')
            et_citation_author_list = ET.SubElement(et_citation, "author_list")

            for auth in auth_list:
                if auth == "":
                    continue
                et_citation_author = ET.SubElement(et_citation_author_list, "author")
                et_citation_author.text = auth

            tag_list = Session.query(model.TagType).join(model.Tag, model.Tag.tag_id == model.TagType.id).filter_by(citation_id=citation.id).all()

            et_citation_tag_list = ET.SubElement(et_citation, "tag_list")

            for tag in tag_list:
                et_citation_tag = ET.SubElement(et_citation_tag_list, "tag")
                et_citation_tag.text = tag.text

            label_list = Session.query(model.Label).filter_by(study_id=citation.id).all()
            et_citation_label_list = ET.SubElement(et_citation, "label_list")

            for label in label_list:
                if not lbl_filter_f(label):
                    continue
                et_citation_label = ET.SubElement(et_citation_label_list, "label")
                et_citation_label_labeler = ET.SubElement(et_citation_label, "labeler")
                et_citation_label_labeler.text = str(label.user_id)
                et_citation_label_decision = ET.SubElement(et_citation_label, "decision")
                et_citation_label_decision.text = str(label.label)

            notes_list = Session.query(model.Note).filter_by(citation_id = citation.id).all()
            et_citation_notes_list = ET.SubElement(et_citation, "notes_list")

            for note in notes_list:
                et_citation_note = ET.SubElement(et_citation_notes_list, "note")
                et_citation_note_creator = ET.SubElement(et_citation_note, "user")
                et_citation_note_creator.text = str(note.creator_id)
                et_citation_note_general = ET.SubElement(et_citation_note, "general")
                et_citation_note_general.text = note.general
                et_citation_note_population = ET.SubElement(et_citation_note, "population")
                et_citation_note_population.text = note.population
                et_citation_note_ic = ET.SubElement(et_citation_note, "ec")
                et_citation_note_ic.text = note.ic
                et_citation_note_outcome = ET.SubElement(et_citation_note, "outcome")
                et_citation_note_outcome.text = note.outcome
        return

    def write_labels(self):
        path_to_export = os.path.join(STATIC_FILES_PATH, "exports", "labels_%s.xml" % self.project_id)
        try:
            fout = open(path_to_export, 'w')
        except IOError:
            os.makedirs(os.path.dirname(path_to_export))
            fout = open(path_to_export, 'w')
        ET.ElementTree(self.root).write(fout)
        fout.close()
        return "%sexports/labels_%s.xml" % (url('/', qualified=True), self.project_id)

#ET.ElementTree(XmlBuilder(8181).root).write(open("export_8181.xml", 'w+'))
#a = XmlBuilder(5844)
#import pdb; pdb.set_trace()
