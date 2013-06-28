'''
a slightly misnamed module, as it can actually handle more than XML.
basically, this contains code to map data from a given format
(pmid list, refman xml, etc.) to abstrackr's SQL representation.
'''

# std libs
import pdb
import string 
import csv
import random

# third party
import sqlite3
import elementtree
from elementtree.ElementTree import ElementTree
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
    
    # title, etc.?
    if all([_field_in(field, headers) for field in OBLIGATORY_FIELDS]):
        return True
    
    return False

def _field_in(field, headers):
    # we'll only enforce that a string *start* with
    # the field; this avoids issues with, e.g.,
    # pluralization and new lines.
    return any([x.startswith(field) for x in headers])

def _parse_pmids(pmids_path):
    pmids = []
    for pmid in [x.strip() for x in open(pmids_path, 'rU').readlines()]:
        if pmid != "":
            try:
                pmids.append(int(pmid))
            except:
                print "couldn't parse this line; %s" % pmid
    return pmids


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
    pmids = _parse_pmids(pmids_path)
    d = pubmed_ids_to_d(pmids)
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d)

def ris_to_sql(ris_path, review):
    print "building a dictionary from %s..." % ris_path
    d = ris_to_d(open(ris_path, 'rU').readlines())
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d)
    
def ris_to_d(ris_data):
    ris_d = {}
    cur_id = 1
    cur_authors, cur_keywords = [], []
    current_citation = {"title":"", "abstract":"", "journal":"",\
                                "keywords":"", "pmid":"", "authors":""}

    # drop garbage/blank lines
    ris_data = [line for line in ris_data if "-" in line]

    # we skip the first line which just starts the
    # first citation (citation 1)
    for line in ris_data[1:]:
        field, value = line.split("-")[0], "-".join(line.split("-")[1:])
        field, value = field.strip(), value.strip()

        if field == "TY":
            # new citation
            current_citation["authors"] = list(set(cur_authors))
            current_citation["keywords"] = list(cur_keywords)
            ris_d[cur_id] = current_citation

            ###
            # now create a new (empty) citation
            # to be overwritten
            current_citation = {"title":"", "abstract":"", "journal":"",\
                                "keywords":"", "pmid":"", "authors":""}
            cur_authors, cur_keywords = [], []
            cur_id += 1
        elif field in ("AU", "A1"):
            # author
            #pdb.set_trace()
            cur_authors.append(value)
        elif field in ("T1", "TI"):
            current_citation["title"] = value[:MAX_TITLE_LENGTH]
        elif field.startswith("J"):
            current_citation["journal"] = value
        elif field == "KW":
            cur_keywords.append(value)
        elif field in ("N2", "AB"):
            current_citation["abstract"] = value
    # add the last citation
    ris_d[cur_id] = current_citation
    
    return ris_d


def tsv_to_d(citations, field_index_d):
    tsv_d = {}

    for citation in citations:
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

    return tsv_d


def tsv_to_sql(tsv_path, review):
    # figure out the indices
    #citations = open(tsv_path).readlines()
    open_f = open(tsv_path, 'rU')
    citations = csv.reader(open_f, delimiter="\t")
    # map field names to the corresponding indices
    # in the tsv, as indicated by the header
    headers = [header.strip().replace(START_FILE_MARKER, "") for header in citations.next()]
    field_index_d = _field_index_d(headers)
    d = tsv_to_d(citations, field_index_d)
    dict_to_sql(d, review)
    open_f.close()
    return len(d)


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
    d = xml_to_dict(xml_path)
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."
    return len(d)


    
def dict_to_sql(xml_d, review): 
    cit_num = 0
    # issue #31: explicitly randomize ordering
    xml_d_items = xml_d.items()
    random.shuffle(xml_d_items)
    for ref_id, citation_d in xml_d_items:
        cit_id = insert_citation(review.review_id, ref_id, citation_d)
        insert_priority_entry(review.review_id, cit_id, cit_num)
        cit_num += 1
    model.Session.commit()

def insert_citation(review_id, ref_id, citation_d):
    citation = model.Citation()
    citation.review_id = review_id
    try:
        ref_id = int(ref_id)
    except:
        ref_id = None

    citation.refman_id = ref_id
    pmid = citation_d['pmid']
    citation.pmid_id =  pmid if (pmid is not None and pmid != '') else 0
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

    return citation.citation_id
 
def insert_priority_entry(review_id, citation_id, \
                            init_priority_num, num_times_labeled=0):
    priority = model.Priority()
    priority.review_id = review_id
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
            print "failed to parse refman document"

        if refmanid is not None:
            # attempt to grab the pubmed id
            pubmed_id = ""
            try:
                pubmed = record.findtext('.//notes/style')
                pubmed = pubmed.split("-")
                for i in range(len(pubmed)):
                    if "UI" in pubmed[i]:
                        pubmed_str = pubmed[i+1].strip()
                        pubmed_id = int("".join([x for x in pubmed_str if x in string.digits]))
            except Exception, ex:
                print "problem getting pmid ..."
                print ex
                print("\n")
    
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
    return ref_ids_to_abs

