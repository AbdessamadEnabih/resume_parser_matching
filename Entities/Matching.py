from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import  declarative_base,relationship
import uuid

Base = declarative_base()

class Matching(Base):
    __tablename__ = 'matching'

    idmatching = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    statut = Column(String)
    score = Column(Integer)

    idcandidat = Column(String)

    idoffre = Column(String)
    
