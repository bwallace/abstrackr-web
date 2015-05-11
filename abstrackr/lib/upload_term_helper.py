import csv
import datetime
import abstrackr.model as model # for access to sqlalchemy
from abstrackr.model.meta import Session

def import_terms(file_path, review, user):
  open_f = open(file_path, 'rU')
  terms = csv.reader(open_f, delimiter="\t")

  # Ensure the header looks correct.
  if (terms.next()[0] != 'term'):
    return False, 1

  # Iterate through each row and insert terms and their labels.
  for row in terms:
    unique, code = _row_unique(row, review.id, user.id)
    if (unique):
      try:
        labeledfeature = model.LabeledFeature()
        labeledfeature.term = row[0]
        labeledfeature.project_id = review.id
        labeledfeature.user_id = user.id
        labeledfeature.label = row[1]
        labeledfeature.date_created = datetime.datetime.now()
        model.Session.add(labeledfeature)
      except IndexError, e:
        return False, 2
      else:
        return False, 3
      finally:
        pass
    else:
      if (code == 2):
        return False, 2
      else:
        continue

  # Commit session data.
  model.Session.commit()

  # Close the file object.
  open_f.close()
  return True, 0

def _row_unique(row, project_id, user_id):
  try:
    labeledfeatures = Session.query(model.LabeledFeature).\
                             filter_by(term = row[0]).\
                             filter_by(label = row[1]).\
                             filter_by(project_id = project_id).\
                             filter_by(user_id = user_id).all()
  except IndexError, e:
    return False, 2

  if labeledfeatures:
    return False, 0
  else:
    return True, 0