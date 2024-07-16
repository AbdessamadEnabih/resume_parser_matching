import os
import re
from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_contact_number_from_resume(text):
    # Use regex pattern to find a potential contact number
    pattern = r"(?:\+212|06|07)([ -]?\d){9}"
    return match.group() if (match := re.search(pattern, text)) else None

def extract_email_from_resume(text):
    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    return match.group() if (match := re.search(pattern, text)) else None

def extract_skills_from_resume(text, skills_list):
    skills = []

    for skill in skills_list:
        pattern = f"\b{re.escape(skill)}\b"
        if match := re.search(pattern, text, re.IGNORECASE):
            skills.append(skill)

    return skills

def extract_education_from_resume(text):
    # Use regex pattern to find education information
    pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]

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
    resume_directory = "./resumes"

    # List all files in the directory
    resume_files = [os.path.join(resume_directory, f) for f in os.listdir(resume_directory)]

    for resume_path in resume_files:
        text = extract_text_from_pdf(resume_path)

        print("Resume:", resume_path)

        if name := extract_name(text):
            print("Name:", name)
        else:
            print("Name not found")

        if contact_number := extract_contact_number_from_resume(text):
            print("Contact Number:", contact_number)
        else:
            print("Contact Number not found")

        if email := extract_email_from_resume(text):
            print("Email:", email)
        else:
            print("Email not found")

        skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL', 'Tableau']
        if extracted_skills := extract_skills_from_resume(text, skills_list):
            print("Skills:", extracted_skills)
        else:
            print("No skills found")

        if extracted_education := extract_education_from_resume(text):
            print("Education:", extracted_education)
        else:
            print("No education information found")

        print()
