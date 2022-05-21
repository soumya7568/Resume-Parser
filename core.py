import fitz
import sys
import docx2txt
import re
import os
import pandas as pd
import spacy


en = spacy.load('en_core_web_sm')
stopwords = set(en.Defaults.stop_words)

YEAR = r'(((20|19)(\d{2})))'
EDUCATION = ['BE','B.E.', 'B.E', 'BS', 'B.S','C.A.','c.a.','B.Com','B. Com','M. Com', 'M.Com','M. Com .',
            'ME', 'M.E', 'M.E.', 'MS', 'M.S','12th','10th',
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
            'PHD', 'phd', 'ph.d', 'Ph.D.','MBA','mba','graduate', 'post-graduate','5 year integrated masters','masters',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII']

def extract_text_pdf(file):
    fname = file
    text = ''
    doc = fitz.open(fname)
    for page in doc:
        text+=str(page.get_text())
    tx = ''.join(text.split('/n'))
    return tx

def extract_text_doc(file):
    temp = docx2txt.process(file)
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    return ' '.join(text)

def extract_text(file,ext):
    if ext=='.pdf':
        text  = extract_text_pdf(file)
    else:
        text = extract_text_doc(file)
    return text

def extract_name(doc,matcher):
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('NAME',[pattern])
    matches = matcher(doc)
    
    for match_id,start ,end in matches:
        span = doc[start:end]
        return span

def extract_email(text):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

def extract_mobile(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

def extract_skills(doc,noun_chunks):
    tokens = [token.text for token in doc if not token.is_stop]
    data = pd.read_csv('skills.csv')
    skills = list(data.columns.values)
    skillset = []
    #for one grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

def extract_education(doc):
    edu = {}
    for index, text in enumerate(doc):
        for tex in text.split():
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in stopwords:
                edu[tex] = text + doc[index + 1]

    education = []
    for key in edu.keys():
        year = re.search(re.compile(YEAR), edu[key])
        if year:
            education.append((key, ''.join(year.group(0))))
        else:
            education.append(key)
    return education

