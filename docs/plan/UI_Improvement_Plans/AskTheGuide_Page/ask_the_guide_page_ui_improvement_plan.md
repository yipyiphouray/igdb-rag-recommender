# Ask the Guide Page UI Improvement Plan

This file consolidates the Ask the Guide page design direction into one readable final-plan record.

## Final page role

Ask the Guide is the website's project-explanation assistant. It is designed to answer project-scoped questions about the IGDB dataset, methodology, analytics findings, hidden gems, recommendation logic, RAG design, and website navigation.

Ranked game recommendations should be handled by the Recommend Me page, not by Ask the Guide.

## Visual direction

The page should match the website's cyberpunk interface:

- black background;
- thin white borders;
- red/orange accent labels;
- terminal-inspired layout;
- direct system-like copy;
- compact controls;
- limited visual clutter.

## Guide identity

The Guide should feel like a focused system intelligence inside the project. It should speak directly and avoid exposing backend details such as model names, provider names, source files, paths, retrieval metadata, or internal modes.

## Chat layout

The main interaction should feel like a terminal session:

- the Guide's first message appears inside the chat stream;
- the response area uses terminal-style typography;
- the user input sits naturally with the terminal experience;
- pressing Enter submits the question;
- the input field should be focused by default;
- the chat area should remain readable and not overflow indefinitely.

## Athena visual panel

The page uses Athena as the visual face of the Guide.

The image should:

- remain static, without face animation;
- be cropped and fitted cleanly inside its panel;
- use a cyberpunk/technical presentation;
- avoid distracting overlays that cover the face;
- support the page's identity without becoming the main interaction.

## Help and prompt behavior

Starter prompts should be subtle. The page should not overload the user with large prompt grids.

Supported examples can be revealed through `/help`, and they should not stay permanently visible after the Guide responds unless the user requests help again.

## User-facing boundaries

The page should make the boundary clear without overexplaining:

- Ask the Guide answers project, methodology, dataset, analytics, RAG, and website-navigation questions.
- Recommend Me handles ranked game matching.
- The Guide should not expose implementation file names or internal source details.

## Final UX intent

The page should feel like a controlled project guide, not a general ChatGPT clone. The user can ask natural language questions, but the experience remains scoped to the project and routes recommendation behavior toward the dedicated recommender page.
