import unittest

import pandas as pd

from src.app.recommendation_service import recommend_games


def recommendation_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "game_id": 1,
                "name": "Hidden RPG",
                "summary": "A strong but less visible fantasy RPG.",
                "release_year": 2021,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Role-playing (RPG)",
                "themes_list": "Fantasy",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Third person",
                "extraction_cohort": "quality",
                "total_rating": 82.0,
                "total_rating_count": 30,
                "custom_interest_percentile": 0.20,
                "normal_playtime_hours": 8.0,
                "hidden_gem_balanced_flag": 1,
            },
            {
                "game_id": 2,
                "name": "Popular RPG",
                "summary": "A very visible fantasy RPG.",
                "release_year": 2022,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Role-playing (RPG)",
                "themes_list": "Fantasy",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Third person",
                "extraction_cohort": "popularity",
                "total_rating": 90.0,
                "total_rating_count": 500,
                "custom_interest_percentile": 0.95,
                "normal_playtime_hours": 42.0,
                "hidden_gem_balanced_flag": 0,
            },
            {
                "game_id": 3,
                "name": "Switch Puzzle",
                "summary": "A short puzzle game for Switch.",
                "release_year": 2020,
                "platforms_list": "Nintendo Switch",
                "genres_list": "Puzzle",
                "themes_list": "Mystery",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Bird view / Isometric",
                "extraction_cohort": "comparison",
                "total_rating": 88.0,
                "total_rating_count": 100,
                "custom_interest_percentile": 0.70,
                "normal_playtime_hours": 6.0,
                "hidden_gem_balanced_flag": 0,
            },
        ]
    )


class RecommendationServiceTests(unittest.TestCase):
    def test_platform_gate_limits_results_to_selected_platform(self):
        results = recommend_games(
            recommendation_catalog(),
            platform="Nintendo Switch",
            genres=["Puzzle"],
            top_n=10,
        )

        self.assertEqual(results["game_id"].tolist(), [3])
        self.assertTrue(results["platforms_list"].str.contains("Nintendo Switch", regex=False).all())

    def test_hidden_gem_preference_boosts_documented_hidden_gem(self):
        results = recommend_games(
            recommendation_catalog(),
            platform="PC (Microsoft Windows)",
            genres=["Role-playing (RPG)"],
            themes=["Fantasy"],
            discovery_preference="Hidden gems",
            top_n=2,
        )

        self.assertEqual(results.iloc[0]["game_id"], 1)
        self.assertGreater(results.iloc[0]["hidden_gem_score_component"], 0)
        self.assertIn("hidden-gem candidate", results.iloc[0]["recommendation_explanation"])

    def test_popular_preference_boosts_visible_game(self):
        results = recommend_games(
            recommendation_catalog(),
            platform="PC (Microsoft Windows)",
            genres=["Role-playing (RPG)"],
            themes=["Fantasy"],
            discovery_preference="Popular / visible games",
            top_n=2,
        )

        self.assertEqual(results.iloc[0]["game_id"], 2)
        self.assertGreater(results.iloc[0]["visibility_score_component"], 0)

    def test_rating_level_is_a_hard_quality_filter(self):
        results = recommend_games(
            recommendation_catalog(),
            platform="PC (Microsoft Windows)",
            rating_level="Exceptional (90+)",
            top_n=10,
        )

        self.assertEqual(results["game_id"].tolist(), [2])

    def test_playtime_preference_adds_fit_bonus_without_excluding_games(self):
        results = recommend_games(
            recommendation_catalog(),
            genres=["Role-playing (RPG)"],
            desired_playtime="Shorter games",
            top_n=3,
        )

        hidden_rpg = results[results["game_id"] == 1].iloc[0]
        popular_rpg = results[results["game_id"] == 2].iloc[0]
        self.assertGreater(hidden_rpg["playtime_score_component"], popular_rpg["playtime_score_component"])
        self.assertIn("shorter games", hidden_rpg["recommendation_explanation"])


if __name__ == "__main__":
    unittest.main()
