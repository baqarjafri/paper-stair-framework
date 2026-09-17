#!/usr/bin/env python3
"""Tests for the display-page scripts. Run: python -m unittest scripts.test_display_page -v"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_display_data as bdd  # noqa: E402
import verify_display_page as vdp  # noqa: E402


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.data = bdd.build()

    def test_five_levels_in_order(self):
        self.assertEqual([lv["id"] for lv in self.data["levels"]], ["L1", "L2", "L3", "L4", "L5"])

    def test_level_scores_match_paper(self):
        self.assertEqual([lv["score"] for lv in self.data["levels"]], [55, 53, 25, 5, 22])

    def test_l3_dimensions_and_arithmetic(self):
        l3 = self.data["levels"][2]
        self.assertEqual(l3["dims"], {"COV": 50, "ACC": 50, "EDU": 0, "TMP": 25, "INT": 0})
        self.assertEqual(round(sum(l3["dims"].values()) / 5), 25)

    def test_28_sub_dimensions_with_definitions(self):
        subs = self.data["subs"]
        self.assertEqual(len(subs), 28)
        for s in subs.values():
            self.assertIn(s["score"], range(5))
            self.assertTrue(s["definition"])
            self.assertTrue(s["evidence"])
            self.assertNotIn("\u2014", s["evidence"])

    def test_bands(self):
        self.assertEqual([lv["band"] for lv in self.data["levels"]],
                         ["ready", "ready", "limited", "critical", "limited"])

    def test_claims(self):
        c = self.data["claims"]
        self.assertEqual((c["cliff"], c["ai_refs_analytics"], c["analytics_refs_ai"],
                          c["web_services"], c["claims_total"]), (28, 0, 0, 402, 13))

    def test_dimension_scores_come_from_table3(self):
        l2 = self.data["levels"][1]
        self.assertEqual(l2["dims"], {"COV": 75, "ACC": 75, "EDU": 25, "TMP": 50, "INT": 38})
        l5 = self.data["levels"][4]
        self.assertEqual(l5["dims"]["EDU"], 12)
        self.assertEqual(l2["subs"][0], "2.1_Raw_Data_Availability")
        self.assertEqual(len(self.data["levels"][2]["subs"]), 7)

    def test_render_is_valid_js_with_json_payload(self):
        text = bdd.render(self.data)
        self.assertTrue(text.startswith("// Generated"))
        payload = text.split("window.STAIR_DATA = ", 1)[1].rstrip().rstrip(";")
        self.assertEqual(json.loads(payload)["levels"][0]["id"], "L1")
        self.assertNotIn("\u2014", text)
        self.assertNotIn(" -- ", text)

    def test_levels_carry_paper_register_copy(self):
        l3 = self.data["levels"][2]
        self.assertEqual(l3["verb"], "Reason")
        self.assertTrue(l3["requirement"].startswith("Platform supports autonomous AI deliberation"))
        self.assertEqual(l3["components"], "AI subsystem \u00b7 Reasoning pipeline \u00b7 SRL detection")
        self.assertEqual(l3["constructs"], {"Z": "Strategic planning", "T": "Agent reasoning loop",
                                           "H": "Planning and goal decomposition"})
        for lv in self.data["levels"]:
            for key in ("question", "answer", "plain"):
                self.assertNotIn(key, lv)
        for lv in self.data["levels"]:
            self.assertEqual(set(lv["constructs"]), {"Z", "T", "H"})
            self.assertEqual(lv["components"].count(chr(183)), 2)
            self.assertTrue(lv["requirement"].startswith("Platform ") and lv["requirement"].endswith("."))

    def test_clean_normalises_double_hyphen_and_em_dash(self):
        self.assertEqual(bdd.clean("a \u2014 b"), "a \u00b7 b")
        self.assertEqual(bdd.clean("Absent (0%) -- no infrastructure"), "Absent (0%): no infrastructure")
        self.assertEqual(self.data["rubric"]["0"], "Absent (0%): no infrastructure; capability does not exist")

    def test_check_mode_reports_missing_sync_and_drift(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site-data.js"
            original = bdd.OUT
            try:
                bdd.OUT = out
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(bdd.main(["--check"]), 1)
                self.assertIn("MISSING", buf.getvalue())
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(bdd.main([]), 0)
                    self.assertEqual(bdd.main(["--check"]), 0)
                out.write_text(out.read_text(encoding="utf-8").replace('"L1"', '"L9"', 1), encoding="utf-8")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(bdd.main(["--check"]), 1)
                self.assertIn("DRIFT", buf.getvalue())
            finally:
                bdd.OUT = original


class VerifyTests(unittest.TestCase):
    def test_expected_keys_cover_page_numbers(self):
        exp = vdp.expected(bdd.build())
        self.assertEqual(exp["L3.EDU"], "0")
        self.assertEqual(exp["3.4_AI_Analytics_Bridge"], "0")
        self.assertEqual(exp["L2.score.ladder"], "53")
        self.assertEqual(exp["L4.mean"], "5")
        self.assertEqual(exp["claims.imports"], "0")
        self.assertEqual(len(exp), 81)
        self.assertEqual(exp["L3.score.banner"], "25")
        self.assertEqual(exp["claims.ai_providers"], "6")
        self.assertEqual(exp["claims.ai_actions"], "4")
        self.assertEqual(exp["claims.analytics_targets"], "8")

    def test_parse_checks_reads_text_of_marked_elements(self):
        html = ('<svg><text data-check="L1.score">55</text></svg>'
                '<p>prose 99</p><b data-check="L2.score">99</b>')
        self.assertEqual(vdp.parse_checks(html), {"L1.score": "55", "L2.score": "99"})

    def test_compare_reports_pass_fail_missing(self):
        rows = vdp.compare({"L1.score": "55", "L2.score": "53", "L3.score": "25"},
                           {"L1.score": "55", "L2.score": "99"})
        status = {r[0]: r[3] for r in rows}
        self.assertEqual((status["L1.score"], status["L2.score"], status["L3.score"]),
                         ("PASS", "FAIL", "MISSING"))

    def test_parse_checks_rejects_rule_violations(self):
        with self.assertRaises(ValueError) as cm:
            vdp.parse_checks('<b data-check="x">28<span>pt</span></b>')
        self.assertIn("CHILD ELEMENT", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            vdp.parse_checks('<b data-check="x">1</b><b data-check="x">2</b>')
        self.assertIn("DUPLICATE", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            vdp.parse_checks('<b data-check="x"><i data-check="y">2</i></b>')
        self.assertIn("NESTED", str(cm.exception))

    def test_compare_flags_unknown_keys(self):
        rows = vdp.compare({"L1.score": "55"}, {"L1.score": "55", "L1.scor": "55"})
        self.assertEqual([(r[0], r[3]) for r in rows], [("L1.score", "PASS"), ("L1.scor", "UNKNOWN")])

    def test_main_exit_codes(self):
        import contextlib
        import io
        import tempfile
        data = bdd.build()
        exp = vdp.expected(data)
        copy = "".join(f"<p>{lv['requirement']} {lv['components'].replace(chr(183), '&middot;')} "
                       + " ".join(lv["constructs"].values()) + "</p>" for lv in data["levels"])
        page = "".join(f'<b data-check="{k}">{v}</b>' for k, v in exp.items()) + copy
        with tempfile.TemporaryDirectory() as tmp:
            original = vdp.INDEX
            try:
                vdp.INDEX = Path(tmp) / "index.html"
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(vdp.main(), 1)
                self.assertIn("not found", buf.getvalue())
                vdp.INDEX.write_text(page, encoding="utf-8")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(vdp.main(), 0)
                self.assertIn("81 matched, 0 drifted, missing or unknown, 81 total; 0 copy gaps.", buf.getvalue())
                vdp.INDEX.write_text(page.replace(">38<", ">37<", 1), encoding="utf-8")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    self.assertEqual(vdp.main(), 1)
                self.assertIn("L2.INT", buf.getvalue())
                self.assertIn("FAIL", buf.getvalue())
            finally:
                vdp.INDEX = original

    def test_copy_gaps_reports_missing_level_copy(self):
        data = bdd.build()
        full = "".join(f"<p>{lv['requirement']} {lv['components']} " + " ".join(lv["constructs"].values()) + "</p>"
                       for lv in data["levels"])
        self.assertEqual(vdp.copy_gaps(full, data), [])
        self.assertEqual(vdp.copy_gaps(full.replace(chr(183), "|"), data)[0][:14], "L1 components:")
        without_l4 = full.replace(data["levels"][3]["requirement"], "")
        self.assertEqual(vdp.copy_gaps(without_l4, data), [f'L4 requirement: "{data["levels"][3]["requirement"]}"'])
        plural = full.replace("Agent reasoning loop", "Agent reasoning loops")
        self.assertEqual(vdp.copy_gaps(plural, data), ['L3 construct T: "Agent reasoning loop"'])


if __name__ == "__main__":
    unittest.main()
