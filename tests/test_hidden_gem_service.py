import unittest

import pandas as pd

from src.app.hidden_gem_service import filter_hidden_gems, hidden_gem_rule_text


def hidden_gem_artifact() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "game_id": 1,
                "name": "Balanced Gem",
                "release_year": 2021,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Adventure",
                "themes_list": "Mystery",
                "total_rating": 84.0,
                "total_rating_count": 40,
                "hidden_gem_score": 0.80,
                "candidate_explanation": "Balanced candidate.",
            },
            {
                "game_id": 2,
                "name": "Weak Evidence",
                "release_year": 2021,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Adventure",
                "themes_list": "Mystery",
                "total_rating": 86.0,
                "total_rating_count": 10,
                "hidden_gem_score": 0.90,
                "candidate_explanation": "Should be filtered by rating evidence.",
            },
        ]
    )


def full_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "game_id": 10,
                "name": "Conservative Gem",
                "release_year": 2022,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Adventure",
                "themes_list": "Mystery",
                "extraction_cohort": "quality",
                "main_game_flag": 1,
                "popscore_available_flag": 1,
                "rating_reliable_flag": 1,
                "total_rating": 88.0,
                "total_rating_count": 60,
                "visibility_percentile_eligible_pool": 0.20,
                "inverse_visibility_percentile": 0.80,
            },
            {
                "game_id": 11,
                "name": "Broad Gem",
                "release_year": 2022,
                "platforms_list": "Nintendo Switch",
                "genres_list": "Puzzle",
                "themes_list": "Fantasy",
                "extraction_cohort": "quality",
                "main_game_flag": 1,
                "popscore_available_flag": 1,
                "rating_reliable_flag": 1,
                "total_rating": 77.0,
                "total_rating_count": 30,
                "visibility_percentile_eligible_pool": 0.45,
                "inverse_visibility_percentile": 0.55,
            },
            {
                "game_id": 12,
                "name": "Too Visible",
                "release_year": 2022,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Adventure",
                "themes_list": "Mystery",
                "extraction_cohort": "quality",
                "main_game_flag": 1,
                "popscore_available_flag": 1,
                "rating_reliable_flag": 1,
                "total_rating": 91.0,
                "total_rating_count": 100,
                "visibility_percentile_eligible_pool": 0.80,
                "inverse_visibility_percentile": 0.20,
            },
            {
                "game_id": 13,
                "name": "Wrong Cohort",
                "release_year": 2022,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Adventure",
                "themes_list": "Mystery",
                "extraction_cohort": "comparison",
                "main_game_flag": 1,
                "popscore_available_flag": 1,
                "rating_reliable_flag": 1,
                "total_rating": 95.0,
                "total_rating_count": 100,
                "visibility_percentile_eligible_pool": 0.10,
                "inverse_visibility_percentile": 0.90,
            },
        ]
    )


class HiddenGemServiceTests(unittest.TestCase):
    def test_balanced_view_uses_hidden_gem_artifact_and_rating_evidence_filter(self):
        results = filter_hidden_gems(hidden_gem_artifact(), sensitivity="Balanced")

        self.assertEqual(results["game_id"].tolist(), [1])

    def test_conservative_view_rebuilds_from_catalog_with_stricter_thresholds(self):
        results = filter_hidden_gems(
            hidden_gem_artifact(),
            catalog=full_catalog(),
            sensitivity="Conservative",
        )

        self.assertEqual(results["game_id"].tolist(), [10])
        self.assertTrue((results["total_rating"] >= 85).all())
        self.assertTrue((results["visibility_percentile_eligible_pool"] <= 0.25).all())

    def test_broad_view_includes_broader_low_visibility_candidates(self):
        results = filter_hidden_gems(
            hidden_gem_artifact(),
            catalog=full_catalog(),
            sensitivity="Broad",
        )

        self.assertEqual(set(results["game_id"].tolist()), {10, 11})
        self.assertNotIn(12, results["game_id"].tolist())
        self.assertNotIn(13, results["game_id"].tolist())

    def test_rule_text_reflects_selected_sensitivity(self):
        text = hidden_gem_rule_text("Conservative")

        self.assertIn("Conservative", text)
        self.assertIn("total rating >= 85", text)
        self.assertIn("visibility percentile <= 25%", text)


if __name__ == "__main__":
    unittest.main()
