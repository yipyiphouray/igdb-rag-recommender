# Home Page UI Improvement Plan

This file consolidates the Home page UI improvement versions into one implementation history. Each section summarizes the intent of that version without preserving the original draft wording.

## V1

- Define the Home page as a game-menu-style launchpad.
- Make each menu choice route users to a different project function.
- Target both the professor/evaluator and casual gamers.
- Establish the first cyberpunk/hacker-terminal visual direction.
- Include a hero section, main calls to action, feature cards, compact trust/status content, and footer.
- Prioritize routes for recommendations, exploration, chatbot, hidden gems, and methodology.
- Keep wording understandable and avoid overly technical language.

## V2

- Remove visible navigation-priority explanations and overly forced copy.
- Remove data trust and project pillar sections that felt out of place.
- Shift the visual direction toward a more polished cyberpunk game launcher.
- Centralize the hero card and make the three main actions clearer.
- Use more user-friendly wording.
- Move away from the early background grid look.

## V3

- Refine the visual system into a high-contrast industrial style.
- Use black, white, and orange as the main design language.
- Use heavy headings, tiny monospaced labels, sharp borders, and mechanical hover states.
- Remove large status tags from feature cards.
- Replace readiness text with smaller status lights.
- Make feature-card titles larger and centered.
- Reveal feature-card descriptions on hover.

## V4

- Remove the large API/status panel from the Home page.
- Explore cyberpunk city background ideas.
- Keep feature-card titles visually centered.
- Use Ghost in the Shell references as visual inspiration.
- Keep the page aesthetic strong while reducing clutter.

## V5

- Shorten labels that wrapped poorly, especially recommendation-related wording.
- Remove the first CSS skyline/visual experiment.
- Replace the old top navigation with a hamburger dropdown that matches the website style.
- Update the top bar away from blue/purple styling.
- Add a GitHub reference link in the footer.

## V6

- Remove the CSS visual background experiment.
- Recenter and refit the hero content.
- Improve the hero description so it feels catchy but still clear.
- Fix hero button wording that wrapped onto two lines.
- Remove the `Hover for details` instruction.

## V7

- Finalize better wording for the recommendation button and feature card.
- Keep the hamburger icon visually simple and white.
- Add white dividing lines between the three hero action buttons.
- Add a glitch/distortion effect to the `FIND YOUR NEXT GAME_` hero title.
- Keep feature-card labels fitting cleanly.

## V8

- Make the hero glitch effect faster, more constant, and more visually intense.
- Keep the hero title stable in two lines even while glitching.
- Improve the `Recommend Me_` feature-card description so it fits as one line.
- Fix unwanted horizontal scrolling caused by overly wide page elements.

## V9

- Use the exact `cyberpunk_nightcity.webp` asset as the hero background.
- Make the hero subtitle readable over the image without using a visible black box, outline, or bordered overlay.
- Keep the image prominent while preserving text contrast.
- Fix the slight `E` and `X` overlap in `NEXT GAME_` by loosening the second line spacing.

## V10

- Add a cyberpunk text-scramble/data-decryption effect to module-card labels.
- Trigger the effect when hovering over the card.
- Make the text cycle through random characters before resolving left to right.
- Keep the effect smooth and responsive.

## V11

- Refine the text-scramble effect timing and behavior.
- Remove the red glow from the scrambled text.
- Ensure the effect starts from the beginning of the word and resolves left to right.
- Tune the animation through several timing passes.
- Finalize the current scramble duration at `0.8 seconds` while keeping the motion smooth.

