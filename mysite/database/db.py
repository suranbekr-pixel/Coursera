from pathlib import Path
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent.parent / 'coursera.db'
DB_URL = f'sqlite:///{DB_PATH.as_posix()}'
engine = create_engine(DB_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
