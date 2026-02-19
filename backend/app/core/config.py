from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'SmartApply API'
    environment: str = 'dev'
    database_url: str = 'sqlite:///./smartapply.db'
    jwt_secret: str = 'change-me'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24

    minio_endpoint: str = 'localhost:9000'
    minio_access_key: str = 'minioadmin'
    minio_secret_key: str = 'minioadmin'
    bucket_name: str = 'resumes'
    minio_secure: bool = False

    max_resume_mb: int = 10
    llm_mode: str = 'mock'
    llm_api_key: str | None = None

    adzuna_app_id: str | None = None
    adzuna_app_key: str | None = None
    remotive_base_url: str = 'https://remotive.com/api/remote-jobs'

    tailor_rate_limit_per_hour: int = 20


settings = Settings()
