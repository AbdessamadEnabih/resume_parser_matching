import re
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_contact_number_from_resume(text):
    contact_number = None

    # Use regex pattern to find a potential contact number
    pattern = r"(?:\+212|06|07)([ -]?\d){9}"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()

    return contact_number

def extract_email_from_resume(text):
    email = None

    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()

    return email

def extract_skills_from_resume(text, skills_list):
    skills = []

    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)

    return skills

def extract_education_from_resume(text):
    education = []

    # Use regex pattern to find education information
    pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    matches = re.findall(pattern, text)
    for match in matches:
        education.append(match.strip())

    return education

def extract_name(resume_text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)

    # Define name patterns
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]  # First name, Middle name, Middle name, and Last name
        # Add more patterns as needed
    ]

    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])

    doc = nlp(resume_text)
    matches = matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text

    return None

if __name__ == '__main__':
    resume_paths = [r"resume.pdf"]

    for resume_path in resume_paths:
        text = extract_text_from_pdf(resume_path)

        print("Resume:", resume_path)

        name = extract_name(text)
        if name:
            print("Name:", name)
        else:
            print("Name not found")

        contact_number = extract_contact_number_from_resume(text)
        if contact_number:
            print("Contact Number:", contact_number)
        else:
            print("Contact Number not found")

        email = extract_email_from_resume(text)
        if email:
            print("Email:", email)
        else:
            print("Email not found")

        skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL', 'Tableau']
        extracted_skills = extract_skills_from_resume(text, skills_list)
        if extracted_skills:
            print("Skills:", extracted_skills)
        else:
            print("No skills found")

        extracted_education = extract_education_from_resume(text)
        if extracted_education:
            print("Education:", extracted_education)
        else:
            print("No education information found")

        print()
