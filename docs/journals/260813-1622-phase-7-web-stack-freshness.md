---
date: 2026-08-13
session: phase-7-web-stack-freshness
severity: high
component: web-stack-search-guidance
status: resolved
---

# Phase 7 Nearly Shipped Fresh Labels on Stale Framework Advice

## What Happened

Phase 7 refreshed 589 rows across React, Next.js, Vue, Svelte, Astro, Angular, Tailwind, shadcn, Nuxt, and Nuxt UI. We now have 573 active rows and 16 explicitly deprecated legacy rows, each with applicability, status, verification date, and official-source coverage for all 179 Critical/High rows. Default search isolates current guidance; explicit supported-old-major queries return labeled legacy rows; unsupported old majors abstain.

## The Brutal Truth

We began with an Astro 7.2 assumption that sounded current and was simply false. Official release evidence said 7.1.6. Worse, the first refresh still carried removed contracts: `output: 'hybrid'`, `<ViewTransitions />`, `@astrojs/tailwind`, and the old prefetch integration. Calling that “freshness” would have been embarrassing. The reviewer then found the legacy parser missed ordinary forms such as `svelte@4` and `Next.js (v15)`, letting explicit legacy intent fall into current guidance. Seeing green gates before those defects surfaced was maddening; the relief came only when each failure became a regression test.

## Technical Details

The corrected Astro rows use `ClientRouter`, on-demand rendering, Tailwind 4 through Vite, and built-in prefetch. Shared stack selection now recognizes plain majors, `@major`, and `(vMajor)`, preserves current-major migration queries such as `Next.js 16 migration`, and returns zero rows when an older generation has no curated corpus.

Final evidence: `npm --prefix cli run verify:data` passed 124/124 Python tests; focused web freshness passed 12/12; smoke coverage passed 12/12 domains and 22/22 stacks. Relevance held at P@1 `0.8026315789`, MRR@3 `0.8618421053`, nDCG@3 `0.8561593731`, abstention `0.9803921569`, and coherence `1.0`. Asset sync, CLI typecheck, CLI build, `git diff --check`, and final reviewer all reported PASS.

## What We Tried

- Rejected blanket version-string replacement because most rows needed semantic verification, not cosmetic edits.
- Retained curated Svelte, Tailwind 3, Next.js 15, and Nuxt 3 guidance as deprecated instead of deleting migration value.
- Rejected fabricating old-major coverage; abstention is safer than mixing generations.

## Root Cause Analysis

We treated a planned version number and passing broad tests as evidence. They were not. Research had to verify the release, while adversarial review had to exercise syntax variants and removed APIs that the initial tests omitted.

## Lessons Learned

Version freshness means executable API validity plus retrieval isolation. Every supported query spelling needs a test, and every removed symbol needs a denylist assertion.

## Next Steps

- Main agent owns Phase 8 native/desktop/3D freshness, then Phase 9 provenance, final judgment review, threshold promotion, and release gates when the user resumes.
- Pause now: the user explicitly mandated a Phase 7 checkpoint.
- Keep `plans/` local and defer any `.gitignore` decision until all phases finish.

Unresolved questions: none for Phase 7; final relevance targets remain Phase 9 work.
