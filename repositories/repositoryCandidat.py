from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy import create_engine
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Entities.Candidat import Base, Candidat, Formation, Langue, Technologie, CompetenceOperationnelle, CompetenceComportementale

DATABASE_URL = 'mysql+pymysql://root:admin@localhost:3306/cvtheque'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def get_candidats(session: Session, batch_size: int, page: int):

    offset = batch_size * page
    candidats= (
        session.query(Candidat)
        .options(
            joinedload(Candidat.langues),
            joinedload(Candidat.technologies),
            joinedload(Candidat.competences_operationnelles),
            joinedload(Candidat.competences_comportementales),
            joinedload(Candidat.formations)
        )
        .filter(Candidat.archived == False)
        .offset(offset)
        .limit(batch_size)
        .all()
    )

    return candidats


def get_candidatById(id_candidat: str,session: Session):
    candidat = (
        session.query(Candidat)
        .options(
            joinedload(Candidat.langues),
            joinedload(Candidat.technologies),
            joinedload(Candidat.competences_operationnelles),
            joinedload(Candidat.competences_comportementales),
            joinedload(Candidat.formations)
        )
        .filter(Candidat.idcandidat == id_candidat)
        .first()
    )

    return candidat

SessionLocal = sessionmaker(bind=engine)

def main():
    db = SessionLocal()

    try:
        candidat= get_candidatById(db,'24b9d9c4-7057-11ef-a090-1fabbf9ea21c')
        if candidat:
            print(candidat.email)
        else:
            print('Candidat non trouvé ')
    finally:
        db.close()

if __name__ == "__main__":
    main()