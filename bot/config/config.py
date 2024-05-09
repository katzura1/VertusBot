from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    SLEEP_TIME: int = 6000

    AUTO_UPGRADE_FARM: bool = True
    MAX_FARM_LEVEL: int = 10
    AUTO_UPGRADE_POPULATION: bool = True
    MAX_POPULATION_LEVEL: int = 10
    AUTO_UPGRADE_STORAGE: bool = True
    MAX_STORAGE_LEVEL: int = 5

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()
