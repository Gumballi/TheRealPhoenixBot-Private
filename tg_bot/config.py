import os
from tg_bot.sample_config import Config as SampleConfig


class Config(SampleConfig):
    # REQUIRED - Pulls safely from Render environment variables
    API_KEY = os.environ.get("API_KEY", "PLACEHOLDER_TOKEN")
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "PLACEHOLDER_USER")

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgresql://user:pass@host/db")


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
