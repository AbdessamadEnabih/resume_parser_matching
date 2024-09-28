from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
Base = declarative_base()

langue_candidat = Table(
    'languecandidat', Base.metadata,
    Column('idcandidat', String, ForeignKey('candidat.idcandidat')),
    Column('idlangue', String, ForeignKey('langue.idlangue'))
)

technologie_candidat = Table(
    'technologiecandidat', Base.metadata,
    Column('idcandidat', String, ForeignKey('candidat.idcandidat')),
    Column('idtechnologie', String, ForeignKey('technologie.idtechnologie'))
)

competence_comportementale_candidat = Table(
    'competencecomportementaleparcandidat', Base.metadata,
    Column('idcandidat', String, ForeignKey('candidat.idcandidat')),
    Column('idcompetencecomportementale', String, ForeignKey('competencecomportementale.idcompetencecomportementale'))
)

competence_operationnelle_candidat = Table(
    'competenceoperationnelleparcandidat', Base.metadata,
    Column('idcandidat', String, ForeignKey('candidat.idcandidat')),
    Column('idcompetenceoperationnelle', String, ForeignKey('competenceoperationnelle.idcompetenceoperationnelle'))
)


class Candidat(Base):
    __tablename__ = 'candidat'
    
    idcandidat = Column(String, primary_key=True)
    nom = Column(String)
    prenom = Column(String)
    civilite = Column(String)
    adresse = Column(String)
    email = Column(String)
    telephone = Column(String)
    anneeexperience = Column(Integer)
    typecontrat = Column(String)
    infossup = Column(LONGTEXT)
    statut = Column(String)
    archived = Column(Boolean, default=False)
    formations = relationship("Formation", back_populates="candidat")
    
    langues = relationship("Langue", secondary=langue_candidat, back_populates="candidats")
    
    technologies = relationship("Technologie", secondary=technologie_candidat, back_populates="candidats")
    
    competences_comportementales = relationship("CompetenceComportementale", secondary=competence_comportementale_candidat, back_populates="candidats")

    competences_operationnelles = relationship("CompetenceOperationnelle", secondary=competence_operationnelle_candidat, back_populates="candidats")


class Langue(Base):
    __tablename__ = 'langue'

    idlangue = Column(String, primary_key=True)
    nom = Column(String)

    # Relation inverse avec Candidat
    candidats = relationship("Candidat", secondary=langue_candidat, back_populates="langues")

class Technologie(Base):
    __tablename__ = 'technologie'

    idtechnologie = Column(String, primary_key=True)
    nomtechnologie = Column(String)

    candidats = relationship("Candidat", secondary=technologie_candidat, back_populates="technologies")

class CompetenceComportementale(Base):
    __tablename__ = 'competencecomportementale'

    idcompetencecomportementale = Column(String, primary_key=True)
    competencecomportementale = Column(String)

    candidats = relationship("Candidat", secondary=competence_comportementale_candidat, back_populates="competences_comportementales")

class CompetenceOperationnelle(Base):
    __tablename__ = 'competenceoperationnelle'

    idcompetenceoperationnelle = Column(String, primary_key=True)
    competenceoperationnelle = Column(String)

    candidats = relationship("Candidat", secondary=competence_operationnelle_candidat, back_populates="competences_operationnelles")
    
    
class Formation(Base):
    __tablename__ = 'formation'
    
    idformation = Column(String, primary_key=True)
    nomformation = Column(String)
    typeformation = Column(String)
    datedebut = Column(String)
    datefin = Column(String)
    etablissement = Column(String)
    
    idcandidat = Column(String, ForeignKey('candidat.idcandidat'))
    candidat = relationship("Candidat", back_populates="formations")