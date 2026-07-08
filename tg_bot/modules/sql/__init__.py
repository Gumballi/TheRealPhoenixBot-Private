from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from tg_bot import DB_URI


def start() -> scoped_session:
    if DB_URI.startswith("sqlite"):
        engine = create_engine(DB_URI)
    else:
        engine = create_engine(DB_URI, client_encoding="utf8")
    BASE.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine, autoflush=False))
    session.bind = engine
    return session


BASE = declarative_base()
SESSION = start()
