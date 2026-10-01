"""Run with: python -m streamlit run app.py"""

from pathlib import Path
from textwrap import wrap

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import (
    genre_breakdown, genre_satisfaction, load_ratings,
    movie_summary, ratings_by_release_year, top_movies,
)

ROOT = Path(__file__).resolve().parent
INK = "#252722"
ACCENT = "#9C402A"
MUTED = "#77776C"
GRID = "#E1DCCE"

st.set_page_config(page_title="The Rating Room · MovieLens", page_icon="🎞️", layout="wide")
st.markdown("""
<style>
.block-container { max-width: 1200px; padding-top: 3rem; padding-bottom: 4rem; }
h1 { font-family: Georgia, 'Times New Roman', serif !important; font-size: clamp(2.5rem, 5vw, 4rem) !important;
     font-weight: 400 !important; letter-spacing: -0.045em; }
h2 { font-family: Georgia, 'Times New Roman', serif !important; font-weight: 400 !important; }
[data-testid="stMetricValue"] { font-family: Georgia, 'Times New Roman', serif; }
[data-testid="stCaptionContainer"] { color: #625F55; opacity: 1 !important; }
[data-testid="stTable"] td { white-space: normal; overflow-wrap: anywhere; }
@media (max-width: 640px) { .block-container { padding: 1.5rem 1rem 3rem; } }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data(path: str, modified: int) -> pd.DataFrame:
    # The modification time invalidates the cache when the source CSV changes.
    return load_ratings(path)


def style_chart(fig: go.Figure, height: int, x_title: str) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color=INK, size=13),
        margin=dict(l=0, r=24, t=16, b=48), showlegend=False,
        xaxis_title=x_title, yaxis_title=None,
        hoverlabel=dict(bgcolor="#FAF7F0", font_color=INK),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, fixedrange=True)
    fig.update_yaxes(showgrid=False, fixedrange=True, automargin=True)
    return fig


def draw(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, width="stretch", theme=None, key=key,
                    config={"displayModeBar": False, "scrollZoom": False})


def table(frame: pd.DataFrame) -> None:
    st.dataframe(frame, hide_index=True, width="stretch")


def ranking_table(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame[["title", "mean_rating", "ratings"]].copy()
    result.insert(0, "Rank", range(1, len(result) + 1))
    result["mean_rating"] = result.mean_rating.round(3)
    return result.rename(columns={"title": "Movie", "mean_rating": "Mean / 5", "ratings": "Ratings"})


try:
    source = ROOT / "movie_ratings.csv"
    ratings = get_data(str(source), source.stat().st_mtime_ns)
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load movie_ratings.csv: {error}")
    st.info("Check that the original CSV is beside app.py and contains the required columns.")
    st.stop()

breakdown = genre_breakdown(ratings)
satisfaction = genre_satisfaction(ratings)
yearly = ratings_by_release_year(ratings)
movies = movie_summary(ratings)

st.caption("MOVIELENS  /  A STUDY IN AUDIENCE TASTE")
st.title("The Rating Room")
st.write("What we watch. What we love. And which films stand up to a larger audience.")
metrics = st.columns(3)
metrics[0].metric("Rated movies", f"{len(movies):,}")
metrics[1].metric("Audience ratings", f"{len(ratings):,}")
metrics[2].metric("Mean rating", f"{ratings.rating.mean():.2f} / 5")
st.divider()

left, right = st.columns(2, gap="large")
with left:
    st.header("01 / The genre mix")
    st.write("Which genres appear most among rated movies?")
    measure = st.radio("Show genre distribution as", ["Movie count", "Share of movies"],
                       horizontal=True, key="genre_measure")
    st.caption("Each movie counts once in every genre it carries. Shares use all rated movies "
               "as the denominator and can total more than 100%.")
    field = "movies" if measure == "Movie count" else "percentage"
    labels = [f"{n:,}" for n in breakdown.movies] if field == "movies" else [
        f"{n:.1f}%" for n in breakdown.percentage
    ]
    fig = go.Figure(go.Bar(
        x=breakdown[field].tolist(), y=breakdown.genre.tolist(), orientation="h",
        marker_color=[MUTED if g == "unknown" else ACCENT for g in breakdown.genre],
        text=labels, textposition="outside", cliponaxis=False,
        customdata=breakdown[["movies", "percentage"]].values,
        hovertemplate="%{y}<br>%{customdata[0]:,.0f} movies<br>%{customdata[1]:.1f}% of rated movies<extra></extra>",
    ))
    style_chart(fig, 650, "Distinct movies" if field == "movies" else "Share of all rated movies (%)")
    fig.update_xaxes(range=[0, float(breakdown[field].max()) * 1.22])
    fig.update_yaxes(autorange="reversed")
    draw(fig, "genre_distribution")
    with st.expander("View genre counts"):
        table(breakdown.rename(columns={"genre": "Genre", "movies": "Movies", "percentage": "Share (%)"}).round(2))

with right:
    st.header("02 / The audience verdict")
    st.write("Which genres receive the highest average ratings?")
    known = satisfaction.loc[satisfaction.genre != "unknown"]
    if not known.empty:
        best, worst = known.iloc[0], known.iloc[-1]
        st.markdown(f"**Highest:** {best.genre} · {best.mean_rating:.2f} / 5  \n"
                    f"**Lowest:** {worst.genre} · {worst.mean_rating:.2f} / 5")
    st.caption("Every rating contributes to each genre attached to its movie. More-rated movies "
               "have more influence. Hover for sample sizes; unknown is not a named genre.")
    fig = go.Figure(go.Bar(
        x=satisfaction.mean_rating.tolist(), y=satisfaction.genre.tolist(), orientation="h",
        marker_color=[MUTED if g == "unknown" else ACCENT for g in satisfaction.genre],
        text=[f"{v:.2f}" for v in satisfaction.mean_rating], textposition="outside", cliponaxis=False,
        customdata=satisfaction[["ratings", "movies"]].values,
        hovertemplate="%{y}<br>Mean: %{x:.3f} / 5<br>%{customdata[0]:,.0f} ratings"
                      "<br>%{customdata[1]:,.0f} movies<extra></extra>",
    ))
    style_chart(fig, 650, "Mean rating / 5")
    fig.update_xaxes(range=[0, 5], dtick=1)
    fig.update_yaxes(autorange="reversed")
    draw(fig, "genre_ratings")
    with st.expander("View genre averages and sample sizes"):
        table(satisfaction.rename(columns={"genre": "Genre", "mean_rating": "Mean / 5", "ratings": "Ratings", "movies": "Movies"}).round(3))

st.divider()
st.header("03 / Through the release years")
st.write("How do ratings differ across the years movies were released?")
missing_year = int(ratings.year.isna().sum())
st.caption("One point per release year, averaging individual ratings. This is not the year a rating was submitted. "
           f"{missing_year:,} ratings without a release year are excluded only from this chart.")
if yearly.empty:
    st.info("No release years are available in this dataset.")
else:
    # Preserve gaps instead of implying observations for years absent from the data.
    continuous = yearly.set_index("year").reindex(range(int(yearly.year.min()), int(yearly.year.max()) + 1))
    fig = go.Figure(go.Scatter(
        x=continuous.index.tolist(), y=continuous.mean_rating.tolist(), mode="lines+markers",
        line=dict(color=ACCENT, width=2), marker=dict(size=6), connectgaps=False,
        customdata=continuous[["ratings", "movies"]].values,
        hovertemplate="Released %{x}<br>Mean: %{y:.3f} / 5<br>%{customdata[0]:,.0f} ratings"
                      "<br>%{customdata[1]:,.0f} movies<extra></extra>",
    ))
    style_chart(fig, 370, "Movie release year")
    fig.update_xaxes(dtick=10)
    fig.update_yaxes(title="Mean rating / 5", range=[1, 5.1], dtick=1, showgrid=True, gridcolor=GRID)
    draw(fig, "release_year_ratings")
    st.caption("Early release years can have few movies. Sample sizes appear on hover; gaps indicate years with no movies.")
    with st.expander("View annual averages and sample sizes"):
        table(yearly.rename(columns={"year": "Release year", "mean_rating": "Mean / 5", "ratings": "Ratings", "movies": "Movies"}).round(3))

st.divider()
st.header("04 / Five films, a higher bar")
st.write("The best-rated movies with enough audience ratings to qualify.")
floor = st.slider("Minimum ratings per movie", min_value=50, max_value=150, value=50, step=1, key="rating_floor")
top = top_movies(movies, floor)
eligible = int((movies.ratings >= floor).sum())
st.caption(f"{eligible:,} movies qualify at ≥ {floor} ratings. This control affects only the movie ranking. "
           "Ties use rating count, then movie ID; ranking uses unrounded averages.")
if top.empty:
    st.info("No movies meet this minimum. Lower the minimum rating count to see results.")
else:
    # Numeric positions keep distinct movie IDs separate even if titles match.
    fig = go.Figure(go.Bar(
        x=top.mean_rating.tolist(), y=list(range(len(top))), orientation="h", marker_color=ACCENT,
        text=[f"{r.mean_rating:.3f} · {r.ratings:,} ratings" for r in top.itertuples()],
        textposition="inside", insidetextanchor="end", textfont=dict(color="#FFFFFF"),
        customdata=top[["title", "ratings"]].values,
        hovertemplate="%{customdata[0]}<br>Mean: %{x:.3f} / 5<br>%{customdata[1]:,.0f} ratings<extra></extra>",
    ))
    style_chart(fig, 380, "Mean rating / 5")
    fig.update_xaxes(range=[0, 5], dtick=1)
    fig.update_yaxes(autorange="reversed", tickvals=list(range(len(top))),
                     ticktext=[f"{i + 1}. " + "<br>".join(wrap(t, 25)) for i, t in enumerate(top.title)])
    draw(fig, "top_five_movies")
    with st.expander("View current top five"):
        table(ranking_table(top))

st.markdown("**What changes from 50 to 150?**")
top50, top150 = top_movies(movies, 50), top_movies(movies, 150)
departed = top50.loc[~top50.movie_id.isin(top150.movie_id), "title"].tolist()
arrived = top150.loc[~top150.movie_id.isin(top50.movie_id), "title"].tolist()
if departed or arrived:
    st.write("Leaves the top five: " + ("; ".join(departed) or "None") + ".")
    st.write("Enters the top five: " + ("; ".join(arrived) or "None") + ".")
else:
    st.write("The same movies remain in the top five at both floors.")
col50, col150 = st.columns(2, gap="large")
with col50:
    st.caption("AT LEAST 50 RATINGS")
    st.table(ranking_table(top50), hide_index=True)
with col150:
    st.caption("AT LEAST 150 RATINGS")
    st.table(ranking_table(top150), hide_index=True)
st.divider()
st.caption("Source: supplied MovieLens movie_ratings.csv · Ratings on a 1–5 scale · Unknown genre labels are retained.")
