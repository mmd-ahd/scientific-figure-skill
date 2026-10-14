# Contributing

Thanks for helping make scientific figures better! Issues and pull requests are welcome, especially:
- **journal-spec corrections**: please link the publisher page and give the date you checked it;
- **new panel recipes** for comp-neuro / NeuroAI data types;
- **palettes**, with a source, and checked with `sp.check.palette_report`;
- bug reports with a minimal script and the PNG it produced.

## Development setup
```bash
git clone https://github.com/mmd-ahd/scientific-figure-skill
cd scientific-figure-skill
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"            # add ,all for every optional dependency
python scripts/install_fonts.py    # optional: Inter, for figures that match the examples
pytest && ruff check .
python scripts/demo_figures.py /tmp/sciplot-demo    # every lint should say OK; then look at the PNGs
```

## Guidelines
- **Pure matplotlib core.** `sciplot` must import and pass the tests with only numpy + matplotlib. Optional
  packages are imported lazily inside functions and need a fallback.
- **Recipes** take an `ax`, draw into it, take their colours from arguments or the active style (never hard-coded
  rcParams), and return the main artist. Add a test in `tests/test_recipes.py`, a panel in
  `scripts/recipe_gallery.py`, a row in `SKILL.md`'s cheat-sheet and an entry in `docs/recipes.md`.
- **Venues** live in `scripts/sciplot/layout.py::VENUES`. Cite the source in a comment and in
  `references/journal-specs.md`.
- **Palettes**: after editing `palettes.py`, regenerate the measurements, galleries and catalogue with
  `python scripts/palette_gallery.py`.
- **Styles**: after changing `styles.py`, regenerate the `.mplstyle` files (a test checks they are up to date):
  `python -c "import sys; sys.path.insert(0, 'scripts'); import sciplot.styles as s; s.write_mplstyles()"`.
- **API docs**: after changing signatures or docstrings, run `python scripts/tools/gen_api_docs.py`.
- Keep `SKILL.md` short. It is loaded into Claude's context, so put long explanations in `references/` or `docs/`.
  The frontmatter `description` must stay under 1024 characters.

## Releasing
Bump `version` in `pyproject.toml` and `scripts/sciplot/__init__.py`, update `CHANGELOG.md`, then tag `vX.Y.Z`.
The release workflow attaches `scientific-figure.zip` (the skill folder) to the GitHub release.
