import csv
import sys
import json
import collections

from Bio import Entrez
from Bio import Medline
from nltk.metrics import edit_distance
from pubmedpy import rank_by_edit_distance

# Set up
INPATH = sys.argv[1]
OUTPATH = sys.argv[2]
Entrez.email = "byron.wallace@gmail.com"
rowCnt = 1
headers = {
        'Error': 'error_code',
        'PMID': 'pmid',
        'CitationId': 'citation_id',
        'Title': 'title',
        'Prediction': 'predicted p of being relevant',
        'Hard': '\'hard\' screening prediction*'
        }
errors = {
        1: "Pubmed id AND title are absent from the row.",
        2: "No 'Count' key found in PubMed response.",
        3: "rank_by_edit_distance returned None.",
        4: "Title search returned 0 records."
        }

def main():
    # Tell python we want to use the global variable rowCnt.
    global rowCnt
    with open(INPATH, 'rU') as f:
        reader = csv.DictReader(f, dialect='excel',
                delimiter='\t')
        with open(OUTPATH, 'w') as csvfile:
            fieldnames = [
                    headers['Error'],
                    headers['PMID'],
                    headers['CitationId'],
                    headers['Title'],
                    headers['Prediction'],
                    headers['Hard'],
                    ]
            writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                output = {}
                pmid = row.get(headers['PMID'])
                citation_id = row.get(headers['CitationId'])
                title = row[headers['Title']]
                prediction = row.get(headers['Prediction'])
                hard = row.get(headers['Hard'])
                error = ""

                # Check value of pmid.
                if not pmid:
                    # We have to have a title for this to work
                    if title:
                        retVal = _find_best_pmid_by_title(title)
                        pmid = retVal.pmid
                        error = retVal.error
                    else:
                        print "Can't process this row. Pubmed "
                        print "id AND title is missing."
                        pmid = ""
                        error = errors[1]

                output = {
                        headers['Error']: error,
                        headers['PMID']: pmid,
                        headers['CitationId']: citation_id,
                        headers['Title']: title,
                        headers['Prediction']: prediction,
                        headers['Hard']: hard
                        }
                writer.writerow(output)

                # Increment counter.
                print "On row: " + str(rowCnt)
                rowCnt = rowCnt + 1

def _find_best_pmid_by_title(title):
    """Retrieve pmid from pubmed based on title string.

    :title: TODO
    :returns: ReturnTuple(INT, INT)

    """
    returnVal = collections.namedtuple('ReturnTuple', ['pmid', 'error'])
    try:
        handle = Entrez.esearch(db="pubmed",
                term='"{0}"'.format(title),
                field="ti")
    except Exception as e:
        return returnVal("", e)
    records = Entrez.read(handle)
    record_count = records.get("Count")
    if record_count:
        if record_count == "1":
            return returnVal(records.get("IdList")[0], "")
        elif record_count == "0":
            return returnVal("", errors[4])
        else:
            sorted_pmids = rank_by_edit_distance(title.strip().lower(),
                    records.get("IdList"))
            if sorted_pmids:
                try:
                    return returnVal(sorted_pmids[0][0], "")
                except Exception as e:
                    return returnVal("", e)
            else:
                return returnVal("", errors[3])
    else:
        return returnVal("", errors[2])

if __name__ == "__main__":
    main()

