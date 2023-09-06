from typing import Optional
from statuspageio.services.component import ComponentService
from statuspageio.services.metric import MetricService
from statuspageio.services.page import PageService
from statuspageio.config import Config
from statuspageio.http_client import HttpClient


class Client:
    def __init__(
        self,
        **kwargs,
    ):
        self.__config = Config(**kwargs)
        self.__config.validate()

        self.__http_client = HttpClient(config=self.__config)

    # Quick update for mutable fields
    @property
    def page_id(self):
        return self.__config.page_id

    @page_id.setter
    def page_id(self, value):
        self.__config.page_id = value

    @property
    def organization_id(self):
        return self.__config.organization_id

    @organization_id.setter
    def organization_id(self, value):
        self.__config.organization_id = value

    @property
    def config(self):
        return self.__config

    def pages(self, page_id: Optional[str] = None):
        return PageService(
            http_client=self.__http_client,
            page_id=page_id if page_id is not None else self.page_id,
        )

    # @property
    # def permissions(self):
    #     return self.__permissions
    #
    # @property
    # def status_embed_config(self):
    #     return self.__status_embed_config
    #
    # @property
    # def page_access_users(self):
    #     return self.__page_access_users
    #
    # @property
    # def page_access_groups(self):
    #     return self.__page_access_groups
    #
    # @property
    # def subscribers(self):
    #     return self.__subcribers
    #
    # @property
    # def incident_templates(self):
    #     return self.__incident_templates
    #
    # @property
    # def incidents(self):
    #     return self.__incidents
    #
    def components(self, page_id: Optional[str] = None):
        return ComponentService(
            http_client=self.__http_client,
            page_id=page_id if page_id is not None else self.page_id,
        )

    # @property
    # def component_groups(self):
    #     return self.__component_groups
    #

    def metrics(self, page_id: Optional[str] = None):
        return MetricService(
            http_client=self.__http_client,
            page_id=page_id if page_id is not None else self.page_id,
        )

    # @property
    # def metric_providers(self):
    #     return self.__metric_providers
    #
    # @property
    # def users(self):
    #     return self.__users
    #
