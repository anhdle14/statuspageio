from dataclasses import dataclass, fields, InitVar
from datetime import date
from enum import Enum
from typing import Optional
from munch import Munch

from statuspageio.http_client import HttpClient


class ComponentStatus(str, Enum):
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    DEGRADED_PERFORMANCE = "degraded_performance"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"


@dataclass
class ComponentBody:
    name: str
    group_id: InitVar[Optional[str]] = InitVar[None]
    status: ComponentStatus = ComponentStatus.OPERATIONAL
    description: str = ""
    only_show_if_degraded: bool = False
    showcase: bool = True
    start_date: Optional[str] = str(date.today())

    def __post_init__(self, group_id):
        if group_id is not None:
            self.group_id = group_id


class ComponentService:
    """
    :class:`statuspageio.ComponentsService` is used by :class:`statuspageio.Client` to make
    actions related to Components resource.

    Normally you won't instantiate this class directly.
    """

    def __init__(self, http_client: HttpClient, page_id: str):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.page_id = page_id
        self.container = "component"

    @property
    def http_client(self):
        return self.__http_client

    def list(self, offset: int = 1, limit: int = 100) -> Munch:
        """
        List components

        Lists components and their information
        If the specified contact does not exist, the request will return an error


        :calls: ``get pages/{page_id}/components/{component_id}.json``
        :return: Dictionary that support attriubte-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, components = self.http_client.get(
            f"/pages/{self.page_id}/components.json?page={offset}&per_page={limit}"
        )
        return components

    def create(self, payload: ComponentBody) -> Munch:
        body = dict(
            (field.name, getattr(payload, field.name))
            for field in fields(payload)
        )

        _, _, component = self.http_client.post(
            f"/pages/{self.page_id}/components.json",
            container=self.container,
            body=body,
        )

        return component

    def delete(self, component_id: str) -> Munch:
        """
        Delete a component

        Deletes a component
        If the specified contact does not exist, the request will return an error


        :calls: ``delete pages/{page_id}/components/{component_id}.json``
        :param int component_id: Unique identifier of a component.
        :return: Dictionary that support attriubte-style access and represents updated Component resource.
        :rtype: dict
        """

        status_code, _, _ = self.http_client.delete(
            "/pages/{page_id}/components/{component_id}.json".format(
                page_id=self.page_id, component_id=component_id
            )
        )
        return status_code

    def update(self, component_id: str, payload: ComponentBody) -> Munch:
        """
        Update a component

        Updates component information
        If the specified contact does not exist, the request will return an error


        :calls: ``patch pages/{page_id}/components/{component_id}.json``
        :param int component_id: Unique identifier of a component.
        :param dict **kwargs:  component payload to update.
        :return: Dictionary that support attriubte-style access and represents updated Component resource.
        :rtype: dict
        """

        body = dict(
            (field.name, getattr(payload, field.name))
            for field in fields(payload)
        )

        _, _, component = self.http_client.patch(
            f"/pages/{self.page_id}/components/{component_id}.json",
            container="component",
            body=body,
        )
        return component
