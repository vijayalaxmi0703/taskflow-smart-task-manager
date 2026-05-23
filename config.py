import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class using environment variables."""

    # Flask secret key for session management
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # PostgreSQL connection string
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:Vijayalaxmi@localhost:5432/taskdb"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Flask-SocketIO async mode (using threading is more compatible on Windows)
    SOCKETIO_ASYNC_MODE = "threading"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Default to development
config = DevelopmentConfig
