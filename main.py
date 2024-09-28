from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import extractDataFromResume
import os
import json
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import JSONResponse
from models import Experience, Education, Skills, Certification, CVResponse
from repositories.repositoryOffre import get_offre,getAllOffres
from repositories.repositoryCandidat import get_candidats,get_candidatById
from datetime import datetime, timedelta
from matchingTest import get_dict_offre,faire_matching,faire_matching_candidat
from database import get_db

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
    file_location = f"resumes/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    try:
        extension = os.path.splitext(file.filename)[1].lower()
        if extension == '.pdf':
            extracted_text = extractDataFromResume.extract_text_from_pdf(file_location)
        else :
            extracted_text = extractDataFromResume.extract_text_from_word(file_location)        
        prompt_text = extractDataFromResume.construct_prompt(extracted_text)
        gpt_response = extractDataFromResume.send_prompt_to_gpt(prompt_text) 
        logging.info(f" \n GPT Response \n : {gpt_response}") 
        
        if "Le fichier n'est pas un CV." in gpt_response:
            return JSONResponse(content={"error": "Le fichier n'est pas un CV."}, status_code=403)
        
        error_messages = [
            "Vous avez dépassé votre quota actuel. Veuillez vérifier votre plan et vos détails de facturation.",
            "Clé API expirée ou inexistante. Veuillez vérifier votre clé API.",
            "Requête invalide. Veuillez vérifier les paramètres d'entrée.",
            "Une erreur inattendue s'est produite lors de la connexion à OpenAI. Veuillez vérifier votre connexion.",
            "Une erreur inattendue s'est produite."
        ]  
        if gpt_response in error_messages:
            status_code = 401 if "Clé API" in gpt_response else 400
            return JSONResponse(content={"error": gpt_response}, status_code=status_code)    
        try:
            gpt_response_cleaned = gpt_response.strip().replace("```json", "").replace("```", "")
            gpt_response_dict = json.loads(gpt_response_cleaned)
        except json.JSONDecodeError as e:
            return JSONResponse(content={"error": "Réponse JSON invalide de GPT."}, status_code=500)
        response = CVResponse(**gpt_response_dict) 
        return response
    except Exception as e:
        logging.error(f"une erreur s'est produite : {str(e)}")
        return JSONResponse(content={"error": "Une erreur s'est produite lors du traitement du fichier. Veuillez réessayer"}, status_code=500)
    finally:
        os.remove(file_location)
@app.get("/")
async def home():
    return {"message":"Welcome to Cvtheque"}

@app.post("/processOffre/{idOffre}")
async def processOffre(idOffre: str, db : Session = Depends(get_db)):
    offre = get_offre(idOffre,db) 
    if offre is None:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    results = faire_matching(offre,db)    
    return {"message": "Matching effectué", "results": results}
    
  
@app.post("/matchOffreCandidat/{idOffre}/{idCandidat}")
async def match_offre_candidat(idOffre:str,idCandidat:str, db:Session = Depends(get_db)):
    offre = get_offre(idOffre,db)
    candidat = get_candidatById(idCandidat,db)
    # Vérification si l'offre et le candidat existent
    if offre is None:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    if candidat is None:
        raise HTTPException(status_code=404, detail="Candidat non trouvé")
    return faire_matching_candidat(offre,candidat,db)
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000) 