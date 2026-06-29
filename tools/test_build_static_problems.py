"""Unit tests for tools/build_static_problems.py (stdlib unittest, no pip).

Covers the grading-relevant bits of bundling: sample/test visibility, test
ordering, skipping a test that is missing its .out, and metadata passthrough.

Run:  python3 -m unittest tools.test_build_static_problems -v
   or: python3 tools/test_build_static_problems.py
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_static_problems as b


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class BuildProblemTest(unittest.TestCase):
    def _make_problem(self, tmp, cases):
        meta = {
            "id": "add-two-d1-0001",
            "title": "A + B",
            "topic": "math",
            "difficulty": 1,
            "tags": ["arithmetic", "io"],
            "samples": [{"input": "1 2", "output": "3"}],
        }
        write(os.path.join(tmp, "meta.json"), json.dumps(meta))
        write(os.path.join(tmp, "statement.md"), "# A + B\n\nAdd two numbers.\n")
        tests_dir = os.path.join(tmp, "tests")
        os.makedirs(tests_dir)
        for name, has_out in cases:
            write(os.path.join(tests_dir, name + ".in"), "1 2\n")
            if has_out:
                write(os.path.join(tests_dir, name + ".out"), "3\n")
        return tmp

    def test_classifies_sample_as_visible_and_test_as_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_problem(tmp, [("sample1", True), ("test1", True)])
            prob = b.build_problem(tmp)
            by_name = {t["name"]: t for t in prob["tests"]}
            self.assertFalse(by_name["sample1"]["hidden"])
            self.assertTrue(by_name["test1"]["hidden"])

    def test_metadata_and_samples_pass_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_problem(tmp, [("sample1", True)])
            prob = b.build_problem(tmp)
            self.assertEqual(prob["id"], "add-two-d1-0001")
            self.assertEqual(prob["difficulty"], 1)
            self.assertEqual(prob["tags"], ["arithmetic", "io"])
            self.assertEqual(prob["samples"], [{"input": "1 2", "output": "3"}])
            self.assertIn("Add two numbers", prob["statement"])

    def test_tests_are_sorted_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_problem(tmp, [("test2", True), ("test1", True), ("sample1", True)])
            prob = b.build_problem(tmp)
            self.assertEqual([t["name"] for t in prob["tests"]], ["sample1", "test1", "test2"])

    def test_skips_input_without_matching_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_problem(tmp, [("sample1", True), ("test1", False)])
            prob = b.build_problem(tmp)
            self.assertEqual([t["name"] for t in prob["tests"]], ["sample1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
