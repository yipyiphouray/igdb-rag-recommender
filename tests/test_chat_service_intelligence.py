import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "api"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.chat import ChatRequest
from app.services import chat_service
from src.lightweight_rag_engine import _contains_any as lightweight_contains_any


def sample_retrieved_game() -> dict:
    return {
        "rank": 1,
        "game_id": 101,
        "name": "Switch RPG Example",
        "slug": "switch-rpg-example",
        "release_year": 2022,
        "cover_url": None,
        "screenshot_url": None,
        "summary": "A cozy fantasy RPG adventure for Nintendo Switch.",
        "total_rating": 86.0,
        "total_rating_count": 300,
        "custom_interest_score": 0.8,
        "custom_interest_percentile": 0.75,
        "extraction_cohort": "quality",
        "platforms": ["Nintendo Switch"],
        "genres": ["RPG", "Adventure"],
        "themes": ["Fantasy"],
        "game_modes": ["Single player"],
        "player_perspectives": [],
        "normal_playtime_hours": 18.0,
        "hidden_gem_balanced_flag": False,
        "rag_ready_flag": True,
        "retrieval_score": 0.91,
        "semantic_score": 0.88,
        "lexical_score": 0.53,
        "evidence": "Matched through genre match context: RPG.",
        "caveats": [],
    }


class ChatServiceIntelligenceTests(unittest.TestCase):
    def test_lightweight_platform_filter_matches_switch_aliases(self):
        self.assertTrue(lightweight_contains_any("Nintendo Switch", ["switch"]))
        self.assertTrue(lightweight_contains_any("Switch", ["Nintendo Switch"]))

    def test_specific_parser_signal_reaches_rag_retrieval(self):
        request = ChatRequest(message="Recommend cozy RPGs on Switch", max_results=3)
        rag_response = {
            "answer_text": "I found catalog-backed matches.",
            "retrieved_games": [sample_retrieved_game()],
            "warnings": [],
            "applied_filters": {"platforms": ["Nintendo Switch"]},
            "mode": "rag_hybrid_retrieval_lightweight",
            "status": "success",
        }

        with patch.object(chat_service, "answer_game_query", return_value=rag_response) as mocked:
            response = chat_service.answer_chat_request(request)

        mocked.assert_called_once()
        self.assertEqual(mocked.call_args.kwargs["filters"]["platforms"], ["Nintendo Switch"])
        self.assertEqual(response["chat_intent"], "game_recommendation")
        self.assertIn("I read your request as:", response["answer"])
        self.assertIn("match_explanation", response["retrieved_games"][0])

    def test_seed_game_recommendation_is_not_hijacked_by_project_context(self):
        request = ChatRequest(
            message="I played Baldur's Gate recently. Can you recommend me games similar to it",
            max_results=3,
        )
        rag_response = {
            "answer_text": "I found catalog-backed matches.",
            "retrieved_games": [sample_retrieved_game()],
            "warnings": [],
            "applied_filters": {},
            "mode": "rag_hybrid_retrieval_lightweight",
            "status": "success",
        }

        with patch.object(chat_service, "answer_game_query", return_value=rag_response) as mocked:
            response = chat_service.answer_chat_request(request)

        mocked.assert_called_once()
        self.assertEqual(response["chat_intent"], "seed_game_recommendation")
        self.assertNotEqual(response["mode"], "predefined_project_context")
        self.assertIn("Baldur's Gate", response["interpreted_preferences"]["recent_games"])
        self.assertEqual(response["route_source"], "semantic_router")

    def test_recently_played_seed_request_does_not_trigger_vague_clarification(self):
        request = ChatRequest(
            message="i recently played League of Legends. Recommend me something similar",
            max_results=3,
        )
        rag_response = {
            "answer_text": "I found catalog-backed matches.",
            "retrieved_games": [sample_retrieved_game()],
            "warnings": [],
            "applied_filters": {},
            "mode": "rag_hybrid_retrieval_lightweight",
            "status": "success",
        }

        with patch.object(chat_service, "answer_game_query", return_value=rag_response) as mocked:
            response = chat_service.answer_chat_request(request)

        mocked.assert_called_once()
        self.assertEqual(response["chat_intent"], "seed_game_recommendation")
        self.assertNotEqual(response["status"], "needs_clarification")
        self.assertIn("League of Legends", response["interpreted_preferences"]["recent_games"])

    def test_recent_game_clarification_answer_routes_to_retrieval_with_history(self):
        request = ChatRequest(
            message="yes my recent game was League of legends",
            max_results=3,
            history=[
                {
                    "role": "user",
                    "content": "Can you recommend a game?",
                },
                {
                    "role": "guide",
                    "content": "Tell me a platform, genre, mood, recent game you liked, or whether you want popular games or hidden gems.",
                },
            ],
        )
        rag_response = {
            "answer_text": "I found catalog-backed matches.",
            "retrieved_games": [sample_retrieved_game()],
            "warnings": [],
            "applied_filters": {},
            "mode": "rag_hybrid_retrieval_lightweight",
            "status": "success",
        }

        with patch.object(chat_service, "answer_game_query", return_value=rag_response) as mocked:
            response = chat_service.answer_chat_request(request)

        mocked.assert_called_once()
        self.assertEqual(response["chat_intent"], "recommendation_follow_up")
        self.assertNotEqual(response["status"], "unsupported_question")
        self.assertIn("League of legends", response["interpreted_preferences"]["recent_games"])

    def test_vague_recommendation_clarifies_before_rag(self):
        request = ChatRequest(message="Can you recommend a game?")

        with patch.object(chat_service, "answer_game_query") as mocked:
            response = chat_service.answer_chat_request(request)

        mocked.assert_not_called()
        self.assertEqual(response["status"], "needs_clarification")
        self.assertEqual(response["chat_intent"], "recommendation_clarification")

    def test_recent_seed_game_is_excluded_from_displayed_recommendations(self):
        request = ChatRequest(
            message="I played Hades recently. Recommend similar games.",
            max_results=2,
        )
        seed_game = sample_retrieved_game()
        seed_game["game_id"] = 201
        seed_game["name"] = "Hades"
        alternative = sample_retrieved_game()
        alternative["game_id"] = 202
        alternative["name"] = "Bastion"
        second_alternative = sample_retrieved_game()
        second_alternative["game_id"] = 203
        second_alternative["name"] = "Transistor"
        rag_response = {
            "answer_text": "The strongest matches are Hades, Bastion, and Transistor.",
            "retrieved_games": [seed_game, alternative, second_alternative],
            "warnings": [],
            "applied_filters": {},
            "mode": "rag_hybrid_retrieval_lightweight",
            "status": "success",
        }

        with patch.object(chat_service, "answer_game_query", return_value=rag_response) as mocked:
            response = chat_service.answer_chat_request(request)

        self.assertEqual(mocked.call_args.kwargs["top_k"], 3)
        self.assertEqual([game["name"] for game in response["retrieved_games"]], ["Bastion", "Transistor"])
        self.assertNotIn("Hades, Bastion, and Transistor", response["answer"])
        self.assertIn("I excluded Hades", response["answer"])


if __name__ == "__main__":
    unittest.main()
