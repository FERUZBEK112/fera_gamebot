import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parent
HTML = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "web" / "app.js").read_text(encoding="utf-8")


class MiniAppTest(unittest.TestCase):
    def test_every_game_card_has_an_explicit_route(self):
        cards = re.findall(r'data-game="([^"]+)"', HTML)
        self.assertGreaterEqual(len(cards), 9)
        route_match = re.search(r"var games=\{([^}]+)\}", APP)
        self.assertIsNotNone(route_match)
        routes = route_match.group(1)
        for game in cards:
            self.assertIn(game + ":", routes, game + " card has no JavaScript route")

    def test_multi_element_handlers_use_query_selector_all(self):
        broken = re.findall(r"(?<!\$)\$\([^\n;]+\)\.forEach", APP)
        self.assertEqual([], broken, "querySelector cannot be used with forEach")

    def test_music_and_cache_busting_are_enabled(self):
        self.assertIn("function startMusic()", APP)
        self.assertIn("function stopMusic()", APP)
        self.assertRegex(HTML, r'app\.js\?v=\d+')


if __name__ == "__main__":
    unittest.main()
