# Explore Games Page UI Improvement Plan

This file consolidates the Explore Games page UI improvement versions into one implementation history. Each section summarizes the intent of that version without preserving the original draft wording.

## V1

- Match the Explore Games page styling to the Home page direction.
- Improve the page header with a more engaging one-liner and a user-friendly description.
- Add deeper filtering while keeping the controls approachable.
- Support multi-select filter categories where useful.
- Improve game image clarity.
- Rename user-facing `evidence` language to `Reviews`.
- Add grid/list view switching.
- Add game sorting controls.

## V2

- Extend the visual style beyond the filters so the full Explore page and game cards match the website.
- Rework the header one-liner and simplify the description so the page purpose is immediately clear.
- Further improve image clarity.
- Add numbered pagination instead of only previous/next controls.
- Add a website-styled loading indicator so page changes do not look broken while results load.

## V3

- Make cover images uniform and properly fitted so cards do not feel uneven or overly zoomed.
- Remove the extra grid/list mode indicator from the header area.
- Apply the final page background styling to the full Explore page, not only cards and filters.

## V4

- Remove remaining off-theme gradients and colors so the full page follows the black, white, and orange style.
- Use the Ghost in the Shell product-page reference as visual inspiration.
- Make game cards clickable.
- Add a game detail page so clicking a game opens a full view of available game data.

## V5

- Prevent Apply/Clear filter actions from forcing the user back to the top of the page.
- Fix Clear Filters so it fully resets active filters.
- Improve dropdown arrow positioning.
- Increase filter-label readability.
- Make the filter area collapsible by default.
- Restyle the pagination footer to avoid large white areas.
- Ensure game detail pages open at the top.
- Improve game detail labels with red/orange styling and larger font size.
- Fix long summaries so they do not end with unresolved truncation.
- Improve tag padding for readability.
- Make Explore page tags clickable so selecting a tag clears previous filters and applies that tag as the new filter.

## V6

- Replace the word-based minimized filter state with `+` and `-` controls.
- Fix Clear Filters so the visible filter buttons reset along with the catalog results.
- Add expandable `Read more` behavior for long game summaries.
- Remove duplicate lower-page summary content when the top summary already handles expansion.
- Make storyline content expandable in the same visual style.

## V7

- Keep the filter section open after Clear Filters is clicked.
- Refine the game detail `Read more` control so it looks like clickable text instead of a tag.

## v8

right now, when you select a different sorting logic, you need to click apply filters to execute the sorting logic. Can you change this to when the user click a different sorting option, it automatically applies without having to click "apply filters" 

