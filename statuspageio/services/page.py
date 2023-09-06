from dataclasses import dataclass, fields
from enum import Enum
from typing import Optional
from munch import Munch

from statuspageio.http_client import HttpClient

PageBrandingEnum = Enum("Branding", ["basic", "premium"])


@dataclass
class PageBody:
    name: str
    domain: str
    subdomain: str
    url: str
    branding: PageBrandingEnum
    css_font_color = str
    css_light_font_color = str
    css_greens = str
    css_yellows = str
    css_oranges = str
    css_reds = str
    css_blues = str
    css_border_color = str
    css_graph_color = str
    css_link_color = str
    css_no_data = str
    hidden_from_search = bool
    viewers_must_be_team_members = bool
    allow_page_subscribers = bool
    allow_incident_subscribers = bool
    allow_email_subscribers = bool
    allow_sms_subscribers = bool
    allow_rss_atom_feeds = bool
    allow_webhook_subscribers = bool
    notifications_from_email = str
    time_zone = str
    notifications_email_footer = str


class PageService:
    def __init__(self, http_client: HttpClient, page_id: str):
        self.__http_client = http_client
        self.container = "page"
        self.page_id = page_id

    @property
    def http_client(self):
        return self.__http_client

    def list(self) -> Munch:
        _, _, pages = self.http_client.get("/pages")

        return pages

    def get(self, page_id: Optional[str] = None) -> Munch:
        _, _, page = self.http_client.get(
            "/pages/{page_id}.json".format(
                page_id=page_id if page_id is not None else self.page_id
            )
        )

        return page

    def update(self, body: PageBody) -> Munch:
        if not body:
            raise ValueError("payload are missing")

        payload = dict((k, v) for k, v in body.iteritems() if k in fields(body))

        page = self.http_client.patch(
            f"/pages/{self.page_id}.json",
            container=self.container,
            body=payload,
        )

        return page
