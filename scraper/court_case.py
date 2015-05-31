__author__ = 'n'

class CourtCase:
    def __init__(self):
        self.link = ''
        self.decision_number = ''
        self.text = ''
        self.reg_date = ''
        self.law_date = ''
        self.case_number = ''
        self.court_name = ''
        self.cs_type = ''
        self.vr_type = ''
        self.chairman = ''

    def from_dict(self, dictionary):
        self.decision_number = dictionary['Decision']
        self.link = dictionary['Link']
        self.reg_date = dictionary['LawDate']
        self.law_date = dictionary['LawDate']
        self.case_number = dictionary['CaseNumber']
        self.court_name = dictionary['CourtName']
        self.cs_type = dictionary['CSType']
        self.vr_type = dictionary['VRType']
        self.chairman = dictionary['ChairmanName']
        self.text = dictionary['Text']
        return self

    def __str__(self):
        return self.link + ' ' + self.chairman + ' ' + self.reg_date
