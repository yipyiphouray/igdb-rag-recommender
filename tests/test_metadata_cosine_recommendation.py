import unittest

import pandas as pd

from src.app.metadata_cosine_recommendation import MetadataCosineRecommender


def cosine_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "game_id": 1,
                "name": "Space RPG Original",
                "summary": "A story rich science fiction RPG with space exploration and companions.",
                "release_year": 2020,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Role-playing (RPG) | Adventure",
                "themes_list": "Science fiction",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Third person",
                "keywords_list": "space | exploration | companions",
                "developers_list": "Example Studio",
                "publishers_list": "Example Publisher",
                "extraction_cohort": "popularity",
                "total_rating": 92.0,
                "total_rating_count": 800,
                "custom_interest_percentile": 0.95,
                "normal_playtime_hours": 42.0,
                "hidden_gem_balanced_flag": 0,
            },
            {
                "game_id": 2,
                "name": "Space RPG Sequel",
                "summary": "A science fiction RPG sequel about space exploration, companions, and choices.",
                "release_year": 2022,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Role-playing (RPG) | Adventure",
                "themes_list": "Science fiction",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Third person",
                "keywords_list": "space | exploration | companions",
                "developers_list": "Example Studio",
                "publishers_list": "Example Publisher",
                "extraction_cohort": "quality",
                "total_rating": 88.0,
                "total_rating_count": 350,
                "custom_interest_percentile": 0.70,
                "normal_playtime_hours": 38.0,
                "hidden_gem_balanced_flag": 0,
            },
            {
                "game_id": 3,
                "name": "Cozy Farm Life",
                "summary": "A cozy farming and crafting game for relaxed play.",
                "release_year": 2021,
                "platforms_list": "Nintendo Switch",
                "genres_list": "Simulator | Adventure",
                "themes_list": "Sandbox",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Bird view / Isometric",
                "keywords_list": "farming | cozy | crafting",
                "developers_list": "Cozy Studio",
                "publishers_list": "Cozy Publisher",
                "extraction_cohort": "comparison",
                "total_rating": 84.0,
                "total_rating_count": 250,
                "custom_interest_percentile": 0.80,
                "normal_playtime_hours": 60.0,
                "hidden_gem_balanced_flag": 0,
            },
            {
                "game_id": 4,
                "name": "Obscure Space Tactics",
                "summary": "A smaller tactical science fiction game with space missions.",
                "release_year": 2019,
                "platforms_list": "PC (Microsoft Windows)",
                "genres_list": "Strategy | Tactical",
                "themes_list": "Science fiction",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Bird view / Isometric",
                "keywords_list": "space | tactical | missions",
                "developers_list": "Other Studio",
                "publishers_list": "Other Publisher",
                "extraction_cohort": "hidden_gem",
                "total_rating": 81.0,
                "total_rating_count": 45,
                "custom_interest_percentile": 0.18,
                "normal_playtime_hours": 18.0,
                "hidden_gem_balanced_flag": 1,
            },
        ]
    )


class MetadataCosineRecommenderTests(unittest.TestCase):
    def test_recent_game_seed_influences_ranking_and_is_excluded(self):
        recommender = MetadataCosineRecommender(cosine_catalog())

        output = recommender.recommend(
            platform="PC (Microsoft Windows)",
            genres=["Role-playing (RPG)"],
            themes=["Science fiction"],
            favorite_games=["Space RPG Original"],
            top_n=5,
        )

        self.assertEqual(output.matched_seed_games, ["Space RPG Original"])
        self.assertEqual(output.unmatched_seed_games, [])
        self.assertFalse(output.recommendations.empty)
        self.assertNotIn(1, output.recommendations["game_id"].tolist())
        self.assertEqual(output.recommendations.iloc[0]["game_id"], 2)
        self.assertTrue(
            output.recommendations["platforms_list"]
            .str.contains("PC (Microsoft Windows)", regex=False)
            .all()
        )

    def test_fuzzy_recent_game_title_matching(self):
        recommender = MetadataCosineRecommender(cosine_catalog())

        output = recommender.recommend(
            platform="PC (Microsoft Windows)",
            favorite_games=["Space RPG Orig"],
            top_n=5,
        )

        self.assertEqual(output.matched_seed_games, ["Space RPG Original"])
        self.assertNotIn(1, output.recommendations["game_id"].tolist())

    def test_unmatched_recent_game_is_reported_without_blocking_results(self):
        recommender = MetadataCosineRecommender(cosine_catalog())

        output = recommender.recommend(
            platform="PC (Microsoft Windows)",
            genres=["Strategy"],
            favorite_games=["Definitely Unknown Game"],
            top_n=5,
        )

        self.assertIn("Definitely Unknown Game", output.unmatched_seed_games)
        self.assertFalse(output.recommendations.empty)
        self.assertEqual(output.recommendations.iloc[0]["game_id"], 4)

    def test_empty_profile_returns_no_cosine_recommendations(self):
        recommender = MetadataCosineRecommender(cosine_catalog())

        output = recommender.recommend(top_n=5)

        self.assertTrue(output.recommendations.empty)


if __name__ == "__main__":
    unittest.main()
