from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import tg_bot

# Standardize the database URI fallback across different forks
DB_URI = getattr(tg_bot, 'SQLALCHEMY_DATABASE_URI', getattr(tg_bot, 'DB_URI', None))

engine = create_engine(DB_URI, client_encoding="utf8")
BASE = declarative_base()
BASE.metadata.bind = engine

SESSION = scoped_session(sessionmaker(bind=engine, autoflush=False))
