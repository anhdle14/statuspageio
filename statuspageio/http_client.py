from requests import HTTPError, Response, Session
from json import JSONDecodeError, dumps
from time import sleep, time
from munch import munchify

from statuspageio.config import Config
from statuspageio.errors import (
    ResourceError,
    RateLimitError,
    RequestError,
    ServerError,
)


class HttpClient:
    API_VERSION = "/v1"

    def __init__(self, config: Config):
        self.config = config
        if self.config.verbose:
            self.enable_logging()

        # Handle Rate Limitting using hook
        self.max_requests = self.config.max_requests
        self.window_seconds = self.config.window_seconds
        self.request_history = []

        # Using Session to reuse TCP connection with hook
        self.session = Session()
        self.session.hooks = {"response": self.handle_rate_limit}

    def handle_rate_limit(self, response: Response, *args, **kwargs):
        # Remove request timestamps older than the specified window
        current_time = time()
        self.request_history = [
            timestamp
            for timestamp in self.request_history
            if current_time - timestamp <= self.window_seconds
        ]

        # If the number of requests in the current window exceeds the limit, calculate wait time
        if len(self.request_history) >= self.max_requests:
            wait_time = max(
                0,
                self.window_seconds
                - (current_time - min(self.request_history)),
            )
            sleep(wait_time)

        # Add the current request timestamp to the history
        self.request_history.append(current_time)

    def get(self, url, params=None, **kwargs):
        return self.request("get", url, params=params, **kwargs)

    def post(self, url, body=None, **kwargs):
        return self.request("post", url, body=body, **kwargs)

    def put(self, url, body=None, **kwargs):
        return self.request("put", url, body=body, **kwargs)

    def patch(self, url, body=None, **kwargs):
        return self.request("patch", url, body=body, **kwargs)

    def delete(self, url, params=None, **kwargs):
        return self.request("delete", url, params=params, **kwargs)

    def request(self, method: str, url: str, params=None, body=None, **kwargs):
        url = (
            f"{self.config.protocol}://{self.config.api_base_url}"
            f"/{self.config.api_version}/{url}"
        )

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "OAuth " + self.config.api_key,
        }

        # Override headers with user_headers if specified
        user_headers = {}
        if "headers" in kwargs and isinstance(kwargs["headers"], dict):
            user_headers = kwargs["headers"]
        self.session.headers.update(user_headers)

        raw = bool(kwargs["raw"]) if "raw" in kwargs else False

        if body is not None:
            headers["Content-Type"] = "application/json"
            payload = (
                body if raw else self.wrap_envelope(kwargs["container"], body)
            )
            body = dumps(payload)

        resp = self.session.request(
            method=method,
            url=url,
            params=params,
            data=body,
            headers=headers,
            timeout=float(self.config.timeout_in_seconds),
            verify=self.config.verify_ssl,
        )

        if not (200 <= resp.status_code < 300):
            self.handle_error_response(resp)

        if (
            "Content-Type" in resp.headers
            and "json" in resp.headers["Content-Type"]
        ):
            resp_body = (
                munchify(resp.json())
                if raw
                else self.unwrap_envelope(resp.json())
            )
        else:
            resp_body = resp.content

        return (resp.status_code, resp.headers, resp_body)

    def handle_error_response(self, resp):
        try:
            errors = resp.json()
        except JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON response: {e}."
                f"HTTP response code={resp.status_code}."
                f"HTTP response body={resp.text}."
            )
        status_code = resp.status_code
        if status_code == 422:
            raise ResourceError(status_code, errors)
        elif status_code == 420 or status_code == 429:
            raise RateLimitError(status_code, errors)
        elif 400 <= status_code < 500:
            raise RequestError(status_code, errors)
        elif 500 <= status_code < 600:
            raise ServerError(status_code, errors)
        else:
            raise HTTPError("Unknown HTTP error response")

    @staticmethod
    def wrap_envelope(container, body):
        return {container: body}

    @staticmethod
    def unwrap_envelope(body):
        return (
            [munchify(item) for item in body["items"]]
            if "items" in body
            else munchify(body)
        )

    def enable_logging(self):
        import logging
        import http.client as http_client

        http_client.HTTPConnection.debuglevel = 1

        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
