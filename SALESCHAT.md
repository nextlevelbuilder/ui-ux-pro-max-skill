# The saleschat branch

This branch is the copy of ui-ux-pro-max that SalesChat's plugin marketplace installs. It is upstream commit `6ae86f6` (`nextlevelbuilder/ui-ux-pro-max-skill`) with these removed:

- the `banner-design`, `brand`, `design`, `design-system`, `slides` and `ui-styling` skills: some read `~/.claude/.env`, call image APIs or run `npx` and `node`, and the design ones compete with SalesChat's design constitution;
- the `stack/` example project, whose `.mcp.json` and settings would sit in every laptop's plugin cache;
- the `gallery/data/styles.csv` symlink.

Only the `ui-ux-pro-max` skill remains, unchanged. It searches the bundled data with the Python standard library and uses no network.

To take a newer upstream version, merge upstream into this branch, remove the same paths again, and have the marketplace pin the new commit after review.
