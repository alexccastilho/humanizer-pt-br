"""Aggregate runs and judgments into a report, and apply the release gates.

Usage:
  python evals/analyze.py --out <bench folder> --split holdout --report evals/results/<version>

Writes <report>/summary.md and <report>/summary.json. The gates are the ones in
evals/README.md, fixed before the first run.
Author: Alex Camacho Castilho
"""
import argparse
import collections
import json
import math
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check import check  # noqa: E402
from run import load_corpus  # noqa: E402

HARD = ("protected", "numbers_missing", "numbers_added", "dashes", "preamble", "punctuation",
        "falta_fonte_missing")


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def load(out, sub, split_ids):
    recs = []
    for f in (out / sub).rglob("*.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("case") in split_ids:
            recs.append(r)
    return recs


def tokens_in(u):
    return (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)


def arm_stats(runs, cases):
    by = collections.defaultdict(list)
    for r in runs:
        # Re-check with the current checker, so a checker fix applies to old runs too.
        r["check"] = check(cases[r["case"]]["text"], r["output"], cases[r["case"]]) if r.get("output") else None
        by[r["arm"]].append(r)
    stats = {}
    for arm, rs in sorted(by.items()):
        rewrite = [r for r in rs if r.get("check") and cases[r["case"]].get("expect", {}).get("mode") != "diagnosis"]
        fails = collections.Counter(f for r in rewrite for f in r["check"]["failures"])
        unchanged = [r["check"]["similarity"] for r in rewrite if cases[r["case"]].get("expect", {}).get("unchanged")]
        ai = [r["check"]["length_ratio"] for r in rewrite if cases[r["case"]]["origin"].startswith("ai-")]
        st = {
            "runs": len(rs),
            "empty": sum(1 for r in rs if not r.get("output")),
            "skill_triggered": sum(1 for r in rs if r.get("skill_calls")),
            "failures": {k: fails.get(k, 0) for k in HARD + ("falta_fonte_spurious",)},
            "rewrites": len(rewrite),
            "runs_with_any_failure": sum(1 for r in rewrite if r["check"]["failures"]),
            "dashes_output_total": sum(r["check"]["dashes_output"] for r in rewrite),
            "length_ratio_ai_median": round(statistics.median(ai), 3) if ai else None,
            "similarity_clean_median": round(statistics.median(unchanged), 3) if unchanged else None,
            "input_tokens_median": statistics.median([tokens_in(r.get("usage") or {}) for r in rs]) if rs else None,
            "output_tokens_median": statistics.median([(r.get("usage") or {}).get("output_tokens") or 0 for r in rs]) if rs else None,
            "cost_usd_mean": round(statistics.mean([r.get("cost_usd") or 0 for r in rs]), 5) if rs else None,
            "output_words_median": statistics.median([r["check"]["words_output"] for r in rewrite]) if rewrite else None,
        }
        stats[arm] = st
    return stats


def pair_stats(judgments):
    by = collections.defaultdict(list)
    for j in judgments:
        by[j["pair"]].append(j)
    res = {}
    fid = collections.defaultdict(list)
    nat = collections.defaultdict(list)
    for pair, js in sorted(by.items()):
        x, y = js[0]["x"], js[0]["y"]
        wx = sum(1 for j in js if j["winner"] == x)
        wy = sum(1 for j in js if j["winner"] == y)
        ties = sum(1 for j in js if j["winner"] == "tie")
        p, lo, hi = wilson(wx, wx + wy)
        pos_a = sum(1 for j in js if j["position_winner"] == "A")
        res[pair] = {"x": x, "y": y, "n": len(js), "wins_x": wx, "wins_y": wy, "ties": ties,
                     "win_rate_x": round(p, 3), "ci95": [round(lo, 3), round(hi, 3)],
                     "position_A_wins": pos_a, "position_B_wins": sum(1 for j in js if j["position_winner"] == "B")}
        for j in js:
            for arm, errs in j["fidelity"].items():
                fid[arm].append(len(errs or []))
            for arm, v in j["naturalness"].items():
                if isinstance(v, (int, float)):
                    nat[arm].append(v)
    fidelity = {a: {"mean_errors": round(statistics.mean(v), 3), "outputs_with_error": round(sum(1 for e in v if e) / len(v), 3), "n": len(v)} for a, v in fid.items()}
    naturalness = {a: round(statistics.mean(v), 2) for a, v in nat.items()}
    return res, fidelity, naturalness


def gates(arms, pairs, fidelity):
    g = {}
    s = arms.get("skill", {})
    b = arms.get("baseline", {})
    g["G1 trechos protegidos intactos (skill)"] = s.get("failures", {}).get("protected", 1) == 0
    nb = b.get("failures", {})
    ns = s.get("failures", {})
    g["G2 números: skill não pior que baseline"] = (ns.get("numbers_missing", 0) + ns.get("numbers_added", 0)) <= (nb.get("numbers_missing", 0) + nb.get("numbers_added", 0))
    g["G3 fidelidade (juiz): skill não pior que baseline"] = fidelity.get("skill", {}).get("mean_errors", 9) <= fidelity.get("baseline", {}).get("mean_errors", 0)
    sb = pairs.get("skill_vs_baseline")
    g["G4 preferência skill x baseline >= 60% e IC acima de 50%"] = bool(sb and sb["win_rate_x"] >= 0.60 and sb["ci95"][0] > 0.50)
    sm = pairs.get("skill_vs_minimal")
    g["G5 skill não perde do prompt mínimo (IC superior >= 50%)"] = bool(sm and sm["ci95"][1] >= 0.50)
    tok = s.get("cost_usd_mean") is not None and b.get("cost_usd_mean") is not None and s["cost_usd_mean"] <= b["cost_usd_mean"]
    g["T economia de tokens real (custo médio skill <= baseline)"] = tok
    return g


def render(split, arms, pairs, fidelity, naturalness, g):
    L = [f"# Resultado do benchmark ({split})", ""]
    L += ["## Checagens determinísticas por braço", "",
          "| Braço | Execuções | Acionou skill | Com alguma falha | Protegidos | Nº sumiu | Nº novo | Travessão | Preâmbulo | Falta fonte ausente | Tamanho (IA, mediana) | Similaridade texto bom | Tokens entrada (med.) | Tokens saída (med.) | Custo médio US$ |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a, s in arms.items():
        f = s["failures"]
        L.append(f"| {a} | {s['runs']} | {s['skill_triggered']} | {s['runs_with_any_failure']}/{s['rewrites']} | {f['protected']} | {f['numbers_missing']} | {f['numbers_added']} | {f['dashes']} | {f['preamble']} | {f['falta_fonte_missing']} | {s['length_ratio_ai_median']} | {s['similarity_clean_median']} | {s['input_tokens_median']} | {s['output_tokens_median']} | {s['cost_usd_mean']} |")
    L += ["", "## Preferência do juiz cego", "", "| Par | n | Vitórias 1º | Vitórias 2º | Empates | Taxa 1º (sem empates) | IC 95% | Venceu posição A/B |", "|---|---|---|---|---|---|---|---|"]
    for p, s in pairs.items():
        L.append(f"| {s['x']} x {s['y']} | {s['n']} | {s['wins_x']} | {s['wins_y']} | {s['ties']} | {s['win_rate_x']:.0%} | {s['ci95'][0]:.0%} a {s['ci95'][1]:.0%} | {s['position_A_wins']}/{s['position_B_wins']} |")
    L += ["", "## Fidelidade e naturalidade (juiz)", "", "| Braço | Erros de fidelidade por saída | Saídas com erro | Naturalidade média (1-10) |", "|---|---|---|---|"]
    for a in sorted(fidelity):
        L.append(f"| {a} | {fidelity[a]['mean_errors']} | {fidelity[a]['outputs_with_error']:.0%} | {naturalness.get(a, '')} |")
    L += ["", "## Critérios de decisão", ""]
    L += [f"- {'PASSOU' if v else 'FALHOU'}: {k}" for k, v in g.items()]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="holdout")
    ap.add_argument("--report", required=True)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    cases = {c["id"]: c for c in load_corpus(args.split)}
    runs = load(out, "runs", cases)
    judgments = load(out, "judgments", cases)
    arms = arm_stats(runs, cases)
    pairs, fidelity, naturalness = pair_stats(judgments)
    g = gates(arms, pairs, fidelity)
    rep = pathlib.Path(args.report)
    rep.mkdir(parents=True, exist_ok=True)
    (rep / "summary.json").write_text(json.dumps({"split": args.split, "arms": arms, "pairs": pairs, "fidelity": fidelity, "naturalness": naturalness, "gates": g}, ensure_ascii=False, indent=1), encoding="utf-8")
    md = render(args.split, arms, pairs, fidelity, naturalness, g)
    (rep / "summary.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
