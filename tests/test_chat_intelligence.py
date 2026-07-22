import unittest

from src.app.chat_intelligence import (
    analyze_message,
    build_filter_overrides,
    build_preference_summary,
    enhance_answer_text,
    enrich_retrieved_games,
    extract_catalog_game_titles,
    extract_recent_game_titles,
    filter_seed_games,
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

    def test_filter_overrides_preserve_existing_filters(self):
        result = analyze_message("Recommend cozy games on Switch")
        filters = build_filter_overrides(
            result.slots,
            {"platforms": ["PC"], "release_year_min": 2015},
        )

        self.assertEqual(filters["platforms"], ["PC"])
        self.assertEqual(filters["release_year_min"], 2015)

    def test_filter_overrides_add_detected_platform_when_missing(self):
        result = analyze_message("Recommend cozy games on Switch")
        filters = build_filter_overrides(result.slots, {})

        self.assertEqual(filters["platforms"], ["Nintendo Switch"])

    def test_enrichment_adds_match_explanation_to_games_and_answer(self):
        result = analyze_message("Recommend cozy adventure games on Switch")
        games = [
            {
                "game_id": 1,
                "name": "Cozy Quest",
                "platforms": ["Nintendo Switch"],
                "genres": ["Adventure"],
                "themes": ["Fantasy"],
                "summary": "A cozy adventure with relaxed exploration.",
                "hidden_gem_balanced_flag": False,
                "evidence": "Matched through genre match context: Adventure.",
            }
        ]

        enriched = enrich_retrieved_games(games, result.slots)
        answer = enhance_answer_text("Here is a match.", result.slots, enriched)

        self.assertIn("match_explanation", enriched[0])
        self.assertIn("I read your request as:", build_preference_summary(result.slots) or "")
        self.assertIn("Why these fit:", answer)
        self.assertIn("Cozy Quest", answer)

    def test_seed_games_are_filtered_from_retrieved_games(self):
        result = analyze_message("I played Hades recently. Recommend similar games.")
        games = [
            {"name": "Hades", "game_id": 1},
            {"name": "Bastion", "game_id": 2},
            {"name": "Transistor", "game_id": 3},
        ]

        filtered, excluded = filter_seed_games(games, result.slots, top_k=2)

        self.assertEqual([game["name"] for game in filtered], ["Bastion", "Transistor"])
        self.assertEqual(excluded, ["Hades"])


if __name__ == "__main__":
    unittest.main()
