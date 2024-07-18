import openai
import pytesseract
from PIL import Image
from pdfminer.high_level import extract_text


def extract_text_from_image(path):
    """
    Extract text from an image using pytesseract.
    """
    try:
        return extract_text(path, codec='utf-8')
    except Exception as e:
        print(f"An error occurred while extracting text from image: {e}")
        return None


def construct_prompt(extracted_text):
    """
    Construct a prompt to extract structured data from the resume text.
    """
    return f"""
    You are given a resume text. Your task is to extract relevant data from the text and provide a structured output. Please follow the guidelines below:

    Extract the following information:
    - `name`: Full name of the person.
    - `contact_information`: Contact details including phone number, email address, and address.
    - `summary`: A brief professional summary.
    - `experience`: A list of previous job experiences, each containing:
        - `job_title`: Title of the job.
        - `company_name`: Name of the company.
        - `dates`: Duration of employment.
        - `responsibilities`: Key responsibilities and achievements.
    - `education`: A list of educational qualifications, each containing:
        - `degree`: Name of the degree.
        - `institution`: Name of the educational institution.
        - `dates`: Duration of study.
    - `skills`: A list of professional skills.
    - `certifications`: A list of certifications, if any.
    - `languages`: Languages spoken and proficiency levels.
    
    all the extracted data should be based on the language of the resume, if its in french return the extracted data in it etc...
    Resume text:
    {extracted_text}
    """


def send_prompt_to_gpt(prompt_text):
    """
    Send the constructed prompt to GPT-4 and print the response.
    """
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_text},
    ]

    # Adjust the API key setting according to your preferred method (directly in code or via environment variable)
    openai.api_key = ""

    try:
        # Use the v1/chat/completions endpoint
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation,
        )
        print(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
if __name__ == "__main__":
    resume_path = ""

    if extracted_text := extract_text_from_image(resume_path):
        # Step 2: Construct the prompt
        prompt_text = construct_prompt(extracted_text)

        # Step 3: Send the prompt to GPT-4 and get the structured data
        send_prompt_to_gpt(prompt_text)
