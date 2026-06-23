import unittest

from src.app.data_loader import load_app_catalog, load_hidden_gems
from src.app.recommendation_service import recommend_games
from src.app.validation import validate_catalog, validate_hidden_gems


class AppDataValidationTests(unittest.TestCase):
    def test_catalog_artifact_is_valid(self):
        catalog = load_app_catalog()
        self.assertEqual(validate_catalog(catalog), [])
        self.assertEqual(catalog["game_id"].nunique(), len(catalog))

    def test_hidden_gem_artifact_is_valid(self):
        hidden_gems = load_hidden_gems()
        self.assertEqual(validate_hidden_gems(hidden_gems), [])
        self.assertGreater(len(hidden_gems), 0)

    def test_recommendations_respect_platform_gate(self):
        catalog = load_app_catalog()
        results = recommend_games(catalog, platform="PC (Microsoft Windows)", genres=["Role-playing (RPG)"], top_n=5)
        self.assertLessEqual(len(results), 5)
        if not results.empty:
            self.assertTrue(results["platforms_list"].str.contains("PC \\(Microsoft Windows\\)", regex=True).all())


if __name__ == "__main__":
    unittest.main()
