import unittest

from src.app.project_terms import (
    answer_recommendation_input_helper,
    answer_term_definition_question,
    answer_website_navigation_question,
)


class ProjectTermsTests(unittest.TestCase):
    def test_answers_hidden_gem_definition(self):
        answer = answer_term_definition_question("What is a hidden gem?")

        self.assertIsNotNone(answer)
        self.assertEqual(answer.intent, "term_definition")
        self.assertEqual(answer.interpreted_preferences["term"], "hidden gem")
        self.assertIn("lower visibility", answer.answer)

    def test_answers_popscore_alias_definition(self):
        answer = answer_term_definition_question("Can you define pop score?")

        self.assertIsNotNone(answer)
        self.assertEqual(answer.interpreted_preferences["term"], "popscore")
        self.assertIn("visibility", answer.answer)

    def test_recommendation_input_helper_uses_planner_preferences(self):
        answer = answer_recommendation_input_helper(
            "I like Hades and want RPGs on Switch.",
            filters={
                "genres": ["Role-playing (RPG)"],
                "platforms": ["Nintendo Switch"],
                "themes": ["Fantasy"],
                "hidden_gems_only": True,
            },
            game_titles=["Hades"],
        )

        self.assertEqual(answer.intent, "recommendation_input_helper")
        self.assertIn("Recent games: Hades", answer.answer)
        self.assertIn("Nintendo Switch", answer.answer)
        self.assertIn("hidden gems", answer.answer)

    def test_website_navigation_points_to_specific_page(self):
        answer = answer_website_navigation_question("Where can I browse games?")

        self.assertEqual(answer.intent, "website_navigation")
        self.assertEqual(answer.interpreted_preferences["page"], "explore")
        self.assertEqual(answer.interpreted_preferences["href"], "/explore")
        self.assertIn("Explore Games_", answer.answer)


if __name__ == "__main__":
    unittest.main()
