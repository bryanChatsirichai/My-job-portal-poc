"""Application settings.

Values are resolved when ``settings = Settings()`` runs at import time.

Priority (highest wins):
  1. Default on each field below
  2. ``backend/.env`` — always resolved from this package (not process cwd)
  3. OS environment variables

``DATABASE_URL`` is the single switch for worker, API (``get_db``), and Alembic.

Field names map to env vars automatically: ``adzuna_app_key`` → ``ADZUNA_APP_KEY``.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    # BaseSettings maps each field name to an env var automatically:
    #   snake_case field → UPPER_SNAKE_CASE env var (e.g. adzuna_app_key → ADZUNA_APP_KEY).
    # Field() only sets defaults/descriptions; it does not wire the env name.
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Core (defaults are enough for local dev) ---
    database_url: str = "sqlite:///./jobportal.db"  # DATABASE_URL
    cors_origins: str = "http://localhost:5173"  # CORS_ORIGINS
    sync_cron_schedule: str = "0 2 * * *"  # SYNC_CRON_SCHEDULE

    # --- Adapter toggles (set *_ENABLED=false to skip sync for a source) ---
    mcf_enabled: bool = True  # MCF_ENABLED
    jobicy_enabled: bool = True  # JOBICY_ENABLED
    adzuna_enabled: bool = True  # ADZUNA_ENABLED
    linkedin_enabled: bool = True  # LINKEDIN_ENABLED
    jobspy_enabled: bool = True  # JOBSPY_ENABLED

    # --- Sync page sizes ---
    mcf_page_size: int = 100  # MCF_PAGE_SIZE
    adzuna_page_size: int = 50  # ADZUNA_PAGE_SIZE
    jobicy_page_size: int = 200  # JOBICY_PAGE_SIZE
    linkedin_page_size: int = 70  # LINKEDIN_PAGE_SIZE
    jobspy_page_size: int = 1  # JOBSPY_PAGE_SIZE — term pagination; only empty pages stop sync

    # --- Adzuna (optional) ---
    # Default "" disables Adzuna; set ADZUNA_APP_ID and ADZUNA_APP_KEY in backend/.env to enable sync.
    adzuna_app_id: str = Field(  # ADZUNA_APP_ID
        default="",
        description="Env ADZUNA_APP_ID. Empty = Adzuna adapter skipped.",
    )
    adzuna_app_key: str = Field(  # ADZUNA_APP_KEY
        default="",
        description="Env ADZUNA_APP_KEY. Empty = Adzuna adapter skipped.",
    )

    # --- Jobicy filters (optional) ---
    jobicy_geo: str = Field(default="", description="Env JOBICY_GEO")  # JOBICY_GEO
    jobicy_industry: str = Field(default="", description="Env JOBICY_INDUSTRY")  # JOBICY_INDUSTRY
    jobicy_tag: str = Field(default="", description="Env JOBICY_TAG")  # JOBICY_TAG

    # --- LinkedIn scraper (optional) ---
    linkedin_jobs_api_url: str = Field(  # LINKEDIN_JOBS_API_URL
        default="http://localhost:3000/api/v1",
        description="Env LINKEDIN_JOBS_API_URL. Empty = LinkedIn adapter skipped.",
    )
    linkedin_keywords: str = Field(default="", description="Env LINKEDIN_KEYWORDS")  # LINKEDIN_KEYWORDS
    linkedin_location: str = "Singapore"  # LINKEDIN_LOCATION
    linkedin_date_since_posted: str = "past_week"  # LINKEDIN_DATE_SINCE_POSTED

    # --- JobSpy scraper (optional self-hosted sidecar) ---
    jobspy_api_url: str = Field(  # JOBSPY_API_URL
        default="http://localhost:8001/v1",
        description="Env JOBSPY_API_URL. Empty = JobSpy adapter skipped.",
    )

    @property
    def database_backend(self) -> str:
        if self.database_url.startswith("sqlite"):
            return "sqlite"
        if self.database_url.startswith("postgresql"):
            return "postgres"
        return "other"


settings = Settings()
