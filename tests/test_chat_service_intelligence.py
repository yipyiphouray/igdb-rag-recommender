import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "api"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat_service
from src.app.llm_provider import LLMToolPlan
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
        self.assertIn("grounding layer", response["answer"])
        self.assertIn("external free-tier LLM", response["answer"])
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

    def test_custom_question_uses_scoped_rag_fallback_without_llm_key(self):
        request = ChatRequest(message="What is your purpose?", route_mode="custom_question")

        with patch.object(chat_service, "generate_grounded_answer") as mock_generate:
            mock_generate.return_value.answer = ""
            mock_generate.return_value.provider = "gemini"
            mock_generate.return_value.model = "gemini-3.5-flash-lite"
            mock_generate.return_value.status = "unavailable"
            mock_generate.return_value.error = "Missing GEMINI_API_KEY."
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_mode"], "custom_question")
        self.assertEqual(response["status"], "success")
        self.assertIn(response["mode"], {"scoped_rag_extractive_fallback", "scoped_rag_llm_project_guide"})
        self.assertGreaterEqual(len(response["sources"]), 1)
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_catalog_count_to_catalog_tool(self):
        request = ChatRequest(
            message="How many games are in the Indie genre?",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="catalog_count",
            intent="catalog_genre_count",
            confidence=0.93,
            filters={"genres": ["Indie"]},
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user asks for a count filtered by genre.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan), patch.object(
            chat_service, "answer_catalog_count_with_filters"
        ) as mock_count:
            mock_count.return_value = chat_service.CatalogFactAnswer(
                intent="catalog_filtered_count",
                answer="The current app catalog contains 12,345 games matching genre = Indie.",
                prompts=["What genre has the most games?"],
                source_files=["data/app/app_game_catalog.parquet"],
                interpreted_filters={"genres": ["Indie"]},
            )
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "catalog_fact_catalog_filtered_count")
        self.assertIn("12,345 games", response["answer"])
        self.assertEqual(response["interpreted_preferences"]["genres"], ["Indie"])
        self.assertEqual(response["interpreted_preferences"]["tool"], "catalog_count")
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_distribution_to_catalog_tool(self):
        request = ChatRequest(
            message="What genre has the most games?",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="catalog_distribution",
            intent="catalog_top_genres",
            confidence=0.91,
            filters={},
            distribution_field="genres",
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user asks for a top category distribution.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan), patch.object(
            chat_service, "answer_catalog_distribution"
        ) as mock_distribution:
            mock_distribution.return_value = chat_service.CatalogFactAnswer(
                intent="catalog_top_genres",
                answer="The most common genres are: Indie: 20,000 games.",
                prompts=["How many Indie games are there?"],
                source_files=["data/app/app_game_catalog.parquet"],
            )
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "catalog_fact_catalog_top_genres")
        self.assertIn("Indie", response["answer"])
        self.assertEqual(response["interpreted_preferences"]["tool"], "catalog_distribution")
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_specific_game_lookup(self):
        request = ChatRequest(
            message="What platforms is Hades on?",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="game_lookup",
            intent="game_lookup",
            confidence=0.95,
            filters={},
            game_title="Hades",
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user asks for metadata about one specific game.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan), patch.object(
            chat_service, "answer_game_lookup_question"
        ) as mock_lookup:
            mock_lookup.return_value = chat_service.CatalogFactAnswer(
                intent="game_lookup",
                answer="Hades is in the current app catalog with game_id 1. Platforms include: PC.",
                prompts=["Where can I explore this game?"],
                source_files=["data/app/app_game_catalog.parquet"],
                interpreted_filters={"game_title": "Hades"},
                game_id=1,
            )
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "catalog_fact_game_lookup")
        self.assertIn("Hades", response["answer"])
        self.assertEqual(response["next_actions"][0]["href"], "/explore/1")
        self.assertEqual(response["interpreted_preferences"]["tool"], "game_lookup")
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_game_compare(self):
        request = ChatRequest(
            message="Compare Hades and Celeste",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="game_compare",
            intent="game_compare",
            confidence=0.94,
            filters={},
            game_titles=["Hades", "Celeste"],
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user asks to compare two specific games.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan), patch.object(
            chat_service, "answer_game_compare_question"
        ) as mock_compare:
            mock_compare.return_value = chat_service.CatalogFactAnswer(
                intent="game_compare",
                answer="Hades and Celeste are compared using catalog metadata.",
                prompts=["Where can I explore these games?"],
                source_files=["data/app/app_game_catalog.parquet"],
                interpreted_filters={"game_titles": ["Hades", "Celeste"], "game_ids": [1, 2]},
                game_id=1,
                game_ids=[1, 2],
            )
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "catalog_fact_game_compare")
        self.assertEqual(response["next_actions"][0]["href"], "/explore/1")
        self.assertEqual(response["next_actions"][1]["href"], "/explore/2")
        self.assertEqual(response["interpreted_preferences"]["tool"], "game_compare")
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_recommendation_input_helper(self):
        request = ChatRequest(
            message="I like Hades. What should I put in Recommend Me?",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="recommendation_input_helper",
            intent="recommendation_input_helper",
            confidence=0.9,
            filters={"platforms": ["Nintendo Switch"], "genres": ["Role-playing (RPG)"]},
            game_titles=["Hades"],
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user wants help preparing recommender inputs.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan):
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "project_tool_recommendation_input_helper")
        self.assertIn("Use Recommend Me_", response["answer"])
        self.assertEqual(response["next_actions"][0]["href"], "/recommendations")
        self.assertEqual(response["interpreted_preferences"]["tool"], "recommendation_input_helper")
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_term_definition(self):
        request = ChatRequest(
            message="What is PopScore?",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="term_definition",
            intent="term_definition",
            confidence=0.92,
            filters={},
            term="PopScore",
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user asks for a project term definition.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan):
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "project_tool_term_definition")
        self.assertIn("visibility", response["answer"])
        self.assertEqual(response["next_actions"][0]["href"], "/methodology")
        self.assertEqual(response["interpreted_preferences"]["tool"], "term_definition")
        self.assert_valid_chat_response(response)

    def test_llm_tool_planner_routes_website_navigation(self):
        request = ChatRequest(
            message="Where can I see the methodology?",
            route_mode="custom_question",
        )
        plan = LLMToolPlan(
            tool="website_navigation",
            intent="website_navigation",
            confidence=0.91,
            filters={},
            provider="gemini",
            model="gemini-3.5-flash-lite",
            status="success",
            reason="The user asks which website page to use.",
        )

        with patch.object(chat_service, "plan_chat_tool", return_value=plan):
            response = chat_service.answer_chat_request(request)

        self.assertEqual(response["route_source"], "llm_tool_planner")
        self.assertEqual(response["mode"], "project_tool_website_navigation")
        self.assertEqual(response["next_actions"][0]["href"], "/methodology")
        self.assertEqual(response["interpreted_preferences"]["tool"], "website_navigation")
        self.assert_valid_chat_response(response)


if __name__ == "__main__":
    unittest.main()
