"""Project settings."""
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Parse settings from environment variables and .env file."""

    algolia_admin_api_key: str
    algolia_app_id: str

    algolia_index_name: str = "dbt_nodes"

    dbt_manifest_path: Path = Path("data/manifest.json")

    algolia_search_only_api_key: str

    dbt_repo_local_path: Path
    git_metadata_cache_path: Path = Path("data/git_metadata")

    class Config:  # noqa:D106
        env_file = ".env"
        env_file_encoding = "utf-8"
