import openai
import pytesseract
from PIL import Image
from pdfminer.high_level import extract_text
from datetime import datetime
import json
from docx import Document
import os
import mammoth
import mysql.connector


# Récuperation des competences Operationnelles de la bdd
def get_competences_from_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="cvtheque"
        )
        cursor = conn.cursor()

        # Extraction des compétences opérationnelles
        cursor.execute("SELECT competenceOperationnelle FROM competenceoperationnelle")
        competences = cursor.fetchall()

        # Convertir la liste de tuples en une liste de chaînes
        competences_list = [comp[0] for comp in competences]

        return competences_list

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
      
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Erreur c'est produite lors de l'extraction du pdf: {e}")
        return None
    

    
def extract_text_from_word(word_path):
    if not os.path.isfile(word_path):
        return None
    
    try:
        with open(word_path, "rb") as docx_file:
            result = mammoth.extract_raw_text(docx_file)
            text = result.value
            return text
    except Exception as e:
        print(f"Erreur s'est produite lors de l'extraction du document Word avec mammoth: {e}")
        return None

   
def construct_prompt(extracted_text):
    current_date = datetime.today().strftime("%d-%m-%Y")
    
    return f"""
    You are given a document. Your first task is to determine with high accuracy if the document is indeed a resume/CV. A resume/CV is a document specifically structured to summarize a person’s professional background, skills, and qualifications for employment purposes. It typically includes the following key sections:

    - **Contact Information**: This usually appears at the top and includes the candidate's name, phone number, email address, and sometimes their physical address and LinkedIn profile or portfolio URL.
    - **Professional Summary**: A brief overview of the candidate's professional background, often in 2-3 sentences.
    - **Work Experience**: This section lists previous job experiences in reverse chronological order, detailing job titles, company names, dates of employment, and key responsibilities or achievements. Accurately calculate the number of months (`nbrMonths`) between `dateStart` and `dateEnd` for each job experience.
    - **Education**: Information about the candidate's educational background, including degrees, institutions, and dates of study.
    - **Skills**: A list of relevant skills, often divided into hard skills (technical skills) and soft skills (interpersonal or organizational skills). Extract technologies separately from hard skills and categorize them appropriately.
    - **Certifications**: Details of any certifications the candidate has obtained, including the certification name, issuing organization, and date obtained.
    - **Languages**: A list of languages spoken by the candidate.
    - **Interests**: Optional, includes hobbies or interests relevant to the job.

    **IMPORTANT**: A resume/CV is typically formatted with bullet points, headings, and short, concise phrases. It is a professional document aimed at employers and should not contain long narrative paragraphs, personal opinions, or detailed project descriptions that are more common in reports or cover letters.

    **Examples of what is NOT a resume/CV:**
    - A **report** that provides detailed findings or analysis on a specific topic, often with sections like Introduction, Methodology, Results, and Conclusion.
    - A **cover letter** that is a narrative letter explaining the reasons for applying to a job, usually addressed to a specific person or company.
    - An **essay** or **personal statement** that provides detailed personal reflections or opinions on a topic.

    **INSTRUCTIONS**:
    - **You must strictly follow the instructions below.**
    - **DO NOT include any introductory phrases, explanations, or any other text.**
    - **ONLY return the JSON data as specified.**
    - **Including any additional text or commentary is STRICTLY FORBIDDEN.**
    - Ensure that the JSON is well-formed and follows the format provided below.
    - If any value is missing, provide a default value as instructed.
    - Ensure that all keys and string values are enclosed in double quotes.

    If the document is not a resume/CV, return the message: "Le fichier n'est pas un CV."

    If the document is a resume/CV, extract the following information and if a field is empty or not present, assign it a default value:
    - `firstName`: First name of the person. If not present, use an empty string "".
    - `lastName`: Last name of the person. If not present, use an empty string "".
    - `current_position`: The current job title or position of the person. Convert any feminine job titles to their masculine equivalents (e.g., "ingénieure" to "ingénieur", "développeuse" to "développeur", "vendeuse" to "vendeur"). Extract only the core job title and exclude any  technologies or company names (e.g., "Manager des ventes chez XYZ" should be returned as "Manager", "Consultant SAP HANA" should be returned as "Consultant SAP"). If not present, use an empty string "".
    - `civilite`: Gender of the person, return "Monsieur" for male and "Madame" for female based on the first name. If not determinable, use an empty string "".
    - `phone_number`: Phone number. If not present, use an empty string "".
    - `email`: Email address. If not present, use an empty string "".
    - `address`: Physical address. If not present, use an empty string "".
    - `url`: URL if present. If not present, use an empty string "".
    - `personalProfile`: A brief professional summary. If not present, use an empty string "".
    - `experience`: A list of previous job experiences, each containing:
        - `job_title`: Title of the job. If not present, use an empty string "".
        - `company_name`: Name of the company. If not present, use an empty string "".
        - `dateStart`: Start date of employment in the format "Month Year" (e.g., "Janvier 2024", "Septembre 2022"). Ensure that this format is strictly followed. If the date is provided in a different format (e.g., "MM/YYYY", "YYYY"), automatically convert it to "Month Year", defaulting to "Janvier" if only the year is provided (e.g., "2021" becomes "Janvier 2021"). If not present, use an empty string "".
        - `dateEnd`: End date of employment in the format "Month Year" (e.g., "Janvier 2024", "Present" if currently employed). Ensure that this format is strictly followed. If the date is provided in a different format (e.g., "MM/YYYY", "YYYY"), automatically convert it to "Month Year", defaulting to "Janvier" if only the year is provided (e.g., "2023" becomes "Janvier 2023"). If not present or if currently employed, use "Present".
        - **Accurately calculate `nbrMonths`:** The number of months between `dateStart` and `dateEnd`. If not available, use 0.
        - `missions`: Key responsibilities and achievements. If not present, use an empty list [].
        - `technologies`: Technologies used in each mission. Extract technologies separately from hard skills and include them here. If not present, use an empty list [].
    - `education`: A list of educational qualifications, each containing:
        - `degree_type`: Type of the degree. Accurately identify and extract the degree type, paying close attention to variations in how degree types might be written or abbreviated. Common examples include "Doctorat", "Baccalauréat", "Licence professionnelle", "Licence fondamentale", "Master", "Diplôme d'ingénieur", "DEUG", "BTS", "DUT", "Bac Pro", but the list is not exhaustive. The model should understand the context and recognize equivalent terms or variations. If not present, use an empty string "".
        - `degree_name`: Name of the degree. Generally, but not always, the degree name follows the degree type in the text. The model should identify and accurately extract the specific name associated with the degree, even if it appears in a different position. For example:
           - In "Master en Informatique", extract "Informatique" as the `degree_name`
           - In "Licence professionnelle en Gestion des entreprises", extract "Gestion des entreprises" as the `degree_name`.
           If not present, use an empty string "".    
          - `institution`: Name of the educational institution. If not present, use an empty string "".
        - `dateStart`: Start date of study. If not present, use an empty string "".
        - `dateEnd`: End date of study. If not present or if currently studying, use an empty string "".
    - `skills`: A list of professional skills, divided into:
        - `hard_skills`: Technical skills directly related to the job. Extract only the technologies and ignore any associated categories. For example, if the text mentions "Langages de programmation: Java, Python, C++", "Frameworks: Angular, React", or "Bases de données: MySQL, PostgreSQL", extract only "Java", "Python", "C++", "Angular", "React", "MySQL", "PostgreSQL" as the `hard_skills`, neglecting the categories like "Langages de programmation", "Frameworks", or "Bases de données". If not present, use an empty list [].
        - `soft_skills`: Non-technical skills. If not present, use an empty list [].
    - `competences_operationnelles`: Dynamically categorize the hard skills into the appropriate operational competencies based on the following categories:
        - **Langage de développement**: Include programming languages such as Java, C, Python, etc.
        - **Framework**: Include frameworks like Spring Boot, Angular, React, Bootstrap, etc.
        - **Systèmes d'exploitation**: Include operating systems like Linux, Windows, etc.
        - **Base de données**: Include databases like MySQL, PostgreSQL, etc.
        - **Méthodologies**: Include methodologies such as Agile, Scrum, etc.
        - **IDE**: Include development environments like Eclipse, IntelliJ, etc.
        - **Bureautique**: Include tools like Excel, Word, PowerPoint, etc.
        - **Autres**: For skills that do not fall under any of the predefined categories, first attempt to dynamically create a new, logical category (e.g., **Big Data**, **Modélisation**, **Cloud Computing**). Only if no such category can be determined, group all uncategorized skills under "Autres" and ensure it appears only once.
           Return the categorized operational competencies as a flat list in the form:
        "competences_operationnelles": ["Langage de développement", "Framework", "Systèmes d'exploitation", "Base de données", "Autres"]
    - `certifications`: A list of certifications, each containing:
        - `certification_name`: Name of the certification. If not present, use an empty string "".
        - `institution`: Name of the institution. If not present, use an empty string "".
        - `year_obtained`: Year of obtaining the certification. If not present, use an empty string "".
        - `type`: Type of the certification (e.g., Java, Project Management, PHP). If not present, use an empty string "".
    - `languages`: A list of languages spoken. If not present, use an empty list [].
    - `interests`: A list of personal interests or hobbies. If not present, use an empty list [].

    **FINAL INSTRUCTION**: If you are not completely sure that the document is a resume/CV, err on the side of caution and return the message "Le fichier n'est pas un CV."

    Please return the extracted data in the following JSON format without any introductory phrase:

    {{
        "firstName": "value",
        "lastName": "value",
        "current_position": "value",
        "civilite": "value",
        "phone_number": "value",
        "email": "value",
        "address": "value",
        "url": "value",
        "personalProfile": "value",
        "experience": [
            {{
                "job_title": "value",
                "company_name": "value",
                "dateStart": "value",
                "dateEnd": "value",
                "nbrMonths": value,
                "missions": ["value"],
                "technologies": ["value"]
            }}
        ],
        "education": [
            {{
                "degree_type": "value",
                "degree_name": "value",
                "institution": "value",
                "dateStart": "value",
                "dateEnd": "value"
            }}
        ],
        "skills": {{
            "hard_skills": ["value"],
            "soft_skills": ["value"]
        }},
        "competences_operationnelles": ["value"],
        "certifications": [
            {{
                "certification_name": "value",
                "institution": "value",
                "year_obtained": "value",
                "type": "value"
            }}
        ],
        "languages": ["value"],
        "interests": ["value"]
    }}

    Resume text:
    {extracted_text}
    """

def send_prompt_to_gpt(prompt_text):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_text},
    ]
    openai.api_key = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=conversation,
        )
        return (response["choices"][0]["message"]["content"])
    
    except openai.error.RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        return "Vous avez dépassé votre quota actuel. Veuillez vérifier votre plan et vos détails de facturation."
    except openai.error.AuthenticationError as e:
        return "Clé API expirée ou inexistante. Veuillez vérifier votre clé API."
    except openai.error.InvalidRequestError as e:
        return "Requête invalide. Veuillez vérifier les paramètres d'entrée."  
    except openai.error.OpenAIError as e:
        return "Une erreur inattendue s'est produite lors de la connexion à OpenAI. Veuillez vérifier votre connexion."
    except Exception as e:
        return "Une erreur inattendue s'est produite."
    
def calculate_months_between_dates(date_start, date_end):
    start_date = datetime.strptime(date_start, '%B %Y')
    end_date = datetime.strptime(date_end, '%B %Y') if date_end.lower() not in ['present','Present','Présent' 'now', 'current', 'en cours'] else datetime.today()
    months_diff = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month 
    return months_diff

def add_months_to_experiences(experiences):
    total_experience_months = 0
    for experience in experiences:
        date_start = experience.get('dateStart')
        date_end = experience.get('dateEnd')
        
        if date_start and date_end:
            if date_end.lower() in  ['present','Present','Présent' 'now', 'current', 'en cours']:
                date_end = datetime.today().strftime('%B %Y')
                experience['dateEnd'] = 'Present'
            experience['nbrMonths'] = calculate_months_between_dates(date_start, date_end)
        else:
            experience['nbrMonths'] = 0

        total_experience_months += experience['nbrMonths']

    total_years, remaining_months = convert_months_to_years_and_months(total_experience_months)

    return experiences, total_years, remaining_months

def convert_months_to_years_and_months(total_months):
    total_years = total_months // 12
    remaining_months = total_months % 12
    return total_years, remaining_months

 