import csv
import datetime
import abstrackr.model as model # for access to sqlalchemy
from abstrackr.model.meta import Session

def import_terms(file_path, review, user):
  open_f = open(file_path, 'rU')
  terms = csv.reader(open_f, delimiter="\t")

  # Collect terms that we couldn't import.
  unprocessable = []

  # Ensure the header looks correct.
  if (terms.next()[0] != 'term'):
    unprocessable.append("Missing header. You need 2 columns with headers: \"term\" and \"label\"")
    return False, 1, unprocessable

  # Iterate through each row and insert terms and their labels.
  for row in terms:
    try:
      term = row[0]
      label = int(row[1])
    except IndexError, e:
      # Maybe label is missing in this row or more likely the row is blank.
      continue
    except ValueError, e:
      # label might not be a number.
      continue

    # We should check that the row is conforming to things we need such as:
    #   1. The label numerical and one of -2, -1, 1, 2
    if not label in [-2, -1, 1, 2]:
      # Skip over row with invalid labels
      continue

    print(row)
    unique, code = _row_unique(row, review.id, user.id)

    if (unique):
      try:
        labeledfeature = model.LabeledFeature()
        labeledfeature.term = term
        labeledfeature.project_id = review.id
        labeledfeature.user_id = user.id
        labeledfeature.label = label
        labeledfeature.date_created = datetime.datetime.now()
        model.Session.add(labeledfeature)
      except IndexError, e:
        return False, 2, unprocessable
      except Exception, e:
        print("-- WARNING -- : Unable to process: %s " % row)
        print("Error stack %s" % e)
        unprocessable.append(row)
        continue
    else:
      if (code == 2):
        return False, 2, unprocessable
      else:
        continue

  # Commit session data.
  model.Session.commit()

  # Close the file object.
  open_f.close()
  return True, 0, unprocessable

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
