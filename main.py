from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
import extractDataFromResume
import os
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse
from models import Experience, Education, Skills, Certifications, CVResponse

logging.basicConfig(level=logging.DEBUG)
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

if not os.path.exists('resumes'):
    os.makedirs('resumes')
"""
gpt_response1 = 
{
    "firstName": "Hiba",
    "lastName": "Tan",
    "current_position": "Developpeur Full Stack JAVA/ANGULAR",
    "civilite": "Madame",
    "phone_number": "+ 212 6 15 00 00 00 ",
    "age": 23,
    "email": "Hiba.tan@gmail.com",
    "address": "CIL, Casablanca",
    "url": "@hibatan",
    "personalProfile": None,
    "experience": [
        {
            "job_title": "Developpeur Full Stack JAVA/ANGULAR",
            "company_name": "OMNISHORE",
            "dateStart": "Avril 2024",
            "dateEnd": "Septembre 2024",
            "nbrMonths": None,
            "missions": ["Conception d’une application web de gestion de recrutement"],
            "technologies": ["JAVA", "ANGULAR"]    
        },
        {
            "job_title": "Conseillère service client",
            "company_name": "Comdata ( Engie home services )",
            "dateStart": "Novembre 2023",
            "dateEnd": "Mars 2024",
            "nbrMonths": None,
            "missions": ["Réception et traitement des appels entrants", "Prise de rendez-vous pour équipements", "Gestion des réclamations"],
            "technologies": None
        },
        {
            "job_title": "Developpeur Full Stack JAVA/ANGULAR",
            "company_name": "OMNISHORE",
            "dateStart": "Juillet 2023",
            "dateEnd": "Octobre 2023",
            "nbrMonths": None,
            "missions": ["Conception d'une application web de gestion des médias"],
            "technologies": ["SPRING BOOT", "SRING SECURITY", "ANGULAR", "MinIO", "MySQL", "GIT", "REST"]
        },
        {
            "job_title": "Developpeur Full Stack", 
            "company_name": "NCRM",
            "dateStart": "Juillet 2022",
            "dateEnd": "Septembre 2022",
            "nbrMonths": None,
            "missions": ["Conception d'une application web pour la gestion bancaire"],
            "technologies": ["SPRING BOOT", "JSP", "MySQL", "GIT"]
        }
    ],
    "education": [
        {
            "degree_type": "Diplôme d'ingénieur d'état",
            "degree_name": "Développement logiciel et technologies de l'information",
            "institution": "Institut du génie appliqué - IGA",
            "dateStart": "2022",
            "dateEnd": "2024"
        },
        {
            "degree_type": "Licence professionnelle",
            "degree_name": "Ingénierie des systèmes informatiques",
            "institution": "Institut du génie appliqué - IGA",
            "dateStart": "2019",
            "dateEnd": "2022"
        },
        {
            "degree_type": "Baccalauréat",
            "degree_name": "Science Physique",     
            "institution": "Ecole Ibn Al Yassamine",
            "dateStart": "2018",
            "dateEnd": "2019"
        }
    ],
    "skills": {
        "hard_skills": ["JAVA", "C", "VB.NET", "Python", "JS", "HTML5", "CSS", "BOOTSTRAP", "JQuery", "SQL Server", "MYSQL", "PostgreSQL", "MariaDB", "SPRING BOOT", "SRING SECURITY", "ANGULAR", "Hadoop", "Méthode Agile", "Scrum", "Merise", "UML", "GIT", "GITHUB", "Docker", "Jira", "Windows", "Linux"],    
        "soft_skills": ["Le goût du challenge", "La rigueur", "Esprit d’équipe", "Communication"]     
    },
    "certifications": [],
    "languages": ["Français", "Anglais", "Arabe"], 
    "interests": ["Natation", "Fitness et musculation", "Lecture"]
}
"""

@app.post("/upload/", response_model=CVResponse)
async def upload_cv(file: UploadFile = File(...)):
    logging.info("Execution de la methode post")
    file_location = f"resumes/{file.filename}"
    logging.info("File location")
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    try:
        extracted_text = extractDataFromResume.extract_text_from_pdf(file_location)
        prompt_text = extractDataFromResume.construct_prompt(extracted_text)
        gpt_response = extractDataFromResume.send_prompt_to_gpt(prompt_text)
       
        logging.info(f"GPT Response: {gpt_response}")
        gpt_response = gpt_response.replace('None', 'null')
        
        try:
            gpt_response1_dict = json.loads(gpt_response)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error occurred: {e}", exc_info=True)
            logging.error(f"Problematic JSON: {gpt_response}")
            return JSONResponse(content={"error": "Invalid JSON response from GPT."}, status_code=500)
        response = CVResponse(**gpt_response1_dict) 
        return response
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        return JSONResponse(content={"error": "An error occurred while processing the file."}, status_code=500)
    finally:
        os.remove(file_location)
@app.get("/")
async def home():
    return {"message":"Welcome to Cvtheque"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
