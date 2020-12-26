from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    algolia_admin_api_key: str
    algolia_app_id: str

    algolia_index_name: str = "dbt_nodes"

    dbt_manifest_path: Path = "data/manifest.json"

    algolia_search_only_api_key: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
