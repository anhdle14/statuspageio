from dataclasses import InitVar, dataclass, fields
from enum import Enum
from time import time
from typing import List, Optional

from munch import Munch

from statuspageio.http_client import HttpClient


class MetricTransform(str, Enum):
    AVERAGE = "average"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    SUM = "sum"


@dataclass
class MetricData:
    timestamp: int
    value: int


@dataclass
class MetricDataBody:
    data: dict[str, List[MetricData]]


@dataclass
class MetricBody:
    name: str
    metric_identifier: str
    transform: MetricTransform
    y_axis_min: int
    y_axis_max: int
    application_id: InitVar[Optional[str]] = InitVar[None]
    suffix: str = ""
    y_axis_hidden: bool = False
    display: bool = True
    decimal_places: int = 0
    tooltip_description: str = ""

    def __post_init__(self, application_id):
        if application_id is not None:
            self.application_id = application_id


class MetricService:
    def __init__(self, http_client: HttpClient, page_id: str):
        self.__http_client = http_client
        self.page_id = page_id
        self.container = "metric"

    @property
    def http_client(self):
        return self.__http_client

    def list(self, offset: int = 1, limit: int = 100) -> Munch:
        _, _, metrics = self.http_client.get(
            f"/pages/{self.page_id}/metrics?page={offset}&per_page={limit}"
        )

        return metrics

    def create(self, metric_provider_id: str, payload: MetricBody) -> Munch:
        payload = dict(
            (field.name, getattr(payload, field.name))
            for field in fields(payload)
        )

        _, _, metric = self.http_client.post(
            f"/metrics_providers/{metric_provider_id}/metrics",
            container=self.container,
            body=payload,
        )

        return metric

    def update(
        self, metric_id: str, name: str, metric_identifier: str
    ) -> Munch:
        payload = {"name": name, "metric_identifier": metric_identifier}

        _, _, metric = self.http_client.patch(
            f"/pages/{self.page_id}/metrics/{metric_id}",
            container=self.container,
            body=payload,
        )

        return metric

    def delete(self, metric_id: str) -> int:
        status_code, _, _ = self.http_client.delete(
            f"/pages/{self.page_id}/metrics/{metric_id}"
        )

        return status_code

    def empty(self, metric_id: str) -> int:
        status_code, _, _ = self.http_client.delete(
            f"/pages/{self.page_id}/metrics/{metric_id}/data"
        )

        return status_code

    def add_data(
        self, metric_id: str, value: float, timestamp: int = int(time())
    ) -> Munch:
        body = {
            "timestamp": timestamp,
            "value": value,
        }
        _, _, data = self.http_client.post(
            f"/pages/{self.page_id}/metrics/{metric_id}/data",
            container="data",
            body=body,
        )

        return data

    def add_datas(self, payload: MetricDataBody) -> Munch:
        body = dict(
            (field.name, getattr(payload, field.name))
            for field in fields(payload)
        )

        _, _, data = self.http_client.post(
            f"/pages/{self.page_id}/metrics/data",
            container="data",
            body=body,
        )

        return data
