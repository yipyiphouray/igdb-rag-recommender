import unittest
from unittest.mock import patch

from src.app import project_facts


class ProjectFactsTests(unittest.TestCase):
    def setUp(self):
        self.metrics = {
            "total_games": 47835,
            "release_year_start": 2010,
            "release_year_end": 2024,
            "games_per_year": 3333,
            "quality_cohort_count": 1425,
            "lower_rated_cohort_count": 147,
            "popularity_cohort_count": 9000,
            "low_visibility_cohort_count": 5329,
            "comparison_cohort_count": 31934,
            "rating_coverage": 0.292860875927668,
            "reliable_rating_coverage": 0.055168809449148114,
            "popscore_coverage": 0.21022264032612104,
            "summary_coverage": 0.9638967283369917,
            "hidden_gem_count": 231,
            "quality_threshold": 80,
            "min_rating_count": 25,
            "hidden_gem_visibility_percentile": 0.4,
        }
        self.insights = {
            "descriptive": {
                "top_genre": "Indie",
                "top_platform": "PC (Microsoft Windows)",
            }
        }
        self.rag_manifest = {
            "row_count": 47835,
            "embedding_shape": [47835, 384],
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        }

    def test_answers_total_games_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "How many games does the dataset have?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_total_games")
        self.assertIn("47,835 games", answer.answer)
        self.assertIn("2010 through 2024", answer.answer)

    def test_answers_release_year_range_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "What years does the dataset cover?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_release_year_range")
        self.assertIn("2010 through 2024", answer.answer)
        self.assertIn("3,333", answer.answer)

    def test_answers_hidden_gem_count_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "How many hidden gems are there?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_hidden_gem_count")
        self.assertIn("231 hidden-gem games", answer.answer)
        self.assertIn("80", answer.answer)

    def test_answers_rating_coverage_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "What is rating coverage?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_rating_coverage")
        self.assertIn("29.29%", answer.answer)
        self.assertIn("rating value", answer.answer)

    def test_answers_reliable_rating_coverage_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "What is reliable rating coverage?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_reliable_rating_coverage")
        self.assertIn("5.52%", answer.answer)
        self.assertIn("25", answer.answer)

    def test_answers_popscore_coverage_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "What is PopScore coverage?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_popscore_coverage")
        self.assertIn("21.02%", answer.answer)

    def test_answers_summary_coverage_from_structured_metrics(self):
        with patch.object(project_facts, "_load_metrics", return_value=self.metrics):
            answer = project_facts.answer_project_fact_question(
                "How many games have summaries?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_summary_coverage")
        self.assertIn("96.39%", answer.answer)

    def test_answers_top_genre_from_insight_summary(self):
        with patch.object(project_facts, "_load_insight_summary", return_value=self.insights):
            answer = project_facts.answer_project_fact_question(
                "What is the top genre?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_top_genre")
        self.assertIn("Indie", answer.answer)

    def test_answers_top_platform_from_insight_summary(self):
        with patch.object(project_facts, "_load_insight_summary", return_value=self.insights):
            answer = project_facts.answer_project_fact_question(
                "What is the top platform?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "dataset_top_platform")
        self.assertIn("PC (Microsoft Windows)", answer.answer)

    def test_answers_rag_index_size_from_manifest(self):
        with patch.object(project_facts, "_load_rag_manifest", return_value=self.rag_manifest):
            answer = project_facts.answer_project_fact_question(
                "How many embeddings are in the vector index?"
            )

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "rag_index_size")
        self.assertIn("47,835 embedded game records", answer.answer)
        self.assertIn("384 embedding dimensions", answer.answer)

    def test_non_fact_question_returns_none(self):
        answer = project_facts.answer_project_fact_question("What is this project?")

        self.assertIsNone(answer)


if __name__ == "__main__":
    unittest.main()

