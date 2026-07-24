# UI Polish Version 2 Plan

## Home Page

Remove the introduction with the stats of the games, release years, hidden gems count, and reliable-rated shared

remove the sentence: "Choose the path that matches what you want to do next."

I want this page to feel like a retro game menu. Right now You have panels of each pages but then you have a small link to it. Instead of this i want the home page like a game menu with the retro feel - change the theme and colors behind to fit this. 

For the panels, make it only the title of the pages and when we hover over it, we have the full details of the page. 

## Explore Games Page

Provide the option for the user to select the type of views. 

Here are the possible view they can list: 

Grid View: Having the Cover of the game like a grid. 

List view: just like we set right now, however for the details can you include it within the rectangle and not outside. 

Detailed view: This view it is like the list view however we provide all the details in one retangle

## Hidden Gems Page

The hidden gem rule can you instead of making it a toggle option just show it in front. 

follow the same request that i asked for Explore Games Page

## Recommendations Page

Can we make it a like an interactive questionnaire instead of a static filter with questions. Like we ask the user each of these questions one by one. 

## Insights Page

I want it to be more in-depth. Looking at our notebooks we have more charts to show. I want everything to be available in this page for both the descriptive and diagnostic 

Remove the hidden gem lab and coverage & caveats. 

This insights page is a dedicated "for the data nerds" page. I want it in depth

## Methodology Page

I don't really like the toggle rectangle option make the experience more seemless. 


## Overall theme Change

I want the entire theme to be like a retro game. Change the colors and the background as needed.

## Clarified Implementation Decisions

- Theme direction: cyberpunk / dark neon arcade.
- Home page: remove dataset stats and the "Choose the path..." sentence.
- Home menu: make each full menu panel clickable; details appear on hover.
- Explore Games default view: List View.
- Explore Games views:
  - Grid View: cover-focused grid.
  - List View: compact horizontal card with useful details inside the rectangle.
  - Detailed View: expanded card with useful fields inside one rectangle.
- Hidden Gems: use the same view options as Explore Games.
- Hidden Gems rule: show the rule directly in a visible styled rule box instead of an expander/toggle.
- Recommendations: use a step-by-step wizard with Back, Next, Reset, and final Show Recommendations controls.
- Insights: make descriptive and diagnostic notebook outputs more available, but exclude hidden-gem and coverage-only analysis sections.
- Methodology: use a seamless continuous report-style page instead of expander/toggle rectangles.

## Implementation Notes

- Shared cyberpunk styling is handled in `src/app/components/ui_style.py`.
- Clickable Home menu panels are handled in `src/app/components/menu_card.py`.
- List/Grid/Detailed game views are handled in `src/app/components/game_card.py`.
- The Streamlit theme colors are configured in `apps/streamlit/.streamlit/config.toml`.
