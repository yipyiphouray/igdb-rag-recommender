import unittest

from src.app.chat_intelligence import (
    analyze_message,
    extract_catalog_game_titles,
    extract_recent_game_titles,
    semantic_route_message,
)


class ChatIntelligenceTests(unittest.TestCase):
    def test_vague_recommendation_request_requires_clarification(self):
        result = analyze_message("Can you recommend a game?")

        self.assertTrue(result.should_clarify)
        self.assertEqual(result.intent, "recommendation_clarification")
        self.assertIn("platform", result.clarification_question or "")
        self.assertGreaterEqual(len(result.clarification_prompts), 3)

    def test_specific_request_extracts_metadata_signals(self):
        result = analyze_message("Recommend cozy RPGs on Switch with strong ratings.")
        slots = result.slots

        self.assertFalse(result.should_clarify)
        self.assertEqual(result.intent, "game_recommendation")
        self.assertIn("Nintendo Switch", slots.platforms)
        self.assertIn("RPG", slots.genres)
        self.assertIn("Cozy", slots.moods)
        self.assertEqual(slots.rating_preference, "strong_rating_evidence")

    def test_recent_game_titles_are_extracted_from_user_language(self):
        titles = extract_recent_game_titles(
            "I played Hades and Dead Cells recently. Recommend similar games."
        )

        self.assertEqual(titles, ("Hades", "Dead Cells"))

    def test_catalog_title_extraction_finds_known_titles_without_sentence_patch(self):
        titles = extract_catalog_game_titles(
            "yes my recent game was League of Legends",
            catalog_titles=("League of Legends", "Hades", "Dead Cells"),
        )

        self.assertEqual(titles, ("League of Legends",))

    def test_semantic_router_handles_paraphrased_seed_recommendation(self):
        route = semantic_route_message("I loved League of Legends. What should I try next?")

        self.assertEqual(route.intent, "seed_game_recommendation")
        self.assertGreater(route.confidence, 0.0)

    def test_semantic_router_handles_project_question(self):
        route = semantic_route_message("Can you explain where your answers come from?")

        self.assertEqual(route.intent, "project_question")


if __name__ == "__main__":
    unittest.main()
