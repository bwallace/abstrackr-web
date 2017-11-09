import os
from exporter_globals import *

import xml.etree.ElementTree as ET
import abstrackr.model as model
from abstrackr.model.meta import Session
from paste.deploy import appconfig
from pylons import url

class RisBuilder:
    def __init__(self, root):
        self.project_id = root.find('id').text
        self.root = root
        return

    def write_citations(self):
        write_buffer = []

        citations = self._get_citations()
        #iterate over citations
        for citation in citations:
            write_buffer.append('TY  - JOUR')
            write_buffer.append('TI  - ' + citation.find('title').text)
            write_buffer.append('AB  - ' + citation.find('abstract').text)

            #im not sure about the tags for different ids
            write_buffer.append('ID  - ' + citation.find('internal_id').text)
            write_buffer.append('C1  - ' + citation.find('source_id').text)
            write_buffer.append('C2  - ' + citation.find('pubmed_id').text)

            write_buffer.append('JO  - ' + citation.find('journal').text)

            authors = self._get_citation_authors(citation)
            for author in authors:
                write_buffer.append('AU  - ' + author.text)

            tags = self._get_citation_tags(citation)
            for tag in tags:
                write_buffer.append('C3  - ' + tag.text)

            keywords = self._get_citation_keywords(citation)
            for keyword in keywords:
                write_buffer.append('KW  - ' + keyword.text)

            write_buffer.append('ER  - \n')

        path_to_export = os.path.join(STATIC_FILES_PATH, "exports", "citations_%s.ris" % self.project_id)
        try:
            fout = open(path_to_export, 'w')
        except IOError:
            os.makedirs(os.path.dirname(path_to_export))
            fout = open(path_to_export, 'w')
        lbls_str = "\n".join(write_buffer)
        lbls_str = lbls_str.encode("utf-8", "ignore")
        fout.write(lbls_str)
        fout.close()
        return "%sexports/citations_%s.ris" % (url('/', qualified=True), self.project_id)

    def write_labels(self):
        write_buffer = []
        citations = self._get_citations()
        member_dict = self._get_member_dict()
        for citation in citations:
            labels = self._get_citation_labels(citation)
            for label in labels:
                decision = label.find('decision').text
                labeler_id = label.find('labeler').text
                write_buffer.append('TY  - LABEL')
                write_buffer.append('LB  - ' + decision)
                """
                    Title and the ids of the citation that the label belongs to
                """
                write_buffer.append('TI  - ' + citation.find('title').text)
                write_buffer.append('ID  - ' + citation.find('internal_id').text)
                write_buffer.append('C1  - ' + citation.find('source_id').text)
                write_buffer.append('C2  - ' + citation.find('pubmed_id').text)

                write_buffer.append('AU  - ' + member_dict[labeler_id])
                write_buffer.append('ER  - \n')

        path_to_export = os.path.join(STATIC_FILES_PATH, "exports", "labels_%s.ris" % self.project_id)
        try:
            fout = open(path_to_export, 'w')
        except IOError:
            os.makedirs(os.path.dirname(path_to_export))
            fout = open(path_to_export, 'w')
        lbls_str = "\n".join(write_buffer)
        lbls_str = lbls_str.encode("utf-8", "ignore")
        fout.write(lbls_str)
        fout.close()
        return "%sexports/labels_%s.ris" % (url('/', qualified=True), self.project_id)

    def _get_citations(self):
        citation_list = self.root.find('citation_list')
        return citation_list.findall('citation')

    def _get_citation_authors(self, citation):
        author_list = citation.find('author_list')
        return author_list.findall('author')

    def _get_citation_tags(self, citation):
        tag_list = citation.find('tag_list')
        return tag_list.findall('tag')

    def _get_citation_keywords(self, citation):
        keyword_list = citation.find('keyword_list')
        return keyword_list.findall('keyword')

    def _get_citation_labels(self, citation):
        label_list = citation.find('label_list')
        return label_list.findall('label')

    def _get_member_dict(self):
        member_list = self.root.find('member_list')
        member_dict = {'0': 'consensus'}
        for member in member_list.findall('member'):
            member_dict[member.find('id').text] = member.find('email').text
        return member_dict

#import pdb; pdb.set_trace();
