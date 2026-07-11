from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import tg_bot

# Standardize the database URI fallback across different forks
DB_URI = getattr(tg_bot, 'SQLALCHEMY_DATABASE_URI', getattr(tg_bot, 'DB_URI', None))

# Enhanced engine initialization to handle sudden remote SSL disconnects
engine = create_engine(
    DB_URI, 
    client_encoding="utf8",
    pool_size=10,            # Keeps up to 10 persistent connections open
    max_overflow=20,         # Allows a burst of up to 20 additional temporary connections
    pool_timeout=30,         # How long to wait for a connection from the pool before timing out
    pool_recycle=1200,       # Recycles connections every 20 minutes before Render forces an idle drop
    pool_pre_ping=True       # Evaluates connection health before running queries; seamlessly reconnects if closed
)

BASE = declarative_base()
BASE.metadata.bind = engine

SESSION = scoped_session(sessionmaker(bind=engine, autoflush=False))
