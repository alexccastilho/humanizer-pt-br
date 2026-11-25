"""Tests for evals/check.py: good and bad rewrites built by hand.

Run: python -B -m unittest discover -s tests -v
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "evals"))
import check  # noqa: E402


class Dashes(unittest.TestCase):
    def test_aside_dash_in_prose_is_found(self):
        for text in ("O time — que já estava cansado — recusou.",
                     "O time – cansado – recusou.",
                     "O prazo era curto - e o time entregou.",
                     "O prazo era curto—e o time entregou."):
            self.assertTrue(check.aside_dashes(text), text)

    def test_legit_dashes_are_ignored(self):
        for text in ("Atendemos de 10-20 pessoas por dia.",
                     "O estudo cobre 2020–2024.",
                     "Reunião na segunda-feira.",
                     "- item de lista com texto",
                     "— Você vem? — perguntou ela.",
                     "Maria Souza - Diretora",
                     "Assessoria de Imprensa – Flor de Lis",
                     "Use `a - b` no código."):
            self.assertEqual(check.aside_dashes(text), [], text)

    def test_tag_allows_kept_dashes_but_not_new_ones(self):
        case = {"tags": ["[TRAVESSAO: OK]"]}
        src = "O time — cansado — recusou."
        self.assertNotIn("dashes", check.check(src, src, case)["failures"])
        worse = "O time — cansado — recusou — e saiu."
        self.assertIn("dashes", check.check(src, worse, case)["failures"])
        self.assertIn("dashes", check.check(src, src, {})["failures"])


class Protected(unittest.TestCase):
    SRC = ('Segundo a diretora, "a meta é dobrar até 2026". Veja https://ex.com/a e fale com '
           'ana@ex.com.br ou @time_dados. #dados Rode `make test`. P&D cresceu 12%.')

    def test_spans_are_found(self):
        spans = check.protected_spans(self.SRC, {"protected": ["P&D"]})
        for s in ('"a meta é dobrar até 2026"', "https://ex.com/a", "ana@ex.com.br",
                  "@time_dados", "#dados", "`make test`", "P&D"):
            self.assertIn(s, spans)
        self.assertNotIn("@ex", spans)

    def test_changed_quote_fails(self):
        out = self.SRC.replace("dobrar", "duplicar")
        r = check.check(self.SRC, out, {"protected": ["P&D"]})
        self.assertIn("protected", r["failures"])

    def test_curly_to_straight_quotes_is_fine(self):
        src = "Ela disse “vamos juntos nessa” e saiu."
        out = 'Ela disse "vamos juntos nessa" e saiu.'
        self.assertEqual(check.missing_protected(src, out), [])


class Numbers(unittest.TestCase):
    def test_missing_and_added(self):
        missing, added = check.number_diff("Foram 1.200 clientes em 2024, cerca de 30%.",
                                           "Foram 1.300 clientes em 2024, cerca de 30%.")
        self.assertEqual(missing, ["1.200"])
        self.assertEqual(added, ["1.300"])

    def test_identical_numbers_pass(self):
        src = "Das 9h às 18h, 3 turnos."
        self.assertEqual(check.number_diff(src, "3 turnos, das 9h às 18h."), ([], []))


class Preamble(unittest.TestCase):
    def test_found(self):
        self.assertTrue(check.preamble("Aqui está o texto:\n\nO time recusou."))
        self.assertTrue(check.preamble("O time recusou.\n\nSe quiser, posso ajustar o tom."))

    def test_plain_text_is_clean(self):
        self.assertEqual(check.preamble("O time recusou.\n\nVoltamos na segunda."), [])


class FaltaFonte(unittest.TestCase):
    def test_expected_line(self):
        src = "Especialistas afirmam que 70% das empresas vão adotar IA."
        case = {"expect": {"falta_fonte": True}}
        self.assertIn("falta_fonte_missing", check.check(src, src, case)["failures"])
        out = src + "\n\nFalta fonte: Especialistas afirmam"
        self.assertNotIn("falta_fonte_missing", check.check(src, out, case)["failures"])

    def test_marker_inside_text_does_not_hide_the_rest(self):
        src = "O time recusou o plano."
        out = "Falta fonte: nada. Aqui está o texto — reescrito — sem mudar."
        r = check.check(src, out)
        self.assertFalse(r["falta_fonte"])
        self.assertIn("dashes", r["failures"])


class Evasion(unittest.TestCase):
    def test_quotes_added_by_output_do_not_exempt_dashes(self):
        src = "O time recusou o plano."
        out = 'O time "recusou — sem pensar — o plano".'
        self.assertIn("dashes", check.check(src, out)["failures"])


class Clean(unittest.TestCase):
    def test_good_rewrite_has_no_failures(self):
        src = ("No mundo atual, vale ressaltar que a equipe — já sobrecarregada — entregou "
               "o projeto em 3 semanas, com 98% dos testes aprovados!!")
        out = "A equipe, já sobrecarregada, entregou o projeto em 3 semanas, com 98% dos testes aprovados."
        r = check.check(src, out)
        self.assertEqual(r["failures"], [])
        self.assertLess(r["length_ratio"], 1)


if __name__ == "__main__":
    unittest.main()
