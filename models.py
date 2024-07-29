from pydantic import BaseModel
from typing import List, Dict, Any

class Experience(BaseModel):
    job_title: str = None
    company_name: str = None
    dateStart: str = None
    dateEnd: str = None
    nbrMonths: int = None
    missions: str = None
    technologies: List[str] = []
    total_experience: Dict[str, int] = {}

class Project(BaseModel):
    project: str = None
    description: str = None
    technologies: List[str] = []

class Education(BaseModel):
    degree_type: str = None
    degree_name: str = None
    institution: str = None
    dateStart: str = None
    dateEnd: str = None

class SkillSet(BaseModel):
    hard_skills: List[str] = []
    soft_skills: List[str] = []

class Certification(BaseModel):
    certification_name: str = None
    institution: str = None
    year_obtained: str = None

class Language(BaseModel):
    language: str = None
    level: str = None

class CVResponse(BaseModel):
    firstName: str = None
    lastName: str = None
    current_position: str = None
    civilite: str = None
    phone_number: str = None
    age: int = None
    email: str = None
    address: str = None
