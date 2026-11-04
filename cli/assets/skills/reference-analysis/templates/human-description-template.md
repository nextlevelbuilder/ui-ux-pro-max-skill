# Human Description Template

Send this to the user, verbatim, once per image, when the runtime cannot show you the image (`viewed_by: "human-description"`). Replace `<label>` with the image's label. Do not add questions about style names; facts only. Observations derived from the answer are capped at `high` and cite `"user description, paragraph N"` as evidence.

```
Describe <label> in up to 8 short paragraphs, facts only, no style names:
1. Overall layout top-to-bottom (what bands/regions, approximate % of height each).
2. Background colour(s) and any gradient direction.
3. The 3-5 most used colours and where each appears; the single most vivid colour and what it is used on.
4. Corner shapes of panels, cards, buttons (sharp / slightly rounded / very rounded / full pill); outline present? colour? thick or thin relative to the element?
5. Shading: flat fill / gradient / glossy highlight / drop shadow / hard bottom edge; where.
6. Text: heavy or light, rounded or sharp, with or without outline, ALL CAPS / Title Case / lower; any font name only if you know it from the source files.
7. Components visible: list buttons (count, shapes, colours), HUD elements, popups, menus, icons (filled / outlined / two-tone).
8. Characters or illustrations: proportions, outline, shading; anything that moves (only if the source is a video/gif).
```

## Recording the answer

- One observation per fact, `refs: ["ref-N"]`, `evidence: "user description, paragraph <n>"`, confidence `high` at most (never `observed`: you are relaying someone else's reading).
- Anything the description does not mention is `not-derivable` with `evidence: "n/a — user description does not mention <topic>"`; add the topic to `not_derivable`.
- Font names the user gives from source files are `high` with `evidence: "user statement"`.
- Write "per your description" in the summary, never "I saw".
- If the user cannot describe the image: set `viewed_by: "none"`, give the reference no roles, and state in the summary that the image was not analysed.
