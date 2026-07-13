import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import fetch_IGDB as fetch


def game_record(
    game_id: int,
    year: int,
    total_rating: float = 68.0,
    total_rating_count: int = 5,
) -> dict:
    return {
        "id": game_id,
        "name": f"Game {game_id}",
        "first_release_date": int(
            datetime(year, 6, 1, tzinfo=timezone.utc).timestamp()
        ),
        "game_type": fetch.MAIN_GAME_TYPE_ID,
        "game_status": None,
        "version_parent": None,
        "genres": [12],
        "platforms": [6],
        "total_rating": total_rating,
        "total_rating_count": total_rating_count,
    }


class YearlySelectionTests(unittest.TestCase):
    def test_year_query_uses_completed_year_and_main_games(self) -> None:
        query = fetch.build_year_candidate_query(2023)
        start, end = fetch.year_bounds(2023)

        self.assertIn(f"first_release_date >= {start}", query)
        self.assertIn(f"first_release_date < {end}", query)
        self.assertIn("game_type = 0", query)
        self.assertIn("version_parent = null", query)

    def test_year_query_can_use_id_cursor(self) -> None:
        query = fetch.build_year_candidate_query(2023, min_game_id=12345)

        self.assertIn("id > 12345", query)
        self.assertIn("sort id asc", query)

    def test_total_target_is_distributed_across_years(self) -> None:
        yearly_targets = [
            fetch.target_games_for_year(year)
            for year in range(fetch.START_YEAR, fetch.END_YEAR + 1)
        ]

        self.assertEqual(sum(yearly_targets), fetch.TARGET_TOTAL_GAMES)
        self.assertEqual(min(yearly_targets), 3333)
        self.assertEqual(max(yearly_targets), 3334)

    def test_local_eligibility_requires_richness_fields(self) -> None:
        game = game_record(1, 2023)
        self.assertTrue(fetch.is_eligible_candidate(game, 2023))

        no_genre = {**game, "genres": []}
        self.assertFalse(fetch.is_eligible_candidate(no_genre, 2023))

        cancelled = {**game, "game_status": 6}
        self.assertFalse(fetch.is_eligible_candidate(cancelled, 2023))

    def test_cohort_selection_is_stratified_unique_and_deterministic(self) -> None:
        candidates = []
        for game_id in range(1, 4501):
            if game_id <= 900:
                candidates.append(
                    game_record(
                        game_id,
                        2023,
                        total_rating=82.0,
                        total_rating_count=100,
                    )
                )
            elif game_id <= 1400:
                candidates.append(
                    game_record(
                        game_id,
                        2023,
                        total_rating=55.0,
                        total_rating_count=100,
                    )
                )
            else:
                candidates.append(game_record(game_id, 2023))

        popularity = {
            game_id: {
                "igdb_interest": game_id / 1_000_000,
                "visits": game_id / 2_000_000,
            }
            for game_id in range(1401, 2601)
        }

        selected, cohorts, summary = fetch.select_year_cohorts(
            2023,
            candidates,
            popularity,
        )
        selected_again, cohorts_again, _ = fetch.select_year_cohorts(
            2023,
            candidates,
            popularity,
        )

        target = fetch.target_games_for_year(2023)

        self.assertEqual(summary["quality_selected_count"], 800)
        self.assertEqual(summary["lower_rated_selected_count"], 400)
        self.assertEqual(summary["popularity_selected_count"], 600)
        self.assertEqual(summary["low_visibility_selected_count"], 400)
        self.assertEqual(summary["comparison_selected_count"], target - 2200)
        self.assertEqual(len(selected), target)
        self.assertEqual(len({game["id"] for game in selected}), target)
        self.assertEqual(len(cohorts), target)
        self.assertEqual(
            [game["id"] for game in selected],
            [game["id"] for game in selected_again],
        )
        self.assertEqual(cohorts, cohorts_again)
        self.assertEqual(
            {row["cohort"] for row in cohorts},
            {"quality", "lower_rated", "popularity", "low_visibility", "comparison"},
        )

    def test_popularity_interest_requires_both_igdb_signals(self) -> None:
        rows = [
            {
                "id": 1,
                "game_id": 10,
                "external_popularity_source": 121,
                "popularity_type": 2,
                "value": 0.8,
                "calculated_at": 100,
            },
            {
                "id": 2,
                "game_id": 10,
                "external_popularity_source": 121,
                "popularity_type": 3,
                "value": 0.5,
                "calculated_at": 100,
            },
            {
                "id": 3,
                "game_id": 11,
                "external_popularity_source": 121,
                "popularity_type": 2,
                "value": 0.9,
                "calculated_at": 100,
            },
        ]

        signals = fetch.popularity_signals_for_games(rows)

        self.assertAlmostEqual(signals[10]["igdb_interest"], 0.68)
        self.assertNotIn(11, signals)


if __name__ == "__main__":
    unittest.main()
