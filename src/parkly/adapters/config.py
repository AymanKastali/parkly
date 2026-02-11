from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    model_config = {"env_prefix": "PARKLY_"}

    app_name: str = "Parkly"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "DEBUG"
