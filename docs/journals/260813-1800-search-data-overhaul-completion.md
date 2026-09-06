---
date: 2026-08-13
session: search-data-overhaul-completion
severity: high
component: search-relevance-data-catalogs-and-release-gates
status: resolved-with-carryover
---

# Search and Data Overhaul Finished, but Green Was Not Enough

## Context

The nine-phase overhaul audited BM25 routing, query interpretation, agent guidance, CSV quality, current UI styles, framework/native stack freshness, generated catalogs, provenance, and release gates. The local plan is complete at 9/9 phases and 148/148 items. `plans/` is ignored by Git as intended; none of those local artifacts belongs in a release.

## What Happened

The final evidence is concrete: 148 Python tests passed; smoke coverage passed 12/12 domains and 22/22 stacks; Playwright passed 8/8; and the relevance suite passed its approved provisional regression gate. The canonical catalogs now contain 1,934 approved Google Fonts plus eight explicit `needs-review` exclusions, and 1,512 upstream Phosphor icons supporting 105 curated icon rows. Google Fonts provenance is pinned to repository revision `038b637da7b3fd956a4ed93ffc607c3d5e4ce172`.

The reviewer still found four release-grade defects after broad gates were green. The release workflow ran only a subset of Playwright tests. Font provenance omitted the exact source revision. Refresh and validation disagreed about allowed exclusion evidence URLs. Generated mirrors could remain stale after canonical-source edits. We fixed all four: full Playwright now gates release, the revision is required and validated, both paths share the same narrow source policy, and mirror synchronization/checks are part of the final verification.

## Reflection

The brutal truth is that we almost called this complete while the release pipeline could certify less than the test suite, and while a future font refresh could not be reproduced from an exact upstream tree. That is not polish; it is a broken evidence chain. It was exhausting to watch “all green” repeatedly collapse under adversarial review, especially after nine phases of careful work. The relief is earned now because the failures became executable contracts instead of comments developers must remember.

## Decisions

- Kept the relevance threshold as a provisional regression gate. We rejected silently promoting it to a final quality target because the held-out judgments still need a second human review.
- Chose fail-closed provenance and evidence policies over permissive refreshes. Unknown revisions, unsupported exclusion URLs, interrupted publication, and stale mirrors must stop validation.
- Kept 8 unresolved font families visible as `needs-review` exclusions instead of inventing license certainty.
- Did not commit or push. This session prepared and verified the work only.

## Next

- Project owner: complete a second human relevance judgment review before promoting final thresholds; preserve the current baseline until then.
- Maintainers: inspect weekly refresh artifacts before accepting catalog changes; never auto-merge upstream data.
- Release owner: retain full Playwright, provenance, mirror, catalog-summary, actionlint, and diff gates on every release.

Unresolved question: when will the independent relevance judgment review be scheduled?
