"""Basic unit tests for apiaberta-py SDK."""

import sys
import os
import unittest

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from apiaberta import ApiAberta, ApiAbertaError


class TestApiAbertaInit(unittest.TestCase):
    def test_instantiates(self):
        api = ApiAberta()
        self.assertIsInstance(api, ApiAberta)

    def test_api_key_stored(self):
        api = ApiAberta(api_key="my-key")
        self.assertEqual(api.api_key, "my-key")

    def test_base_url_trailing_slash_stripped(self):
        api = ApiAberta(base_url="http://localhost:4000/v1/")
        self.assertFalse(api.base_url.endswith("/"))

    def test_env_var_fallback(self):
        os.environ["APIABERTA_KEY"] = "env-key"
        api = ApiAberta()
        self.assertEqual(api.api_key, "env-key")
        del os.environ["APIABERTA_KEY"]

    def test_explicit_key_overrides_env(self):
        os.environ["APIABERTA_KEY"] = "env-key"
        api = ApiAberta(api_key="explicit-key")
        self.assertEqual(api.api_key, "explicit-key")
        del os.environ["APIABERTA_KEY"]


class TestApiAbertaErrors(unittest.TestCase):
    def test_error_is_exception(self):
        err = ApiAbertaError("test", 404)
        self.assertIsInstance(err, Exception)
        self.assertEqual(err.status_code, 404)

    def test_usage_without_key_raises(self):
        api = ApiAberta()
        with self.assertRaises(ApiAbertaError) as ctx:
            api.usage()
        self.assertEqual(ctx.exception.status_code, 401)

    def test_weather_city_without_id_raises(self):
        api = ApiAberta()
        with self.assertRaises(ApiAbertaError) as ctx:
            api.weather_city(None)
        self.assertEqual(ctx.exception.status_code, 400)


class TestBdpMethods(unittest.TestCase):
    def test_bdp_rates_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.bdp_rates))

    def test_bdp_lending_rates_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.bdp_lending_rates))

    def test_bdp_meta_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.bdp_meta))


class TestGeoMethods(unittest.TestCase):
    def test_geo_districts_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.geo_districts))

    def test_geo_district_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.geo_district))

    def test_geo_municipalities_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.geo_municipalities))

    def test_geo_municipality_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.geo_municipality))

    def test_geo_parishes_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.geo_parishes))

    def test_geo_postal_method_exists(self):
        api = ApiAberta()
        self.assertTrue(callable(api.geo_postal))

    def test_geo_district_without_id_raises(self):
        api = ApiAberta()
        with self.assertRaises(ApiAbertaError) as ctx:
            api.geo_district("")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_geo_municipality_without_slug_raises(self):
        api = ApiAberta()
        with self.assertRaises(ApiAbertaError) as ctx:
            api.geo_municipality("")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_geo_postal_without_code_raises(self):
        api = ApiAberta()
        with self.assertRaises(ApiAbertaError) as ctx:
            api.geo_postal("")
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
