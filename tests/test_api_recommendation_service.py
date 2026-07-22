import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "api"))
sys.path.insert(0, str(PROJECT_ROOT / "tests"))

from app.schemas.recommendations import RecommendationRequest
from app.services import recommendation_service
from test_metadata_cosine_recommendation import cosine_catalog


class ApiRecommendationServiceTests(unittest.TestCase):
    def setUp(self):
        recommendation_service._COSINE_RECOMMENDER = None
        recommendation_service._COSINE_CATALOG_ID = None

    def test_recommendation_endpoint_service_uses_metadata_cosine(self):
        request = RecommendationRequest(
            platform="PC (Microsoft Windows)",
            genres=["Role-playing (RPG)"],
            themes=["Science fiction"],
            favorite_games=["Space RPG Original"],
            max_results=5,
        )

        with patch.object(recommendation_service, "load_catalog", return_value=cosine_catalog()):
            response = recommendation_service.recommend_from_request(request)

        self.assertEqual(response["mode"], "cosine_similarity")
        self.assertEqual(response["similarity_status"], "metadata_cosine_similarity_active")
        self.assertEqual(response["request_summary"]["matched_seed_games"], ["Space RPG Original"])
        self.assertEqual(response["items"][0]["game_id"], 2)
        self.assertNotIn(1, [item["game_id"] for item in response["items"]])

    def test_recommendation_endpoint_service_keeps_structured_fallback(self):
        request = RecommendationRequest(max_results=3)

        with patch.object(recommendation_service, "load_catalog", return_value=cosine_catalog()):
            response = recommendation_service.recommend_from_request(request)

        self.assertEqual(response["mode"], "structured_fallback")
        self.assertEqual(response["similarity_status"], "structured_fallback_active")
        self.assertTrue(response["items"])


if __name__ == "__main__":
    unittest.main()
