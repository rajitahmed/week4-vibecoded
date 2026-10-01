"""The Rating Room — a terminal-styled MovieLens dashboard."""

from html import escape
from pathlib import Path
import re
from textwrap import shorten

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis import (
    genre_breakdown, genre_satisfaction, load_ratings,
    movie_summary, ratings_by_release_year, top_movies,
)

ROOT = Path(__file__).resolve().parent
CSS = (ROOT / "terminal.css").read_text(encoding="utf-8")
# Plotly cannot resolve CSS variables; read its colors from the same token block.
COLORS = dict(re.findall(r"--([\w-]+):\s*(#[\da-fA-F]{6})", CSS))
FONT = '"Fira Mono", Consolas, monospace'

st.set_page_config(page_title="rating room / MovieLens", page_icon="▤", layout="wide")
st.html(f"<style>{CSS}</style>")


@st.cache_data
def get_data(path: str, modified: int) -> pd.DataFrame:
    # The modification time invalidates the cache when the source CSV changes.
    return load_ratings(path)


def pane_heading(number: str, title: str, question: str) -> None:
    st.html(f'<div class="pane-heading"><h2 class="pane-title" id="pane-title-{number}">'
            f'{number} / {title}</h2></div><p class="pane-query">{question}</p>')


def style_chart(fig: go.Figure, height: int, x_title: str) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["bg"],
        font=dict(family=FONT, color=COLORS["fg"], size=14),
        margin=dict(l=0, r=36, t=10, b=50), showlegend=False, bargap=0.30,
        xaxis_title=x_title, yaxis_title=None,
        hoverlabel=dict(bgcolor=COLORS["raise"], bordercolor=COLORS["dim"],
                        font=dict(family=FONT, color=COLORS["bright"], size=14)),
    )
    fig.update_xaxes(gridcolor=COLORS["line"], zeroline=False, fixedrange=True,
                     tickfont=dict(color=COLORS["dim"], size=14), title_font=dict(size=14))
    fig.update_yaxes(showgrid=False, fixedrange=True, automargin=True, tickfont=dict(size=14))
    return fig


def draw(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, width="stretch", theme=None, key=key,
                    config={"displayModeBar": False, "scrollZoom": False})


def table(frame: pd.DataFrame) -> None:
    st.dataframe(frame, hide_index=True, width="stretch")


def ranking_table(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame[["title", "mean_rating", "ratings"]].copy()
    result.insert(0, "rank", range(1, len(result) + 1))
    result["mean_rating"] = result.mean_rating.map(lambda value: f"{value:.3f}")
    return result.rename(columns={"title": "movie", "mean_rating": "mean / 5", "ratings": "ratings"})


try:
    source = ROOT / "movie_ratings.csv"
    ratings = get_data(str(source), source.stat().st_mtime_ns)
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f"✗ ERR  cannot load movie_ratings.csv: {error}")
    st.info("check that the original CSV is beside app.py and contains the required columns")
    st.stop()

breakdown = genre_breakdown(ratings)
satisfaction = genre_satisfaction(ratings)
yearly = ratings_by_release_year(ratings)
movies = movie_summary(ratings)

st.html(f"""
<header class="terminal-header">
  <div class="session-top"><span class="session-path">~/movielens / rating-room</span>
    <span class="session-detail">movie_ratings.csv <span aria-hidden="true">│</span> <span class="mode">VIEW</span></span></div>
  <div class="session-title"><h1>THE RATING ROOM</h1>
    <p><span class="prompt" aria-hidden="true">&gt; </span>four views into audience taste.</p></div>
  <dl class="dataset-meta"><div><dt>movies:</dt><dd>{len(movies):,}</dd></div>
    <div><dt>ratings:</dt><dd>{len(ratings):,}</dd></div>
    <div><dt>mean:</dt><dd>{ratings.rating.mean():.2f}/5</dd></div>
    <div><dt>source:</dt><dd>MovieLens</dd></div></dl>
</header>
""")

left, right = st.columns(2, gap="small")
with left, st.container(key="pane_genres"):
    pane_heading("01", "genre breakdown", "distribution of genres among rated movies")
    measure = st.radio("display:", ["Movie count", "Share of movies"],
                       format_func=lambda value: "count" if value == "Movie count" else "share %",
                       horizontal=True, key="genre_measure", label_visibility="collapsed")
    st.html('<p class="scope-note">one movie counts once in each genre. shares use all rated movies; '
            'overlapping genres can total above 100%.</p>')
    field = "movies" if measure == "Movie count" else "percentage"
    labels = [f"{n:,}" for n in breakdown.movies] if field == "movies" else [f"{n:.1f}%" for n in breakdown.percentage]
    fig = go.Figure(go.Bar(
        x=breakdown[field].tolist(), y=breakdown.genre.tolist(), orientation="h",
        marker_color=[COLORS["dim"] if g == "unknown" else COLORS["data"] for g in breakdown.genre],
        text=labels, textposition="outside", textfont=dict(size=14, color=COLORS["bright"]), cliponaxis=False, constraintext="none",
        customdata=breakdown[["movies", "percentage"]].values,
        hovertemplate="%{y}<br>%{customdata[0]:,.0f} movies<br>%{customdata[1]:.1f}% of rated movies<extra></extra>",
    ))
    style_chart(fig, 480, "distinct movies" if field == "movies" else "share of all rated movies (%)")
    fig.update_xaxes(range=[0, float(breakdown[field].max()) * 1.25], nticks=4)
    fig.update_yaxes(autorange="reversed")
    draw(fig, "genre_distribution")
    with st.expander("view genre counts"):
        table(breakdown.rename(columns={"percentage": "share (%)"}).round(2))
    st.html(f'<div class="pane-status">unit: <b>distinct movie</b> | total: <b>{len(movies):,}</b></div>')

with right, st.container(key="pane_satisfaction"):
    pane_heading("02", "genre satisfaction", "average rating by genre, highest to lowest")
    known = satisfaction.loc[satisfaction.genre != "unknown"]
    if not known.empty:
        best, worst = known.iloc[0], known.iloc[-1]
        st.html(f'<div class="verdict"><span class="key">highest:</span> {escape(best.genre)} '
                f'<strong>{best.mean_rating:.2f}</strong><br><span class="key">lowest:</span> '
                f'{escape(worst.genre)} <strong>{worst.mean_rating:.2f}</strong></div>')
    st.html('<p class="scope-note">each rating contributes to every genre on its movie. '
            'more-rated movies carry more weight. unknown stays visible.</p>')
    fig = go.Figure(go.Bar(
        x=satisfaction.mean_rating.tolist(), y=satisfaction.genre.tolist(), orientation="h",
        marker_color=[COLORS["dim"] if g == "unknown" else COLORS["data"] for g in satisfaction.genre],
        text=[f"{v:.2f}" for v in satisfaction.mean_rating], textposition="outside",
        textfont=dict(size=14, color=COLORS["bright"]), cliponaxis=False, constraintext="none",
        customdata=satisfaction[["ratings", "movies"]].values,
        hovertemplate="%{y}<br>mean: %{x:.3f}/5<br>%{customdata[0]:,.0f} ratings<br>%{customdata[1]:,.0f} movies<extra></extra>",
    ))
    style_chart(fig, 480, "mean rating / 5")
    fig.update_xaxes(range=[0, 5.3], dtick=1)
    fig.update_yaxes(autorange="reversed")
    draw(fig, "genre_ratings")
    with st.expander("view averages + sample sizes"):
        table(satisfaction.rename(columns={"mean_rating": "mean / 5"}).round(3))
    st.html('<div class="pane-status">unit: <b>individual rating</b> | scale: <b>1–5</b></div>')

left, right = st.columns(2, gap="small")
with left, st.container(key="pane_years"):
    pane_heading("03", "release years", "mean rating across movie release years")
    missing_year = int(ratings.year.isna().sum())
    st.html('<p class="scope-note">grouped by release year, not the year rated. '
            'hover for sample sizes; gaps mean no movies.</p>')
    if yearly.empty:
        st.info("no release years available (check the source CSV)")
    else:
        continuous = yearly.set_index("year").reindex(range(int(yearly.year.min()), int(yearly.year.max()) + 1))
        fig = go.Figure(go.Scatter(
            x=continuous.index.tolist(), y=continuous.mean_rating.tolist(), mode="lines+markers",
            line=dict(color=COLORS["data"], width=1), marker=dict(size=5, color=COLORS["data"]), connectgaps=False,
            customdata=continuous[["ratings", "movies"]].values,
            hovertemplate="released %{x}<br>mean: %{y:.3f}/5<br>%{customdata[0]:,.0f} ratings"
                          "<br>%{customdata[1]:,.0f} movies<extra></extra>",
        ))
        style_chart(fig, 400, "movie release year")
        fig.update_xaxes(nticks=5, showgrid=False, showspikes=True, spikemode="across", spikesnap="cursor",
                         spikecolor=COLORS["dim"], spikethickness=1, spikedash="solid")
        fig.update_yaxes(title=dict(text="mean / 5", font=dict(size=14)), range=[1, 5.1], dtick=1,
                         showgrid=True, gridcolor=COLORS["line"], tickfont=dict(color=COLORS["dim"]))
        draw(fig, "release_year_ratings")
        with st.expander("view annual averages + sample sizes"):
            table(yearly.rename(columns={"year": "release year", "mean_rating": "mean / 5"}).round(3))
    st.html(f'<div class="pane-status">missing year: <b>{missing_year} ratings</b> | excluded here only</div>')

with right, st.container(key="pane_movies"):
    pane_heading("04", "best movies", "top five films with a minimum audience")
    floor = st.slider("minimum ratings:", min_value=50, max_value=150, value=50, step=1, key="rating_floor")
    top = top_movies(movies, floor)
    eligible = int((movies.ratings >= floor).sum())
    st.caption(f"{eligible:,} movies qualify at ≥{floor} ratings. applies to this pane only.")
    if top.empty:
        st.info("no movies meet this minimum (lower the rating floor)")
    else:
        # Titles sit above bars, preserving chart space and 14px type on phones.
        # Full titles remain in hover labels and the keyboard-accessible table.
        fig = go.Figure(go.Bar(
            x=top.mean_rating.tolist(), y=list(range(len(top))), orientation="h", marker_color=COLORS["data"],
            width=0.28, text=[f"{r.mean_rating:.3f}" for r in top.itertuples()],
            textposition="outside", textfont=dict(size=14, color=COLORS["bright"]), cliponaxis=False, constraintext="none",
            customdata=top[["title", "ratings"]].values,
            hovertemplate="%{customdata[0]}<br>mean: %{x:.3f}/5<br>%{customdata[1]:,.0f} ratings<extra></extra>",
        ))
        style_chart(fig, 360, "mean rating / 5")
        fig.update_xaxes(range=[0, 5.5], dtick=1)
        fig.update_yaxes(range=[4.5, -0.8], showticklabels=False, showgrid=False)
        for i, row in enumerate(top.itertuples()):
            fig.add_annotation(x=0, xref="paper", y=i - 0.38, yref="y", showarrow=False,
                               text=f"{i + 1:02d}  {escape(shorten(row.title, width=43, placeholder='…'))}",
                               xanchor="left", align="left", font=dict(size=14, color=COLORS["orange"]))
        draw(fig, "top_five_movies")
        with st.expander("view full titles + rating counts"):
            st.table(ranking_table(top), hide_index=True)

    top50, top150 = top_movies(movies, 50), top_movies(movies, 150)
    departed = top50.loc[~top50.movie_id.isin(top150.movie_id), "title"].tolist()
    arrived = top150.loc[~top150.movie_id.isin(top50.movie_id), "title"].tolist()
    with st.expander(f"compare 50 → 150 / {len(arrived)} changes"):
        st.caption("leaves: " + ("; ".join(departed) or "none"))
        st.caption("enters: " + ("; ".join(arrived) or "none"))
        st.caption("floor: 50 ratings")
        st.table(ranking_table(top50), hide_index=True)
        st.caption("floor: 150 ratings")
        st.table(ranking_table(top150), hide_index=True)
    st.html('<div class="pane-status">rank: <b>unrounded mean</b> | ties: rating count, then movie ID</div>')

st.html(f"""
<p class="help-line"><kbd>tab</kbd> focus <span aria-hidden="true">│</span>
  <kbd>← →</kbd> adjust control <span aria-hidden="true">│</span> hover for sample sizes</p>
<footer class="session-status"><span class="mode">VIEW</span>
  <nav aria-label="chart sections"><a href="#pane-title-01">1:genres</a><a href="#pane-title-02">2:ratings</a>
    <a href="#pane-title-03">3:years</a><a href="#pane-title-04">4:movies</a></nav>
  <span class="status-context">MovieLens | {len(ratings):,} ratings | floor ≥{floor}</span>
</footer>
""")
st.html((ROOT / "terminal.js").read_text(encoding="utf-8"), unsafe_allow_javascript=True)
