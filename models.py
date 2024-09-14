import ast
import json
from typing import List, Optional
from pydantic import BaseModel, Field
class Experience(BaseModel):
    job_title: str = ""
    company_name: str = ""
    dateStart: str = ""
    dateEnd: str = ""
    nbrMonths: Optional[int] = 0
    missions: List[str] = []
    technologies: List[str] = []  # Changer de Optional[List[str]] à List[str]

class Education(BaseModel):
    degree_type: str = ""
    degree_name: str = ""
    institution: str = ""
    dateStart: str = ""  
    dateEnd: str = ""

class Skills(BaseModel):
    hard_skills: List[str] = []
    soft_skills: List[str] = []

class Certification(BaseModel):
    certification_name: str = ""
    institution: str = ""
    year_obtained: str = ""
    type: str = ""

class CVResponse(BaseModel):
    firstName: str = ""
    lastName: str = ""
    current_position: str = ""
    civilite: str = ""
    phone_number: str = ""
    email: str = ""
    address: str = ""
    url: Optional[str] = ""  # Garder Optional mais avec valeur par défaut vide
    personalProfile: Optional[str] = ""  # Garder Optional mais avec valeur par défaut vide
    experience: List[Experience] = []
    education: List[Education] = []
    skills: Skills = Skills()
    competences_operationnelles: List[str] = []
    certifications: List[Certification] = []
    languages: List[str] = []
    interests: List[str] = []

    class Config:
        arbitrary_types_allowed = True