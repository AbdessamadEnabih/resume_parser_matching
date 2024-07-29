from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
import extractDataFromResume
import os
import json
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse
from .models import (
    Experience,
    Project,
    Education,
    SkillSet,
    Certification,
    Language,
    CVResponse
)

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

@app.post("/upload/", response_model=CVResponse)
async def upload_cv(file: UploadFile = File(...)):
    print("Execution de la methode post")
    file_location = f"resumes/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    try:
        extracted_text = extractDataFromResume.extract_text_from_pdf(file_location)
        prompt_text = extractDataFromResume.construct_prompt(extracted_text)
        gpt_response = extractDataFromResume.send_prompt_to_gpt(prompt_text)

        if gpt_response:
            data = json.loads(gpt_response)
            if 'experience' in data:
                data['experience'], total_years, remaining_months = extractDataFromResume.add_months_to_experiences(data['experience'])
                for exp in data['experience']:
                    exp['total_experience'] = {
                        'total_years': total_years,
                        'remaining_months': remaining_months
                    }
                cv_response = CVResponse(
                    firstName=data.get('firstName', ''),
                    lastName=data.get('lastName', ''),
                    current_position=data.get('current_position', ''),
                    civilite=data.get('civilite', ''),
                    phone_number=data.get('phone_number', ''),
                    age=data.get('age', 0),
                    email=data.get('email', ''),
                    address=data.get('address', ''),
                    url=data.get('url', ''),
                    personalProfile=data.get('personalProfile', ''),
                    experience=[Experience(**exp) for exp in data.get('experience', [])],
                    projects=[Project(**proj) for proj in data.get('projects', [])],
                    education=[Education(**edu) for edu in data.get('education', [])],
                    skills=SkillSet(**data.get('skills', {'hard_skills': [], 'soft_skills': []})),
                    certifications=[Certification(**cert) for cert in data.get('certifications', [])],
                    languages=[Language(**lang) for lang in data.get('languages', [])],
                    interests=data.get('interests', [])
                )
                return cv_response
    except Exception as e:
        return JSONResponse(content={"error": "An error occurred while processing the file."}, status_code=500)
    finally:
        os.remove(file_location)
@app.get("/")
async def home():
    return {"message":"Welcome to Cvtheque"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
