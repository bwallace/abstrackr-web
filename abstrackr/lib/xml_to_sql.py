
# std libs
import pdb
import string 

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

def pubmed_ids_to_d(pmids):
    print "fetching articles..."
    articles = pubmedpy.batch_fetch(pmids)
    print "ok."

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

def _parse_pmids(pmids_path):
    pmids = []
    for pmid in [x.replace("\n", "") for x in open(pmids_path, 'r').readlines()]:
        if pmid != "":
            try:
                pmids.append(int(pmid))
            except:
                print "couldn't parse this line; %s" % pmid
    return pmids
    
def xml_to_sql(xml_path, review):
    print "building a dictionary from %s..." % xml_path
    d = xml_to_dict(xml_path)
    print "ok. now inserting into sql..."
    dict_to_sql(d, review)
    print "ok."

def dict_to_sql(xml_d, review): 
    for ref_id, citation_d in xml_d.items():
        insert_citation(review.review_id, ref_id, citation_d)
        
def insert_citation(review_id, ref_id, citation_d):
    citation = model.Citation()
    citation.review_id = review_id
    citation.refman_id = ref_id
    pmid = citation_d['pmid']
    citation.pmid_id =  pmid if (pmid is not None and pmid != '') else 0
    citation.title = citation_d['title']
    citation.abstract = citation_d['abstract']
    citation.authors = " and ".join(citation_d['authors'])
    citation.keywords = ','.join(citation_d['keywords'])
    citation.journal = citation_d['journal']
    model.Session.add(citation)
    model.Session.commit()
 
#def insert_priority_entry(re)


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
        pubmed_id = None
        refmanid = None
        try:
            refmanid = eval(record.findtext('.//rec-number'))
        except:
            print "failed to parse a refman document."
            

        if refmanid is not None:
            # attempt to grab the pubmed id
            pubmed_id = ""
            try:
                pubmed = record.findtext('.//notes/style')
                pubmed = pubmed.split("-")
                for i in range(len(pubmed)):
                    if "UI" in pubmed[i]:
                        pubmed_str = pubmed[i+1].strip()
                        pubmed_id = eval("".join([x for x in pubmed_str if x in string.digits]))
            except Exception, ex:
                print "problem getting pmid ..."
                print ex
    
            ab_text = record.findtext('.//abstract/style')
            if ab_text is None:
                num_no_abs += 1
    
            title_text = record.findtext('.//titles/title/style')
    
            # Also grab keywords
            keywords = [keyword.text.strip().lower() for keyword in record.findall(".//keywords/keyword/style")]
    
            # and authors
            authors = [author.text for author in record.findall(".//contributors/authors/author/style")]
    
            # journal
            journal = record.findtext(".//periodical/abbr-1/style")
    
            ref_ids_to_abs[refmanid] = {"title":title_text, "abstract":ab_text, "journal":journal,\
                        "keywords":keywords, "pmid":pubmed_id, "authors":authors}

    print "Finished. Returning %s title/abstract/keyword sets, %s of which have no abstracts." \
                    % (len(ref_ids_to_abs.keys()), num_no_abs)
    return ref_ids_to_abs


