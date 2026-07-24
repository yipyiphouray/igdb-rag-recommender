# Website Usability Testing Protocol

Generated: 2026-07-24

## Purpose

This protocol defines a concrete usability testing bar for the final IGDB game-discovery website.


## Testing Scope

The usability test covers the main website experience across the project pillars and product pages:

| Area | Website Page | Purpose Tested |
|---|---|---|
| Home / navigation | `/` | Can users understand the site and choose the right path? |
| Descriptive / catalog exploration | `/explore` | Can users browse and filter the game catalog? |
| Diagnostic / hidden gems | `/hidden-gems` | Can users understand and inspect hidden-gem candidates? |
| Prescriptive / recommendation workflow | `/recommendations` | Can users complete the structured recommendation flow? |
| Project explanation / RAG guide | `/guide` | Can users use Ask the Guide to understand the project? |
| Insights | `/insights` | Can users interpret high-level project findings? |
| Methodology | `/methodology` | Can users find the explanation of data, rules, and limitations? |

## Tester Requirement

Minimum testing group:

```text
5 testers
```

Recommended tester mix:

- at least 2 testers who are familiar with video games;
- at least 2 testers who are not deeply familiar with the project;
- at least 1 tester who focuses on professor/evaluator-style interpretation.

If only a smaller group is available, document the limitation directly.

## Pass Standard

The website usability test passes if all of the following are true:

```text
At least 5 testers complete the protocol.
At least 80% of testers complete each core task without help.
No critical blocker appears on any main page.
At least 80% of testers say the page purpose is clear after using it.
At least 80% of testers can identify where to go for recommendations.
At least 80% of testers can identify where to go for hidden gems.
```

## Failure Severity Levels

| Severity | Meaning | Example |
|---|---|---|
| Critical | Blocks the main task completely | Page fails to load; recommendation flow cannot submit; hidden gems do not display |
| High | User completes task only with help or workaround | User cannot find filters; user cannot understand which page gives recommendations |
| Medium | Confusing but not blocking | Wording unclear; visual hierarchy causes hesitation |
| Low | Minor polish issue | Small alignment issue; mild spacing inconsistency |

The website fails the usability protocol if any critical issue appears during testing.

## Testing Rules

During each test:

- Do not explain the website before the tester starts.
- Give the tester one task at a time.
- Let the tester think aloud if possible.
- Do not help unless the tester is stuck for more than 2 minutes.
- Record whether the tester completed the task:
  - without help;
  - with help;
  - failed;
  - blocked by bug.
- Record confusion points and page-specific comments.

## Tester Recording Template

Use one copy of this table per tester.

| Field | Response |
|---|---|
| Tester ID | T01 / T02 / T03 / T04 / T05 |
| Date |  |
| Browser | Chrome / Edge / Firefox / Safari |
| Device | Laptop / desktop / tablet |
| Gamer familiarity | Low / medium / high |
| Project familiarity | Low / medium / high |

## Core Task Sheet

### Task 1: Home Page Navigation

Task prompt:

```text
Start on the Home page. Tell me what you think this website does, then choose where you would go if you wanted game recommendations.
```

Expected behavior:

- Tester understands that the website helps users discover games.
- Tester identifies `Recommend Me_` as the page for recommendations.
- Tester can reach the recommendation page from the Home page.

Pass criteria:

```text
Pass if tester reaches Recommend Me without help within 60 seconds.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

### Task 2: Explore Games

Task prompt:

```text
Use Explore Games to browse the catalog and find a game that looks interesting.
```

Expected behavior:

- Tester reaches `/explore`.
- Tester understands that this page is for browsing the catalog.
- Tester can use at least one filter, search, pagination, or game-card interaction.
- Tester can open or inspect a game detail if available.

Pass criteria:

```text
Pass if tester finds at least one game and can explain why it looks interesting within 2 minutes.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

### Task 3: Hidden Gems

Task prompt:

```text
Find the Hidden Gems page and explain what makes these games different from ordinary catalog results.
```

Expected behavior:

- Tester reaches `/hidden-gems`.
- Tester understands that hidden gems are project-defined.
- Tester recognizes that hidden gems balance quality and lower visibility.
- Tester can inspect at least one hidden-gem game.

Pass criteria:

```text
Pass if tester can identify that hidden gems are high-quality, lower-visibility candidates within 2 minutes.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

### Task 4: Recommend Me

Task prompt:

```text
Use Recommend Me to get a ranked game recommendation based on your preferences.
```

Expected behavior:

- Tester reaches `/recommendations`.
- Tester understands the structured questions.
- Tester completes the recommendation flow.
- Tester receives ranked results.
- Tester understands at least one explanation or score reason.

Pass criteria:

```text
Pass if tester completes the recommendation flow and receives results within 3 minutes without help.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

### Task 5: Ask the Guide

Task prompt:

```text
Use Ask the Guide to understand what the project does or how the recommendation system works.
```

Expected behavior:

- Tester reaches `/guide`.
- Tester understands that the Guide explains the project and methodology.
- Tester understands that actual ranked recommendations belong in `Recommend Me_`.
- Tester can use `/help` or ask a supported project question.

Pass criteria:

```text
Pass if tester receives a relevant project explanation and can state that Recommend Me is the main recommendation page.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

### Task 6: Insights

Task prompt:

```text
Use the Insights page to find one meaningful pattern from the dataset.
```

Expected behavior:

- Tester reaches `/insights`.
- Tester can identify at least one chart, table, or finding.
- Tester can explain the finding in plain language.

Pass criteria:

```text
Pass if tester identifies one dataset insight and explains it without help within 2 minutes.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

### Task 7: Methodology

Task prompt:

```text
Use the Methodology page to find how the project defines hidden gems or recommendations.
```

Expected behavior:

- Tester reaches `/methodology`.
- Tester can locate the explanation of data, methodology, or hidden-gem/recommendation logic.
- Tester understands that project outputs are based on a curated IGDB sample, not the full game market.

Pass criteria:

```text
Pass if tester can find and summarize one methodology rule within 2 minutes.
```

Record:

| Result | Notes |
|---|---|
| Pass / Helped / Failed / Blocked |  |

---

## Post-Test Questions

Ask each tester these questions after all tasks are complete.

| Question | Response |
|---|---|
| What did you think the website was for? |  |
| Which page felt most useful? |  |
| Which page was most confusing? |  |
| Could you tell where to go for recommendations? Yes / No |  |
| Could you tell where to go for hidden gems? Yes / No |  |
| Did any wording feel unclear? |  |
| Did anything feel broken or unfinished? |  |
| Overall usability rating from 1 to 5 |  |

## Final Summary Template

Complete this table after all testers finish.

| Metric | Result |
|---|---:|
| Total testers |  |
| Home task pass rate |  |
| Explore task pass rate |  |
| Hidden Gems task pass rate |  |
| Recommend Me task pass rate |  |
| Ask the Guide task pass rate |  |
| Insights task pass rate |  |
| Methodology task pass rate |  |
| Critical blockers found |  |
| High-severity issues found |  |
| Medium-severity issues found |  |
| Low-severity issues found |  |
| Overall usability pass? | Yes / No |

## Overall Pass Formula

Use this formula:

```text
Page task pass rate = testers who completed task without help / total testers
```

Overall website usability passes if:

```text
Every core page has at least an 80% task pass rate
AND
0 critical blockers are found
AND
at least 80% of testers correctly identify Recommend Me as the recommendation page
AND
at least 80% of testers correctly explain Hidden Gems as high-quality, lower-visibility candidates
```

## Professor-Facing Summary Sentence

Use this after the test is completed:

```text
Usability testing was evaluated with a five-user task protocol across Home, Explore, Hidden Gems, Recommend Me, Ask the Guide, Insights, and Methodology; each page required at least an 80% unaided completion rate and zero critical blockers to pass.
```

## Current Status

```text
Protocol created.
Testing not yet executed.
Results pending.
```
