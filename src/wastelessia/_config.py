import os
from dataclasses import dataclass


@dataclass
class Config:
    api_key: str
    endpoint: str


_config: Config | None = None


def configure(api_key: str, endpoint: str = "https://api.wastelessia.com") -> None:
    global _config
    _config = Config(api_key=api_key, endpoint=endpoint.rstrip("/"))


def get_config() -> Config:
    global _config
    if _config is None:
        key = os.environ.get("WASTELESSIA_API_KEY", "")
        endpoint = os.environ.get("WASTELESSIA_ENDPOINT", "https://api.wastelessia.com")
        _config = Config(api_key=key, endpoint=endpoint.rstrip("/"))
    return _config
