'''
a slightly misnamed module, as it can actually handle more than XML.
basically, this contains code to map data from a given format
(pmid list, refman xml, etc.) to abstrackr's SQL representation.
'''

# std libs
import string
import csv
import random
import os
import collections
import re

# third party
import sqlite3
from xml.etree.ElementTree import ElementTree
import Bio
from Bio import Entrez

# homegrown
import pubmedpy
import abstrackr.model as model # for access to sqlalchemy

pubmedpy.set_email("byron.wallace@gmail.com")

# for tsv importing
OBLIGATORY_FIELDS = ["id", "title", "abstract"] # these have to be there
OPTIONAL_FIELDS = ["authors", "keywords", "journal", "pmid"]

MAX_TITLE_LENGTH = 480
START_FILE_MARKER = "\xef\xbb\xbf" # AKA BOM

def looks_like_tsv(file_path):
    header_line = open(file_path, 'rU').readline()
    headers = [x.lower().strip().replace(START_FILE_MARKER, "") for x in header_line.split("\t")]
    if len(headers) == 0:
        return False
    print [_field_in(field, headers) for field in OBLIGATORY_FIELDS]
    # title, etc.?
    if all([_field_in(field, headers) for field in OBLIGATORY_FIELDS]):
        return True

    return False

def looks_like_ris(file_path):
    file_data = open(file_path, 'rU').read()

    re_pattern = re.compile("([A-Z][A-Z0-9]\s{2}-)", re.MULTILINE)
    if re.search(re_pattern, file_data) is not None:
        lines = re.split(re_pattern, file_data)
        o_c = 0 #open count
        c_c = 0 #close count
        for l in lines:
            if l == "TY  -":
                o_c += 1
            elif l == "ER  -":
                if o_c == c_c + 1:
                    c_c += 1
                else:
                    return False
        if o_c == c_c and o_c > 0:
            print "Looks like ris"
            return True
    return False

def looks_like_cochrane(file_path):
    file_data = open(file_path, 'rU').read()

    print file_data
    re_pattern = re.compile('Record\s#[0-9]+\sof\s[0-9]+', re.MULTILINE)
    tag_pattern = re.compile('[A-Z]{2}:\s', re.MULTILINE)
    if len(re.findall(re_pattern, file_data)) > 0 and len(re.findall(tag_pattern, file_data)) > 0:
        return True
    return False

def looks_like_list(file_path):
    f = open(file_path, 'rU')
    re_pattern = re.compile("^[0-9]+$", re.MULTILINE)
    for line in f:
        if re.match(re_pattern, line.strip()) is None:
            return False
    return True

def _field_in(field, headers):
    # we'll only enforce that a string *start* with
    # the field; this avoids issues with, e.g.,
    # pluralization and new lines.
    return any([x.startswith(field) for x in headers])

def _parse_pmids(pmids_path):
    parsing_errors = []
    pmids = []
    for pmid in [x.strip() for x in open(pmids_path, 'rU').readlines()]:
        if pmid != "":
            try:
                pmids.append(int(pmid))
            except:
                error = "Unable to parse '%s' in '%s'. This does not appear to be a valid Pubmed ID" % (pmid, os.path.basename(pmids_path))
                parsing_errors.append(error)
    return pmids, {"import-errors": parsing_errors}


def pubmed_ids_to_d(pmids):
    print "fetching articles..."
    articles = pubmedpy.batch_fetch(pmids)
    print "ok."

    articles = [article for article in articles if len(article)>=3]

    pmids_d = {}
    none_to_str = lambda x: x if x is not None else ""

    for article in articles:
        title_text = article.get("TI")
        ab_text = article.get("AB")
        authors = none_to_str(article.get("AU"))
        journal = none_to_str(article.get("JT"))
        keywords = none_to_str(article.get("MH"))
        pmid = int(article["PMID"])
        pmids_d[pmid] = {"title":title_text, "abstract":ab_text, "journal":journal,\
                                             "keywords":keywords, "pmid":pmid, "authors":authors}
    return pmids_d

def pmid_list_to_sql(pmids_path, review):
    pmids, dict_misc = _parse_pmids(pmids_path)
    # Find all citations in the project
    all_citations = model.Session.query(model.Citation).filter(model.Citation.project_id==review.id).all()
    # Get list of PMID's already in the project
    all_pmids = [c.pmid for c in all_citations]
    # List of PMID's to import
    pmid_import_list = []
    for p in pmids:
        if p not in all_pmids:
            pmid_import_list.append(p)
    d = pubmed_ids_to_d(pmid_import_list)
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d), dict_misc

def ris_to_sql(ris_path, review):
    print "building a dictionary from %s..." % ris_path
    d = ris_to_d(open(ris_path).read())
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d)

def ris_to_d(ris_data):
    ris_data = ris_data.decode('utf-8-sig')

    cur_id = 1
    ris_d  = {}

    # Define re pattern to capture ris style tags.
    re_pattern = re.compile('([A-Z][A-Z0-9]\s{2}-\s)', re.DOTALL)

    # Use re.split() to split the ris_data.
    lsof_lines = re.split(re_pattern, ris_data)

    # Get rid of empty strings.
    lsof_lines = [var for var in lsof_lines if var]

    for idx, line in enumerate(lsof_lines):
        if line == "TY  - ":
            # Clear fields
            current_citation = {"title":"", "abstract":"", "journal":"",\
                                        "keywords":"", "pmid":"", "authors":""}
            cur_authors, cur_keywords = [], []

            while cur_id in ris_d.keys():
                cur_id += 1

            ris_d[cur_id] = current_citation

        elif line in ("AU  - ", "A1  - "):
            cur_authors.append(lsof_lines[idx + 1])
        elif line in ("T1  - ", "TI  - "):
            current_citation["title"] = lsof_lines[idx + 1].strip()[:MAX_TITLE_LENGTH]
        elif re.match("^J[A-Z0-9]\s{2}-\s|^T2\s{2}-\s", line):
        # Test this -Birol
            current_citation["journal"] = lsof_lines[idx + 1].strip()
        elif line == "KW  - ":
            cur_keywords += [x.strip() for x in lsof_lines[idx + 1].splitlines()]
        elif line in ("N2  - ", "AB  - "):
            current_citation["abstract"] = lsof_lines[idx + 1]
        elif line in ("AN  - "):
            current_citation["pmid"] = lsof_lines[idx + 1].strip()
        elif line in ("ID  - "):
            # Sometimes ID's are given (source id). If this is the case
            # let's try to override the cur_id counter and give preference to this id
            try:
                internal_id = int(lsof_lines[idx + 1])
            except ValueError:
                continue

            # Swap IDs if necessary
            if internal_id in ris_d.keys():
                temp = ris_d[internal_id]
                ris_d[internal_id] = ris_d[cur_id]
                ris_d[cur_id] = temp
                cur_id = internal_id
            else:
                ris_d[internal_id] = ris_d.pop(cur_id)
                cur_id = internal_id

        elif line in ("ER  - "):
            current_citation["authors"] = list(OrderedSet(cur_authors))
            current_citation["keywords"] = list(cur_keywords)
            ris_d[cur_id] = current_citation

    return ris_d

def cochrane_to_sql(c_path, review):
    print "building a dictionary from %s..." % c_path
    d = cochrane_to_d(open(c_path, 'rU').read())
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d)

def cochrane_to_d(c_data):
    c_data = c_data.decode('iso-8859-1')
    cur_id = 1
    c_d  = {}

    # Define re pattern to capture cochrane style tags.
    re_pattern = re.compile('^Record\s#[0-9]+\sof\s[0-9]+$', re.MULTILINE)
    tag_re = re.compile('(^[A-Z][A-Z]:\s)', re.DOTALL | re.MULTILINE)

    # Use re.split() to split the c_data.
    lsof_lines = re.split(re_pattern, c_data)

    # Get rid of empty strings.
    lsof_lines = [var for var in lsof_lines if var]

    for idx, line in enumerate(lsof_lines):
        # Clear fields
        current_citation = {"title":"", "abstract":"", "journal":"",\
                                        "keywords":"", "pmid":"", "authors":""}
        cur_authors, cur_keywords = [], []

        while cur_id in c_d.keys():
            cur_id += 1

        c_d[cur_id] = current_citation

        ls = re.split(tag_re, line)

        for i, ll in enumerate(ls):
            print ll
            print ll == 'AU: '
            if ll == 'AU: ':
                cur_authors.append(ls[i + 1])
            elif ll == 'TI: ':
                current_citation["title"] = ls[i + 1].strip()[:MAX_TITLE_LENGTH]
            elif ll == 'SO: ':
                current_citation["journal"] = ls[i + 1].strip()
            elif ll == 'KY: ':
                cur_keywords = [ ss.strip() for ss in ls[i + 1].split(';')]
            elif ll == 'AB: ':
                current_citation["abstract"] = ls[i + 1]
            elif ll == 'PM: ':
                current_citation["pmid"] = ls[i + 1].strip()
            elif ll == 'ID: ':
                # Sometimes ID's are given (source id). If this is the case
                # let's try to override the cur_id counter and give preference to this id
                try:
                    internal_id = int(ls[i + 1])
                except ValueError:
                    continue

                # Swap IDs if necessary
                if internal_id in c_d.keys():
                    temp = c_d[internal_id]
                    c_d[internal_id] = c_d[cur_id]
                    c_d[cur_id] = temp
                    cur_id = internal_id
                else:
                    c_d[internal_id] = c_d.pop(cur_id)
                    cur_id = internal_id
        print current_citation
        current_citation["authors"] = list(OrderedSet(cur_authors))
        current_citation["keywords"] = list(cur_keywords)
        c_d[cur_id] = current_citation

    return c_d


# def ris_to_d(ris_data):
#     cur_id = 1
#     ris_d = {}

#     # drop garbage/blank lines
#     ris_data = [line for line in ris_data if "-" in line]

#     for line in ris_data:
#         # Prevent BOM unicode signature from messing up line parsing
#         line = line.decode('utf-8-sig')

#         field, value = line.split("-")[0], "-".join(line.split("-")[1:])
#         field, value = field.strip(), value.strip()

#         # Marks start of new citation
#         if field == "TY":

#             # Clear fields
#             current_citation = {"title":"", "abstract":"", "journal":"",\
#                                         "keywords":"", "pmid":"", "authors":""}
#             cur_authors, cur_keywords = [], []

#             while cur_id in ris_d.keys():
#                 cur_id += 1

#             ris_d[cur_id] = current_citation

#         elif field in ("AU", "A1"):
#             cur_authors.append(value)
#         elif field in ("T1", "TI"):
#             current_citation["title"] = value[:MAX_TITLE_LENGTH]
#         elif field.startswith("J"):
#             current_citation["journal"] = value
#         elif field == "KW":
#             cur_keywords.append(value)
#         elif field in ("N2", "AB"):
#             current_citation["abstract"] = value
#         elif field in ("ID"):
#             # Sometimes ID's are given (internal id). If this is the case
#             # let's try to override the cur_id counter and give preference to this id
#             try:
#                 internal_id = int(value)
#             except ValueError:
#                 continue

#             # Swap IDs if necessary
#             if internal_id in ris_d.keys():
#                 temp = ris_d[internal_id]
#                 ris_d[internal_id] = ris_d[cur_id]
#                 ris_d[cur_id] = temp
#                 cur_id = internal_id
#             else:
#                 ris_d[internal_id] = ris_d.pop(cur_id)
#                 cur_id = internal_id

#         elif field in ("ER"):
#             current_citation["authors"] = list(OrderedSet(cur_authors))
#             current_citation["keywords"] = list(cur_keywords)
#             ris_d[cur_id] = current_citation

#     return ris_d


def tsv_to_d(citations, field_index_d):
    tsv_d = {}
    parsing_errors = []

    for citation in citations:
        ## Make sure that the fields we are interested in are within range first
        ## If the line is misformed then we don't want to even consider when committing
        ## any data to the database and so we skip to the next citation without adding
        ## anything to tsv_d dictionary but we record the error for reporting
        try:
            for field in OPTIONAL_FIELDS:
                if field in field_index_d:
                    citation[field_index_d[field]].decode('utf8', 'replace')
            for field in OBLIGATORY_FIELDS:
                citation[field_index_d[field]].decode('utf8', 'replace')
        except (IndexError, KeyError) as e:
            error = "Problem with %s. This line is misformed and missing critical fields" % (citation)
            parsing_errors.append(error)
            continue
        ## Now build the tsv_d dictionary. If we did this earlier then we
        ## will get into trouble for having an entry with missing fields and it
        ## will throw errors later in the program
        cur_id = citation[field_index_d["id"]]
        tsv_d[cur_id] = {}
        for field in OPTIONAL_FIELDS:
            if field in field_index_d:
                tsv_d[cur_id][field] = \
                    citation[field_index_d[field]].decode('utf8', 'replace')

                # issue 2 -- if this is the authors field, we expect author names
                # to be separated by commas. later in the pipeline, we'll expect
                # a *list* here, so we create that now.
                if field == "authors" or field=="keywords":
                    tsv_d[cur_id][field] = tsv_d[cur_id][field].split(",")
            else:
                # just insert a blank string
                tsv_d[cur_id][field] = ""

        # now add the obligatory fields
        for field in OBLIGATORY_FIELDS:
            tsv_d[cur_id][field] = citation[field_index_d[field]].decode('utf8', 'replace')
    return tsv_d, {"import-errors": parsing_errors}


def tsv_to_sql(tsv_path, review):
    # figure out the indices
    #citations = open(tsv_path).readlines()
    open_f = open(tsv_path, 'rU')
    citations = csv.reader(open_f, delimiter="\t")
    # map field names to the corresponding indices
    # in the tsv, as indicated by the header
    headers = [header.lower().strip().replace(START_FILE_MARKER, "") for header in citations.next()]
    field_index_d = _field_index_d(headers)
    d, dict_misc = tsv_to_d(citations, field_index_d)
    dict_to_sql(d, review)
    open_f.close()
    return len(d), dict_misc

#def ris_to_d(ris_data):
#    ris_d = {}
#    cur_id = 1
#    cur_authors, cur_keywords = [], []
#    current_citation = {"title":"", "abstract":"", "journal":"",\
#                                "keywords":"", "pmid":"", "authors":""}
#
#    # drop garbage/blank lines
#    ris_data = [line for line in ris_data if "-" in line]
#
#    # we skip the first line which just starts the
#    # first citation (citation 1)
#    for line in ris_data[1:]:
#        field, value = line.split("-")[0], "-".join(line.split("-")[1:])
#        field, value = field.strip(), value.strip()
#
#        if field == "TY":
#            # new citation
#            current_citation["authors"] = list(set(cur_authors))
#            current_citation["keywords"] = list(cur_keywords)
#            ris_d[cur_id] = current_citation
#
#            ###
#            # now create a new (empty) citation
#            # to be overwritten
#            current_citation = {"title":"", "abstract":"", "journal":"",\
#                                "keywords":"", "pmid":"", "authors":""}
#            cur_authors, cur_keywords = [], []
#            cur_id += 1
#        elif field in ("AU", "A1"):
#            # author
#            #pdb.set_trace()
#            cur_authors.append(value)
#        elif field in ("T1", "TI"):
#            current_citation["title"] = value[:MAX_TITLE_LENGTH]
#        elif field.startswith("J"):
#            current_citation["journal"] = value
#        elif field == "KW":
#            cur_keywords.append(value)
#        elif field in ("N2", "AB"):
#            current_citation["abstract"] = value
#    # add the last citation
#    ris_d[cur_id] = current_citation
#
#    return ris_d

def _field_index_d(headers):
    field_index_d = {}
    for field in OBLIGATORY_FIELDS:
        # we know these exist
        field_index_d[field] = headers.index(field)

    # now let's see if they've optional headers
    for field in OPTIONAL_FIELDS:
        if field in headers:
            field_index_d[field] = headers.index(field)

    return field_index_d

def xml_to_sql(xml_path, review):
    print "building a dictionary from %s..." % xml_path
    d, dict_misc = xml_to_dict(xml_path)
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d), dict_misc



def dict_to_sql(xml_d, review):
    cit_num = 0
    # issue #31: explicitly randomize ordering
    xml_d_items = xml_d.items()
    random.shuffle(xml_d_items)
    for ref_id, citation_d in xml_d_items:
        cit_id = insert_citation(review.id, ref_id, citation_d)
        insert_priority_entry(review.id, cit_id, cit_num)
        cit_num += 1
    model.Session.commit()

def insert_citation(review_id, ref_id, citation_d):
    citation = model.Citation()
    citation.project_id = review_id
    # Ensure that ref_id is an integer, drop it otherwise.
    # try:
    #     ref_id = int(ref_id)
    # except:
    #     ref_id = None

    citation.refman = ref_id
    pmid = citation_d['pmid']
    citation.pmid =  pmid if (pmid is not None and pmid != '') else 0
    # we truncate the citation if it's too long!
    citation.title = citation_d['title'][:MAX_TITLE_LENGTH] if \
                                citation_d['title'] is not None else "(no title found)"
    citation.abstract = citation_d['abstract'][:9980] if \
                                citation_d['abstract'] is not None else None
    citation.authors = " and ".join(citation_d['authors'])
    citation.keywords = ','.join(citation_d['keywords'])
    citation.journal = citation_d['journal']

    model.Session.add(citation)
    model.Session.commit()

    return citation.id

def insert_priority_entry(review_id, citation_id, \
                            init_priority_num, num_times_labeled=0):
    priority = model.Priority()
    priority.project_id = review_id
    priority.citation_id = citation_id
    priority.priority = init_priority_num
    priority.num_times_labeled = num_times_labeled
    priority.is_out = False
    model.Session.add(priority)


def xml_to_dict(fpath):
    '''
    Converts study data from (ref man generated) XML to a dictionary matching study IDs (keys) to
    title/abstract tuples (values). For example: dict[n] might map to a tuple [t_n, a_n] where t_n is the
    title of the nth paper and a_n is the abstract
    '''
    ref_ids_to_abs = {}
    parsing_errors = []
    num_no_abs = 0
    tree = ElementTree(file=fpath)

    num_failed = 0

    for record in tree.findall('.//record'):
        pubmed_id, refmanid = None, None

        refman_version = record.findtext('.//source-app')
        path_str = None
        ### here we check the RefMan version, and change
        # the xml path accordingly. this fixes issue #7
        if refman_version == 'Reference Manager 12.0':
            path_str = './/rec-number/style'
            journal_path_str = './/periodical/full-title/style'
        elif refman_version == 'Reference Manager 11.0':
            path_str = './/rec-number'
            journal_path_str = './/periodical/abbr-1/style'

        try:
            refmanid = int(record.findtext(path_str))
        except:
            error = "Unable to parse record '%s' in '%s'" % (record, os.path.basename(fpath))
            #print "failed to parse refman document"
            parsing_errors.append(error)

        if refmanid is not None:
            # attempt to grab the pubmed id
            pubmed_id = ""
            try:
                pubmed = record.findtext('.//notes/style')
                pubmed = re.split('([A-Z][A-Z0-9]\s[\-]\s)', pubmed, re.DOTALL)
                for i in range(len(pubmed)):
                    if "UI - " in pubmed[i]:
                        pubmed_str = pubmed[i+1].strip()
                        pubmed_id = int("".join([x for x in pubmed_str if x in string.digits]))
            except Exception, ex:
                error = "Problem getting pmid from '%s' in '%s'" % (record, os.path.basename(fpath))
                parsing_errors.append(error)
                #print "problem getting pmid ..."
                #print ex
                #print("\n")

            ab_text = record.findtext('.//abstract/style')
            if ab_text is None:
                num_no_abs += 1

            title_text = record.findtext('.//titles/title/style')

            # Also grab keywords
            keywords = [keyword.text.strip().lower() for keyword in record.findall(".//keywords/keyword/style")]

            # and authors
            authors = [author.text for author in record.findall(".//contributors/authors/author/style")]

            # journal
            journal = record.findtext(journal_path_str)

            ref_ids_to_abs[refmanid] = {"title":title_text, "abstract":ab_text, "journal":journal,\
                        "keywords":keywords, "pmid":pubmed_id, "authors":authors}


    print "\nFinished. Returning %s title/abstract/keyword sets, %s of which have no abstracts.\n" \
                    % (len(ref_ids_to_abs.keys()), num_no_abs)
    return ref_ids_to_abs, {"import-errors": parsing_errors}


class OrderedSet(collections.MutableSet):
    """ Stolen from http://code.activestate.com/recipes/576694/
    """

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)




