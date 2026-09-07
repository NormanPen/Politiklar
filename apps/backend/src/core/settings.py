"""Typed runtime settings loaded from the selected environment."""

from pathlib import Path

from pydantic import HttpUrl, PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    crawler_user_agent: str = "PolitiklarCrawler/0.1 (+https://github.com/)"
    crawler_request_timeout_seconds: PositiveFloat = 30.0
    crawler_requests_per_second: PositiveFloat = 1.0
    crawler_max_response_bytes: int = 20_000_000
    crawler_max_retries: int = 3
    crawler_source_archive_path: Path = Path("var/source-archive")
    bundestag_electoral_term: int = 21
    bundestag_base_url: HttpUrl = "https://www.bundestag.de"
    bundestag_named_votes_url: HttpUrl = "https://www.bundestag.de/parlament/plenum/abstimmung/liste"
    wikidata_api_url: HttpUrl = "https://www.wikidata.org/w/api.php"
    wikimedia_commons_api_url: HttpUrl = "https://commons.wikimedia.org/w/api.php"

    model_config = SettingsConfigDict(extra="ignore")