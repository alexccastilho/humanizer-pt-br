"""Regression tests for the defects found in the 27/11/2026 audit of evals/ and scripts/.

Run: python -B -m unittest discover -s tests -v
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))
sys.path.insert(0, str(ROOT / "evals" / "tools"))
import analyze  # noqa: E402
import check  # noqa: E402
import judge  # noqa: E402
import trigger  # noqa: E402
import vocab_report  # noqa: E402


class CheckerDashes(unittest.TestCase):
    def test_short_line_without_final_period_is_prose(self):
        for text in ("Só existe um caminho — cortar custos",
                     "O time — cansado — recusou",
                     "Resultado - todo mundo saiu ganhando"):
            self.assertTrue(check.aside_dashes(text), text)

    def test_dash_inside_list_item_is_found(self):
        for text in ("- O time — cansado — recusou.",
                     "* O prazo era curto - e o time entregou.",
                     "1. A meta — ambiciosa — foi batida."):
            self.assertTrue(check.aside_dashes(text), text)

    def test_dash_inside_heading_is_found(self):
        self.assertTrue(check.aside_dashes("## O futuro — e o que ele esconde"))

    def test_labels_and_markers_still_ignored(self):
        for text in ("Maria Souza - Diretora",
                     "Assessoria de Imprensa – Flor de Lis",
                     "- Maria Souza – Diretora de RH",
                     "- item de lista com texto",
                     "Contato - 11 99999-0000",
                     "> Citação — com travessão do autor"):
            self.assertEqual(check.aside_dashes(text), [], text)


class CheckerProtected(unittest.TestCase):
    def test_span_only_in_falta_fonte_line_fails(self):
        src = 'Segundo o relatório, "a meta é dobrar até 2026" e o time concordou.'
        out = 'O time concordou com o relatório.\n\nFalta fonte: "a meta é dobrar até 2026"'
        self.assertIn("protected", check.check(src, out)["failures"])

    def test_url_drops_trailing_punctuation(self):
        spans = check.protected_spans("Veja https://ex.com/a! Ou https://ex.com/b? Ou https://ex.com/c: fim.")
        for s in ("https://ex.com/a", "https://ex.com/b", "https://ex.com/c"):
            self.assertIn(s, spans)


class CheckerPreamble(unittest.TestCase):
    def test_closing_in_single_line_answer(self):
        self.assertTrue(check.preamble("O time recusou. Se quiser, posso ajustar."))

    def test_single_line_with_legit_ending_is_clean(self):
        self.assertEqual(check.preamble("Caso queira participar, a inscrição fecha sexta."), [])


class CheckerNumbers(unittest.TestCase):
    def test_count_change_is_reported_but_not_a_failure(self):
        r = check.check("Foram 10 vagas em março e 10 em abril.", "Foram 10 vagas em março e em abril.")
        self.assertEqual(r["numbers_count_changed"], ["10"])
        self.assertNotIn("numbers_missing", r["failures"])


class CheckerPunctuation(unittest.TestCase):
    def test_ampersand_for_e_in_prose(self):
        self.assertIn("&", check.punctuation("Vendas & marketing cresceram juntos."))

    def test_brand_with_ampersand_is_fine(self):
        r = check.check("A P&D da Johnson & Johnson cresceu.", "A P&D da Johnson & Johnson cresceu.",
                        {"protected": ["Johnson & Johnson"]})
        self.assertNotIn("punctuation", r["failures"])

    def test_arrow_in_step_list_is_fine(self):
        self.assertEqual(check.punctuation("Para exportar:\n\n1. Abra Arquivo → Exportar.\n2. Salve."), [])

    def test_more_than_one_exclamation_per_block(self):
        self.assertIn("!", check.punctuation("Deu certo! Batemos a meta! Parabéns ao time."))
        self.assertEqual(check.punctuation("Deu certo! Batemos a meta.\n\nParabéns ao time!"), [])


class Judge(unittest.TestCase):
    def test_valid_verdict(self):
        self.assertTrue(judge.valid_verdict({"vencedor": "A"}))
        self.assertTrue(judge.valid_verdict({"vencedor": "empate"}))
        for bad in (None, {}, {"vencedor": "C"}, {"vencedor": None}, ["A"]):
            self.assertFalse(judge.valid_verdict(bad), bad)

    def test_default_pairs_have_no_novocab(self):
        self.assertNotIn("novocab", judge.DEFAULT_PAIRS)


def _judgment(pair, x, y, case, rep, fx, fy, winner):
    return {"pair": pair, "x": x, "y": y, "case": case, "rep": rep, "winner": winner,
            "position_winner": "A", "fidelity": {x: fx, y: fy}, "naturalness": {x: 7, y: 5}}


class Analyze(unittest.TestCase):
    def test_fidelity_counts_each_output_once(self):
        js = [_judgment("skill_vs_baseline", "skill", "baseline", "c1", 1, ["erro"], [], "baseline"),
              _judgment("skill_vs_minimal", "skill", "minimal", "c1", 1, [], [], "skill"),
              _judgment("skill_vs_baseline", "skill", "baseline", "c2", 1, [], [], "skill"),
              _judgment("skill_vs_minimal", "skill", "minimal", "c2", 1, [], [], "skill")]
        _, fid, nat = analyze.pair_stats(js)
        self.assertEqual(fid["skill"]["n"], 2)
        self.assertEqual(fid["baseline"]["n"], 2)
        self.assertEqual(fid["skill"]["mean_errors"], 0.25)
        # c1 was flagged by one of its two judgments: half an output with error.
        self.assertEqual(fid["skill"]["outputs_with_error"], 0.25)
        self.assertEqual(nat["skill"], 7)

    def _arms(self, n_min=40):
        base = {"rewrites": 40, "failures": {k: 0 for k in analyze.HARD}, "cost_usd_mean": 0.1}
        return {"skill": dict(base), "baseline": dict(base), "minimal": dict(base, rewrites=n_min)}

    def _pairs(self, n=40):
        return {p: {"n": n, "win_rate_x": 0.7, "ci95": [0.55, 0.8]} for p in ("skill_vs_baseline", "skill_vs_minimal")}

    def test_g0_needs_minimal_and_pairs(self):
        g0 = lambda arms, pairs: next(v for k, v in analyze.gates(arms, pairs, {}).items() if k.startswith("G0"))
        self.assertTrue(g0(self._arms(), self._pairs()))
        self.assertFalse(g0(self._arms(n_min=10), self._pairs()))
        self.assertFalse(g0(self._arms(), self._pairs(n=10)))
        self.assertFalse(g0(self._arms(), {}))

    def test_empty_output_counts_as_failure(self):
        cases = {"c1": {"id": "c1", "text": "O time recusou.", "origin": "ai-slop", "expect": {}}}
        runs = [{"arm": "skill", "case": "c1", "output": ""},
                {"arm": "skill", "case": "c1", "output": "O time recusou."}]
        st = analyze.arm_stats(runs, cases)["skill"]
        self.assertEqual(st["rewrites"], 2)
        self.assertEqual(st["failures"]["empty"], 1)
        self.assertEqual(st["runs_with_any_failure"], 1)


class Trigger(unittest.TestCase):
    def test_error_is_not_a_silent_no(self):
        r = trigger.classify({"is_error": True, "error": "timeout"}, "humanizer-pt-br")
        self.assertIsNone(r["fired"])
        self.assertEqual(r["error"], "timeout")

    def test_crash_without_result_event_is_an_error(self):
        # What claude_cli.parse_stream returns when the CLI exits before its "result" line.
        r = trigger.classify({"skill_calls": [], "exit_code": 1, "stderr_tail": "boom"}, "humanizer-pt-br")
        self.assertIsNone(r["fired"])
        self.assertIn("exit 1", r["error"])

    def test_fired(self):
        r = trigger.classify({"skill_calls": ["humanizer-pt-br:humanizer-pt-br"], "is_error": False}, "humanizer-pt-br")
        self.assertTrue(r["fired"])
        self.assertIsNone(r["error"])

    def test_reps_flag_exists(self):
        self.assertIn("--reps", trigger.parser().format_help())


class Vocab(unittest.TestCase):
    def test_placeholder_matches_any_word(self):
        rx = vocab_report.stem_rx("um verdadeiro x")
        self.assertTrue(rx.search("Foi um verdadeiro marco."))

    def test_stem_does_not_reach_other_words(self):
        self.assertFalse(vocab_report.stem_rx("universo").search("A Universidade abriu."))
        self.assertTrue(vocab_report.stem_rx("universo").search("o universos paralelos"))
        self.assertTrue(vocab_report.stem_rx("mergulhar").search("mergulhando fundo"))
        self.assertTrue(vocab_report.stem_rx("robusto").search("soluções robustas"))

    def test_short_content_word_keeps_plural(self):
        self.assertTrue(vocab_report.stem_rx("pilar").search("os pilares da empresa"))
        self.assertFalse(vocab_report.stem_rx("pilar").search("pilastra"))

    def test_short_last_word_is_exact(self):
        rx = vocab_report.stem_rx("trata-se de")
        self.assertTrue(rx.search("trata-se de um caso"))
        self.assertFalse(rx.search("trata-se desde"))
        self.assertFalse(vocab_report.stem_rx("é fundamental que").search("é fundamental quem"))


class Package(unittest.TestCase):
    def test_zip_is_byte_identical_between_builds(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for d in (a, b):
                subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "build_zip.py"), "--out", d],
                               check=True, capture_output=True)
            za, zb = next(pathlib.Path(a).glob("*.zip")), next(pathlib.Path(b).glob("*.zip"))
            with zipfile.ZipFile(za) as z:
                self.assertTrue(all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in z.infolist()))
            self.assertEqual(za.read_bytes(), zb.read_bytes())


if __name__ == "__main__":
    unittest.main()
