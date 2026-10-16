import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parent
HTML = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
I18N = (ROOT / "web" / "i18n.js").read_text(encoding="utf-8")


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

    def test_three_language_chooser_is_complete(self):
        for language in ("uz", "ru", "en"):
            self.assertIn('data-language="' + language + '"', HTML)
            self.assertIn(language + ":{", I18N)
        self.assertIn("changeLanguageBtn", HTML)
        self.assertIn("onFeraLanguageChange", APP)
        self.assertIn("/api/language", APP)

    def test_language_switch_has_click_delegation_and_local_precedence(self):
        self.assertIn('target.closest("[data-language]")', I18N)
        self.assertIn("localLanguage", APP)
        self.assertIn("profile.language!==localLanguage", APP)

    def test_quiz_content_is_fully_localized(self):
        self.assertIn("QUIZ_BANKS", APP)
        self.assertIn("Какой город является столицей Узбекистана?", APP)
        self.assertIn("What is the capital of Uzbekistan?", APP)
        self.assertIn('challengeText("quizSub")', APP)
        self.assertNotIn("shuffle(QUIZ_BANK.slice())", APP)

    def test_music_and_cache_busting_are_enabled(self):
        self.assertIn("function startMusic()", APP)
        self.assertIn("function stopMusic()", APP)
        self.assertRegex(HTML, r'app\.js\?v=\d+')


if __name__ == "__main__":
    unittest.main()
