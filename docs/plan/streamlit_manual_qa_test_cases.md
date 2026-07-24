# Streamlit MVP Manual QA Test Cases

This checklist is for manually testing the current Streamlit MVP before additional UI polish, similarity integration, or RAG integration.

Run the app before starting:

```text
cd apps/streamlit
streamlit run streamlit_app.py
```

If app-ready data is missing, rebuild it:

```text
python src/pipeline/build_app_catalog.py
```

## Test Environment

Record this before testing:

```text
Tester:
Date:
Branch:
Python environment:
Streamlit version:
Browser:
Notes:
```

Expected current app status:

```text
Home:                 Implemented
Explore Games:        Implemented
Hidden Gems:          Implemented
Recommendations:      MVP implemented
Chatbot:              Placeholder / RAG integration pending
Insights:             MVP implemented
Predictive/Similarity: Placeholder / similarity integration pending
Methodology:          Implemented
```

Core trust rules to verify throughout:

- Missing PopScore is not shown as low visibility.
- `total_rating_count` is described as rating evidence/activity.
- Hidden-gem candidates are described as within-sample candidates, not full-market claims.
- Recommendation explanations match actual filters and score components.
- The app does not claim unsupported metadata.

---

# 1. Home Page Tests

## TC-HOME-001: Main app loads

Steps:

1. Run `cd apps/streamlit`, then run `streamlit run streamlit_app.py`.
2. Open the app in the browser.
3. Verify the landing page loads.

Expected result:

- Page title appears.
- Metric cards appear.
- Caveat notices appear.
- Featured hidden-gem cards appear.
- No blank page.
- No Python traceback appears in the app.

Result:

```text
Pass / Fail:
Notes:
```

## TC-HOME-002: Sidebar Home page loads

Steps:

1. Click `Home` from the Streamlit sidebar page navigation.
2. Verify the page renders.

Expected result:

- Home page content appears.
- Metric cards appear.
- Quick action links appear.
- Featured hidden-gem cards appear.
- Page is not blank.

Result:

```text
Pass / Fail:
Notes:
```

## TC-HOME-003: Quick action links work

Steps:

1. On Home, click each quick action link:
   - Explore games;
   - Find hidden gems;
   - Get recommendations;
   - Ask chatbot.

Expected result:

- Each link opens the correct page.
- No page opens blank.
- No traceback appears.

Result:

```text
Pass / Fail:
Notes:
```

---

# 2. Explore Games Tests

## TC-EXPLORE-001: Basic catalog load

Steps:

1. Open `Explore Games`.
2. Do not apply filters.

Expected result:

- Matching game count appears.
- Game cards appear.
- Each card has title, release year, rating/evidence fields, summary, genres, and platforms.

Result:

```text
Pass / Fail:
Notes:
```

## TC-EXPLORE-002: Search works

Steps:

1. In search, type:

```text
Baldur
```

Expected result:

- Matching results include relevant Baldur's Gate entries if present.
- Result count changes.
- No duplicate game cards appear.

Result:

```text
Pass / Fail:
Notes:
```

## TC-EXPLORE-003: Platform filter works

Steps:

1. Select platform:

```text
PC (Microsoft Windows)
```

Expected result:

- All displayed cards include `PC (Microsoft Windows)` in platforms.
- No games unavailable on PC are shown.

Result:

```text
Pass / Fail:
Notes:
```

## TC-EXPLORE-004: Genre filter works

Steps:

1. Select genre:

```text
Role-playing (RPG)
```

Expected result:

- Displayed cards include `Role-playing (RPG)` in genres.
- Multi-genre games are handled correctly.

Result:

```text
Pass / Fail:
Notes:
```

## TC-EXPLORE-005: Combined platform, genre, and rating filters

Steps:

1. Select platform:

```text
PC (Microsoft Windows)
```

2. Select genre:

```text
Role-playing (RPG)
```

3. Set minimum total rating:

```text
80
```

4. Sort by:

```text
Highest rating
```

Expected result:

- All shown games satisfy the selected platform.
- All shown games satisfy the selected genre.
- All shown games with ratings have `total_rating >= 80`.
- Sort order is logical.

Result:

```text
Pass / Fail:
Notes:
```

## TC-EXPLORE-006: Hidden-gem-only filter

Steps:

1. Turn on `Hidden-gem candidates only`.
2. Keep or add platform/genre filters.

Expected result:

- Only hidden-gem candidate cards appear.
- Cards show hidden-gem candidate label.
- Empty states are understandable if no games match.

Result:

```text
Pass / Fail:
Notes:
```

## TC-EXPLORE-007: Missing data is shown honestly

Steps:

1. Browse several cards.
2. Look for games with missing ratings or missing visibility.

Expected result:

- Unrated games are not labeled as low-rated.
- Missing visibility appears as unknown, not low.
- `total_rating_count` appears as rating evidence.

Result:

```text
Pass / Fail:
Notes:
```

---

# 3. Hidden Gems Tests

## TC-GEMS-001: Balanced hidden gems load

Steps:

1. Open `Hidden Gems`.
2. Select sensitivity:

```text
Balanced
```

Expected result:

- Candidate count appears.
- Candidate cards appear.
- Rule explanation appears.
- Caveat is visible.

Result:

```text
Pass / Fail:
Notes:
```

## TC-GEMS-002: Sensitivity options change results

Steps:

1. Record candidate count for `Balanced`.
2. Switch to `Conservative`.
3. Record candidate count.
4. Switch to `Broad`.
5. Record candidate count.

Expected result:

- Conservative should generally return fewer or equal candidates than Balanced.
- Broad should generally return more or equal candidates than Balanced.
- Labels make clear that Conservative and Broad are exploratory views.

Result:

```text
Balanced count:
Conservative count:
Broad count:
Pass / Fail:
Notes:
```

## TC-GEMS-003: Platform filter works

Steps:

1. Select platform:

```text
PC (Microsoft Windows)
```

Expected result:

- All displayed hidden-gem candidates include PC in platforms.

Result:

```text
Pass / Fail:
Notes:
```

## TC-GEMS-004: Genre filter works

Steps:

1. Select genre:

```text
Role-playing (RPG)
```

Expected result:

- All displayed hidden-gem candidates include RPG in genres.

Result:

```text
Pass / Fail:
Notes:
```

## TC-GEMS-005: Candidate explanation quality

Steps:

1. Review at least five hidden-gem cards.
2. Read the explanation text.

Expected result:

- Explanation includes high rating.
- Explanation includes rating evidence.
- Explanation references low within-year visibility.
- Explanation does not claim the game is overlooked in the full market.

Result:

```text
Pass / Fail:
Notes:
```

---

# 4. Recommendations Tests

## TC-REC-001: Basic recommendations generate

Steps:

1. Open `Recommendations`.
2. Select platform:

```text
PC (Microsoft Windows)
```

3. Click `Generate recommendations`.

Expected result:

- Recommendation cards appear.
- All recommendations include PC as a platform.
- Each recommendation includes an explanation.

Result:

```text
Pass / Fail:
Notes:
```

## TC-REC-002: RPG fantasy recommendation scenario

Steps:

1. Select platform:

```text
PC (Microsoft Windows)
```

2. Select genre:

```text
Role-playing (RPG)
```

3. Select theme:

```text
Fantasy
```

4. Select quality level:

```text
Highly rated (80+)
```

5. Generate recommendations.

Expected result:

- All recommendations are available on PC.
- Results prioritize RPG/Fantasy matches.
- Results satisfy the quality level where rating exists.
- Explanations mention the selected preference matches.

Result:

```text
Pass / Fail:
Notes:
```

## TC-REC-003: Hidden-gem boost changes ranking

Steps:

1. Use the same inputs as TC-REC-002.
2. Generate recommendations with hidden-gem boost off.
3. Generate recommendations with hidden-gem boost on.
4. Compare result order.

Expected result:

- Hidden-gem boost changes ranking when hidden-gem candidates are available.
- Hidden-gem boost does not override the required platform gate.
- Explanations identify hidden-gem candidates where applicable.

Result:

```text
Pass / Fail:
Notes:
```

## TC-REC-004: No-match behavior

Steps:

1. Choose restrictive filters that are unlikely to match.
2. Generate recommendations.

Expected result:

- App shows a helpful empty state.
- App does not crash.
- App suggests broadening filters.

Result:

```text
Pass / Fail:
Notes:
```

---

# 5. Chatbot Tests

## TC-CHAT-001: Chatbot placeholder loads

Steps:

1. Open `Chatbot`.

Expected result:

- Page loads.
- RAG artifact status appears.
- Expected teammate artifact list appears.
- No crash occurs even if RAG artifacts are missing.

Result:

```text
Pass / Fail:
Notes:
```

## TC-CHAT-002: Placeholder query response

Steps:

1. Use the default example prompt.
2. Click `Ask`.

Expected result:

- App returns a safe placeholder response.
- App states that RAG retrieval is not integrated yet if artifacts are missing.
- App does not hallucinate recommendations.

Result:

```text
Pass / Fail:
Notes:
```

---

# 6. Insights Tests

## TC-INSIGHTS-001: Insights page loads

Steps:

1. Open `Insights`.

Expected result:

- Metric cards appear.
- Tabs appear.
- No traceback occurs.

Result:

```text
Pass / Fail:
Notes:
```

## TC-INSIGHTS-002: Catalog overview charts render

Steps:

1. Open the `Catalog Overview` tab.

Expected result:

- Top genre chart renders.
- Top platform chart renders.
- Charts are readable.

Result:

```text
Pass / Fail:
Notes:
```

## TC-INSIGHTS-003: Reception and visibility tables render

Steps:

1. Open the `Reception and Visibility` tab.

Expected result:

- Quality versus PopScore diagnostic table appears.
- User versus critic agreement table appears.
- The page does not overclaim causality.

Result:

```text
Pass / Fail:
Notes:
```

## TC-INSIGHTS-004: Coverage and limits are visible

Steps:

1. Open the `Coverage and Limits` tab.

Expected result:

- Methodology metrics are visible.
- Missing optional metadata is explained as unknown.
- Caveats are clear.

Result:

```text
Pass / Fail:
Notes:
```

---

# 7. Predictive / Similarity Scoring Tests

## TC-PRED-001: Similarity placeholder loads

Steps:

1. Open `Predictive / Similarity Scoring`.

Expected result:

- Page loads.
- Predictive/similarity artifact status appears.
- Expected teammate artifact list appears.
- Missing artifacts do not crash the page.

Result:

```text
Pass / Fail:
Notes:
```

---

# 8. Methodology Tests

## TC-METH-001: Methodology page loads

Steps:

1. Open `Methodology`.

Expected result:

- Page loads.
- Sample caveat appears.
- Signal caveat appears.
- Hidden-gem definition appears.
- Artifact audit appears.
- Implementation boundaries appear.

Result:

```text
Pass / Fail:
Notes:
```

## TC-METH-002: Artifact audit is accurate

Steps:

1. Review the artifact audit JSON.

Expected result:

- Database status is true.
- App catalog status is true.
- App hidden-gem status is true.
- Predictive/RAG statuses may be false or partial until teammate integration.

Result:

```text
Pass / Fail:
Notes:
```

---

# 9. Terminal and Browser Error Log

Record any terminal warnings/errors here:

```text
Warning/error:
Page:
Steps that caused it:
Screenshot available? Yes / No
```

Record any browser-visible errors here:

```text
Error:
Page:
Steps that caused it:
Screenshot available? Yes / No
```

---

# 10. Final QA Summary

```text
Total tests run:
Passed:
Failed:
Blocked:

Highest-priority fixes:
1.
2.
3.

UX polish notes:
1.
2.
3.

Ready for next development pass? Yes / No
```

