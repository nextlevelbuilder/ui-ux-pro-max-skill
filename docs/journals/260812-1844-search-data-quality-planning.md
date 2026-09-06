# Planning Stopped Us from Making Search Worse

**Date**: 2026-08-12 18:44
**Severity**: High
**Component**: Search, datasets, agent guidance, UI taxonomy
**Status**: Resolved

## What Happened

We completed a nine-phase overhaul plan, not an implementation. Data expansion was gated behind a human-judged relevance corpus because the existing 36 unit tests, 12 domain smokes, and 22 stack smokes mostly prove that output is non-empty—not relevant. Adding rows before measuring P@1, MRR@3, nDCG@3, abstention, and typo recovery would amplify noise and erase our baseline.

## The Brutal Truth

The repository looked healthier than it was. Passing tests concealed a router where 37 of 122 non-product keywords return zero hits in their own domain, while normalization can turn `navigation` into `navigationigation`. Shipping more data into that system would have been busywork dressed up as progress. It is frustrating that basic relevance remained unmeasured while catalog counts made the product look mature.

## Technical Details

BM25 stays because the offline, stdlib-only CLI and public command contract are deliberate constraints. We rejected embeddings, a vector database, and a graph database without evidence that lexical retrieval is the bottleneck. The planned repair is normalization, field and phrase boosts, and score calibration; hybrid retrieval is reconsidered only if measured paraphrase recall remains the dominant failure.

Agent query guidance is first-class because bad instructions corrupt retrieval before ranking starts. “Always use design-system” is wrong for fixes, reviews, and stack questions, and the advertised AI example currently selects a Marketplace/Directory landing pattern. The plan therefore requires intent separation, category/result validation, and low-confidence abstention.

UI research also rejected trend dumping. Consolidate Bento, Aurora/gradient, and Swiss families; preserve mobile Neumorphism/Claymorphism variants; add Fluent 2, Shopify Polaris, and Clean Science only with official evidence. Holographic aliases to HUD, High Imagery remains a treatment, and Spectrum 2 plus Canvas/Workspace stay gated.

## What We Tried

- Compared runtime behavior, 35 CSVs, agent guidance, and official UI-system sources.
- Red-teamed all nine phases, then propagated three blockers and seven important corrections.
- Rejected immediate dataset expansion and architecture replacement because neither had relevance evidence.

## Root Cause Analysis

We optimized structural validity before relevance and let cross-file contracts drift: 192 products exist, but only 161 reasoning rows do, with unsafe substring fallback masking gaps.

## Lessons Learned

Measure before expanding. Treat prompts as production interfaces. A generated catalog is not correct merely because it parses.

## Next Steps

Phase 1 owner must obtain human judgments and freeze executable thresholds before ranking changes. Phase 2 owns BM25/router repair; Phases 3–5 own schema, agent contract, and taxonomy. Red-team corrections require exact reasoning for all 192 products, explicit Phase 7/8 runtime ownership, a closed `Decision_Rules` grammar, and one aggregate CI gate.

The plan artifacts are local and untracked. No implementation occurred, and no source or CSV file was changed.
