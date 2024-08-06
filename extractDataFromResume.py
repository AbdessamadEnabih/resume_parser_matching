import openai
import pytesseract
from PIL import Image
from pdfminer.high_level import extract_text
from datetime import datetime
import json
import ast
import re
#Ajout d'une méthode qui extrait le texte du word !!!
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Erreur c'est produite lors de l'extraction du pdf: {e}")
        return None


def construct_prompt(extracted_text):
    current_date = datetime.today().strftime("%d-%m-%Y")
    return f"""
    You are given a resume text. Your task is to extract relevant data from the text and provide a structured output in JSON format. Please follow the guidelines below:

    Extract the following information and if a field is empty or not present, assign it a value of None:
    - `firstName`: First name of the person.
    - `lastName`: Last name of the person.
    - `current_position`: The current job title or position of the person. Do not include the company name.
    - `civilite`: Gender of the person, return "Monsieur" for male and "Madame" for female based on the first name.
    - `phone_number`: Phone number.
    - `age`: The age of the person, or calculate it from the date of birth if available (e.g., "01 January 1987", "05/12/2003", "04-04-2001") using the current date ({current_date}).
    - `email`: Email address.
    - `address`: Physical address.
    - `url`: URL if present.
    - `personalProfile`: A brief professional summary.
    - `experience`: A list of previous job experiences, each containing:
        - `job_title`: Title of the job.
        - `company_name`: Name of the company.
        - `dateStart`: Start date of employment (e.g., "April 2024","Novembre 2023","07/2024","06-24").
        - `dateEnd`: End date of employment (e.g., "September 2024","Janvier 2024", "06/2024"). If the end date is not available or indicated as "en cours", "now", or similar, use "Present".
        - `nbrMonths`: Number of months spent in this experience, calculated from `dateStart` to `dateEnd`. If the end date is "Present", calculate up to the current date ({current_date}).
        - `missions`: Key responsibilities and achievements.
        - `technologies`: Technologies used in each mission.
    - `education`: A list of educational qualifications, each containing:
        - `degree_type`: Type of the degree.
        - `degree_name`: Name of the degree.
        - `institution`: Name of the educational institution.
        - `dateStart`: Start date of study.
        - `dateEnd`: End date of study. If currently studying, indicate it.
    - `skills`: A list of professional skills, divided into:
        - `hard_skills`: Technical skills, ignore category keywords such as "programming", "development languages", "frameworks", etc., and extract only the skills.
        - `soft_skills`: Non-technical skills such as communication, teamwork, leadership, etc.
    - `certifications`: A list of certifications, each containing:
        - `certificationName`: Name of the certification.
        - `institution`: Name of the institution.
        - `year_obtained`: Year of obtaining the certification.
    - `languages`: A list of languages spoken, each containing:
        - `language`: Name of the language.
    - `interests`: A list of personal interests or hobbies.
    
    Please return the extracted data in the following JSON format:

    {{
        "firstName": "value",
        "lastName": "value",
        "current_position": "value",
        "civilite": "value",
        "phone_number": "value",
        "age": value,
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
        "certifications": [
            {{
                "certificationName": "value",
                "institution": "value",
                "year_obtained": "value"
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
            model="gpt-4",
            messages=conversation,
        )
        return (response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"une erreur s'est produite: {e}")
        return None

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
def validate_and_correct_json(json_data):
    """
    Valide et corrige les types de données dans le JSON.
    """

    # Fonction de validation récursive
    def correct_types(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.lower() == "none":
                    data[key] = None
                elif isinstance(value, list):
                    data[key] = correct_types(value)
                elif isinstance(value, dict):
                    data[key] = correct_types(value)
        elif isinstance(data, list):
            return [correct_types(item) for item in data]
        return data

    try:
        data = json.loads(json_data)
        data = correct_types(data)
        return json.dumps(data, indent=4)
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return None