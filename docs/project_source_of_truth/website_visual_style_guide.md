# Website Visual Style Guide

This document defines the current visual direction for the final IGDB Game Discovery website. It should be used as the design source of truth when improving existing pages or building new website pages.

The goal is not to make every page visually identical. The goal is to keep the website coherent: same atmosphere, same interaction logic, same typography attitude, and same readability standards.

## 1. Overall Visual Direction

The website uses a dark cyberpunk visual style inspired by Night City, neon signage, game discovery terminals, and high-contrast digital interfaces.

The intended feeling is:

- futuristic;
- game-focused;
- cinematic;
- high-contrast;
- slightly aggressive;
- readable despite the visual intensity.

The website should feel more custom and expressive than Streamlit. It should not look like a generic dashboard, a plain analytics report, or a corporate SaaS page.

## 2. Current Home Page Reference

The current home page is the strongest visual reference for the website.

Current key decisions:

- The home page uses a full-width hero section.
- The hero background uses the exact asset `cyberpunk_nightcity.webp`.
- The main title is large, uppercase, and glitch-styled.
- The main call-to-action is `RECOMMEND ME`.
- The page uses black, white, and orange as the strongest structural colors.
- Pending features are shown clearly instead of hidden.
- The home page acts as a launchpad, not as a data-heavy report.

Important implementation files:

- `apps/website/src/app/page.tsx`
- `apps/website/src/app/globals.css`
- `apps/website/src/components/SiteHeader.tsx`
- `apps/website/public/assets/cyberpunk_nightcity.webp`

## 3. Color System

### Primary Background

Use near-black backgrounds as the base.

Recommended values:

- `#000000`
- `#02040b`
- `#060817`
- `#0b1024`

### Primary Text

Use white or near-white text for important content.

Recommended values:

- `#ffffff`
- `rgba(255, 255, 255, 0.94)`
- `rgba(255, 255, 255, 0.78)` for secondary text

### Main Accent

The current strongest accent is orange.

Recommended value:

- `#FF3E00`

Use orange for:

- section labels;
- active visual marks;
- cyberpunk UI details;
- underline accents;
- small system/status labels;
- hero glow accents.

### Secondary Neon Accents

Use cyan, magenta, and green carefully. They should support the cyberpunk feel without making the page visually noisy.

Recommended values:

- cyan: `#00FFF0`
- magenta/red: `#FF0050`
- green active status: `#39FF14`

Use these mostly for:

- glitch text shadows;
- active status lights;
- small highlights;
- subtle neon effects.

Do not use all neon accents at full strength in the same component unless the component is intentionally glitchy or high-energy.

## 4. Typography

### Main Display Text

Use heavy uppercase typography for hero titles and feature-card titles.

Current style:

- font family: `"Arial Black", Impact, system-ui, sans-serif`
- uppercase;
- tight letter spacing;
- large scale;
- strong line-height compression.

Example usage:

- `FIND YOUR NEXT GAME_`
- `RECOMMEND ME_`
- `EXPLORE GAMES_`

### Micro/System Text

Use monospace for small labels and system-like UI text.

Current style:

- font family: `Consolas, "Courier New", monospace`
- uppercase;
- wide letter spacing;
- small font size.

Use this for:

- section labels;
- status labels;
- menu labels;
- metadata labels;
- footer labels.

Example usage:

- `INDEX_ // IGDB GAME DISCOVERY`
- `SELECT MODULE_`
- `SEC_01 //`
- `MENU_INDEX_`

### Body Text

Body text should stay readable and calmer than display text.

Recommended rules:

- avoid overly small body text;
- use comfortable line-height;
- use white or near-white;
- keep paragraph widths controlled;
- avoid long paragraphs on visually intense backgrounds.

## 5. Hero Section Rules

The home-page hero sets the standard for cinematic website sections.

Current hero rules:

- Use full-width visual impact.
- Keep the image or background dominant.
- Use a large title as the main visual anchor.
- Place primary CTA buttons below the supporting sentence.
- Preserve readability without hiding the background too much.

Current hero background:

- asset: `cyberpunk_nightcity.webp`
- served from: `apps/website/public/assets/cyberpunk_nightcity.webp`
- CSS reference: `url("/assets/cyberpunk_nightcity.webp")`

Important rule: if a section uses an image background, text must be readable without placing an obvious rectangular black box behind it unless the design explicitly calls for a terminal/card style.

Preferred readability techniques:

- text shadow;
- radial glow behind text;
- subtle gradient overlay;
- controlled font weight;
- limited background darkening;
- careful text placement over lower-detail image areas.

Avoid:

- visible black boxes behind hero subtitles unless intentionally designed;
- heavy borders around text;
- outlined body text;
- overlays so dark that the background image becomes pointless.

## 6. Button and CTA Rules

Primary homepage CTAs currently use a stark black-and-white modular style.

Current behavior:

- default state: black background, white text;
- hover state: white background, black text;
- disabled state: black background, muted white text.

Buttons should feel direct and game-like, not soft or corporate.

Recommended CTA wording:

- `RECOMMEND ME`
- `EXPLORE`
- `ASK GUIDE` only when the guide/chatbot is ready or clearly disabled.

Avoid long button labels when possible. Short commands work better with the current visual style.

## 7. Feature Card Rules

Feature/module cards should act like selectable modules.

Current card behavior:

- black background;
- white text;
- white grid dividers;
- large uppercase card titles;
- small section codes;
- active or pending status lights;
- description revealed on hover.

Current module pattern:

- `RECOMMEND ME_`
- `EXPLORE GAMES_`
- `ASK THE GUIDE_`
- `HIDDEN GEMS_`
- `INSIGHTS_`
- `METHOD_`

Active modules should be clickable.

Pending modules should:

- be visible;
- be labeled as pending or soon;
- not pretend to be finished;
- avoid broken links.

## 8. Navigation Rules

The current navigation is a cyberpunk hamburger menu.

Current behavior:

- black header;
- white border;
- orange project label;
- hamburger menu;
- active routes listed as clickable entries;
- pending routes listed separately only when unfinished modules exist;
- active links close the menu on click.

Navigation should keep the project structure clear without overcrowding the top bar.

Current active links:

- `HOME_`
- `EXPLORE_`
- `HIDDEN GEMS_`
- `RECOMMEND_`
- `ASK THE GUIDE_`
- `INSIGHTS_`
- `METHOD_`

Current pending links:

- None in the current website shell.

## 9. Status and Availability Rules

The website should be honest about what exists and what is planned.

Use status indicators for:

- active modules;
- pending modules;
- offline or unavailable functionality;
- future model/RAG integrations.

Current status color logic:

- active: green `#39FF14`;
- pending: orange `#FF3E00`;
- offline/error: red.

Do not hide future modules if they are important to the product story. Mark them clearly as pending.

## 10. Image and Asset Rules

Images used by the website should be available from the Next.js public directory.

For browser-served static assets, use:

- `apps/website/public/assets/`

Example:

- local file path: `apps/website/public/assets/cyberpunk_nightcity.webp`
- browser path: `/assets/cyberpunk_nightcity.webp`

Do not reference files directly from `assets/` in CSS or React components unless they are copied into the website public folder or imported through the build system.

If an image is essential to a page, make sure it is committed with the page changes.

## 11. Animation Rules

Animation should be used carefully.

Allowed animation types:

- subtle glitch effects for hero titles;
- small hover state changes;
- slight neon flickers if not distracting;
- small motion on decorative effects.

Avoid:

- constant large motion that fights readability;
- animation on every component;
- effects that make the page feel unstable;
- heavy animation that could slow the page.

The current home title glitch is intentionally aggressive because it is the primary landing-page visual identity. Other pages should generally use calmer styling unless they need a strong visual moment.

## 12. Readability Rules

Readability is a hard requirement.

For text over complex backgrounds:

- use strong text contrast;
- use text shadow;
- use controlled line length;
- use stronger font weight;
- use soft radial backing if needed;
- keep overlays subtle but effective.

Do not solve every readability issue with a visible rectangle. Use a visible card only when the content is meant to feel like a panel, terminal, or module.

For analytic or explanatory pages:

- prioritize clear text hierarchy;
- avoid huge decorative backgrounds behind dense content;
- use panels or sections for longer reading;
- reserve intense visuals for headers and transitions.

## 13. Page-Type Guidance

### Home Page

Purpose:

- introduce the product;
- create visual identity;
- route users to core modules.

Style:

- cinematic;
- high-impact;
- visual-heavy;
- minimal explanation.

### Explore Games Page

Purpose:

- browse and filter the catalog.

Style:

- more functional than the home page;
- still cyberpunk;
- cards and filters should be readable first.

Avoid making the catalog difficult to scan just to preserve the visual style.

### Recommendations Page

Purpose:

- guide the user through preference-based game discovery.

Style:

- wizard-like;
- clear steps;
- strong progress indication;
- recommendations should feel like results from a system, not a generic list.

Use `RECOMMEND ME` consistently as the user-facing action label.

### Methodology Page

Purpose:

- explain data source, extraction logic, scoring logic, limitations, and interpretation rules.

Style:

- calmer;
- structured;
- transparent;
- readable.

This page can use cyberpunk panels but should not sacrifice clarity.

### Ask the Guide Page

Purpose:

- allow users to ask natural-language questions about games and recommendations;
- display catalog-grounded retrieved games;
- show caveats when RAG artifacts, ratings, or metadata are incomplete.

Style:

- conversational terminal or guide interface;
- clear distinction between user question, retrieved context, and final answer;
- visible limitations and source/context indicators.

## 14. Implementation Notes

Current main style file:

- `apps/website/src/app/globals.css`

Current home page:

- `apps/website/src/app/page.tsx`

Current header:

- `apps/website/src/components/SiteHeader.tsx`

When adding new styles:

- reuse existing classes where reasonable;
- avoid duplicating large visual systems per page;
- use semantic class names for page-specific visual rules;
- keep global CSS organized by page or component family;
- validate the frontend after meaningful changes with `npm.cmd run build`.

## 15. Current Validation Standard

Before committing website UI work, run:

```powershell
cd "C:\Users\calvi\Data Science\Community_Project\apps\website"
npm.cmd run build
```

The build should complete successfully.

The current webpack cache warning is non-blocking if the production build still compiles and all routes are generated.

## 16. Current Design Status

The home page is considered visually accepted as of the current session.

The current homepage style should be treated as the baseline for future website polish. Future pages can adapt the style, but they should not introduce an unrelated visual language without updating this guide.
