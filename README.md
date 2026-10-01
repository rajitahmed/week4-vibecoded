# The Rating Room

A Streamlit dashboard for the four questions in `Week4_Vibe_Coding_Dashboard_Build.md`.

## Run locally (PowerShell)

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m streamlit run app.py
```

Open http://localhost:8501. The app reads `movie_ratings.csv` beside `app.py`, regardless of the terminal's working directory. The implementation was tested with Python 3.14.

## Calculations

- **Genre breakdown:** deduplicate by `movie_id`, split pipe-separated genres, then count a movie once in each genre. Share = genre movie count / all distinct rated movies. Shares overlap and can sum above 100%.
- **Genre satisfaction:** arithmetic mean of individual ratings for movies carrying each genre. Multi-genre ratings contribute once to each genre. Movies with more ratings have more influence.
- **Release years:** arithmetic mean of ratings grouped by movie release `year`. Missing years are excluded only here. Years with no movies create gaps in the line.
- **Top five:** group by movie ID, retain rating count greater than or equal to the floor, then sort by unrounded mean descending, count descending, and movie ID ascending.
- Unknown genres remain visible. Sample sizes appear in chart tooltips and expandable tables. The source CSV is not changed.

The radio control switches counts and shares for genre breakdown. The 50–150 slider affects only the top-five movie ranking. The comparison tables always show the two assignment endpoints.

## Interface

The four existing charts now use the terminal design system in `design.md`: dark square panes, color-coded pane titles, a pinned tmux-style statusline, and 14px monospace text. Fira Mono carries the interface and chart labels; Departure Mono provides the pixel-style display title. Mint marks keyboard focus, while the data uses a separate muted teal.

The scope remains four charts and two data controls: count/share for genre breakdown and a 50–150 minimum-ratings slider for the top five. Full titles, sample sizes, and the fixed 50-versus-150 comparison remain available in expandable tables. The restyle does not change any calculations or source data.

`terminal.css` contains the visual tokens and layout rules. `terminal.js` adds labelled pane regions and adjusts long chart titles to the available width. Both files are loaded by `app.py`.

### Bundled fonts

Fonts are served locally from `static/fonts/` with Streamlit static serving enabled in `.streamlit/config.toml`; visitors do not need to contact a font CDN. Regular and bold Fira Mono include separate box-drawing symbol subsets. Both font families use the SIL Open Font License 1.1, with their license texts included alongside the files:

- [Fira Mono, official Google Fonts repository](https://github.com/google/fonts/tree/main/ofl/firamono) — `static/fonts/FiraMono-OFL.txt`.
- [Departure Mono, official project repository](https://github.com/rektdeckard/departure-mono) — version 1.500, `static/fonts/DepartureMono-OFL.txt`.

Restart Streamlit after changing server settings such as static serving.

## Verify

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Tests cover overlapping genres, rating weighting, release-year semantics, inclusive floors, ties, source validation, independent CSV reconciliation, and Streamlit widget reruns.

## Deploy for the assignment

1. Push this project to a public GitHub repository, including `movie_ratings.csv`, `app.py`, `analysis.py`, `terminal.css`, `terminal.js`, `requirements.txt`, `.streamlit/config.toml`, and the complete `static/fonts/` directory with its license files. Do not commit `.venv` or secrets.
2. In Streamlit Community Cloud, create an app from that repository, choose `main`, and use `app.py` as the entrypoint. Select a Python version compatible with the pinned dependencies (Python 3.12 or newer).
3. Open the deployed URL in a private/incognito window and exercise both controls before submitting.

Deployment has not yet been performed. See the [official deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

`BUILD_LOG.md` preserves prompt excerpts and the decisions made during this session. The current visual treatment follows the terminal restyle requested in `design.md`.
