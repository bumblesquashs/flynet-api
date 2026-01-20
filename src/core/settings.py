from typing import Any, Dict, List, Optional, Union

from pydantic import field_validator, AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # pylint: disable=no-self-argument
    INTERNAL_DEV_MODE: bool = False
    API_V1_PREFIX: str = "/v1"
    HOST_PREFIX: str
    LOGGING_LEVEL: Optional[str] = "INFO"

    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_SCHEME: str = "http"

    MAILGUN_DOMAIN: str
    MAILGUN_API_KEY: str
    ACCOUNT_MANAGEMENT_TO_EMAIL: str = "james@jmward.net"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:9010", "http://localhost:8081", "http://localhost:8080"]
    AUDIENCE: str
    ISSUER: str

    # @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]

        if isinstance(v, (list, str)):
            return v

        raise ValueError(v)

    PROJECT_NAME: str = "Flynet API"

    POSTGRES_SERVER: Optional[str]
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_DB: Optional[str]
    POSTGRES_PORT: Optional[int]
    POSTGRES_EXTRAS: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    TOKEN_EXPIRES_MINUTES: int = 60 * 24 * 7
    TOKEN_EXPIRES_MINUTES_PASS_RESET: int = 30
    TOKEN_ALGORITHM: str = "HS256"
    TOKEN_SECRET: Optional[str]

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:

        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get('POSTGRES_PORT') or 5432,
            path=f"{values.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    # model_config = SettingsConfigDict()

    class Config:
        case_sensitive: bool = True
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        env_prefix: str = "FLYNET_API__"


settings = Settings()
