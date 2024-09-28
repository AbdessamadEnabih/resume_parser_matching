from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from Entities import Candidat, Offre
from Entities.Matching import Matching
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from repositories.repositoryCandidat import get_candidats
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import uuid
from geopy.geocoders import Nominatim
from unidecode import unidecode
from fuzzywuzzy import fuzz
from datetime import datetime

diplome_mapping = {
    "bac+8":["doctorat","doctorante","doctorant","bac+8"],
    "bac+5": ["bac+5"],
    "diplome d'ingenieur":[ "ingenieur","cycle ing","cycle ingenieur","diplome d'ingénieur","formation d'ing","formation d'ingenieur","formation d'ingenierie"],
    "master":["master", "MBA","double diplomation"],
    "bac+3": ["licence", "bachelor", "bac+3"],
    "bac+2": ["dut", "bts","deug" "bac+2"],
    "bac": ["bac", "baccalaureat", "baccalauréat"]
}


def normaliser_texte(texte):
    return unidecode(texte).lower()

def convertir_datefin(datefin):
    if isinstance(datefin, str):
        try:
            return int(datefin.split()[-1]) 
        except (ValueError, IndexError):
            return None
    return datefin 

def trouver_diplome(texte):
    texte_normalise = normaliser_texte(texte)
    for key, values in diplome_mapping.items():
        for value in values:
            if value.lower() in texte_normalise.lower():
                return key
    return None

# Comparaison diplome du candidat a celui de l'offre en tenant compte de l'année d'obtention et la formation la plus recente
# Etapes : Récuperation de la derniere formation , Verifier si le diplome a ete obtenu, Verification si diplome fait partie du dict 
def comparer_diplome(candidat, offre):
    
    if candidat.formations:
        latest_formation = max(candidat.formations, key=lambda f: f.datefin)
        annee_fin_formation = convertir_datefin(latest_formation.datefin)
        if annee_fin_formation is None:
            return 0.1  
        annee_actuelle = datetime.now().year
        if annee_fin_formation > annee_actuelle:
            if annee_fin_formation - annee_actuelle <= 1:
                score_diplome = 0.7  
            else:
                score_diplome = 0.3  
        else:
            score_diplome = 1.0

        diplome_candidat = trouver_diplome(latest_formation.typeformation)
        diplome_offre = trouver_diplome(offre.niveaudiplome)
        if diplome_offre == 'bac+5':
            if diplome_candidat in ['master', 'diplome_ingenieur']:
                return score_diplome

        if diplome_candidat == diplome_offre:
            return score_diplome  
        else:
            #Autre diplome que celui demandé // Apparait dans le dictionnaire
            if diplome_candidat in diplome_mapping and diplome_offre in diplome_mapping:
                return score_diplome * 0.5  
            else:
                #Autre diplome que celui demandé // N'apparait pas dans le dictionnaire
                return score_diplome * 0.1 

    else:
        # pas de diplome
        return 0  
    
def geocoder(adresse):
    geolocator = Nominatim(user_agent="resume_parser_matching")  
    location = geolocator.geocode(adresse)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Adresse non trouvée : {adresse}")
def calculer_delai_expiration(offre):
    dateEcheance = offre["dateEcheance"]
    delai = (dateEcheance - datetime.now()).total_seconds()
    return max(0, delai)

def get_dict_offre(offre):
    offre_data = {
        "idOffre": offre.idoffre,
        "referenceOffre": offre.referenceoffre,
        "titreOffre": offre.titreoffre,
        "dateCreation": offre.datecreation,
        "datePublication": offre.datepublication,
        "dateEcheance": offre.dateecheance,
        "etat": offre.etat,
        "nomDonneur": offre.nomdonneur,
        "emailDonneur": offre.emaildonneur,
        "telephoneDonneur": offre.telephonedonneur,
        "nomOrganisation": offre.nomorganisation,
        "adresseOrganisation": offre.adresseorganisation,
        "niveaudiplome": offre.niveaudiplome,
        "niveauexpertise": offre.niveauexpertise,
        "anneeExperience": offre.anneeexperience,
        "typeContrat": offre.typecontrat,
        "description": offre.description,
        "langues": [langue.nom for langue in offre.langues],
        "technologies": [tech.nomtechnologie for tech in offre.technologies],
        "competences_operationnelles": [comp.competenceoperationnelle for comp in offre.competences_operationnelles]
    }
    return offre_data    

def calculer_proximite_geographique(candidat, offre):
    try:
        organisation_coord = geocoder(offre.adresseorganisation)
        candidat_coord = geocoder(candidat.adresse)
        
        knn = NearestNeighbors(n_neighbors=1, metric='euclidean')
        knn.fit([organisation_coord])
        distance = knn.kneighbors([candidat_coord], return_distance=True)[0][0]
        return (1 / (1 + distance))
    
    except ValueError as e:
        return 0  


def comparer_experience(candidat, offre):
    diff_experience = abs(candidat.anneeexperience - offre.anneeexperience)
    if diff_experience == 0:
        return 1
    elif diff_experience <= 0.5: 
        return 0.9
    elif diff_experience <= 2:
        return 0.8
    elif diff_experience <= 5:
        return 0.6
    else:
        return 0.4


def comparer_competences(candidat, offre, seuil_correspondance=85):
    vecteur_offre = np.array([1] * len(offre.competences_operationnelles))
    
    vecteur_candidat = np.array([
        1 if any(fuzz.ratio(comp.competenceoperationnelle, cand_comp.competenceoperationnelle) >= seuil_correspondance 
        for cand_comp in candidat.competences_operationnelles) 
        else 0 
        for comp in offre.competences_operationnelles
    ])
    
    score_comp = round(cosine_similarity([vecteur_candidat], [vecteur_offre])[0][0],1)
    return score_comp

def comparer_technologies(candidat, offre, seuil_correspondance=85):
    technologies_offre = set([tech.nomtechnologie for tech in offre.technologies])
    technologies_candidat = set([cand_tech.nomtechnologie for cand_tech in candidat.technologies])
    
    intersection = set()
    for tech_offre in technologies_offre:
        for tech_candidat in technologies_candidat:
            if fuzz.ratio(tech_offre, tech_candidat) >= seuil_correspondance:
                intersection.add(tech_offre)
    
    union = technologies_offre.union(technologies_candidat)
    
    if len(union) == 0: 
        return 0.0
    
    score_jaccard = len(intersection) / len(union)
    
    return round(score_jaccard, 2)
def comparer_langues(candidat, offre, seuil_correspondance=85):
    vecteur_offre = np.array([1] * len(offre.langues))
    
    vecteur_candidat = np.array([
        1 if any(fuzz.ratio(langue.nom, cand_langue.nom) >= seuil_correspondance for cand_langue in candidat.langues) 
        else 0 
        for langue in offre.langues
    ])
    
    score_langue = cosine_similarity([vecteur_candidat], [vecteur_offre])[0][0]
    return score_langue


def calculer_score_global(scores):
    
    score_geo = 0.2 * scores['geo']  
    score_diplome = 0.15 * scores['diplome']  
    score_experience = 0.2 * scores['experience']  
    score_competences = 0.20 * scores['competences']  
    score_technologies = 0.15 * scores['technologies']  
    score_langues = 0.1 * scores['langues']  

    print(f"Score Géographique (20%): {score_geo}")
    print(f"Score Diplôme (15%): {score_diplome}")
    print(f"Score Expérience (20%): {score_experience}")
    print(f"Score Compétences (20%): {score_competences}")
    print(f"Score Technologies (15%): {score_technologies}")
    print(f"Score Langues (10%): {score_langues}")
    
    score_final = (
        score_geo +
        score_diplome +
        score_experience +
        score_competences +
        score_technologies +
        score_langues
    )
    
    print(f"Score Global: {score_final}")
    
    return score_final


def faire_matching(offre: Offre, session: Session, batch_size: int = 100):
    page = 0

    try:
        while True:
            candidats = get_candidats(session, batch_size=batch_size, page=page)

            if not candidats: 
                break

            for candidat in candidats:
                existing_match = session.query(Matching).filter_by(
                    idcandidat=candidat.idcandidat,
                    idoffre=offre.idoffre
                ).first()

                if existing_match:
                    continue

                score_geo = calculer_proximite_geographique(candidat, offre)
                score_diplome = comparer_diplome(candidat, offre)
                score_experience = comparer_experience(candidat, offre)
                score_comp = comparer_competences(candidat, offre)
                score_tech = comparer_technologies(candidat, offre)
                score_langue = comparer_langues(candidat, offre)

                scores = {
                    'geo': score_geo,
                    'diplome': score_diplome,
                    'experience': score_experience,
                    'competences': score_comp,
                    'technologies': score_tech,
                    'langues': score_langue
                }
                score_final = calculer_score_global(scores)

                statut = "adapté" if score_final > 0.7 else "rejeté"
                print(f"Score final pour {candidat.email} : {score_final}, Statut : {statut}")

                matching = Matching(
                    idmatching=str(uuid.uuid4()),
                    idcandidat=candidat.idcandidat,
                    idoffre=offre.idoffre,
                    score=int(score_final * 100), 
                    statut=statut
                )

                try:
                    session.add(matching)
                    session.commit() 
                except Exception as e:
                    session.rollback() 
                    raise
            page += 1

    except Exception as e:
        raise

    finally:
        session.close()
        
def faire_matching_candidat(offre: Offre, candidat: Candidat, session: Session):
    try:
        existing_match = session.query(Matching).filter_by(
            idcandidat=candidat.idcandidat,
            idoffre=offre.idoffre
        ).first()

        if existing_match:
            return {"message": "Matching déjà existant"}

        score_geo = calculer_proximite_geographique(candidat, offre)
        score_diplome = comparer_diplome(candidat, offre)
        score_experience = comparer_experience(candidat, offre)
        score_comp = comparer_competences(candidat, offre)
        score_tech = comparer_technologies(candidat, offre)
        score_langue = comparer_langues(candidat, offre)

        scores = {
            'geo': score_geo,
            'diplome': score_diplome,
            'experience': score_experience,
            'competences': score_comp,
            'technologies': score_tech,
            'langues': score_langue
        }
        score_final = calculer_score_global(scores)

        statut = "adapté" if score_final > 0.7 else "rejeté"
        print(f"Score final pour {candidat.email} : {score_final}, Statut : {statut}")

        matching = Matching(
            idmatching=str(uuid.uuid4()),
            idcandidat=candidat.idcandidat,
            idoffre=offre.idoffre,
            score=int(score_final * 100), 
            statut=statut
        )

        session.add(matching)
        session.commit()

        return {"message": "Matching effectué", "statut": statut}

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()


def comparer_technologies_CosineSimilarity(candidat, offre, seuil_correspondance=85):
    vecteur_offre = np.array([1] * len(offre.technologies))
    
    vecteur_candidat = np.array([
        1 if any(fuzz.ratio(tech.nomtechnologie, cand_tech.nomtechnologie) >= seuil_correspondance for cand_tech in candidat.technologies) 
        else 0 
        for tech in offre.technologies
    ])
    
    score_tech = round(cosine_similarity([vecteur_candidat], [vecteur_offre])[0][0],1)
    return score_tech


def comparer_technologies_DistanceJaccard(candidat, offre, seuil_correspondance=85):
    technologies_offre = set([tech.nomtechnologie for tech in offre.technologies])
    technologies_candidat = set([cand_tech.nomtechnologie for cand_tech in candidat.technologies])
    
    intersection = set()
    for tech_offre in technologies_offre:
        for tech_candidat in technologies_candidat:
            if fuzz.ratio(tech_offre, tech_candidat) >= seuil_correspondance:
                intersection.add(tech_offre)
    
    union = technologies_offre.union(technologies_candidat)
    
    if len(union) == 0: 
        return 0.0
    
    score_jaccard = len(intersection) / len(union)
    
    return round(score_jaccard, 2)