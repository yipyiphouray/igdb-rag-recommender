import unittest

import pandas as pd

from src.app.filters import apply_catalog_filters, sort_catalog


def sample_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "game_id": 1,
                "name": "Neon RPG",
                "summary": "A cyberpunk fantasy role playing game.",
                "release_year": 2021,
                "platforms_list": "PC (Microsoft Windows) | Nintendo Switch",
                "genres_list": "Role-playing (RPG) | Adventure",
                "themes_list": "Fantasy | Science fiction",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Third person",
                "extraction_cohort": "quality",
                "total_rating": 88.0,
                "total_rating_count": 150,
                "custom_interest_percentile": 0.40,
                "hidden_gem_balanced_flag": 1,
            },
            {
                "game_id": 2,
                "name": "Arena Shooter",
                "summary": "A multiplayer action shooter.",
                "release_year": 2023,
                "platforms_list": "PC (Microsoft Windows) | PlayStation 5",
                "genres_list": "Shooter",
                "themes_list": "Action | Warfare",
                "game_modes_list": "Multiplayer",
                "player_perspectives_list": "First person",
                "extraction_cohort": "popularity",
                "total_rating": 74.0,
                "total_rating_count": 500,
                "custom_interest_percentile": 0.95,
                "hidden_gem_balanced_flag": 0,
            },
            {
                "game_id": 3,
                "name": "Quiet Puzzle",
                "summary": "A short cozy puzzle game.",
                "release_year": 2019,
                "platforms_list": "Nintendo Switch | iOS",
                "genres_list": "Puzzle | Indie",
                "themes_list": "Kids | Mystery",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Bird view / Isometric",
                "extraction_cohort": "comparison",
                "total_rating": 81.0,
                "total_rating_count": 40,
                "custom_interest_percentile": 0.15,
                "hidden_gem_balanced_flag": 0,
            },
            {
                "game_id": 3,
                "name": "Quiet Puzzle Duplicate",
                "summary": "Duplicate row that should be removed by game_id.",
                "release_year": 2019,
                "platforms_list": "Nintendo Switch",
                "genres_list": "Puzzle",
                "themes_list": "Kids",
                "game_modes_list": "Single player",
                "player_perspectives_list": "Bird view / Isometric",
                "extraction_cohort": "comparison",
                "total_rating": 81.0,
                "total_rating_count": 40,
                "custom_interest_percentile": 0.15,
                "hidden_gem_balanced_flag": 0,
            },
        ]
    )


class AppFilterTests(unittest.TestCase):
    def test_combined_filters_return_expected_game(self):
        result = apply_catalog_filters(
            sample_catalog(),
            search_text="cyberpunk",
            release_year_range=(2020, 2022),
            platforms=["PC (Microsoft Windows)"],
            genres=["Role-playing (RPG)"],
            themes=["Fantasy"],
            game_modes=["Single player"],
            perspectives=["Third person"],
            cohorts=["quality"],
            min_rating=85,
            min_rating_count=100,
            hidden_gems_only=True,
        )

        self.assertEqual(result["game_id"].tolist(), [1])

    def test_filters_deduplicate_by_game_id(self):
        result = apply_catalog_filters(sample_catalog(), genres=["Puzzle"])

        self.assertEqual(result["game_id"].tolist(), [3])
        self.assertEqual(len(result), result["game_id"].nunique())

    def test_missing_rating_is_not_promoted_by_min_rating_filter(self):
        catalog = pd.concat(
            [
                sample_catalog(),
                pd.DataFrame(
                    [
                        {
                            "game_id": 4,
                            "name": "Unrated Game",
                            "summary": "No rating yet.",
                            "release_year": 2024,
                            "platforms_list": "PC (Microsoft Windows)",
                            "genres_list": "Adventure",
                            "themes_list": "Mystery",
                            "game_modes_list": "Single player",
                            "player_perspectives_list": "Third person",
                            "extraction_cohort": "comparison",
                            "total_rating": float("nan"),
                            "total_rating_count": float("nan"),
                            "custom_interest_percentile": float("nan"),
                            "hidden_gem_balanced_flag": 0,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

        result = apply_catalog_filters(catalog, min_rating=1, min_rating_count=1)

        self.assertNotIn(4, result["game_id"].tolist())

    def test_sort_catalog_handles_known_and_unknown_sort_options(self):
        catalog = sample_catalog().drop_duplicates("game_id")

        by_rating = sort_catalog(catalog, "Highest rating")
        self.assertEqual(by_rating.iloc[0]["game_id"], 1)

        by_visibility = sort_catalog(catalog, "Lowest visibility among reliable high-rated games")
        self.assertEqual(by_visibility.iloc[0]["game_id"], 3)

        by_unknown = sort_catalog(catalog, "Not a real sort")
        self.assertEqual(by_unknown["name"].tolist(), sorted(catalog["name"].tolist()))


if __name__ == "__main__":
    unittest.main()
