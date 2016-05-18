import pubmedpy
import time
import csv
import sys

from paste.deploy import appconfig
from pylons import config

from abstrackr.config.environment import load_environment
from abstrackr.model.meta import Session

import abstrackr.model as model

from sqlalchemy import and_

conf = appconfig('config:development.ini', relative_to='.')
load_environment(conf.global_conf, conf.local_conf)

#### Match abstract title to PMID
FILE_PATH = sys.argv[1]
OUT_PATH  = sys.argv[2]

hPmid       = 'pmid'
hCitation   = 'citation_id'
hTitle      = 'title'
hPrediction = 'predicted p of being relevant'
hHard       = '\'hard\' screening prediction*'

with open(FILE_PATH, 'rU') as f:
    reader = csv.DictReader(f, dialect='excel', delimiter='\t')

    with open(OUT_PATH, 'w') as csvfile:
        fieldnames = [hPmid, hCitation, hTitle, hPrediction, hHard]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for row in reader:
            output_row = {}
            citation_id = row[hCitation]
            title = row[hTitle]
            predicted = row[hPrediction]
            hard = row[hHard]
            try:
                pmid = pubmedpy.get_pmid_from_title(title)
                pmid = int(pmid)
            except Exception as e:
                pmid = '-- Cannot find --'

            output_row = { hPmid: pmid, hCitation: citation_id,
                    hTitle: title, hPrediction: predicted,
                    hHard: hard }
            writer.writerow(output_row)

###############################################################################################

#### This is fixing Emily's project. The refman ids weren't saved when she imported the project
#PROJECT_ID = 219
#FILE_PATH = './Abstraktr_Update_Lit_Review_11.12.13.txt'
#citations_q = Session.query(model.Citation)
#
#found = 0
#not_found = 0
#
#with open(FILE_PATH, 'r') as f:
#    reader = csv.DictReader(f, delimiter='\t')
#
#    for row in reader:
#        #print(row['id'], row['title'], row['abstract'])
#        citation = citations_q.filter_by(title=row['title'], project_id=PROJECT_ID).first()
#        if not citation:
#            print('could not find title matching with %s' % row['title'])
#            not_found += 1
#        else:
#            found += 1
#            citation.refman = row['id']
#            Session.add(citation)
#            Session.commit()
#
#print("found %s" % found)
#print("not found %s" % not_found)
###############################################################################################


### This was for getting PMID's from the titles
#citations_q = Session.query(model.Citation)
#citations = citations_q.filter(model.Citation.pmid == 0).all()
#
#print(len(citations))
#
#for c in citations:
#  id = c.id
#  title = c.title
#  try:
#    pmid = pubmedpy.get_pmid_from_title(title)
#    pmid = int(pmid)
#  except:
#    pmid = None
#  finally:
#    if pmid==0:
#      pmid = None
#    c.pmid = pmid
#    Session.add(c)
#    Session.commit()
#print("done")
####################################################################################


### This is for counting the number of labels for each citation in Issa's project
# d_user_studies_labeled = {'chris': [], 'issa': [], 'galan': [], 'dale': []}
# d_map = {'chris': 6, 'issa': 7, 'galan': 8, 'dale': 9}
# users = ['chris', 'issa', 'galan', 'dale']
# summary = {}
# lof_citation_ids_with_one_label = []
# lof_citation_ids_with_three_labels = []
#
# all_citations_q = Session.query(model.Citation)
# all_citations = all_citations_q.filter_by(project_id=80).all()
# all_citation_ids = [c.id for c in all_citations]
#
# for user in users:
#   print("Working on %s" % user)
#   #time.sleep(3)
#   labels_q = Session.query(model.Label)
#   labels = labels_q.filter_by(project_id=80, user_id=d_map[user]).all()
#   for label in labels:
#     d_user_studies_labeled[user].append(label.study_id)
#   print("  %s has labeled %s studies" % (user, len(d_user_studies_labeled[user])))
#
# print("")
# print("*This project has %s citations*" % (len(all_citations)))
#
# for cit_id in all_citation_ids:
#   for user in users:
#     if cit_id in d_user_studies_labeled[user]:
#       try:
#         summary[cit_id] += 1
#       except KeyError:
#         summary[cit_id] = 1
#
# for key, val in summary.items():
#   if val==1:
#     lof_citation_ids_with_one_label.append(key)
#   elif val==3:
#     lof_citation_ids_with_three_labels.append(key)
#
# for c_id in lof_citation_ids_with_one_label:
#   print str(c_id) + ",",
#
# print ""
# print "Need to label %s more" % len(lof_citation_ids_with_one_label)
# print "%s citations have 3 labels" % len(lof_citation_ids_with_three_labels)
#
# for i in lof_citation_ids_with_one_label:
#   p = Session.query(model.Priority).filter_by(project_id=80, citation_id=i).first()
#
#   if p is None:
#     priority = model.Priority()
#     priority.project_id = 80
#     priority.citation_id = i
#     priority.num_times_labeled = 1
#     Session.add(priority)
# Session.commit()
###########################################################################################
