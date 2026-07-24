# UI Polish Version 1 Plan

This plan defines the first UI polish pass for the Streamlit MVP.

The goal is to make the app feel more like a game-discovery product and less like a raw analytics prototype, while keeping the methodology and caveats available for users who want the technical details.

## Global Direction

- Keep the app local-MVP friendly.
- Do not add predictive or RAG implementation in this polish pass.
- Preserve all existing trust rules and caveats.
- Move technical explanations out of user-facing discovery pages and into Methodology or expandable sections.
- Make Explore, Hidden Gems, and Recommendations use a consistent compact game-card style.

## Home Page

Goal:

- Turn the Home page into a game-menu style landing page.
- Make it clear where users should go next.
- Remove visual clutter.

Changes:

- Remove the technical signal explanation from Home:
  - `total_rating = quality/reception`
  - `total_rating_count = rating evidence/activity`
  - `PopScore interest = visibility/current interest`
- Keep the curated-sample caveat, but display it as a small footnote-style notice instead of a large blue info box.
- Remove featured hidden-gem cards from Home.
- Emphasize quick links to each major page:
  - Explore Games
  - Hidden Gems
  - Recommendations
  - Insights
  - Methodology
  - Chatbot
  - Predictive / Similarity Scoring

## Explore Games Page

Goal:

- Make Explore feel closer to a Steam-style catalog browser.

Changes:

- Replace large vertical game cards with compact horizontal cards.
- Left side: game cover image.
- Right side:
  - title;
  - release year;
  - rating;
  - rating evidence;
  - visibility status/percentile;
  - short summary;
  - compact genre/theme tags;
  - platform badges instead of long platform text.
- Use a detail expander for deeper metadata instead of placing every detail in the main card.
- Remove the technical signal explanation from the top of the page.

Implementation note:

- Native Streamlit hover cards are limited. Use compact cards plus a detail expander for V1.
- True platform icons can come later. For V1, use short platform badges such as `PC`, `Switch`, `PS`, `Xbox`, `Mac`, `Linux`, `iOS`, and `Android`.

## Hidden Gems Page

Goal:

- Make the page focused and simple.

Changes:

- Remove the technical signal explanation from the top of the page.
- Under the title, include one short paragraph explaining how hidden gems are identified.
- Use the same compact game-card style as Explore Games.
- Keep the hidden-gem caveat concise.

## Recommendations Page

Goal:

- Make Recommendations feel like a guided recommender, not another filter page.

Change the page into a guided preference form with user-facing questions:

- What platform do you play on?
- What kind of game are you in the mood for?
- Do you prefer popular games or hidden gems?
- How important is rating quality?
- Do you want shorter or longer games?
- How many recommendations do you want?

Additional changes:

- Hide technical scoring details inside an expander.
- Use the same compact game-card style as Explore Games.
- Keep recommendation explanations visible on result cards.

## Chatbot Page

Status:

- Not part of this UI polish implementation beyond keeping the placeholder stable.

## Insights Page

Goal:

- Make Insights feel like the "Data Nerds Only" page.
- It should present descriptive and diagnostic findings from previous notebooks in a dashboard style.

Changes:

- Separate descriptive and diagnostic insights clearly.
- Keep relevant charts and tables.
- Add short interpretation text.
- Make caveats visible but not overwhelming.

## Predictive / Similarity Scoring Page

Status:

- Not part of this UI polish implementation beyond keeping the placeholder stable.

## Methodology Page

Goal:

- Make Methodology the academic/trust page.
- This page should hold the technical explanations that are removed from user-facing discovery pages.

Changes:

- Explain source data.
- Explain sample design.
- Explain key metric definitions.
- Explain hidden-gem formula.
- Explain recommendation scoring.
- Show artifact audit.
- Show limitations and implementation boundaries.

## Acceptance Criteria

- Home feels like a clean app menu.
- Explore and Hidden Gems use compact horizontal cards.
- Recommendations uses guided questions instead of a technical filter form.
- Technical caveats are moved out of the main user flow and into Methodology/expanders.
- Insights feels intentionally analytical.
- Existing app data artifacts still load.
- Existing validation tests still pass.
- Predictive and Chatbot placeholders still load safely.
