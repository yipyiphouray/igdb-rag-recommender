# Insights Page UI Improvement Plan

This file consolidates the Insights page UI improvement versions into one implementation history. Each section summarizes the intent of that version without preserving the original draft wording.

## V1

- Redesign the Insights page as a full dashboard.
- Use the strongest metrics and outputs from the descriptive and diagnostic notebooks.
- Split the page into two main tabs:
  - Descriptive;
  - Diagnostic.

## V2

- Simplify the header to focus on `Insights`.
- Make the description direct and easy to understand.
- Simplify tab labels to `Descriptive` and `Diagnostic`.
- Add hoverable definitions for useful technical labels.
- Improve diagnostic finding readability.
- Fix the layout issue that left an unwanted white gap in the findings section.
- Add terminology explanations for project-specific or technical concepts.

## V3

- Remove the red `Insights_` eyebrow from the header.
- Make tooltip popups stay readable within the viewport.
- Remove redundant dashboard-mode labels inside the tab content.
- Move tab explanations into the tab selector area.
- Apply the same simplification to both Descriptive and Diagnostic tabs.

## V4

- Return the Insights header to a left-aligned layout so it matches the other pages.
- Restore the red label format using:
  - `INSIGHTS_ // READ THE SIGNALS BEHIND THE CATALOG`
- Use the same `?` tooltip style as the Methodology page.
- Match red label sizing to the Methodology page.
- Increase the game-count font size in the Top Genres and Top Platforms sections.
- Remove horizontal table scrolling.
- Increase table header font size.
- Increase contrast for `?` icons inside table headers.
- Change the Project Terminology section to plain `{term}: {definition}` formatting instead of tooltip-based definitions.

