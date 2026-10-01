"""The four assignment calculations, independent of Streamlit and chart styling."""

from pathlib import Path

import pandas as pd


def load_ratings(path: str | Path) -> pd.DataFrame:
    required = ["user_id", "movie_id", "rating", "title", "year", "genres"]
    frame = pd.read_csv(path, usecols=required)
    if frame.empty:
        raise ValueError("The ratings file is empty.")
    for column in ["user_id", "movie_id", "rating", "year"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if frame[["user_id", "movie_id", "rating", "title"]].isna().any().any():
        raise ValueError("Every rating needs a user ID, movie ID, title, and rating.")
    if not frame.rating.between(1, 5).all():
        raise ValueError("Ratings must be between 1 and 5.")
    for column in ["user_id", "movie_id", "year"]:
        values = frame[column].dropna()
        if not (values % 1 == 0).all():
            raise ValueError(f"{column} must contain whole numbers.")
        frame[column] = frame[column].astype("Int64")
    if frame.duplicated(["user_id", "movie_id"]).any():
        raise ValueError("Duplicate user/movie ratings need to be resolved before analysis.")
    frame["genres"] = frame.genres.fillna("unknown").map(
        lambda value: "|".join(sorted({g.strip() for g in value.split("|") if g.strip()}))
        or "unknown"
    )
    metadata = frame.groupby("movie_id")[["title", "year", "genres"]].nunique(dropna=False)
    if (metadata > 1).any().any():
        raise ValueError("A movie ID has conflicting titles, release years, or genres.")
    return frame


def genre_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.assign(genre=frame.genres.str.split("|")).explode("genre")


def genre_breakdown(frame: pd.DataFrame) -> pd.DataFrame:
    movies = frame.drop_duplicates("movie_id")
    counts = genre_rows(movies).groupby("genre").movie_id.nunique().rename("movies").reset_index()
    counts["percentage"] = counts.movies / len(movies) * 100 if len(movies) else 0.0
    return counts.sort_values(["movies", "genre"], ascending=[False, True]).reset_index(drop=True)


def genre_satisfaction(frame: pd.DataFrame) -> pd.DataFrame:
    result = genre_rows(frame).groupby("genre").agg(
        mean_rating=("rating", "mean"), ratings=("rating", "size"), movies=("movie_id", "nunique")
    ).reset_index()
    return result.sort_values(["mean_rating", "genre"], ascending=[False, True]).reset_index(drop=True)


def ratings_by_release_year(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.dropna(subset=["year"]).groupby("year").agg(
        mean_rating=("rating", "mean"), ratings=("rating", "size"), movies=("movie_id", "nunique")
    ).reset_index().sort_values("year")


def movie_summary(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.groupby("movie_id").agg(
        title=("title", "first"), mean_rating=("rating", "mean"), ratings=("rating", "size")
    ).reset_index()


def top_movies(summary: pd.DataFrame, floor: int) -> pd.DataFrame:
    if floor < 1:
        raise ValueError("The minimum rating count must be positive.")
    # Rank on unrounded means; count and ID make ties reproducible.
    return summary.loc[summary.ratings >= floor].sort_values(
        ["mean_rating", "ratings", "movie_id"], ascending=[False, False, True]
    ).head(5).reset_index(drop=True)
