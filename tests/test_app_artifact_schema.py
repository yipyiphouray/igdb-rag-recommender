import unittest

from src.app.data_loader import load_app_catalog, load_filter_options, load_hidden_gems, load_json_artifact
from src.app import config


CATALOG_PAGE_COLUMNS = {
    "game_id",
    "name",
    "summary",
    "release_year",
    "cover_url",
    "platforms_list",
    "genres_list",
    "themes_list",
    "game_modes_list",
    "player_perspectives_list",
    "extraction_cohort",
    "total_rating",
    "total_rating_count",
    "custom_interest_percentile",
    "popscore_available_flag",
    "normal_playtime_hours",
    "rating_available_flag",
    "rating_reliable_flag",
    "hidden_gem_balanced_flag",
}

HIDDEN_GEM_PAGE_COLUMNS = {
    "game_id",
    "name",
    "release_year",
    "platforms_list",
    "genres_list",
    "themes_list",
    "total_rating",
    "total_rating_count",
    "visibility_percentile_eligible_pool",
    "hidden_gem_score",
    "candidate_explanation",
}

FILTER_OPTION_KEYS = {
    "release_years",
    "genres",
    "themes",
    "platforms",
    "game_modes",
    "player_perspectives",
    "cohorts",
}

METHODOLOGY_KEYS = {
    "total_games",
    "release_year_start",
    "release_year_end",
    "hidden_gem_count",
    "popscore_coverage",
    "reliable_rating_coverage",
}


class AppArtifactSchemaTests(unittest.TestCase):
    def test_catalog_has_columns_required_by_streamlit_pages(self):
        catalog = load_app_catalog()
        missing = CATALOG_PAGE_COLUMNS.difference(catalog.columns)

        self.assertEqual(missing, set())
        self.assertEqual(catalog["game_id"].nunique(), len(catalog))
        self.assertFalse(catalog["name"].fillna("").eq("").any())

    def test_hidden_gem_artifact_has_page_columns_and_catalog_membership(self):
        catalog = load_app_catalog()
        hidden_gems = load_hidden_gems()
        missing = HIDDEN_GEM_PAGE_COLUMNS.difference(hidden_gems.columns)

        self.assertEqual(missing, set())
        self.assertGreater(len(hidden_gems), 0)
        self.assertTrue(set(hidden_gems["game_id"]).issubset(set(catalog["game_id"])))

    def test_filter_options_support_sidebar_controls(self):
        options = load_filter_options()
        missing = FILTER_OPTION_KEYS.difference(options.keys())

        self.assertEqual(missing, set())
        for key in FILTER_OPTION_KEYS:
            self.assertIsInstance(options[key], list)
            self.assertGreater(len(options[key]), 0)

    def test_methodology_metrics_support_home_and_methodology_pages(self):
        metrics = load_json_artifact(config.APP_METHODOLOGY_METRICS_PATH)
        missing = METHODOLOGY_KEYS.difference(metrics.keys())

        self.assertEqual(missing, set())
        self.assertGreater(metrics["total_games"], 0)
        self.assertLessEqual(metrics["release_year_start"], metrics["release_year_end"])


if __name__ == "__main__":
    unittest.main()
