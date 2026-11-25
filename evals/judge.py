"""Blind pairwise judge: which of two rewrites of the same text is better, and what each
got wrong on fidelity.

The judge never sees arm names. A/B order is drawn per (case, rep, pair) from a hash, so
it is random across cases but stable between runs. The judge runs isolated, like the
arms (see claude_cli.py), on a stronger model than the one under test.

Usage:
  python evals/judge.py --out <same folder as run.py> [--pairs skill:baseline,skill:minimal,skill:novocab]
      [--model opus] [--jobs 4] [--split holdout]

Results: <out>/judgments/<a>_vs_<b>/<case>__r<rep>.json
Author: Alex Camacho Castilho
"""
import argparse
import concurrent.futures
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from claude_cli import run_claude  # noqa: E402
from run import load_corpus  # noqa: E402

PROMPT = """Você é um editor brasileiro experiente. Avalie duas reescritas do mesmo texto, feitas a pedido de um usuário.

PEDIDO DO USUÁRIO:
{request}

TEXTO ORIGINAL:
<<<
{source}
>>>

REESCRITA A:
<<<
{a}
>>>

REESCRITA B:
<<<
{b}
>>>

Critérios, nesta ordem de peso:
1. Fidelidade. Para cada reescrita, liste os erros: fato, número, nome, data ou citação acrescentado, alterado ou removido; ressalva ("pode", "cerca de", "até") removida ou afirmação mais forte ou mais fraca que no original; informação relevante perdida; trecho que deveria ser copiado igual (citação, código, URL, @menção, #hashtag, marca) alterado. Cortar enchimento que não informa nada NÃO é erro. Uma linha extra "Falta fonte: ..." apontando atribuição vaga NÃO é erro.
2. Atendimento ao pedido: só o texto pedido, sem comentário antes ou depois; respeito a tags como [CASUAL], [FORMAL], [ESTRUTURA], [TRAVESSAO: OK]; diagnóstico em vez de reescrita quando o usuário pediu só diagnóstico; manter pt-PT, diálogo de ficção e estrutura de passo a passo quando for o caso.
3. Naturalidade: soa como texto escrito por uma pessoa brasileira no canal do pedido, sem marcas de IA (travessão como aparte, clichês, "não é X, é Y", tríade decorativa, pergunta retórica, abertura ou fechamento genérico) e sem exagero na correção (gíria forçada, frases picotadas, texto já bom reescrito sem necessidade).

Um erro de fidelidade pesa mais que qualquer diferença de estilo. Declare empate só se as duas forem equivalentes.

Responda APENAS com um objeto JSON, sem cercas de código:
{{"fidelidade_A": ["..."], "fidelidade_B": ["..."], "pedido_A": true, "pedido_B": true, "naturalidade_A": 7, "naturalidade_B": 7, "vencedor": "A", "motivo": "uma frase"}}
"""


def swap(case_id, rep, pair):
    return int(hashlib.sha256(f"{case_id}|{rep}|{pair}".encode()).hexdigest(), 16) % 2 == 1


def parse_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def judge_one(case, rep, x, y, out, model):
    pair = f"{x}_vs_{y}"
    dest = out / "judgments" / pair / f"{case['id']}__r{rep}.json"
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    rx = out / "runs" / x / f"{case['id']}__r{rep}.json"
    ry = out / "runs" / y / f"{case['id']}__r{rep}.json"
    if not (rx.exists() and ry.exists()):
        return None
    ox = json.loads(rx.read_text(encoding="utf-8")).get("output", "")
    oy = json.loads(ry.read_text(encoding="utf-8")).get("output", "")
    flipped = swap(case["id"], rep, pair)
    a, b = (oy, ox) if flipped else (ox, oy)
    verdict = None
    for _ in range(2):
        res = run_claude(PROMPT.format(request=case["request"], source=case["text"], a=a, b=b), model=model)
        verdict = parse_json(res.get("result"))
        if verdict and verdict.get("vencedor") in ("A", "B", "empate"):
            break
    if not verdict:
        print("FAIL judge", pair, case["id"], rep, file=sys.stderr)
        return None
    side = {"A": y if flipped else x, "B": x if flipped else y}
    winner = {"A": side["A"], "B": side["B"], "empate": "tie"}[verdict["vencedor"]]
    rec = {
        "case": case["id"], "rep": rep, "pair": pair, "x": x, "y": y, "flipped": flipped,
        "winner": winner, "position_winner": verdict["vencedor"],
        "fidelity": {side["A"]: verdict.get("fidelidade_A", []), side["B"]: verdict.get("fidelidade_B", [])},
        "request_ok": {side["A"]: verdict.get("pedido_A"), side["B"]: verdict.get("pedido_B")},
        "naturalness": {side["A"]: verdict.get("naturalidade_A"), side["B"]: verdict.get("naturalidade_B")},
        "reason": verdict.get("motivo"), "judge_model": model,
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{pair:20} {case['id']:24} r{rep} -> {winner}", flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", default="skill:baseline,skill:minimal,skill:novocab")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--split", default="all")
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    pairs = [tuple(p.split(":")) for p in args.pairs.split(",") if p]
    jobs = [(c, r, x, y) for c in load_corpus(args.split) for r in range(1, args.reps + 1) for x, y in pairs]
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
        list(ex.map(lambda j: judge_one(*j, out, args.model), jobs))


if __name__ == "__main__":
    main()
