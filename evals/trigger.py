"""Does the description trigger the skill when it should, and stay quiet when it should not?

Each request runs isolated with the skill loaded as a plugin (see claude_cli.py) and
records whether the Skill tool was called for this skill. The near misses are requests a
user might phrase the same way but that belong elsewhere: translation, grammar only,
watermarks, code, summaries.

Usage:
  python evals/trigger.py --out <bench folder> [--skill-dir <folder>] [--label cand] [--reps 1]
Author: Alex Camacho Castilho
"""
import argparse
import concurrent.futures
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from claude_cli import run_claude  # noqa: E402
from run import ROOT, export_plugin  # noqa: E402

TXT = "No mundo atual, vale ressaltar que a nossa equipe — robusta e inovadora — entregou o projeto em 3 semanas."

SHOULD = [
    f"Humaniza esse texto: {TXT}",
    f"Tira o jeito de IA disso aqui: {TXT}",
    f"Isso tá com muita cara de ChatGPT, arruma pra mim: {TXT}",
    f"Deixa mais natural pro LinkedIn: {TXT}",
    f"Tira os travessões e deixa fluido: {TXT}",
    f"Vão perceber que foi IA que escreveu, me ajuda: {TXT}",
    f"Melhora a redação desse parágrafo: {TXT}",
    f"Deixa esse texto mais informal pro WhatsApp: {TXT}",
    f"Não tá com a minha cara, reescreve: {TXT}",
    f"Deixa esse e-mail menos robótico: Prezado, venho por meio deste informar que a reunião — conforme alinhado — foi remarcada.",
]
SHOULD_NOT = [
    f"Traduz pro inglês: {TXT}",
    f"Corrige só a ortografia, sem mudar nada: Ontem nós fomos no mercado e compramo arroz.",
    "Remove a marca d'água e os metadados dessa imagem gerada por IA.",
    "Refatora essa função Python: def soma(a,b): return a+b",
    f"Resume em uma frase: {TXT}",
    "Escreve um poema sobre o mar.",
    "Qual a diferença entre travessão e hífen?",
    "Tem algum caractere Unicode invisível nesse texto? Olá​ mundo",
    f"Humanize this text, it's in English: Our team — robust and innovative — delivered in 3 weeks.",
    "Me explica o que é LGPD em poucas palavras.",
]


def classify(res, name):
    """fired is True/False when the run worked, None when it failed: a failed run says
    nothing about the description and must not count as "did not trigger"."""
    if res.get("is_error"):
        return {"fired": None, "error": res.get("error") or "is_error"}
    if "is_error" not in res:  # the CLI died before its final "result" event
        return {"fired": None, "error": f"sem resultado (exit {res.get('exit_code')}): {(res.get('stderr_tail') or '')[-120:]}"}
    return {"fired": any(name in (s or "") for s in res.get("skill_calls", [])), "error": None}


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--skill-dir", default=str(next(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())))
    ap.add_argument("--label", default="cand")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--reps", type=int, default=1, help="runs per request")
    return ap


def main():
    args = parser().parse_args()
    plugin = export_plugin(args.out, args.skill_dir, f"trigger_{args.label}")
    name = pathlib.Path(args.skill_dir).name
    jobs = [(q, exp, rep) for q, exp in [(q, True) for q in SHOULD] + [(q, False) for q in SHOULD_NOT]
            for rep in range(1, args.reps + 1)]

    def work(job):
        q, expected, rep = job
        res = run_claude(q, model=args.model, plugin_dir=plugin)
        return {"query": q, "expected": expected, "rep": rep, **classify(res, name)}

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(work, jobs))
    ok = [r for r in results if r["error"] is None]
    errors = [r for r in results if r["error"] is not None]
    pos = [r for r in ok if r["expected"]]
    neg = [r for r in ok if not r["expected"]]
    tp = sum(r["fired"] for r in pos)
    fp = sum(r["fired"] for r in neg)
    summary = {"label": args.label, "reps": args.reps, "should_fire": len(pos), "fired_when_should": tp,
               "should_not_fire": len(neg), "fired_when_should_not": fp, "errors": len(errors),
               "results": results}
    dest = pathlib.Path(args.out) / f"trigger_{args.label}.json"
    dest.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{args.label}: acionou {tp}/{len(pos)} quando devia, {fp}/{len(neg)} quando não devia")
    for r in ok:
        if r["fired"] != r["expected"]:
            print("  ERRO", "deveria" if r["expected"] else "não deveria", "|", r["query"][:90])
    if errors:
        print(f"  {len(errors)} execução(ões) falharam e ficaram fora da conta; rode de novo:", file=sys.stderr)
        for r in errors:
            print("  FALHA", r["error"], "|", r["query"][:90], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
