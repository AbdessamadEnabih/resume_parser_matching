from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Entities.Offre import Offre
from matchingTest import get_dict_offre
from database import get_db

DATABASE_URL = 'mysql+pymysql://root:admin@localhost:3306/cvtheque'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_offre(offre_id,db:Session):
    try:
        offre = db.query(Offre).options(
            joinedload(Offre.langues),
            joinedload(Offre.technologies),
            joinedload(Offre.competences_operationnelles)
        ).filter(Offre.idoffre == offre_id).first()

        return offre
    finally:
        db.close()

def getAllOffres(db:Session):
    try:
        offres = db.query(Offre).options(
            joinedload(Offre.langues),
            joinedload(Offre.technologies),
            joinedload(Offre.competences_operationnelles)
        ).all()
        return offres
    except Exception as e:
        return []
    
    
