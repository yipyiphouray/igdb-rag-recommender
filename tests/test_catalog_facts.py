import unittest
from unittest.mock import patch

import pandas as pd

from src.app import catalog_facts


class CatalogFactsTests(unittest.TestCase):
    def setUp(self):
        self.catalog = pd.DataFrame(
            [
                {
                    "game_id": 1,
                    "genres_list": "Indie | Adventure",
                    "platforms_list": "Nintendo Switch | PC (Microsoft Windows)",
                    "themes_list": "Fantasy",
                    "game_modes_list": "Single player",
                    "hidden_gem_balanced_flag": 1,
                },
                {
                    "game_id": 2,
                    "genres_list": "Indie | Puzzle",
                    "platforms_list": "PC (Microsoft Windows)",
                    "themes_list": "Comedy",
                    "game_modes_list": "Single player",
                    "hidden_gem_balanced_flag": 0,
                },
                {
                    "game_id": 3,
                    "genres_list": "Shooter",
                    "platforms_list": "PlayStation 5",
                    "themes_list": "Science fiction",
                    "game_modes_list": "Multiplayer",
                    "hidden_gem_balanced_flag": 0,
                },
            ]
        )
        self.filter_options = {
            "genres": ["Adventure", "Indie", "Puzzle", "Shooter"],
            "platforms": ["Nintendo Switch", "PC (Microsoft Windows)", "PlayStation 5"],
            "themes": ["Comedy", "Fantasy", "Science fiction"],
            "game_modes": ["Multiplayer", "Single player"],
        }

    def test_answers_genre_count_before_total_dataset_count(self):
        with patch.object(catalog_facts, "_load_catalog", return_value=self.catalog), patch.object(
            catalog_facts, "_load_filter_options", return_value=self.filter_options
        ):
            answer = catalog_facts.answer_catalog_count_question(
                "How many games are there in the Indie genre?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "catalog_genre_count")
        self.assertIn("2 games", answer.answer)
        self.assertIn("Indie", answer.answer)

    def test_answers_platform_alias_count(self):
        with patch.object(catalog_facts, "_load_catalog", return_value=self.catalog), patch.object(
            catalog_facts, "_load_filter_options", return_value=self.filter_options
        ):
            answer = catalog_facts.answer_catalog_count_question(
                "How many games are on Switch?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "catalog_platform_count")
        self.assertIn("1 games", answer.answer)
        self.assertIn("Nintendo Switch", answer.answer)

    def test_answers_hidden_gem_count_within_genre(self):
        with patch.object(catalog_facts, "_load_catalog", return_value=self.catalog), patch.object(
            catalog_facts, "_load_filter_options", return_value=self.filter_options
        ):
            answer = catalog_facts.answer_catalog_count_question(
                "How many hidden gem games are in the Indie genre?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "catalog_genre_count")
        self.assertIn("1 hidden-gem games", answer.answer)
        self.assertIn("Indie", answer.answer)

    def test_answers_catalog_count_from_structured_filters(self):
        with patch.object(catalog_facts, "_load_catalog", return_value=self.catalog), patch.object(
            catalog_facts, "_load_filter_options", return_value=self.filter_options
        ):
            answer = catalog_facts.answer_catalog_count_with_filters(
                {"genres": ["Indie"], "platforms": ["PC (Microsoft Windows)"]}
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "catalog_filtered_count")
        self.assertIn("2 games", answer.answer)
        self.assertIn("genre = Indie", answer.answer)
        self.assertIn("platform = PC (Microsoft Windows)", answer.answer)

    def test_answers_catalog_distribution(self):
        with patch.object(catalog_facts, "_load_catalog", return_value=self.catalog):
            answer = catalog_facts.answer_catalog_distribution("genres")

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "catalog_top_genres")
        self.assertIn("Indie: 2 games", answer.answer)

    def test_answers_specific_game_lookup(self):
        catalog = self.catalog.copy()
        catalog["name"] = ["Hades", "Celeste", "League of Legends"]
        catalog["release_year"] = [2018, 2018, 2009]
        catalog["total_rating"] = [90.0, 88.0, 78.0]
        catalog["total_rating_count"] = [1000, 500, 2500]
        catalog["summary"] = ["A rogue-like dungeon crawler.", "A platforming game.", "A MOBA."]
        catalog["rag_ready_flag"] = [1, 1, 1]

        with patch.object(catalog_facts, "_load_catalog", return_value=catalog):
            answer = catalog_facts.answer_game_lookup_question("What platforms is Hades on?")

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "game_lookup")
        self.assertEqual(answer.game_id, 1)
        self.assertIn("Hades is in the current app catalog", answer.answer)
        self.assertIn("Platforms include", answer.answer)

    def test_answers_game_compare_question(self):
        catalog = self.catalog.copy()
        catalog["name"] = ["Hades", "Celeste", "League of Legends"]
        catalog["release_year"] = [2018, 2018, 2009]
        catalog["total_rating"] = [90.0, 88.0, 78.0]
        catalog["total_rating_count"] = [1000, 500, 2500]
        catalog["summary"] = ["A rogue-like dungeon crawler.", "A platforming game.", "A MOBA."]
        catalog["rag_ready_flag"] = [1, 1, 1]

        with patch.object(catalog_facts, "_load_catalog", return_value=catalog):
            answer = catalog_facts.answer_game_compare_question("Compare Hades and Celeste")

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "game_compare")
        self.assertEqual(answer.game_ids, [1, 2])
        self.assertIn("Hades", answer.answer)
        self.assertIn("Celeste", answer.answer)
        self.assertIn("higher total rating", answer.answer)

    def test_non_catalog_count_question_returns_none(self):
        answer = catalog_facts.answer_catalog_count_question("What is this project?")

        self.assertIsNone(answer)


if __name__ == "__main__":
    unittest.main()
