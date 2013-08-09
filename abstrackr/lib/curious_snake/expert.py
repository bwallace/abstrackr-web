class Expert:
    
    def __init__(self, alpha, cost, name="", lbl_d=None):
        self.alpha = alpha
        self.cost = cost
        self.lbl_d = lbl_d
        self.name = name
        
    def get_label(self, doc_id):
        if lbl_d is not None and lbl_d.has_key(doc_id):
            return lbl_d[doc_id]
        raise Exception, "Either no label dictionary has been provided or the label dictionary doesn't have a value for %s" % doc_id