import time
from dataclasses import dataclass, field

import requests


@dataclass(kw_only=True)
class JsonResponseProbe:
    """A generic class for probing a JSON HTTP endpoint."""

    host: str
    url: str
    endpoint: str
    session: object = field(init=False, default=requests.Session())
    sleep_time: int = field(default=0)
    debug: bool = field(default=False)

    def __post_init__(self):
        """Initialize the class instance."""

        self.full_url = (
            f"{self.host}/{self.url}/{self.endpoint}"
            if not self.endpoint == ""
            else f"{self.host}/{self.url}"
        )
        try:
            self.response = self.session.get(self.full_url)
            if not self.response.ok:
                return self.response.raise_for_status()
        except Exception as e:
            raise e

    @property
    def get_keys(self):
        """Return a list of keys from the JSON response."""
        if isinstance(self.response.json(), list):
            return self.response.json()[0].keys()
        return self.response.json().keys()

    @property
    def is_paged(self):
        """Return True if the endpoint is paged, False otherwise."""

        return "X-WP-TotalPages" in self.response.headers

    @property
    def get_total_pages(self):
        """Return the total number of pages."""

        if self.is_paged:
            return int(self.response.headers["X-WP-TotalPages"])

        return 1

    @property
    def get_total_results(self):
        """Return the total number of results."""

        if "X-WP-Total" in self.response.headers:
            return int(self.response.headers["X-WP-Total"])

    def generate_paged_endpoints(self):
        """Generate a list of URLs that can be fetched.
        The 'page' parameter is always appended to the URL.
        Returns:
            A list of URLs.
        Example:
            [
                "https://foo.com/endpoint/bar/baz?page=1",
                "https://foo.com/endpoint/bar/baz?page=2",
            ]
        """

        total_pages = self.get_total_pages

        if self.debug and total_pages > self.debug:
            total_pages = self.debug

        endpoint_list = []
        for page in range(1, total_pages + 1):
            endpoint_list.append(f"{self.full_url}?page={page}")
        return endpoint_list
