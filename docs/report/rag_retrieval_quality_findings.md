# RAG Retrieval Quality Findings

Generated at: `2026-07-22 16:11:29`

## Purpose

This report evaluates whether the RAG retrieval engine returns games that match expected user intent across a small golden-query set.

This is a relevance smoke test, not a perfect objective benchmark. It checks whether top retrieved games contain expected concepts, respect platform constraints when specified, and avoid obvious mismatches.

## Inputs

- Golden-query file: `C:/Users/calvi/Data Science/Community_Project/tests/rag_golden_queries.json`
- Top-k reviewed per query: `5`
- Backend: `chroma`
- Engine: `src.rag_engine.RAGAgent` when backend is `chroma`; `src.lightweight_rag_engine.LightweightRAGAgent` when backend is `lightweight`
- Vector artifacts: `data/vector_store/` for Chroma; `data/rag/lightweight/` for lightweight NumPy retrieval

## Weight Profile Summary

| Profile | Semantic Weight | Lexical Weight | Passed | Total | Pass Rate | Runtime Errors |
|---|---:|---:|---:|---:|---:|---:|
| `semantic_90_lexical_10` | 0.90 | 0.10 | 13 | 15 | 86.7% | 0 |
| `semantic_80_lexical_20` | 0.80 | 0.20 | 14 | 15 | 93.3% | 0 |
| `semantic_70_lexical_30` | 0.70 | 0.30 | 14 | 15 | 93.3% | 0 |

## Current Recommendation

The strongest evaluated profile was `semantic_80_lexical_20` with a pass rate of `93.3%`.

Use this as a tuning signal, not a final truth. Review the failed queries manually before changing production weights.


## Detailed Results: `semantic_90_lexical_10`

### cozy_farming_switch

Query: `Recommend cozy farming games on Switch.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Farm Together | 2018 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Simulator / Strategy |  | 0.578 | 0.592 | 0.335 |
| 2 | Garden Life: A Cozy Simulator | 2024 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Simulator |  | 0.560 | 0.573 | 0.328 |
| 3 | Sun Haven | 2023 | Mac / Nintendo Switch / PC (Microsoft Windows) | Adventure / Indie / Role-playing (RPG) / Simulator |  | 0.555 | 0.566 | 0.144 |
| 4 | Echoes of the Plum Grove | 2024 | Nintendo Switch / PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.534 | 0.513 | 0.405 |
| 5 | Farm Land | 2021 | Android / Nintendo Switch / iOS | Adventure / Simulator |  | 0.534 | 0.554 | 0.231 |

### story_rich_rpg_pc

Query: `Find story-rich RPGs on PC.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Wither | 2011 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.570 | 0.621 | 0.000 |
| 2 | Forgotten Tales RPG | 2012 | Android | Adventure |  | 0.557 | 0.585 | 0.000 |
| 3 | Wartales | 2023 | Nintendo Switch / PC (Microsoft Windows) / Xbox Series X/S | Adventure / Indie / Role-playing (RPG) / Strategy / Tactical / Turn-based strate |  | 0.546 | 0.573 | 0.000 |
| 4 | La Tale | 2014 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.535 | 0.571 | 0.000 |
| 5 | Fantasy Tales Online | 2016 | Mac / PC (Microsoft Windows) | Indie / Role-playing (RPG) |  | 0.525 | 0.561 | 0.000 |

### hades_dead_cells_similarity

Query: `I played Hades and Dead Cells recently. Recommend similar games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | 8Doors: Arum's Afterlife Adventure | 2021 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Adventure / Indie / Platform |  | 2.690 | 0.522 | 0.000 |
| 2 | Posshexor | 2023 | PC (Microsoft Windows) | Adventure / Indie / Platform |  | 1.893 | 0.514 | 0.000 |
| 3 | Crystal Plague | 2021 | PC (Microsoft Windows) | Adventure / Hack and slash/Beat 'em up / Indie / Role-playing (RPG) |  | 1.872 | 0.502 | 0.000 |
| 4 | Indecision. | 2018 | PC (Microsoft Windows) | Adventure / Indie / Platform |  | 1.439 | 0.000 | 0.082 |
| 5 | Pillars of Eternity II: Deadfire | 2018 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Adventure / Role-playing (RPG) |  | 1.328 | 0.541 | 0.000 |

### hidden_gem_fantasy_exploration

Query: `Find hidden gems with exploration and fantasy themes.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Jewel Adventures | 2012 | Nintendo DS / Nintendo DSi | Puzzle / Strategy |  | 0.597 | 0.571 | 0.417 |
| 2 | Gem Miner | 2021 | Nintendo Switch | Arcade / Puzzle / Strategy |  | 0.582 | 0.603 | 0.179 |
| 3 | Hidden Through Time 2: Myths & Magic | 2023 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 5 / Xbox Series X/S | Adventure / Indie / Point-and-click / Puzzle |  | 0.575 | 0.593 | 0.000 |
| 4 | Jewel Match IV | 2014 | PC (Microsoft Windows) | Adventure / Puzzle |  | 0.570 | 0.539 | 0.333 |
| 5 | 1001 Nights: The Adventures of Sindbad | 2010 | Mac / PC (Microsoft Windows) | Adventure / Point-and-click / Puzzle |  | 0.566 | 0.545 | 0.349 |

### short_atmospheric_horror

Query: `Recommend short atmospheric horror games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Visitor | 2021 | Linux / Mac / PC (Microsoft Windows) | Indie |  | 0.735 | 0.756 | 0.326 |
| 2 | Polydeuces | 2020 | PC (Microsoft Windows) | Adventure / Indie / Puzzle |  | 0.662 | 0.602 | 0.893 |
| 3 | Delirious | 2020 | PC (Microsoft Windows) | Adventure |  | 0.659 | 0.684 | 0.220 |
| 4 | The Interview | 2021 | PC (Microsoft Windows) | Adventure / Puzzle |  | 0.649 | 0.596 | 0.815 |
| 5 | Sky High Games Horror Collection | 2023 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.647 | 0.676 | 0.171 |

### coop_strong_ratings

Query: `Suggest co-op games with strong ratings.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Couch Co-Op Bundle Vol. 2 | 2020 | Nintendo Switch | Adventure / Platform / Shooter |  | 0.631 | 0.544 | 1.000 |
| 2 | The Two of Us | 2021 | PC (Microsoft Windows) | Indie / Platform / Puzzle / Strategy |  | 0.597 | 0.551 | 0.597 |
| 3 | Horror Stories | 2019 | Nintendo 3DS / PC (Microsoft Windows) / PlayStation 4 / Wii U | Arcade / Indie / Puzzle |  | 0.594 | 0.606 | 0.272 |
| 4 | KoGaMa | 2011 | Android / Web browser | Adventure / Arcade / Shooter / Strategy |  | 0.557 | 0.544 | 0.358 |
| 5 | Scarecrow Co-op 2 | 2021 | PC (Microsoft Windows) | Adventure |  | 0.556 | 0.536 | 0.423 |

### stardew_less_obvious

Query: `Suggest games similar to Stardew Valley but less obvious.`

Overall: **Review**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Review |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | StarSim | 2024 | PC (Microsoft Windows) | Adventure / Indie / Role-playing (RPG) / Simulator / Strategy |  | 1.914 | 0.548 | 0.000 |
| 2 | Valley Peaks | 2024 | Nintendo Switch / PC (Microsoft Windows) | Adventure / Indie / Platform / Puzzle |  | 1.445 | 0.000 | 0.241 |
| 3 | Albert and Otto: The Adventure Begins | 2015 | Mac / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Adventure / Indie / Platform / Puzzle |  | 1.433 | 0.000 | 0.030 |
| 4 | A Valley Without Wind 2 | 2013 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie / Platform / Strategy / Turn-based strategy (TBS) |  | 0.554 | 0.559 | 0.097 |
| 5 | Starwisp Hyperdrive | 2024 | Linux / Mac / PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.544 | 0.604 | 0.000 |

### neon_scifi

Query: `Find neon sci-fi games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | NeonCode | 2018 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie |  | 0.605 | 0.649 | 0.000 |
| 2 | Neon Warp | 2016 | PC (Microsoft Windows) | Indie |  | 0.603 | 0.658 | 0.000 |
| 3 | Neon Space Ultra | 2016 | PC (Microsoft Windows) | Indie |  | 0.601 | 0.644 | 0.000 |
| 4 | Neon Space 2 | 2016 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie / Strategy |  | 0.599 | 0.653 | 0.000 |
| 5 | Neonicum | 2017 | PC (Microsoft Windows) | Indie |  | 0.594 | 0.637 | 0.000 |

### relaxing_low_pressure

Query: `Suggest low-pressure relaxing games after a long day.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | StressOut | 2020 | PC (Microsoft Windows) | Adventure / Indie |  | 0.436 | 0.472 | 0.000 |
| 2 | Air Attack | 2010 | PC (Microsoft Windows) | Indie |  | 0.421 | 0.444 | 0.000 |
| 3 | Playne | 2020 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.418 | 0.441 | 0.000 |
| 4 | Kamer | 2018 | Mac / PC (Microsoft Windows) | Indie |  | 0.416 | 0.417 | 0.000 |
| 5 | Aery: Calm Mind | 2021 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Simulator |  | 0.410 | 0.391 | 0.072 |

### strategic_turn_based_pc

Query: `Recommend strategic turn-based games on PC.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Ground Pounders | 2014 | Linux / Mac / PC (Microsoft Windows) | Indie / Strategy |  | 0.643 | 0.547 | 0.999 |
| 2 | Hexarchy | 2023 | Mac / PC (Microsoft Windows) | Card & Board Game / Strategy / Turn-based strategy (TBS) |  | 0.638 | 0.611 | 0.562 |
| 3 | Wargroove | 2019 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Strategy / Tactical / Turn-based strategy (TBS) |  | 0.621 | 0.592 | 0.377 |
| 4 | Battle Worlds: Kronos | 2013 | Android / Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One / iOS | Simulator / Strategy / Turn-based strategy (TBS) |  | 0.609 | 0.609 | 0.000 |
| 5 | Wart | 2022 | PC (Microsoft Windows) | Strategy |  | 0.605 | 0.578 | 0.633 |

### mysterious_rainy_night

Query: `Recommend mysterious atmospheric games for a rainy night.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | One Rainy Night | 2022 | PC (Microsoft Windows) | Indie |  | 0.679 | 0.586 | 1.000 |
| 2 | Watching Blade Runner on a Rainy Night | 2022 | Web browser | Indie / Visual Novel |  | 0.593 | 0.563 | 0.541 |
| 3 | All Haze Eve | 2017 | PC (Microsoft Windows) | Adventure / Indie |  | 0.590 | 0.599 | 0.193 |
| 4 | Rain | 2016 | Web browser | Indie / Simulator |  | 0.582 | 0.634 | 0.000 |
| 5 | Rainy Season | 2020 | PC (Microsoft Windows) | Adventure / Indie |  | 0.560 | 0.588 | 0.093 |

### open_world_adventure_playstation

Query: `Find open-world adventure games on PlayStation 5.`

Overall: **Review**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Review |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Bonfire Peaks | 2021 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 | Adventure / Indie / Puzzle |  | 0.579 | 0.502 | 0.951 |
| 2 | Astro's Playroom | 2020 | PlayStation 5 | Adventure / Platform |  | 0.570 | 0.599 | 0.000 |
| 3 | Minishoot' Adventures | 2024 | Nintendo Switch / Nintendo Switch 2 / PC (Microsoft Windows) / PlayStation 5 / Xbox One / Xbox Serie | Adventure / Indie / Role-playing (RPG) / Shooter |  | 0.554 | 0.571 | 0.000 |
| 4 | Let's Play! Oink Games | 2021 | Android / Nintendo Switch / PC (Microsoft Windows) / PlayStation 5 / iOS | Card & Board Game / Indie |  | 0.546 | 0.550 | 0.000 |
| 5 | My Little Universe | 2021 | Android / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One  | Adventure / Indie / Simulator |  | 0.541 | 0.544 | 0.000 |

### puzzle_switch

Query: `Recommend puzzle games on Switch.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Puzzle 9 | 2021 | Nintendo Switch | Puzzle |  | 0.681 | 0.653 | 0.622 |
| 2 | Mujo | 2017 | Nintendo Switch | Puzzle |  | 0.628 | 0.563 | 1.000 |
| 3 | Swap Puzzles | 2023 | Nintendo Switch | Card & Board Game / Puzzle |  | 0.623 | 0.680 | 0.000 |
| 4 | Puzzle Playground | 2024 | Nintendo Switch | Adventure / Card & Board Game / Puzzle |  | 0.607 | 0.660 | 0.017 |
| 5 | Puzzle Frenzy | 2021 | Nintendo Switch / PlayStation 4 / PlayStation 5 | Arcade / Card & Board Game / Indie / Puzzle |  | 0.598 | 0.561 | 0.622 |

### cinematic_single_player

Query: `Find cinematic single-player games with strong story.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | ScreenPlay | 2024 | PC (Microsoft Windows) | Card & Board Game / Strategy |  | 0.598 | 0.618 | 0.105 |
| 2 | Morphine | 2015 | PC (Microsoft Windows) | Adventure / Indie |  | 0.577 | 0.568 | 0.438 |
| 3 | Storyscape | 2019 | Android / iOS | Role-playing (RPG) / Visual Novel |  | 0.575 | 0.594 | 0.000 |
| 4 | Stories One | 2023 | PC (Microsoft Windows) | Indie / MOBA / Shooter |  | 0.538 | 0.597 | 0.000 |
| 5 | La Tale | 2014 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.538 | 0.564 | 0.000 |

### weird_experimental

Query: `Give me weird experimental games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | 4:32 | 2010 | Web browser | Indie |  | 0.518 | 0.496 | 0.399 |
| 2 | These Monsters | 2016 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie |  | 0.515 | 0.539 | 0.087 |
| 3 | Funky Physics | 2015 | Wii U | Puzzle / Strategy |  | 0.503 | 0.546 | 0.000 |
| 4 | Crazy Machines 3 | 2016 | PC (Microsoft Windows) | Indie / Puzzle / Simulator / Strategy |  | 0.496 | 0.539 | 0.000 |
| 5 | 000000052573743 | 2013 | PC (Microsoft Windows) | Indie |  | 0.494 | 0.510 | 0.135 |


## Detailed Results: `semantic_80_lexical_20`

### cozy_farming_switch

Query: `Recommend cozy farming games on Switch.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Farm Together | 2018 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Simulator / Strategy |  | 0.552 | 0.592 | 0.335 |
| 2 | Gleaner Heights | 2018 | Linux / Nintendo Switch / PC (Microsoft Windows) / Xbox One | Adventure / Indie / Role-playing (RPG) / Simulator |  | 0.538 | 0.463 | 0.684 |
| 3 | Garden Life: A Cozy Simulator | 2024 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Simulator |  | 0.535 | 0.573 | 0.328 |
| 4 | Echoes of the Plum Grove | 2024 | Nintendo Switch / PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.523 | 0.513 | 0.405 |
| 5 | Cozy Grove: Camp Spirit | 2024 | Android / Nintendo Switch / Nintendo Switch 2 / PC (Microsoft Windows) / PlayStation 4 / PlayStation | Adventure / Indie / Puzzle / Simulator |  | 0.518 | 0.515 | 0.474 |

### story_rich_rpg_pc

Query: `Find story-rich RPGs on PC.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Wither | 2011 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.508 | 0.621 | 0.000 |
| 2 | Forgotten Tales RPG | 2012 | Android | Adventure |  | 0.499 | 0.585 | 0.000 |
| 3 | Wartales | 2023 | Nintendo Switch / PC (Microsoft Windows) / Xbox Series X/S | Adventure / Indie / Role-playing (RPG) / Strategy / Tactical / Turn-based strate |  | 0.489 | 0.573 | 0.000 |
| 4 | RPG in a Box | 2022 | PC (Microsoft Windows) | Role-playing (RPG) |  | 0.489 | 0.519 | 0.311 |
| 5 | TaleSpire | 2021 | Linux / PC (Microsoft Windows) | Indie / Role-playing (RPG) / Simulator |  | 0.479 | 0.537 | 0.142 |

### hades_dead_cells_similarity

Query: `I played Hades and Dead Cells recently. Recommend similar games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | 8Doors: Arum's Afterlife Adventure | 2021 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Adventure / Indie / Platform |  | 2.638 | 0.522 | 0.000 |
| 2 | Posshexor | 2023 | PC (Microsoft Windows) | Adventure / Indie / Platform |  | 1.842 | 0.514 | 0.000 |
| 3 | Crystal Plague | 2021 | PC (Microsoft Windows) | Adventure / Hack and slash/Beat 'em up / Indie / Role-playing (RPG) |  | 1.822 | 0.502 | 0.000 |
| 4 | Indecision. | 2018 | PC (Microsoft Windows) | Adventure / Indie / Platform |  | 1.447 | 0.000 | 0.082 |
| 5 | Pillars of Eternity II: Deadfire | 2018 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Adventure / Role-playing (RPG) |  | 1.273 | 0.541 | 0.000 |

### hidden_gem_fantasy_exploration

Query: `Find hidden gems with exploration and fantasy themes.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Jewel Adventures | 2012 | Nintendo DS / Nintendo DSi | Puzzle / Strategy |  | 0.581 | 0.571 | 0.417 |
| 2 | Genies & Gems | 2016 | iOS | Arcade / Puzzle |  | 0.562 | 0.486 | 0.665 |
| 3 | Jewel Match IV | 2014 | PC (Microsoft Windows) | Adventure / Puzzle |  | 0.549 | 0.539 | 0.333 |
| 4 | 1001 Nights: The Adventures of Sindbad | 2010 | Mac / PC (Microsoft Windows) | Adventure / Point-and-click / Puzzle |  | 0.547 | 0.545 | 0.349 |
| 5 | Gem Miner | 2021 | Nintendo Switch | Arcade / Puzzle / Strategy |  | 0.539 | 0.603 | 0.179 |

### short_atmospheric_horror

Query: `Recommend short atmospheric horror games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Visitor | 2021 | Linux / Mac / PC (Microsoft Windows) | Indie |  | 0.692 | 0.756 | 0.326 |
| 2 | Polydeuces | 2020 | PC (Microsoft Windows) | Adventure / Indie / Puzzle |  | 0.691 | 0.602 | 0.893 |
| 3 | The Interview | 2021 | PC (Microsoft Windows) | Adventure / Puzzle |  | 0.671 | 0.596 | 0.815 |
| 4 | Delirious | 2020 | PC (Microsoft Windows) | Adventure |  | 0.613 | 0.684 | 0.220 |
| 5 | Sky High Games Horror Collection | 2023 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.596 | 0.676 | 0.171 |

### coop_strong_ratings

Query: `Suggest co-op games with strong ratings.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Couch Co-Op Bundle Vol. 2 | 2020 | Nintendo Switch | Adventure / Platform / Shooter |  | 0.677 | 0.544 | 1.000 |
| 2 | The Two of Us | 2021 | PC (Microsoft Windows) | Indie / Platform / Puzzle / Strategy |  | 0.602 | 0.551 | 0.597 |
| 3 | Horror Stories | 2019 | Nintendo 3DS / PC (Microsoft Windows) / PlayStation 4 / Wii U | Arcade / Indie / Puzzle |  | 0.561 | 0.606 | 0.272 |
| 4 | Scarecrow Co-op 2 | 2021 | PC (Microsoft Windows) | Adventure |  | 0.545 | 0.536 | 0.423 |
| 5 | KoGaMa | 2011 | Android / Web browser | Adventure / Arcade / Shooter / Strategy |  | 0.538 | 0.544 | 0.358 |

### stardew_less_obvious

Query: `Suggest games similar to Stardew Valley but less obvious.`

Overall: **Review**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Review |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | StarSim | 2024 | PC (Microsoft Windows) | Adventure / Indie / Role-playing (RPG) / Simulator / Strategy |  | 1.859 | 0.548 | 0.000 |
| 2 | Valley Peaks | 2024 | Nintendo Switch / PC (Microsoft Windows) | Adventure / Indie / Platform / Puzzle |  | 1.469 | 0.000 | 0.241 |
| 3 | Albert and Otto: The Adventure Begins | 2015 | Mac / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Adventure / Indie / Platform / Puzzle |  | 1.436 | 0.000 | 0.030 |
| 4 | A Valley Without Wind 2 | 2013 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie / Platform / Strategy / Turn-based strategy (TBS) |  | 0.508 | 0.559 | 0.097 |
| 5 | Starwisp Hyperdrive | 2024 | Linux / Mac / PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.484 | 0.604 | 0.000 |

### neon_scifi

Query: `Find neon sci-fi games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Unit 404 | 2020 | Android / Mac / PC (Microsoft Windows) / iOS | Adventure / Indie / Platform / Puzzle |  | 0.577 | 0.539 | 0.574 |
| 2 | NL Community | 2021 | PC (Microsoft Windows) | Racing |  | 0.577 | 0.522 | 0.687 |
| 3 | Neon Chrome | 2016 | Android / Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / P | Adventure / Indie / Role-playing (RPG) / Shooter |  | 0.544 | 0.503 | 0.557 |
| 4 | NeonCode | 2018 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie |  | 0.540 | 0.649 | 0.000 |
| 5 | Neon Warp | 2016 | PC (Microsoft Windows) | Indie |  | 0.537 | 0.658 | 0.000 |

### relaxing_low_pressure

Query: `Suggest low-pressure relaxing games after a long day.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | StressOut | 2020 | PC (Microsoft Windows) | Adventure / Indie |  | 0.388 | 0.472 | 0.000 |
| 2 | Aery: Calm Mind | 2021 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Simulator |  | 0.378 | 0.391 | 0.072 |
| 3 | Air Attack | 2010 | PC (Microsoft Windows) | Indie |  | 0.376 | 0.444 | 0.000 |
| 4 | Kamer | 2018 | Mac / PC (Microsoft Windows) | Indie |  | 0.374 | 0.417 | 0.000 |
| 5 | Playne | 2020 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.373 | 0.441 | 0.000 |

### strategic_turn_based_pc

Query: `Recommend strategic turn-based games on PC.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Ground Pounders | 2014 | Linux / Mac / PC (Microsoft Windows) | Indie / Strategy |  | 0.688 | 0.547 | 0.999 |
| 2 | Hexarchy | 2023 | Mac / PC (Microsoft Windows) | Card & Board Game / Strategy / Turn-based strategy (TBS) |  | 0.633 | 0.611 | 0.562 |
| 3 | Wart | 2022 | PC (Microsoft Windows) | Strategy |  | 0.610 | 0.578 | 0.633 |
| 4 | Wargroove | 2019 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Strategy / Tactical / Turn-based strategy (TBS) |  | 0.600 | 0.592 | 0.377 |
| 5 | Alma | 2020 | PC (Microsoft Windows) | Card & Board Game / Strategy / Turn-based strategy (TBS) |  | 0.573 | 0.576 | 0.402 |

### mysterious_rainy_night

Query: `Recommend mysterious atmospheric games for a rainy night.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | One Rainy Night | 2022 | PC (Microsoft Windows) | Indie |  | 0.721 | 0.586 | 1.000 |
| 2 | Watching Blade Runner on a Rainy Night | 2022 | Web browser | Indie / Visual Novel |  | 0.590 | 0.563 | 0.541 |
| 3 | All Haze Eve | 2017 | PC (Microsoft Windows) | Adventure / Indie |  | 0.549 | 0.599 | 0.193 |
| 4 | Rainyday | 2017 | PC (Microsoft Windows) | Adventure / Indie |  | 0.533 | 0.545 | 0.281 |
| 5 | Rain | 2016 | Web browser | Indie / Simulator |  | 0.518 | 0.634 | 0.000 |

### open_world_adventure_playstation

Query: `Find open-world adventure games on PlayStation 5.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Bonfire Peaks | 2021 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 | Adventure / Indie / Puzzle |  | 0.623 | 0.502 | 0.951 |
| 2 | Towers of Aghasba | 2024 | Linux / PC (Microsoft Windows) / PlayStation 5 | Adventure / Role-playing (RPG) |  | 0.591 | 0.450 | 1.000 |
| 3 | Goodbye World | 2022 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Adventure / Indie / Platform / Puzzle / Visual Novel |  | 0.528 | 0.485 | 0.440 |
| 4 | Astro's Playroom | 2020 | PlayStation 5 | Adventure / Platform |  | 0.510 | 0.599 | 0.000 |
| 5 | Dysmantle | 2021 | Android / Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / X | Adventure / Indie / Puzzle / Role-playing (RPG) / Simulator |  | 0.510 | 0.511 | 0.350 |

### puzzle_switch

Query: `Recommend puzzle games on Switch.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Puzzle 9 | 2021 | Nintendo Switch | Puzzle |  | 0.678 | 0.653 | 0.622 |
| 2 | Mujo | 2017 | Nintendo Switch | Puzzle |  | 0.672 | 0.563 | 1.000 |
| 3 | Puzzle Frenzy | 2021 | Nintendo Switch / PlayStation 4 / PlayStation 5 | Arcade / Card & Board Game / Indie / Puzzle |  | 0.605 | 0.561 | 0.622 |
| 4 | 30-in-1 Game Collection: Volume 2 | 2019 | Nintendo Switch | Arcade / Puzzle |  | 0.568 | 0.518 | 0.662 |
| 5 | Swap Puzzles | 2023 | Nintendo Switch | Card & Board Game / Puzzle |  | 0.555 | 0.680 | 0.000 |

### cinematic_single_player

Query: `Find cinematic single-player games with strong story.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Morphine | 2015 | PC (Microsoft Windows) | Adventure / Indie |  | 0.564 | 0.568 | 0.438 |
| 2 | ScreenPlay | 2024 | PC (Microsoft Windows) | Card & Board Game / Strategy |  | 0.547 | 0.618 | 0.105 |
| 3 | Storyscape | 2019 | Android / iOS | Role-playing (RPG) / Visual Novel |  | 0.516 | 0.594 | 0.000 |
| 4 | La Tale | 2014 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.482 | 0.564 | 0.000 |
| 5 | Stories One | 2023 | PC (Microsoft Windows) | Indie / MOBA / Shooter |  | 0.478 | 0.597 | 0.000 |

### weird_experimental

Query: `Give me weird experimental games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | 4:32 | 2010 | Web browser | Indie |  | 0.508 | 0.496 | 0.399 |
| 2 | Slot Waste | 2024 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.475 | 0.482 | 0.293 |
| 3 | These Monsters | 2016 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie |  | 0.470 | 0.539 | 0.087 |
| 4 | 000000052573743 | 2013 | PC (Microsoft Windows) | Indie |  | 0.457 | 0.510 | 0.135 |
| 5 | Funky Physics | 2015 | Wii U | Puzzle / Strategy |  | 0.448 | 0.546 | 0.000 |


## Detailed Results: `semantic_70_lexical_30`

### cozy_farming_switch

Query: `Recommend cozy farming games on Switch.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Gleaner Heights | 2018 | Linux / Nintendo Switch / PC (Microsoft Windows) / Xbox One | Adventure / Indie / Role-playing (RPG) / Simulator |  | 0.560 | 0.463 | 0.684 |
| 2 | Farming Simulator 20 | 2019 | Nintendo Switch / iOS | Simulator |  | 0.531 | 0.448 | 0.621 |
| 3 | Farm Together | 2018 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Simulator / Strategy |  | 0.526 | 0.592 | 0.335 |
| 4 | Cozy Grove | 2021 | Mac / Nintendo Switch / Nintendo Switch 2 / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / | Adventure / Indie / Puzzle / Role-playing (RPG) / Simulator |  | 0.517 | 0.463 | 0.573 |
| 5 | Cozy Grove: Camp Spirit | 2024 | Android / Nintendo Switch / Nintendo Switch 2 / PC (Microsoft Windows) / PlayStation 4 / PlayStation | Adventure / Indie / Puzzle / Simulator |  | 0.514 | 0.515 | 0.474 |

### story_rich_rpg_pc

Query: `Find story-rich RPGs on PC.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | RPG in a Box | 2022 | PC (Microsoft Windows) | Role-playing (RPG) |  | 0.468 | 0.519 | 0.311 |
| 2 | To Carry a Sword | 2022 | PC (Microsoft Windows) | Adventure / Indie |  | 0.446 | 0.499 | 0.220 |
| 3 | Wither | 2011 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.445 | 0.621 | 0.000 |
| 4 | Forgotten Tales RPG | 2012 | Android | Adventure |  | 0.440 | 0.585 | 0.000 |
| 5 | TaleSpire | 2021 | Linux / PC (Microsoft Windows) | Indie / Role-playing (RPG) / Simulator |  | 0.439 | 0.537 | 0.142 |

### hades_dead_cells_similarity

Query: `I played Hades and Dead Cells recently. Recommend similar games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | 8Doors: Arum's Afterlife Adventure | 2021 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Adventure / Indie / Platform |  | 2.586 | 0.522 | 0.000 |
| 2 | Posshexor | 2023 | PC (Microsoft Windows) | Adventure / Indie / Platform |  | 1.790 | 0.514 | 0.000 |
| 3 | Crystal Plague | 2021 | PC (Microsoft Windows) | Adventure / Hack and slash/Beat 'em up / Indie / Role-playing (RPG) |  | 1.772 | 0.502 | 0.000 |
| 4 | Indecision. | 2018 | PC (Microsoft Windows) | Adventure / Indie / Platform |  | 1.455 | 0.000 | 0.082 |
| 5 | Pillars of Eternity II: Deadfire | 2018 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Adventure / Role-playing (RPG) |  | 1.219 | 0.541 | 0.000 |

### hidden_gem_fantasy_exploration

Query: `Find hidden gems with exploration and fantasy themes.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Genies & Gems | 2016 | iOS | Arcade / Puzzle |  | 0.580 | 0.486 | 0.665 |
| 2 | Jewel Adventures | 2012 | Nintendo DS / Nintendo DSi | Puzzle / Strategy |  | 0.566 | 0.571 | 0.417 |
| 3 | Jewel Match IV | 2014 | PC (Microsoft Windows) | Adventure / Puzzle |  | 0.529 | 0.539 | 0.333 |
| 4 | 1001 Nights: The Adventures of Sindbad | 2010 | Mac / PC (Microsoft Windows) | Adventure / Point-and-click / Puzzle |  | 0.527 | 0.545 | 0.349 |
| 5 | Gem Miner | 2021 | Nintendo Switch | Arcade / Puzzle / Strategy |  | 0.497 | 0.603 | 0.179 |

### short_atmospheric_horror

Query: `Recommend short atmospheric horror games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Polydeuces | 2020 | PC (Microsoft Windows) | Adventure / Indie / Puzzle |  | 0.720 | 0.602 | 0.893 |
| 2 | The Interview | 2021 | PC (Microsoft Windows) | Adventure / Puzzle |  | 0.693 | 0.596 | 0.815 |
| 3 | Visitor | 2021 | Linux / Mac / PC (Microsoft Windows) | Indie |  | 0.649 | 0.756 | 0.326 |
| 4 | Delirious | 2020 | PC (Microsoft Windows) | Adventure |  | 0.566 | 0.684 | 0.220 |
| 5 | Sky High Games Horror Collection | 2023 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.546 | 0.676 | 0.171 |

### coop_strong_ratings

Query: `Suggest co-op games with strong ratings.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Couch Co-Op Bundle Vol. 2 | 2020 | Nintendo Switch | Adventure / Platform / Shooter |  | 0.722 | 0.544 | 1.000 |
| 2 | The Two of Us | 2021 | PC (Microsoft Windows) | Indie / Platform / Puzzle / Strategy |  | 0.606 | 0.551 | 0.597 |
| 3 | Scarecrow Co-op 2 | 2021 | PC (Microsoft Windows) | Adventure |  | 0.533 | 0.536 | 0.423 |
| 4 | Horror Stories | 2019 | Nintendo 3DS / PC (Microsoft Windows) / PlayStation 4 / Wii U | Arcade / Indie / Puzzle |  | 0.527 | 0.606 | 0.272 |
| 5 | KoGaMa | 2011 | Android / Web browser | Adventure / Arcade / Shooter / Strategy |  | 0.519 | 0.544 | 0.358 |

### stardew_less_obvious

Query: `Suggest games similar to Stardew Valley but less obvious.`

Overall: **Review**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Review |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | StarSim | 2024 | PC (Microsoft Windows) | Adventure / Indie / Role-playing (RPG) / Simulator / Strategy |  | 1.804 | 0.548 | 0.000 |
| 2 | Valley Peaks | 2024 | Nintendo Switch / PC (Microsoft Windows) | Adventure / Indie / Platform / Puzzle |  | 1.493 | 0.000 | 0.241 |
| 3 | Albert and Otto: The Adventure Begins | 2015 | Mac / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Adventure / Indie / Platform / Puzzle |  | 1.439 | 0.000 | 0.030 |
| 4 | A Valley Without Wind 2 | 2013 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie / Platform / Strategy / Turn-based strategy (TBS) |  | 0.462 | 0.559 | 0.097 |
| 5 | Harvest Moon: The Lost Valley | 2014 | Nintendo 3DS | Adventure / Role-playing (RPG) / Simulator / Strategy |  | 0.427 | 0.499 | 0.191 |

### neon_scifi

Query: `Find neon sci-fi games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | NL Community | 2021 | PC (Microsoft Windows) | Racing |  | 0.593 | 0.522 | 0.687 |
| 2 | Unit 404 | 2020 | Android / Mac / PC (Microsoft Windows) / iOS | Adventure / Indie / Platform / Puzzle |  | 0.581 | 0.539 | 0.574 |
| 3 | Neon Chrome | 2016 | Android / Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / P | Adventure / Indie / Role-playing (RPG) / Shooter |  | 0.550 | 0.503 | 0.557 |
| 4 | Nova: Space Armada | 2024 | PC (Microsoft Windows) | Strategy |  | 0.503 | 0.499 | 0.442 |
| 5 | NeonCode | 2018 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie |  | 0.475 | 0.649 | 0.000 |

### relaxing_low_pressure

Query: `Suggest low-pressure relaxing games after a long day.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Swim Out | 2017 | Android / Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / Xbox One / iOS | Indie / Puzzle / Sport / Strategy / Turn-based strategy (TBS) |  | 0.349 | 0.388 | 0.154 |
| 2 | Aery: Calm Mind | 2021 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Simulator |  | 0.346 | 0.391 | 0.072 |
| 3 | StressOut | 2020 | PC (Microsoft Windows) | Adventure / Indie |  | 0.341 | 0.472 | 0.000 |
| 4 | My First Furry | 2021 | PC (Microsoft Windows) | Indie |  | 0.341 | 0.000 | 1.000 |
| 5 | Kamer | 2018 | Mac / PC (Microsoft Windows) | Indie |  | 0.332 | 0.417 | 0.000 |

### strategic_turn_based_pc

Query: `Recommend strategic turn-based games on PC.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Ground Pounders | 2014 | Linux / Mac / PC (Microsoft Windows) | Indie / Strategy |  | 0.734 | 0.547 | 0.999 |
| 2 | Hexarchy | 2023 | Mac / PC (Microsoft Windows) | Card & Board Game / Strategy / Turn-based strategy (TBS) |  | 0.628 | 0.611 | 0.562 |
| 3 | Wart | 2022 | PC (Microsoft Windows) | Strategy |  | 0.615 | 0.578 | 0.633 |
| 4 | Wargroove | 2019 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / Xbox One | Indie / Strategy / Tactical / Turn-based strategy (TBS) |  | 0.578 | 0.592 | 0.377 |
| 5 | Metroplex Zero | 2023 | Nintendo Switch / PC (Microsoft Windows) | Adventure / Card & Board Game / Indie / Puzzle / Role-playing (RPG) / Strategy / |  | 0.564 | 0.557 | 0.477 |

### mysterious_rainy_night

Query: `Recommend mysterious atmospheric games for a rainy night.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | One Rainy Night | 2022 | PC (Microsoft Windows) | Indie |  | 0.762 | 0.586 | 1.000 |
| 2 | Watching Blade Runner on a Rainy Night | 2022 | Web browser | Indie / Visual Novel |  | 0.588 | 0.563 | 0.541 |
| 3 | All Haze Eve | 2017 | PC (Microsoft Windows) | Adventure / Indie |  | 0.509 | 0.599 | 0.193 |
| 4 | Rainyday | 2017 | PC (Microsoft Windows) | Adventure / Indie |  | 0.507 | 0.545 | 0.281 |
| 5 | Forgotten Passages | 2020 | PC (Microsoft Windows) | Adventure / Indie |  | 0.467 | 0.540 | 0.159 |

### open_world_adventure_playstation

Query: `Find open-world adventure games on PlayStation 5.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Bonfire Peaks | 2021 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 | Adventure / Indie / Puzzle |  | 0.668 | 0.502 | 0.951 |
| 2 | Towers of Aghasba | 2024 | Linux / PC (Microsoft Windows) / PlayStation 5 | Adventure / Role-playing (RPG) |  | 0.646 | 0.450 | 1.000 |
| 3 | Goodbye World | 2022 | Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One / Xbox Series X/ | Adventure / Indie / Platform / Puzzle / Visual Novel |  | 0.523 | 0.485 | 0.440 |
| 4 | Agent Walker: Secret Journey | 2016 | Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / Xbox One /  | Adventure / Puzzle |  | 0.511 | 0.447 | 0.590 |
| 5 | Dysmantle | 2021 | Android / Linux / Mac / Nintendo Switch / PC (Microsoft Windows) / PlayStation 4 / PlayStation 5 / X | Adventure / Indie / Puzzle / Role-playing (RPG) / Simulator |  | 0.493 | 0.511 | 0.350 |

### puzzle_switch

Query: `Recommend puzzle games on Switch.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Mujo | 2017 | Nintendo Switch | Puzzle |  | 0.716 | 0.563 | 1.000 |
| 2 | Puzzle 9 | 2021 | Nintendo Switch | Puzzle |  | 0.675 | 0.653 | 0.622 |
| 3 | Puzzle Frenzy | 2021 | Nintendo Switch / PlayStation 4 / PlayStation 5 | Arcade / Card & Board Game / Indie / Puzzle |  | 0.611 | 0.561 | 0.622 |
| 4 | 30-in-1 Game Collection: Volume 2 | 2019 | Nintendo Switch | Arcade / Puzzle |  | 0.583 | 0.518 | 0.662 |
| 5 | Candy Shake Cup | 2024 | Nintendo Switch | Puzzle |  | 0.549 | 0.494 | 0.606 |

### cinematic_single_player

Query: `Find cinematic single-player games with strong story.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | Morphine | 2015 | PC (Microsoft Windows) | Adventure / Indie |  | 0.551 | 0.568 | 0.438 |
| 2 | ScreenPlay | 2024 | PC (Microsoft Windows) | Card & Board Game / Strategy |  | 0.496 | 0.618 | 0.105 |
| 3 | Storyscape | 2019 | Android / iOS | Role-playing (RPG) / Visual Novel |  | 0.456 | 0.594 | 0.000 |
| 4 | Once Alive | 2024 | PC (Microsoft Windows) | Adventure / Indie |  | 0.431 | 0.532 | 0.093 |
| 5 | La Tale | 2014 | PC (Microsoft Windows) | Adventure / Role-playing (RPG) |  | 0.425 | 0.564 | 0.000 |

### weird_experimental

Query: `Give me weird experimental games.`

Overall: **Pass**

| Check | Result |
|---|---|
| Expected terms present | Pass |
| Platform constraint | Pass |
| Avoid terms absent | Pass |
| Seed/excluded titles absent | Pass |

| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | 4:32 | 2010 | Web browser | Indie |  | 0.498 | 0.496 | 0.399 |
| 2 | Slot Waste | 2024 | PC (Microsoft Windows) | Adventure / Indie / Simulator |  | 0.456 | 0.482 | 0.293 |
| 3 | These Monsters | 2016 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie |  | 0.425 | 0.539 | 0.087 |
| 4 | 000000052573743 | 2013 | PC (Microsoft Windows) | Indie |  | 0.419 | 0.510 | 0.135 |
| 5 | Weird Worlds: Return to Infinite Space | 2013 | Linux / Mac / PC (Microsoft Windows) | Adventure / Indie / Simulator / Strategy |  | 0.416 | 0.487 | 0.179 |

## Interpretation Rules

- A `Pass` means the top retrieved set contains at least one expected concept and did not violate the explicit avoid checks.
- A `Review` does not automatically mean the engine is wrong. It means the result should be manually inspected.
- Platform failures are more serious than broad concept failures because platform intent is usually a hard user constraint.
- Seed-title failures mean the engine returned a game that the user provided as a reference point instead of an alternative.
- If 0.7/0.3 or 0.8/0.2 beats 0.9/0.1, lexical evidence is probably underweighted.

## Recommended Next Actions

1. Manually inspect all `Review` queries.
2. Confirm whether failed results are truly bad or only missing expected vocabulary.
3. Tune semantic/lexical weights only after reviewing the detailed result tables.
4. Expand the golden-query set with real prompts from user testing.
5. Rerun this report after every vector-store rebuild or major retrieval change.
