# IGDB API Endpoints — Categorized Summary and Alphabetical Reference

## Part 1 — Endpoint Categories by Relevance

### 1. Core Game Catalog

These endpoints describe the main game object and basic game-level metadata.

| Endpoint               |         Relevance | Quick Description                                                                                                                                                     |
| ---------------------- | ----------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `games`                |         Essential | Main game endpoint. Contains titles, summaries, storylines, ratings, genres, platforms, release dates, companies, media, similar games, and many relationship fields. |
| `alternative_names`    |            Useful | Stores alternate names, regional names, acronyms, or old names for games.                                                                                             |
| `game_localizations`   | Optional / Useful | Stores localized names and covers for games in different regions or languages.                                                                                        |
| `game_types`           |         Essential | Defines whether a game is a main game, DLC, expansion, bundle, remake, remaster, port, etc.                                                                           |
| `game_statuses`        |            Useful | Tracks game status such as released, alpha, beta, cancelled, early access, etc.                                                                                       |
| `game_release_formats` |          Optional | Describes the release format or release type. Useful for more detailed release modeling.                                                                              |
| `game_time_to_beats`   |       Very Useful | Stores time-to-beat estimates, such as quick completion, normal completion, and completionist time.                                                                   |

---

### 2. Game Classification, Vibe, and Discovery

These endpoints describe what kind of game it is, how it feels, and how it plays. These are very important for recommendation logic and RAG.

| Endpoint              |   Relevance | Quick Description                                                                                                           |
| --------------------- | ----------: | --------------------------------------------------------------------------------------------------------------------------- |
| `genres`              |   Essential | Broad game categories such as RPG, Shooter, Adventure, Strategy, Platformer, Racing, etc.                                   |
| `themes`              |   Essential | High-level themes or moods such as Fantasy, Sci-Fi, Horror, Survival, Mystery, Comedy, etc.                                 |
| `keywords`            |   Essential | Fine-grained descriptive tags such as cyberpunk, zombies, stealth, open world, medieval, etc.                               |
| `game_modes`          | Very Useful | Gameplay modes such as single-player, multiplayer, co-op, MMO, split-screen, etc.                                           |
| `player_perspectives` | Very Useful | Camera/view style such as first-person, third-person, bird view, side view, text-based, etc.                                |
| `multiplayer_modes`   |      Useful | Detailed multiplayer support by game/platform, such as online co-op, LAN, split-screen, and max players.                    |
| `search`              |     Utility | General search endpoint. Useful for finding IDs or testing searches, but not usually stored as a relational database table. |

---

### 3. Platforms and Hardware

These endpoints describe where games can be played.

| Endpoint                         |         Relevance | Quick Description                                                                                         |
| -------------------------------- | ----------------: | --------------------------------------------------------------------------------------------------------- |
| `platforms`                      |         Essential | Main platform endpoint. Stores PC, PlayStation, Xbox, Nintendo Switch, iOS, Android, older consoles, etc. |
| `platform_families`              |            Useful | Groups related platforms into families, such as PlayStation, Xbox, Nintendo, etc.                         |
| `platform_types`                 |            Useful | Platform category/type, such as console, computer, operating system, arcade, portable console, etc.       |
| `platform_logos`                 | Optional / Useful | Logo image metadata for platforms. Useful for UI design.                                                  |
| `platform_versions`              |          Optional | Specific hardware/platform versions or variants.                                                          |
| `platform_version_companies`     |          Optional | Companies associated with specific platform versions.                                                     |
| `platform_version_release_dates` |          Optional | Release dates for specific platform hardware versions.                                                    |
| `platform_websites`              |          Optional | Websites associated with platforms.                                                                       |

---

### 4. Release Dates, Date Formats, and Regions

These endpoints describe when and where games were released.

| Endpoint                | Relevance | Quick Description                                                                                                                  |
| ----------------------- | --------: | ---------------------------------------------------------------------------------------------------------------------------------- |
| `release_dates`         | Essential | Detailed release dates by game, platform, region, date format, and status. Better than relying only on `games.first_release_date`. |
| `release_date_regions`  |    Useful | Lookup table for release regions such as North America, Europe, Japan, worldwide, etc.                                             |
| `release_date_statuses` |    Useful | Lookup table for release status such as released, delayed, cancelled, TBD, etc.                                                    |
| `date_formats`          |    Useful | Date precision lookup, such as exact date, month/year only, year-only, or TBD.                                                     |
| `regions`               |    Useful | General region lookup table used by regional endpoints.                                                                            |

---

### 5. Companies, Developers, and Publishers

These endpoints describe who made, published, ported, or supported a game.

| Endpoint                 |         Relevance | Quick Description                                                                                                                |
| ------------------------ | ----------------: | -------------------------------------------------------------------------------------------------------------------------------- |
| `companies`              |         Essential | Main company endpoint. Stores developers, publishers, descriptions, country, parent company, logos, websites, and related games. |
| `involved_companies`     |         Essential | Bridge endpoint linking games to companies and identifying roles: developer, publisher, porting, or supporting.                  |
| `company_logos`          | Optional / Useful | Company logo image metadata.                                                                                                     |
| `company_websites`       |            Useful | Official and external websites for companies.                                                                                    |
| `company_sizes`          |          Optional | Lookup table for company size categories.                                                                                        |
| `company_statuses`       |          Optional | Lookup table for company status, such as active, defunct, merged, or renamed.                                                    |
| `company_types`          |          Optional | Lookup table for company type categories.                                                                                        |
| `company_type_histories` |          Optional | Historical company type or company relationship changes.                                                                         |

---

### 6. Media, Visuals, and External Links

These endpoints enrich the UI and make dashboards or recommendation cards more visual.

| Endpoint        |   Relevance | Quick Description                                                                                           |
| --------------- | ----------: | ----------------------------------------------------------------------------------------------------------- |
| `covers`        | Very Useful | Game cover image metadata. Great for recommendation cards and game profile pages.                           |
| `screenshots`   | Very Useful | Screenshot image metadata for games. Useful for visual browsing and detail pages.                           |
| `artworks`      |      Useful | Promotional or official artwork images.                                                                     |
| `artwork_types` |    Optional | Lookup table describing artwork types.                                                                      |
| `game_videos`   |      Useful | Game trailer/video metadata, often connected to YouTube IDs.                                                |
| `websites`      | Very Useful | Game-related external URLs, such as official website, Steam page, wiki, social media, Discord, Reddit, etc. |
| `website_types` |      Useful | Lookup table defining website categories.                                                                   |

---

### 7. Popularity, Attention, and Demand Signals

These endpoints help measure visibility, demand, or player attention.

| Endpoint                |   Relevance | Quick Description                                                                           |
| ----------------------- | ----------: | ------------------------------------------------------------------------------------------- |
| `popularity_primitives` | Very Useful | Popularity signal records for games. Useful for hidden-gem logic and popularity analysis.   |
| `popularity_types`      | Very Useful | Lookup table defining what each popularity signal means. Used with `popularity_primitives`. |

---

### 8. Collections, Series, and Franchises

These endpoints describe game series and broader intellectual property relationships.

| Endpoint                      |         Relevance | Quick Description                                                                                  |
| ----------------------------- | ----------------: | -------------------------------------------------------------------------------------------------- |
| `collections`                 |            Useful | Groups related games, often representing a series or collection.                                   |
| `collection_memberships`      |            Useful | Links games to collections.                                                                        |
| `collection_membership_types` | Optional / Useful | Defines how a game belongs to a collection.                                                        |
| `collection_relations`        | Optional / Useful | Defines relationships between collections, such as parent/child series relationships.              |
| `collection_relation_types`   |          Optional | Lookup table for collection relationship types.                                                    |
| `collection_types`            |          Optional | Lookup table for collection types.                                                                 |
| `franchises`                  |            Useful | Broader intellectual property/franchise groupings, such as Pokémon, Final Fantasy, Star Wars, etc. |

---

### 9. Age Ratings and Content Warnings

These endpoints help with mature-content filtering, family-friendly filtering, or content-aware recommendations.

| Endpoint                               |         Relevance | Quick Description                                                             |
| -------------------------------------- | ----------------: | ----------------------------------------------------------------------------- |
| `age_ratings`                          |            Useful | Age ratings assigned to games by rating organizations.                        |
| `age_rating_categories`                |            Useful | Lookup table for rating labels/categories.                                    |
| `age_rating_organizations`             |            Useful | Rating boards such as ESRB, PEGI, CERO, USK, etc.                             |
| `age_rating_content_descriptions`      | Optional / Legacy | Older endpoint for age-rating content warnings. Prefer V2 when possible.      |
| `age_rating_content_description_types` |          Optional | Lookup table for types of content warnings.                                   |
| `age_rating_content_descriptions_v2`   |            Useful | Updated content warning descriptions explaining why a game received a rating. |

---

### 10. Language and Localization

These endpoints help if recommendations need language constraints.

| Endpoint                 |         Relevance | Quick Description                                                       |
| ------------------------ | ----------------: | ----------------------------------------------------------------------- |
| `languages`              |            Useful | Language lookup table, such as English, French, Japanese, Spanish, etc. |
| `language_supports`      |            Useful | Links games to supported languages and support types.                   |
| `language_support_types` |            Useful | Defines support type, such as interface, subtitles, or audio.           |
| `game_localizations`     | Optional / Useful | Localized game names and covers. Also related to the core game catalog. |

---

### 11. External Game Matching

These endpoints help connect IGDB games to other services, stores, or datasets.

| Endpoint                |         Relevance | Quick Description                                                                                                     |
| ----------------------- | ----------------: | --------------------------------------------------------------------------------------------------------------------- |
| `external_games`        | Very Useful Later | Links IGDB games to external services, stores, platforms, or databases. Useful for matching to Steam, GOG, Epic, etc. |
| `external_game_sources` |            Useful | Lookup table defining the external source/platform.                                                                   |

---

### 12. Game Engines and Technical Metadata

These endpoints describe technical development metadata.

| Endpoint            |         Relevance | Quick Description                                                              |
| ------------------- | ----------------: | ------------------------------------------------------------------------------ |
| `game_engines`      | Optional / Useful | Game engines used to develop games, such as Unity, Unreal Engine, Source, etc. |
| `game_engine_logos` |          Optional | Logo image metadata for game engines.                                          |

---

### 13. Game Versions and Editions

These endpoints describe editions, versions, remasters, bundles, and version-specific features.

| Endpoint                      |         Relevance | Quick Description                                       |
| ----------------------------- | ----------------: | ------------------------------------------------------- |
| `game_versions`               | Optional / Useful | Connects a main game to editions or versions.           |
| `game_version_features`       |          Optional | Features that differ between game versions or editions. |
| `game_version_feature_values` |          Optional | Specific values for game version features.              |

---

### 14. Characters

These endpoints describe characters inside games.

| Endpoint              | Relevance | Quick Description                                                                           |
| --------------------- | --------: | ------------------------------------------------------------------------------------------- |
| `characters`          |  Optional | Game characters, including names, descriptions, related games, gender, species, and images. |
| `character_genders`   |  Optional | Lookup table for character gender categories.                                               |
| `character_species`   |  Optional | Lookup table for character species.                                                         |
| `character_mug_shots` |  Optional | Character portrait/image metadata.                                                          |

---

### 15. Events and Event Networks

These endpoints describe gaming events, showcases, and event-related links.

| Endpoint         | Relevance | Quick Description                                                 |
| ---------------- | --------: | ----------------------------------------------------------------- |
| `events`         |  Optional | Gaming events, showcases, conferences, streams, or announcements. |
| `event_logos`    |  Optional | Event logo image metadata.                                        |
| `event_networks` |  Optional | External links or networks associated with events.                |
| `network_types`  |  Optional | Lookup table for event network/link types.                        |

---

### 16. Reports, Moderation, Webhooks, and System Utility

These are mostly irrelevant for a student analytics/recommendation project.

| Endpoint       |          Relevance | Quick Description                                                                                                           |
| -------------- | -----------------: | --------------------------------------------------------------------------------------------------------------------------- |
| `reports`      |             Ignore | IGDB moderation/reporting records. Not useful for this project.                                                             |
| `report_types` |             Ignore | Lookup table for report/moderation categories.                                                                              |
| `entity_types` |   Ignore / Utility | Internal IGDB entity type definitions. Only useful for a generic IGDB explorer.                                             |
| `webhooks`     | Production Utility | Used to receive notifications when IGDB records change. Useful for production sync pipelines, not a normal analytics table. |

---

## Part 2 — Alphabetical Endpoint List With Quick Descriptions

| Endpoint                               | Category                                          | Quick Description                                                                                             |
| -------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `age_rating_categories`                | Age Ratings and Content Warnings                  | Lookup table for age-rating labels/categories.                                                                |
| `age_rating_content_description_types` | Age Ratings and Content Warnings                  | Lookup table for types of content warnings.                                                                   |
| `age_rating_content_descriptions`      | Age Ratings and Content Warnings                  | Older content-warning endpoint. Prefer V2 when possible.                                                      |
| `age_rating_content_descriptions_v2`   | Age Ratings and Content Warnings                  | Updated content-warning endpoint explaining rating reasons.                                                   |
| `age_rating_organizations`             | Age Ratings and Content Warnings                  | Rating boards such as ESRB, PEGI, CERO, USK, etc.                                                             |
| `age_ratings`                          | Age Ratings and Content Warnings                  | Age ratings assigned to games by rating organizations.                                                        |
| `alternative_names`                    | Core Game Catalog                                 | Alternate, regional, acronym, or old names for games.                                                         |
| `artwork_types`                        | Media, Visuals, and External Links                | Lookup table describing artwork types.                                                                        |
| `artworks`                             | Media, Visuals, and External Links                | Promotional or official artwork images for games.                                                             |
| `character_genders`                    | Characters                                        | Lookup table for character gender categories.                                                                 |
| `character_mug_shots`                  | Characters                                        | Character portrait/image metadata.                                                                            |
| `character_species`                    | Characters                                        | Lookup table for character species categories.                                                                |
| `characters`                           | Characters                                        | Game characters with names, descriptions, related games, images, gender, and species.                         |
| `collection_membership_types`          | Collections, Series, and Franchises               | Lookup table explaining how a game belongs to a collection.                                                   |
| `collection_memberships`               | Collections, Series, and Franchises               | Links games to collections.                                                                                   |
| `collection_relation_types`            | Collections, Series, and Franchises               | Lookup table for relationship types between collections.                                                      |
| `collection_relations`                 | Collections, Series, and Franchises               | Relationships between collections, such as parent/child series.                                               |
| `collection_types`                     | Collections, Series, and Franchises               | Lookup table defining collection types.                                                                       |
| `collections`                          | Collections, Series, and Franchises               | Groups of related games, often representing a series or collection.                                           |
| `companies`                            | Companies, Developers, and Publishers             | Main company endpoint for developers, publishers, parent companies, descriptions, logos, and websites.        |
| `company_logos`                        | Companies, Developers, and Publishers             | Company logo image metadata.                                                                                  |
| `company_sizes`                        | Companies, Developers, and Publishers             | Lookup table for company size categories.                                                                     |
| `company_statuses`                     | Companies, Developers, and Publishers             | Lookup table for company status, such as active, defunct, merged, or renamed.                                 |
| `company_type_histories`               | Companies, Developers, and Publishers             | Historical company type or relationship changes.                                                              |
| `company_types`                        | Companies, Developers, and Publishers             | Lookup table for company type categories.                                                                     |
| `company_websites`                     | Companies, Developers, and Publishers             | Official and external websites for companies.                                                                 |
| `covers`                               | Media, Visuals, and External Links                | Game cover image metadata.                                                                                    |
| `date_formats`                         | Release Dates, Date Formats, and Regions          | Date precision lookup, such as exact date, month/year, year-only, or TBD.                                     |
| `entity_types`                         | Reports, Moderation, Webhooks, and System Utility | Internal IGDB entity type definitions. Usually not needed.                                                    |
| `event_logos`                          | Events and Event Networks                         | Event logo image metadata.                                                                                    |
| `event_networks`                       | Events and Event Networks                         | External links or networks associated with events.                                                            |
| `events`                               | Events and Event Networks                         | Gaming events, showcases, conferences, streams, or announcements.                                             |
| `external_game_sources`                | External Game Matching                            | Lookup table defining external sources/platforms.                                                             |
| `external_games`                       | External Game Matching                            | Links IGDB games to external services, stores, platforms, or databases.                                       |
| `franchises`                           | Collections, Series, and Franchises               | Broader intellectual property/franchise groupings.                                                            |
| `game_engine_logos`                    | Game Engines and Technical Metadata               | Logo image metadata for game engines.                                                                         |
| `game_engines`                         | Game Engines and Technical Metadata               | Game engines used to develop games, such as Unity or Unreal Engine.                                           |
| `game_localizations`                   | Core Game Catalog / Language and Localization     | Localized game names and covers by region or language.                                                        |
| `game_modes`                           | Game Classification, Vibe, and Discovery          | Gameplay modes such as single-player, multiplayer, co-op, MMO, split-screen, etc.                             |
| `game_release_formats`                 | Core Game Catalog                                 | Release format or release type metadata.                                                                      |
| `game_statuses`                        | Core Game Catalog                                 | Game status such as released, beta, alpha, cancelled, or early access.                                        |
| `game_time_to_beats`                   | Core Game Catalog                                 | Time-to-beat estimates for quick, normal, and completionist playthroughs.                                     |
| `game_types`                           | Core Game Catalog                                 | Game type/category such as main game, DLC, expansion, remake, remaster, port, etc.                            |
| `game_version_feature_values`          | Game Versions and Editions                        | Specific values for version/edition features.                                                                 |
| `game_version_features`                | Game Versions and Editions                        | Features that differ between versions or editions.                                                            |
| `game_versions`                        | Game Versions and Editions                        | Connects main games to editions or versions.                                                                  |
| `game_videos`                          | Media, Visuals, and External Links                | Game trailers or video metadata, often connected to YouTube IDs.                                              |
| `games`                                | Core Game Catalog                                 | Main game endpoint and center of the database.                                                                |
| `genres`                               | Game Classification, Vibe, and Discovery          | Broad gameplay categories such as RPG, Shooter, Adventure, Racing, Strategy, etc.                             |
| `involved_companies`                   | Companies, Developers, and Publishers             | Bridge endpoint connecting games to companies and identifying developer/publisher/porting/supporting roles.   |
| `keywords`                             | Game Classification, Vibe, and Discovery          | Fine-grained tags and concepts such as zombies, cyberpunk, stealth, open world, etc.                          |
| `language_support_types`               | Language and Localization                         | Defines language support type, such as interface, subtitles, or audio.                                        |
| `language_supports`                    | Language and Localization                         | Connects games to supported languages and support types.                                                      |
| `languages`                            | Language and Localization                         | Language lookup table.                                                                                        |
| `multiplayer_modes`                    | Game Classification, Vibe, and Discovery          | Detailed multiplayer support by game/platform.                                                                |
| `network_types`                        | Events and Event Networks                         | Lookup table for event network/link types.                                                                    |
| `platform_families`                    | Platforms and Hardware                            | Groups related platforms, such as PlayStation, Xbox, or Nintendo.                                             |
| `platform_logos`                       | Platforms and Hardware                            | Platform logo image metadata.                                                                                 |
| `platform_types`                       | Platforms and Hardware                            | Platform category/type such as console, computer, operating system, arcade, etc.                              |
| `platform_version_companies`           | Platforms and Hardware                            | Companies associated with specific platform versions.                                                         |
| `platform_version_release_dates`       | Platforms and Hardware                            | Release dates for specific platform hardware versions.                                                        |
| `platform_versions`                    | Platforms and Hardware                            | Specific hardware/platform versions or variants.                                                              |
| `platform_websites`                    | Platforms and Hardware                            | Websites associated with platforms.                                                                           |
| `platforms`                            | Platforms and Hardware                            | Main platform endpoint for PC, PlayStation, Xbox, Nintendo Switch, mobile, older consoles, etc.               |
| `player_perspectives`                  | Game Classification, Vibe, and Discovery          | Camera/view style such as first-person, third-person, side view, bird view, text-based, etc.                  |
| `popularity_primitives`                | Popularity, Attention, and Demand Signals         | Popularity signal records for games. Useful for hidden-gem logic.                                             |
| `popularity_types`                     | Popularity, Attention, and Demand Signals         | Defines what each popularity signal means.                                                                    |
| `regions`                              | Release Dates, Date Formats, and Regions          | General region lookup table.                                                                                  |
| `release_date_regions`                 | Release Dates, Date Formats, and Regions          | Lookup table for release regions such as North America, Europe, Japan, worldwide, etc.                        |
| `release_date_statuses`                | Release Dates, Date Formats, and Regions          | Lookup table for release status such as released, delayed, cancelled, or TBD.                                 |
| `release_dates`                        | Release Dates, Date Formats, and Regions          | Detailed release dates by game, platform, region, date format, and status.                                    |
| `report_types`                         | Reports, Moderation, Webhooks, and System Utility | Lookup table for report/moderation categories.                                                                |
| `reports`                              | Reports, Moderation, Webhooks, and System Utility | IGDB moderation/reporting records. Not useful for this project.                                               |
| `screenshots`                          | Media, Visuals, and External Links                | Screenshot image metadata for games.                                                                          |
| `search`                               | Game Classification, Vibe, and Discovery          | General search endpoint used for lookup/testing.                                                              |
| `themes`                               | Game Classification, Vibe, and Discovery          | High-level themes or moods such as Fantasy, Sci-Fi, Horror, Survival, Mystery, Comedy, etc.                   |
| `webhooks`                             | Reports, Moderation, Webhooks, and System Utility | Production utility for receiving notifications when IGDB records change.                                      |
| `website_types`                        | Media, Visuals, and External Links                | Lookup table defining website categories.                                                                     |
| `websites`                             | Media, Visuals, and External Links                | Game-related external URLs such as official websites, Steam pages, social links, wikis, Discord, Reddit, etc. |

---

## Part 3 — Best Groups to Prioritize for the Project

For the IGDB Game Discovery & RAG Recommendation System, the most important groups are:

1. **Core Game Catalog**
2. **Game Classification, Vibe, and Discovery**
3. **Platforms and Hardware**
4. **Release Dates, Date Formats, and Regions**
5. **Companies, Developers, and Publishers**
6. **Media, Visuals, and External Links**
7. **Popularity, Attention, and Demand Signals**

The optional groups are still useful, but they should come after the main database works correctly:

1. **Collections, Series, and Franchises**
2. **Age Ratings and Content Warnings**
3. **Language and Localization**
4. **External Game Matching**
5. **Game Engines and Technical Metadata**
6. **Game Versions and Editions**
7. **Characters**
8. **Events and Event Networks**

The lowest priority group is:

1. **Reports, Moderation, Webhooks, and System Utility**

For the relational database design, the most important distinction is whether each endpoint behaves like a:

* **Core entity table**: `games`, `companies`, `platforms`
* **Lookup table**: `genres`, `themes`, `game_types`, `platform_types`
* **Bridge/detail table**: `involved_companies`, `release_dates`, `language_supports`
* **Media/enrichment table**: `covers`, `screenshots`, `websites`, `game_videos`
* **Utility/system endpoint**: `search`, `reports`, `webhooks`
