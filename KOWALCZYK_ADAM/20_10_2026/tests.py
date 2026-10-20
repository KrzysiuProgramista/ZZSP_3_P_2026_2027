import io
import unittest
from contextlib import redirect_stdout

import pandas as pd

from solutions import filter_below, filter_between, filter_by_values, top_n, report


class Base(unittest.TestCase):
    def setUp(self):
        self.df = pd.read_csv("data.csv")


class TestToolkit(Base):
    def test_filter_below(self):
        self.assertTrue((filter_below(self.df, "quantity", 10)["quantity"] < 10).all())

    def test_filter_between(self):
        r = filter_between(self.df, "quantity", 5, 20)
        self.assertTrue(r["quantity"].between(5, 20).all())
        self.assertEqual(len(r), 9)

    def test_filter_by_values(self):
        r = filter_by_values(self.df, "region", ["North", "East"])
        self.assertEqual(set(r["region"]), {"North", "East"})

    def test_top_n(self):
        r = top_n(self.df, "unit_price", 3)
        self.assertEqual(len(r), 3)
        self.assertTrue((r["unit_price"] == 3500).all())

    def test_unknown_column(self):
        calls = [
            lambda: filter_below(self.df, "nope", 1),
            lambda: filter_between(self.df, "nope", 1, 2),
            lambda: filter_by_values(self.df, "nope", [1]),
            lambda: top_n(self.df, "nope", 1),
        ]
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaisesRegex(ValueError, "Unknown column"):
                    call()


class TestReport(Base):
    def test_one_filter(self):
        r = report(self.df, region="North")
        self.assertTrue((r["region"] == "North").all())

    def test_two_filters_and(self):
        r = report(self.df, region="North", category="Electronics")
        self.assertEqual(len(r), 4)
        self.assertTrue((r["category"] == "Electronics").all())

    def test_no_match(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            r = report(self.df, region="Mars")
        self.assertTrue(r.empty)
        self.assertIn("Total value: 0.00", buf.getvalue())

    def test_unknown_column(self):
        with self.assertRaisesRegex(ValueError, "Unknown column"):
            report(self.df, department="North")

    def test_no_filters(self):
        self.assertEqual(len(report(self.df)), len(self.df))


if __name__ == "__main__":
    unittest.main()