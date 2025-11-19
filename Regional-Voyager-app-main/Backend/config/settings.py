from pydantic import BaseSettings

class Settings(BaseSettings):
    azure_maas_base_url: str
    azure_maas_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
