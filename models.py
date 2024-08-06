import ast
import json
from typing import List, Optional
from pydantic import BaseModel, Field

class Experience(BaseModel):
    job_title: str = ""
    company_name: str = ""
    dateStart: str = ""
    dateEnd: str = ""
    nbrMonths: Optional[int] = None
    missions: List[str] = []
    technologies: Optional[List[str]] = None

class Education(BaseModel):
    degree_type: str = ""
    degree_name: str = ""
    institution: str = ""
    dateStart: Optional[str] = None
    dateEnd: str = ""

class Skills(BaseModel):
    hard_skills: List[str] = []
    soft_skills: List[str] = []

class Certifications(BaseModel):
    certificationName: str = ""
    institution: str = ""
    year_obtained: str = ""

class CVResponse(BaseModel):
    firstName: str = ""
    lastName: str = ""
    current_position: str = ""
    civilite: str = ""
    phone_number: str = ""
    age: int = 0
    email: str = ""
    address: str = ""
    url: Optional[str] = None
    personalProfile: Optional[str] = None
    experience: List[Experience] = []
    education: List[Education] = []
    skills: Skills = Skills()
    certifications: List[Certifications] = []
    languages: List[str] = []
    interests: List[str] = []

    class Config:
        arbitrary_types_allowed = True
