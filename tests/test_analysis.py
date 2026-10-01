import csv
from collections import defaultdict
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from analysis import (
    genre_breakdown, genre_satisfaction, load_ratings,
    movie_summary, ratings_by_release_year, top_movies,
)

ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame([
            (1, 1, 5, "A", 2000, "Comedy|Romance"),
            (2, 1, 3, "A", 2000, "Comedy|Romance"),
            (3, 1, 4, "A", 2000, "Comedy|Romance"),
            (1, 2, 2, "B", 2000, "Comedy"),
            (1, 3, 1, "C", None, "Drama"),
        ], columns=["user_id", "movie_id", "rating", "title", "year", "genres"])

    def test_genres_count_movies_not_ratings_and_allow_overlap(self):
        result = genre_breakdown(self.frame).set_index("genre")
        self.assertEqual(result.movies.to_dict(), {"Comedy": 2, "Drama": 1, "Romance": 1})
        self.assertAlmostEqual(result.loc["Comedy", "percentage"], 200 / 3)
        self.assertAlmostEqual(result.percentage.sum(), 400 / 3)

    def test_satisfaction_weights_individual_ratings(self):
        result = genre_satisfaction(self.frame).set_index("genre")
        self.assertEqual(result.loc["Comedy", "mean_rating"], 3.5)
        self.assertEqual(result.loc["Romance", "mean_rating"], 4)
        self.assertEqual(result.loc["Comedy", "ratings"], 4)

    def test_release_year_not_rating_year_and_missing_year_exclusion(self):
        self.frame["rating_year"] = 2026
        result = ratings_by_release_year(self.frame)
        self.assertEqual(result.year.tolist(), [2000])
        self.assertEqual(result.iloc[0].mean_rating, 3.5)
        self.assertEqual(result.iloc[0].ratings, 4)
        self.assertEqual(len(movie_summary(self.frame)), 3)

    def test_floor_is_inclusive_and_ties_are_deterministic(self):
        summary = pd.DataFrame([
            (1, "Below 50", 5.0, 49), (2, "At 50", 4.9, 50),
            (3, "Below 150", 4.8, 149), (4, "At 150", 4.7, 150),
            (5, "More ratings", 4.7, 151), (6, "Same count", 4.7, 150),
            (7, "Lower mean", 4.0, 200),
        ], columns=["movie_id", "title", "mean_rating", "ratings"])
        self.assertEqual(top_movies(summary, 50).movie_id.tolist(), [2, 3, 5, 4, 6])
        self.assertEqual(top_movies(summary, 150).movie_id.tolist(), [5, 4, 6, 7])
        self.assertTrue(top_movies(summary, 201).empty)

    def test_loader_rejects_duplicate_ratings_and_conflicting_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ratings.csv"
            pd.concat([self.frame, self.frame.iloc[:1]]).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_ratings(path)
            frame = self.frame.copy()
            frame.loc[1, "genres"] = "Drama"
            frame.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "conflicting"):
                load_ratings(path)

    def test_loader_normalizes_repeated_genre_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ratings.csv"
            frame = self.frame.copy()
            frame.loc[frame.movie_id == 1, "genres"] = " Comedy |Romance|Comedy"
            frame.to_csv(path, index=False)
            clean = load_ratings(path)
            self.assertEqual(genre_breakdown(clean).set_index("genre").loc["Comedy", "movies"], 2)

    def test_real_data_against_independent_csv_accumulation(self):
        totals, memberships, genres, years = {}, defaultdict(set), defaultdict(list), defaultdict(list)
        with (ROOT / "movie_ratings.csv").open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                movie_id, rating = int(row["movie_id"]), float(row["rating"])
                totals.setdefault(movie_id, []).append(rating)
                for genre in set(row["genres"].split("|")):
                    memberships[genre].add(movie_id)
                    genres[genre].append(rating)
                if row["year"]:
                    years[int(float(row["year"]))].append(rating)
        frame = load_ratings(ROOT / "movie_ratings.csv")
        self.assertEqual(len(frame), 100000)
        self.assertEqual(len(totals), 1682)
        self.assertEqual(genre_breakdown(frame).set_index("genre").movies.to_dict(),
                         {genre: len(ids) for genre, ids in memberships.items()})
        for row in genre_satisfaction(frame).itertuples():
            self.assertAlmostEqual(row.mean_rating, sum(genres[row.genre]) / len(genres[row.genre]))
        for row in ratings_by_release_year(frame).itertuples():
            self.assertAlmostEqual(row.mean_rating, sum(years[row.year]) / len(years[row.year]))
        for floor in [50, 150]:
            expected = sorted((i for i, values in totals.items() if len(values) >= floor),
                              key=lambda i: (-sum(totals[i]) / len(totals[i]), -len(totals[i]), i))[:5]
            self.assertEqual(top_movies(movie_summary(frame), floor).movie_id.tolist(), expected)


if __name__ == "__main__":
    unittest.main()
