from dataclasses import dataclass
from typing import Optional
import warnings

from statuspageio.errors import ConfigError
from statuspageio.version import VERSION


@dataclass
class Config:
    # Required
    api_key: str

    # Optional
    page_id: Optional[str] = None
    organization_id: Optional[str] = None

    # Defaults
    verbose: bool = False
    timeout_in_seconds: int = 30
    verify_ssl: bool = True
    api_version: str = "v1"

    # NOTE: This has been fine tuned so it will work around the rate limit.
    # However, it is better to use many api_keys or asking support directly.
    max_requests: int = 5
    window_seconds: float = 5.6

    def __post_init__(self):
        self.protocol = "https"
        self.api_base_url = "api.statuspage.io"
        self.user_agent = f"StatusPage/v1 Python/{VERSION}"

    def validate(self) -> bool:
        if self.api_key is None:
            raise ConfigError("No `api_key` provided. Set your `api_key` via statuspageio.Client(api_key=<api_key>.")

        if self.page_id is None:
            warnings.warn(
                "No `page_id` provided. Set your `page_id` via statuspageio.Client(page_id=<page_id>). Or `client.page_id = <page_id>`.")

        if self.organization_id is None:
            warnings.warn("No `organization_id` provided. Set your `organization_id` via statuspageio.Client(organization_id=<organization_id>). Or `client.organization_id = <organization_id>`.")

        return True
