from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Table
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

langueOffre = Table(
    'langueoffre', Base.metadata,
    Column('idoffre', String, ForeignKey('offre.idoffre')),
    Column('idlangue', String, ForeignKey('langue.idlangue'))
)

technologieOffre = Table(
    'technologieoffre', Base.metadata,
    Column('idoffre', String, ForeignKey('offre.idoffre')),
    Column('idtechnologie', String, ForeignKey('technologie.idtechnologie')),
)

competenceOperationnelleOffre = Table(
    'competenceoperationnelleparoffre', Base.metadata,
    Column('idoffre', String, ForeignKey('offre.idoffre'), primary_key=True),
    Column('idcompetenceoperationnelle', String, ForeignKey('competenceoperationnelle.idcompetenceoperationnelle'), primary_key=True)
)

class Offre(Base):
    __tablename__ = 'offre'
    
    idoffre = Column(String, primary_key=True)
    referenceoffre = Column(String)
    titreoffre = Column(String)
    datecreation = Column(String)
    datepublication = Column(DateTime, default=datetime.utcnow)
    dateecheance = Column(DateTime)
    etat = Column(String)
    infossup = Column(LONGTEXT)
    objet = Column(Text)
    nomdonneur = Column(String)
    emaildonneur = Column(String)
    telephonedonneur = Column(String)
    nomorganisation = Column(String)
    adresseorganisation = Column(String)
    niveaudiplome = Column(String)
    niveauexpertise = Column(String)
    anneeexperience = Column(Integer)
    typecontrat = Column(String)
    archived = Column(Boolean, default=False)
    description = Column(LONGTEXT)
    estMatche = Column(Boolean, default=False) 
    
    langues = relationship("Langue", secondary=langueOffre, back_populates="offres")
    
    technologies = relationship("Technologie", secondary=technologieOffre, back_populates="offres")

    competences_operationnelles = relationship("CompetenceOperationnelle", secondary=competenceOperationnelleOffre, back_populates="offres")



    

class Langue(Base):
    __tablename__ = 'langue'

    idlangue = Column(String, primary_key=True)
    nom = Column(String)
    
    offres = relationship("Offre", secondary=langueOffre, back_populates="langues")


class CompetenceOperationnelle(Base):
    __tablename__ = 'competenceoperationnelle'

    idcompetenceoperationnelle = Column(String, primary_key=True)
    competenceoperationnelle = Column(String)

    offres = relationship("Offre", secondary=competenceOperationnelleOffre, back_populates="competences_operationnelles")


class Technologie(Base):
    __tablename__ = 'technologie'

    idtechnologie = Column(String, primary_key=True)
    nomtechnologie = Column(String)

    offres = relationship("Offre", secondary=technologieOffre, back_populates="technologies")
