import unittest

from src.app.rag_ranking import compute_ranking_scores, has_hidden_gem_intent, rank_candidates


def candidate(
    name: str,
    *,
    relevance: float,
    interest: float,
    rating_count: int,
    rating: float,
    hidden: bool = False,
    cohort: str = "comparison",
) -> dict:
    return {
        "name": name,
        "normalized_vec": relevance,
        "normalized_bm25": relevance,
        "hybrid_score": relevance,
        "custom_interest_percentile": interest,
        "total_rating_count": rating_count,
        "total_rating": rating,
        "hidden_gem_balanced_flag": int(hidden),
        "extraction_cohort": cohort,
        "summary": "A complete summary.",
        "genres": "RPG",
        "themes": "Fantasy",
        "platforms": "PC",
        "distance": 1.0 - relevance,
    }


class RAGRankingTests(unittest.TestCase):
    def test_default_ranking_favors_credible_popular_match_when_relevance_is_close(self):
        obscure = candidate(
            "Obscure Close Match",
            relevance=0.86,
            interest=0.05,
            rating_count=8,
            rating=72,
            hidden=True,
            cohort="hidden_gem",
        )
        credible = candidate(
            "Credible Familiar Match",
            relevance=0.82,
            interest=0.92,
            rating_count=900,
            rating=88,
            hidden=False,
            cohort="popularity",
        )

        ranked = rank_candidates([obscure, credible])

        self.assertEqual(ranked[0]["name"], "Credible Familiar Match")
        self.assertEqual(ranked[0]["ranking_profile"], "default_quality_popularity")
        self.assertLess(obscure["hidden_gem_adjustment"], 0)

    def test_hidden_gem_ranking_rewards_hidden_gem_when_requested(self):
        obvious = candidate(
            "Obvious Match",
            relevance=0.86,
            interest=0.95,
            rating_count=1000,
            rating=88,
            hidden=False,
            cohort="popularity",
        )
        hidden = candidate(
            "Hidden Gem Match",
            relevance=0.84,
            interest=0.25,
            rating_count=160,
            rating=86,
            hidden=True,
            cohort="hidden_gem",
        )

        ranked = rank_candidates([obvious, hidden], hidden_gem_mode=True)

        self.assertEqual(ranked[0]["name"], "Hidden Gem Match")
        self.assertEqual(ranked[0]["ranking_profile"], "hidden_gem")
        self.assertGreater(hidden["hidden_gem_adjustment"], 0)

    def test_relevance_still_matters_more_than_popularity_for_large_gap(self):
        weak_popular = candidate(
            "Weak Popular Match",
            relevance=0.30,
            interest=0.99,
            rating_count=1200,
            rating=90,
            hidden=False,
            cohort="popularity",
        )
        strong_relevant = candidate(
            "Strong Relevant Match",
            relevance=0.90,
            interest=0.10,
            rating_count=25,
            rating=78,
            hidden=False,
            cohort="comparison",
        )

        ranked = rank_candidates([weak_popular, strong_relevant])

        self.assertEqual(ranked[0]["name"], "Strong Relevant Match")

    def test_hidden_gem_intent_detection_supports_profile_selection(self):
        self.assertTrue(has_hidden_gem_intent("Find underrated RPGs"))
        self.assertTrue(has_hidden_gem_intent(ranking_mode="hidden_gems"))
        self.assertFalse(has_hidden_gem_intent("Recommend popular RPGs"))

    def test_ranking_scores_expose_interpretable_components(self):
        scores = compute_ranking_scores(
            candidate(
                "Readable Components",
                relevance=0.80,
                interest=0.70,
                rating_count=500,
                rating=85,
                hidden=False,
                cohort="quality",
            )
        )

        self.assertIn("relevance_score", scores)
        self.assertIn("popularity_score", scores)
        self.assertIn("rating_count_score", scores)
        self.assertIn("quality_score", scores)
        self.assertGreater(scores["primary_rank_score"], 0)


if __name__ == "__main__":
    unittest.main()
