import openai
import pytesseract
from PIL import Image
from pdfminer.high_level import extract_text
from datetime import datetime
import json

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
    You are given a resume text. Your task is to extract relevant data from the text and provide a structured output. Please follow the guidelines below:

    Extract the following information and if a field is empty or not present, assign it a value of null:
    - `firstName`: first name of the person.
    - `lasttName`: last name of the person.
    - `current_position`: The current job title or position of the person. Do not include the company name.
    - `civilite`: gender of the person, return "homme" for male and "femme" for female based on the first name.
    - `phone_number`: Phone number.
    - `age`: The age of the person, or calculate it from the date of birth if available(e.g. , "01 January 1987", "05/12/2003" , "04-04-2001") using the current date ({current_date}).
    - `email`: Email address.
    - `address`: Physical address.
    - `url`: URL if present.
    - `personalProfile`: A brief professional summary.
    - `experience`: A list of previous job experiences, each containing:
        - `job_title`: Title of the job.
        - `company_name`: Name of the company.
        - `dateStart`: Start date of employment.
        - `dateEnd`: End date of employment. If the end date is not available or indicated as "en cours", "now", or similar, use "Present".
        - `nbrMonths`: Number of months spent in this experience(to be calculated).
        - `missions`: Key responsibilities and achievements.
        - `technologies`: Technologies used in each mission.
        -`total_experience`: Calculate the total experince across all jobs,each containing :
           - `total_years`: Number of years spend in all experiences (to be calculated and never null)
           - `remaining_months`: Number of months remaining after accounting for complete years (to be calculated and never null).
    - `projects`: A list of projects, each containing:
        - `project`: Name of the project.
        - `description`: Brief description of the project.
        - `technologies`: Technologies used in the project.
    - `education`: A list of educational qualifications, each containing:
        - `degree_type`: Type of the degree.
        - `degree_name`: Name of the degree.
        - `institution`: Name of the educational institution.
        - `dateStart`: Start date of study.
        - `dateEnd`: End date of study. If currently studying, indicate it.
     - `skills`: A list of professional skills, divided into:
        - `hard_skills`: Technical skills, ignore category keywords such as "programming", "development languages", "frameworks", etc., and extract only the skills.
        - `soft_skills`: Non-technical skills such as communication, teamwork, leadership, etc.  - `certifications`: A list of certifications, each containing:
    - `certification`: List of certifications, each containing :
        - `certificationName`: Name of the institution.
        - `institution`: Name of the institution.
        - `year_obtained`: Year of obtaining the certification.
    - `languages`: A list of languages spoken and levels, each containing:
        - `language`: Name of the language.
        - `level`: level of the language. 
    - `interests`: A list of personal interests or hobbies.
    
    all the extracted data should be based on the language of the resume, if its in french return the extracted data in it etc...
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
