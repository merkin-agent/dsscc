"""Offline coverage for the automatic provider fallback chain and real auth flow."""

import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "DS Style Thumbnail Scraper.py"
SPEC = importlib.util.spec_from_file_location("thumbnail_scraper_provider_chain_test", APP_PATH)
APP_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = APP_MODULE
SPEC.loader.exec_module(APP_MODULE)


class Value:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


def png_bytes():
    stream = io.BytesIO()
    Image.new("RGB", (20, 32), (12, 30, 70)).save(stream, format="PNG")
    return stream.getvalue()


def make_provider_app(tmp_path):
    return SimpleNamespace(
        base_dir=Path(tmp_path),
        tgdb_key_var=Value("tgdb-key"),
        ss_dev_id_var=Value("ss-developer"),
        ss_dev_pass_var=Value("ss-developer-secret"),
        ss_user_var=Value(""),
        ss_pass_var=Value(""),
        igdb_client_var=Value("twitch-client-id"),
        igdb_secret_var=Value("twitch-client-secret"),
        igdb_token_var=Value(""),
    )


class ProviderFallbackChainTests(unittest.TestCase):
    def test_request_json_reads_and_closes_a_bounded_response(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"ok": true}'

        with patch.object(APP_MODULE.urllib.request, "urlopen", return_value=response):
            payload = APP_MODULE.request_json("https://api.example/data")

        self.assertEqual(payload, {"ok": True})
        response.read.assert_called_once_with(APP_MODULE.MAX_PROVIDER_JSON_BYTES + 1)
        response.__exit__.assert_called_once()

    def test_json_provider_helpers_cap_response_size(self):
        requests = (
            (APP_MODULE.request_json, ("https://api.example/data",)),
            (APP_MODULE.post_json, ("https://api.example/data", "{}", {})),
            (APP_MODULE.post_form_json, ("https://api.example/token", {"grant_type": "client_credentials"})),
        )
        for request_method, args in requests:
            with self.subTest(method=request_method.__name__):
                response = Mock()
                response.__enter__ = Mock(return_value=response)
                response.__exit__ = Mock(return_value=False)
                response.read.return_value = b"x" * 9
                with patch.object(APP_MODULE, "MAX_PROVIDER_JSON_BYTES", 8), patch.object(
                    APP_MODULE.urllib.request, "urlopen", return_value=response
                ):
                    with self.assertRaisesRegex(ValueError, "exceeds the 10 MiB limit"):
                        request_method(*args)
                response.read.assert_called_once_with(9)

    def test_fetch_bytes_caps_download_size(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b"x" * 9
        opener = Mock()
        opener.open.return_value = response

        with patch.object(APP_MODULE, "MAX_REMOTE_IMAGE_BYTES", 8), patch.object(
            APP_MODULE.urllib.request, "build_opener", return_value=opener
        ):
            with self.assertRaisesRegex(ValueError, "exceeds the 25 MiB download limit"):
                APP_MODULE.fetch_bytes("https://cdn.thegamesdb.net/art.png", provider="TheGamesDB")

        response.read.assert_called_once_with(9)

    def test_fetch_bytes_rejects_unapproved_hosts_and_schemes_before_network(self):
        unsafe_urls = (
            "http://cdn.thegamesdb.net/art.png",
            "https://127.0.0.1/art.png",
            "https://images.example/art.png",
            "https://user@cdn.thegamesdb.net/art.png",
            "https://cdn.thegamesdb.net:8443/art.png",
        )
        with patch.object(APP_MODULE.urllib.request, "build_opener") as build_opener:
            for url in unsafe_urls:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    APP_MODULE.fetch_bytes(url, provider="TheGamesDB")
        build_opener.assert_not_called()

    def test_image_redirect_rejects_unapproved_destination(self):
        handler = APP_MODULE._ProviderImageRedirectHandler("TheGamesDB")
        request = APP_MODULE.urllib.request.Request("https://cdn.thegamesdb.net/art.png")

        with self.assertRaisesRegex(ValueError, "outside its approved HTTPS hosts"):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "http://127.0.0.1/private",
            )

    def test_image_redirect_allows_approved_https_cdn_subdomain(self):
        handler = APP_MODULE._ProviderImageRedirectHandler("TheGamesDB")
        request = APP_MODULE.urllib.request.Request("https://cdn.thegamesdb.net/art.png")

        redirected = handler.redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://images.cdn.thegamesdb.net/art.png",
        )

        self.assertEqual(redirected.full_url, "https://images.cdn.thegamesdb.net/art.png")

    def test_chain_order_is_tgdb_then_screenscraper_then_igdb(self):
        with tempfile.TemporaryDirectory() as temp:
            providers = APP_MODULE.Providers(make_provider_app(temp))
            libretro = Mock(side_effect=LookupError("libretro image miss"))
            tgdb = Mock(side_effect=LookupError("TGDB no match"))
            ss = Mock(return_value=[APP_MODULE.ProviderResult("ScreenScraper", "invalid", b"<html>bad</html>", "Game Boy")])
            expected = APP_MODULE.ProviderResult("IGDB", "Tetris cover", png_bytes(), "Game Boy")
            igdb = Mock(return_value=[expected])
            providers.search_libretro_many = libretro
            providers.search_thegamesdb_many = tgdb
            providers.search_screenscraper_many = ss
            providers.search_igdb_many = igdb

            result = providers.search_many("Libretro", "Tetris", max_results=1, system="Game Boy")

            self.assertEqual(result, [expected])
            libretro.assert_called_once_with("Tetris", 1, None, "Game Boy")
            tgdb.assert_called_once_with("Tetris", 1, system="Game Boy")
            ss.assert_called_once_with("Tetris", 1, system="Game Boy")
            igdb.assert_called_once_with("Tetris", 1, system="Game Boy")

    def test_igdb_obtains_oauth_token_and_filters_games_to_requested_system(self):
        with tempfile.TemporaryDirectory() as temp:
            providers = APP_MODULE.Providers(make_provider_app(temp))
            image = png_bytes()
            post_calls = []

            def fake_post_json(url, body, headers):
                post_calls.append((url, body, headers))
                if url.endswith("/platforms"):
                    return [{"id": 33, "name": "Game Boy", "slug": "game-boy"}]
                if url.endswith("/games"):
                    return [{"name": "Tetris", "cover": {"image_id": "cover123"}, "artworks": []}]
                raise AssertionError(f"Unexpected IGDB URL: {url}")

            with patch.object(
                APP_MODULE,
                "post_form_json",
                return_value={"access_token": "oauth-token", "expires_in": 3600},
            ) as token_request, patch.object(APP_MODULE, "post_json", side_effect=fake_post_json), patch.object(
                APP_MODULE, "fetch_bytes", return_value=image
            ):
                results = providers.search_igdb_many("Tetris", max_results=1, system="Game Boy")

            token_request.assert_called_once_with(
                "https://id.twitch.tv/oauth2/token",
                {
                    "client_id": "twitch-client-id",
                    "client_secret": "twitch-client-secret",
                    "grant_type": "client_credentials",
                },
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].provider, "IGDB")
            self.assertEqual(results[0].system, "Game Boy")
            game_query = next(body for url, body, _headers in post_calls if url.endswith("/games"))
            self.assertIn("where platforms = (33)", game_query)
            self.assertTrue(all(call[2]["Authorization"] == "Bearer oauth-token" for call in post_calls))

    def test_screenscraper_search_uses_resolved_system_id_and_rejects_bad_image_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            providers = APP_MODULE.Providers(make_provider_app(temp))
            requested_urls = []

            def fake_request_json(url, _headers=None):
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if parsed.path.endswith("/systemesListe.php"):
                    return {
                        "response": {
                            "systemes": {
                                "systeme": [
                                    {"id": "9", "noms": {"nom_eu": "Nintendo Game Boy", "nom_us": "Game Boy"}},
                                    {"id": "12", "noms": {"nom_eu": "Nintendo Game Boy Advance"}},
                                ]
                            }
                        }
                    }
                if parsed.path.endswith("/jeuRecherche.php"):
                    self.assertEqual(params["systemeid"], ["9"])
                    self.assertEqual(params["recherche"], ["Tetris"])
                    return {
                        "response": {
                            "jeux": {
                                "jeu": {
                                    "id": "44",
                                    "nom": "Tetris",
                                    "medias": {
                                        "media": [
                                            {"type": "box-2D", "url": "https://www.screenscraper.fr/bad.png"},
                                            {"type": "box-3D", "url": "https://www.screenscraper.fr/good.png"},
                                        ]
                                    },
                                }
                            }
                        }
                    }
                raise AssertionError(f"Unexpected ScreenScraper URL: {url}")

            def fake_fetch(url, provider, headers=None):
                requested_urls.append(url)
                if url.endswith("bad.png"):
                    return b"not an image"
                return png_bytes()

            with patch.object(APP_MODULE, "request_json", side_effect=fake_request_json), patch.object(
                APP_MODULE, "fetch_bytes", side_effect=fake_fetch
            ):
                results = providers.search_screenscraper_many("Tetris", max_results=1, system="Game Boy")

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].provider, "ScreenScraper")
            self.assertEqual(results[0].system, "Game Boy")
            self.assertEqual(requested_urls, ["https://www.screenscraper.fr/bad.png", "https://www.screenscraper.fr/good.png"])

    def test_screen_scraper_requires_developer_credentials_but_user_credentials_are_optional(self):
        with tempfile.TemporaryDirectory() as temp:
            app = make_provider_app(temp)
            app.ss_dev_id_var = Value("")
            providers = APP_MODULE.Providers(app)
            with self.assertRaisesRegex(LookupError, "developer ID"):
                providers._screenscraper_credentials()

            app.ss_dev_id_var = Value("developer")
            app.ss_dev_pass_var = Value("password")
            params = providers._screenscraper_credentials()
            self.assertEqual(params["devid"], "developer")
            self.assertNotIn("ssid", params)
            app.ss_user_var = Value("username")
            with self.assertRaisesRegex(LookupError, "both be filled"):
                providers._screenscraper_credentials()


if __name__ == "__main__":
    unittest.main()
