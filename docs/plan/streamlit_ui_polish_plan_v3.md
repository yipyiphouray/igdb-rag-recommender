# UI Polish Version 3 Plan

## Home Page

remove the word tag "cyberpunk game menu" 

For the titles of each panels, can you decrease the font size because certain title is too big and it goes through 2 lines

For the menu grid panel style, can you stack it into like  3 x 3 grid even though i know we have 7 panels only

## Explore Games Page

For the type of view, remove completely the list view. Keep only the grid view and the detailed view. 

Would it be possible to make sure that the picture of  the games cover the rectangle because right now the pictures are smaller than the actual rectangle. Also make sure the pictures are clear. 

## Hidden Gem Page

Can you make it overall easier for the users to use this page, I feel it has too much technical terms. You can keep terms but my overall feel right now is it is kinda overwhelming. 

Same comment for the picture as the Explore Games Page

## Recommendation Page

I want the experience to minimalistic. right now i feel it is very overwhelming. 

Also for the series of the questionnaire would it be possible like a central pop out question and then user click next or back and at the end they can review and confirm. 

## Insights Page

Can we make it clear for like a sub section for descriptive and diagnostic

also for the export browser don't show the source that contains my folder structure. Remove it. 


## Overall theme

For the cyberpunk theme use these following colors: 

 electric blues, hot pinks, vivid purples, and bright "Cyberpunk Yellow".

Same for background

## Other Request

What else can you suggest me to change/modify?

I want to maximize the capabilities of streamlit 

## Approved Additional Suggestions

- Add clearer empty states with practical suggestions for broadening filters.
- Make Hidden Gems presets more user-friendly:
  - Balanced discovery;
  - Strict hidden gems;
  - More discoveries.
- Add recommendation quick-start personas.
- Keep technical caveats mostly in Methodology instead of the main discovery flow.

## Implementation Notes

- Home now uses a reusable 3-column menu grid from `src/app/components/home_menu.py`.
- Home no longer shows the "cyberpunk game menu" tag.
- Menu title font size was reduced to avoid two-line overflow.
- Explore Games and Hidden Gems now expose only:
  - Grid View;
  - Detailed View.
- Game cover URLs are upgraded to larger IGDB image variants when possible, and card CSS uses `object-fit: cover`.
- Hidden Gems now uses user-facing discovery modes instead of technical sensitivity labels.
- Recommendations now uses:
  - quick-start personas;
  - centered question cards;
  - Back / Next / Reset controls;
  - final Review / Confirm before results.
- Insights now has:
  - Descriptive Insights;
  - Diagnostic Insights;
  - Export Browser.
- The export browser no longer displays local source file paths.
