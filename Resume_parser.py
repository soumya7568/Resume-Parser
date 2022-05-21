from core import *
import os
import spacy
from spacy.matcher import Matcher

class Resume_Pars:
    def __init__(self,resume):
        nlp = spacy.load('en_core_web_sm')
        self.matcher = Matcher(nlp.vocab)
        self.details = {
            'name'              : None,
            'email'             : None,
            'mobile_number'     : None,
            'skills'            : None,
            'eduaction'         : None
        }
        self.resume_ = resume
        self.rawtext = extract_text(self.resume_,os.path.splitext(self.resume_)[1])
        self.text = ' '.join(self.rawtext.split())
        self.doc = nlp(self.text)
        self.noun_chunks = list(self.doc.noun_chunks)
        self.get_basic_details()
    
    def extracted_data(self):
        return self.details

    def get_basic_details(self):
        name = extract_name(self.doc,self.matcher)
        email = extract_email(self.text)
        mobile = extract_mobile(self.text)
        skills = extract_skills(self.doc,self.noun_chunks)
        education = extract_education(list(sent.text.strip() for sent in self.doc.sents))
        self.details['name'] = name
        self.details['email'] = email
        self.details['mobile_number'] = mobile
        self.details['skills'] = skills
        self.details['education'] = education
        return

def result(resume):
    parsed = Resume_Pars(resume)
    print(parsed.doc)
    return parsed.extracted_data()

ans = result('test/fakepdf.pdf')
print(ans)

