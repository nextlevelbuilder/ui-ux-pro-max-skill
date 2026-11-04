<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: 73c0e76468b6 -->
# Page overrides

Each `pages/<page>.md` holds **deviations only** for one screen. Create one with:

    python3 scripts/vd.py page --dir design-system/pet-diary-redesign --name <page> --reason "why this screen differs"

Rules enforced by `vd.py validate`:

1. Every row in `## Overrides` needs a non-empty reason.
2. A page restating ≥ 3 MASTER.md values unchanged, or copying ≥ 80 % of its lines, is rejected (`page.copies-master`).
3. `Token / rule` must be a path that exists in `tokens.json` or a component id from the catalog.
4. Pages never remap `semantic.color.*` meanings or `$extensions.vdp.platformUnit`.
5. Rows count against the drift budget written in MASTER.md § Page Override Logic.
6. Page-scoped intentional exceptions need an `Expires` date (or `never`).
