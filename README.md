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

## Verify

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Tests cover overlapping genres, rating weighting, release-year semantics, inclusive floors, ties, source validation, independent CSV reconciliation, and Streamlit widget reruns.

## Deploy for the assignment

1. Push this project to a public GitHub repository, including `movie_ratings.csv`, `app.py`, `analysis.py`, `requirements.txt`, and `.streamlit/config.toml`. Do not commit `.venv` or secrets.
2. In Streamlit Community Cloud, create an app from that repository, choose `main`, and use `app.py` as the entrypoint. Select a Python version compatible with the pinned dependencies (Python 3.12 or newer).
3. Open the deployed URL in a private/incognito window and exercise both controls before submitting.

Deployment has not yet been performed. See the [official deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

`BUILD_LOG.md` preserves prompt excerpts and the decisions made during this session. The dashboard is an initial working visual treatment for further design discussion.
