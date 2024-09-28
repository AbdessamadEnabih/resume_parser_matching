from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, declarative_base

# Créer une instance de Base
Base = declarative_base()
DATABASE_URL = 'mysql+pymysql://root:admin@localhost:3306/cvtheque'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
