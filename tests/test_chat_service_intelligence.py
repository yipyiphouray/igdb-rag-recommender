import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "api"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat_service
from src.app.project_facts import ProjectFactAnswer


class ChatServiceIntelligenceTests(unittest.TestCase):
    def assert_valid_chat_response(self, response: dict) -> ChatResponse:
        parsed = ChatResponse(**response)
        self.assertIsInstance(parsed.answer, str)
        self.assertIsInstance(parsed.follow_up_prompts, list)
        return parsed

    def test_explain_project_topic_returns_project_overview(self):
        request = ChatRequest(
            message="Explain this project",
            route_mode="explain_project",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "explain_project")
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["route_source"], "selected_route_mode")
        self.assertIn("IGDB-powered", response["answer"])
        self.assertIn("Recommend Me", response["answer"])
        self.assert_valid_chat_response(response)

    def test_explain_data_topic_returns_dataset_context(self):
        request = ChatRequest(
            message="Explain the data",
            route_mode="explain_data",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "explain_data")
        self.assertIn("IGDB data", response["answer"])
        self.assertIn("metadata", response["answer"])
        self.assert_valid_chat_response(response)

    def test_dataset_size_route_uses_project_fact_artifact(self):
        request = ChatRequest(message="How many games are in the dataset?", route_mode="dataset_size")
        fact_answer = ProjectFactAnswer(
            intent="dataset_total_games",
            answer="The current app dataset contains 47,835 games.",
            prompts=["What years does the dataset cover?"],
            caveats=["This answer comes from a structured metric artifact."],
            source_files=["data/app/app_methodology_metrics.json"],
        )

        with patch.object(chat_service, "answer_project_fact_question", return_value=fact_answer):
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "dataset_size")
        self.assertEqual(response["mode"], "project_fact_dataset_total_games")
        self.assertIn("47,835 games", response["answer"])
        self.assertIn("Source artifact", " ".join(response["caveats"]))
        self.assert_valid_chat_response(response)

    def test_dataset_year_range_route_uses_project_fact_artifact(self):
        request = ChatRequest(
            message="What years does the dataset cover?",
            route_mode="dataset_year_range",
        )
        fact_answer = ProjectFactAnswer(
            intent="dataset_release_year_range",
            answer="The current app dataset covers games released from 2010 through 2024.",
            prompts=["How many games are in the dataset?"],
            source_files=["data/app/app_methodology_metrics.json"],
        )

        with patch.object(chat_service, "answer_project_fact_question", return_value=fact_answer):
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "dataset_year_range")
        self.assertEqual(response["mode"], "project_fact_dataset_release_year_range")
        self.assertIn("2010 through 2024", response["answer"])
        self.assert_valid_chat_response(response)

    def test_rating_coverage_route_uses_project_fact_artifact(self):
        request = ChatRequest(message="What is rating coverage?", route_mode="rating_coverage")
        fact_answer = ProjectFactAnswer(
            intent="dataset_rating_coverage",
            answer="The current rating coverage is 29.29%.",
            prompts=["What is reliable rating coverage?"],
            source_files=["data/app/app_methodology_metrics.json"],
        )

        with patch.object(chat_service, "answer_project_fact_question", return_value=fact_answer):
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "rating_coverage")
        self.assertEqual(response["mode"], "project_fact_dataset_rating_coverage")
        self.assertIn("29.29%", response["answer"])
        self.assert_valid_chat_response(response)

    def test_explain_rag_topic_returns_controlled_rag_context(self):
        request = ChatRequest(
            message="Explain RAG",
            route_mode="explain_rag",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "explain_rag")
        self.assertIn("simplified Guide design", response["answer"])
        self.assertIn("controlled answers", response["answer"])
        self.assert_valid_chat_response(response)

    def test_explain_hidden_gems_topic_returns_definition(self):
        request = ChatRequest(
            message="Explain hidden gems",
            route_mode="explain_hidden_gems",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "explain_hidden_gems")
        self.assertIn("hidden gem", response["answer"].lower())
        self.assertIn("lower visibility", response["answer"])
        self.assert_valid_chat_response(response)

    def test_explain_recommendation_topic_returns_cosine_context(self):
        request = ChatRequest(
            message="Explain recommendations",
            route_mode="explain_recommendation",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "explain_recommendation")
        self.assertIn("cosine similarity", response["answer"])
        self.assertIn("structured user inputs", response["answer"])
        self.assert_valid_chat_response(response)

    def test_recommend_me_guidance_topic_returns_main_flow_guidance(self):
        request = ChatRequest(
            message="Help me use Recommend Me",
            route_mode="recommend_me_guidance",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "recommend_me_guidance")
        self.assertEqual(response["mode"], "recommend_me_guidance")
        self.assertIn("structured inputs", response["answer"])
        self.assertIn("hidden gems", response["answer"])
        self.assert_valid_chat_response(response)

    def test_search_catalog_topic_points_to_explore_games(self):
        request = ChatRequest(
            message="Where do I browse games?",
            route_mode="search_catalog",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "search_catalog")
        self.assertEqual(response["mode"], "catalog_navigation_guidance")
        self.assertIn("Explore Games", response["answer"])
        self.assert_valid_chat_response(response)

    def test_website_navigation_topic_returns_page_map(self):
        request = ChatRequest(
            message="Website navigation",
            route_mode="website_navigation",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "website_navigation")
        self.assertIn("Explore Games", response["answer"])
        self.assertIn("Methodology", response["answer"])
        self.assert_valid_chat_response(response)

    def test_limitations_topic_returns_project_caveats(self):
        request = ChatRequest(
            message="Explain limitations",
            route_mode="explain_limitations",
            max_results=3,
        )

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "explain_limitations")
        self.assertIn("metadata coverage", response["answer"])
        self.assertIn("rating sparsity", response["answer"])
        self.assert_valid_chat_response(response)

    def test_custom_question_is_not_supported_in_condition_based_guide(self):
        request = ChatRequest(message="What is your purpose?", route_mode="custom_question")

        response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "custom_question")
        self.assertEqual(response["status"], "unsupported_question")
        self.assertIn("condition-based", response["answer"])
        self.assert_valid_chat_response(response)


if __name__ == "__main__":
    unittest.main()
