import pytest
import responses

from importer_generator.wordpress.probe import JsonResponseProbe


class TestJsonResponseProbe:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_instance(self):
        probe = JsonResponseProbe(
            host="http://domain.com", url="some/resource", endpoint="an-endpoint"
        )
        assert isinstance(probe, JsonResponseProbe)

    def test_instance_raises(self):
        with pytest.raises(TypeError) as e:
            JsonResponseProbe()
        assert "'host', 'url', and 'endpoint'" in str(e.value)

    def test_is_paged(self):
        with responses.RequestsMock() as r:
            r.add(
                responses.GET,
                "http://domain.com/some/resource/an-endpoint",
                headers={"X-WP-TotalPages": "2"},
            )
            probe = JsonResponseProbe(
                host="http://domain.com",
                url="some/resource",
                endpoint="an-endpoint",
            )
            assert probe.is_paged is True
            assert probe.get_total_pages == 2

    def test_is_not_paged(self):
        with responses.RequestsMock() as r:
            r.add(
                responses.GET,
                "http://domain.com/some/resource/an-endpoint",
                headers={},
            )
            probe = JsonResponseProbe(
                host="http://domain.com",
                url="some/resource",
                endpoint="an-endpoint",
            )
            assert probe.is_paged is False
            assert probe.get_total_pages == 1

    def test_get_total_results_is_paged(self):
        with responses.RequestsMock() as r:
            r.add(
                responses.GET,
                "http://domain.com/some/resource/an-endpoint",
                headers={"X-WP-Total": "200", "X-WP-TotalPages": "2"},
            )
            probe = JsonResponseProbe(
                host="http://domain.com",
                url="some/resource",
                endpoint="an-endpoint",
            )
            assert probe.get_total_results == 200

    def test_get_total_results_is_not_paged(self):
        with responses.RequestsMock() as r:
            r.add(
                responses.GET,
                "http://domain.com/some/resource/an-endpoint",
                headers={"X-WP-Total": "100"},
            )
            probe = JsonResponseProbe(
                host="http://domain.com",
                url="some/resource",
                endpoint="an-endpoint",
            )
            assert probe.get_total_results == 100

    def test_generate_paged_endpoints(self):
        with responses.RequestsMock() as r:
            r.add(
                responses.GET,
                "http://domain.com/some/resource/an-endpoint",
                headers={"X-WP-TotalPages": "2", "X-WP-Total": "200"},
            )
            probe = JsonResponseProbe(
                host="http://domain.com",
                url="some/resource",
                endpoint="an-endpoint",
            )
            assert probe.generate_paged_endpoints() == [
                "http://domain.com/some/resource/an-endpoint?page=1",
                "http://domain.com/some/resource/an-endpoint?page=2",
            ]

    def test_generate_paged_no_endpoint(self):
        with responses.RequestsMock() as r:
            r.add(
                responses.GET,
                "http://domain.com/some/resource",
                headers={"X-WP-TotalPages": "2", "X-WP-Total": "200"},
            )
            probe = JsonResponseProbe(
                host="http://domain.com", url="some/resource", endpoint=""
            )
            assert probe.generate_paged_endpoints() == [
                "http://domain.com/some/resource?page=1",
                "http://domain.com/some/resource?page=2",
            ]
