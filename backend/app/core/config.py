# TODO: Implement module logic
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Ticket System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings (Using a local SQLite DB for now to get started quickly)
    DATABASE_URL: str = "sqlite:///./tickets.db"
    
    # AI Provider Settings
    OPENAI_API_KEY: str = ""

    # This tells Pydantic to read from a .env file if it exists
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()