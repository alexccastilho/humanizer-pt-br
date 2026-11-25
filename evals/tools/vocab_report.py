"""Report on the vocabulary list of §4: which suspects still show up in what current
models write, and which new expressions are candidates for the list.

It reads the reference list in evals/suspeitos.md (the list the skill carried up to v2.0).
Three sources are counted:
  generated   texts written by the models (evals/corpus/generated.jsonl), by generator
  baseline    what the models leave behind when asked to humanize without the skill
              (runs of the baseline arm, if a bench folder is given)
  human       texts written by people (evals/corpus/human/*.json), the reference

A suspect that no current model uses is a candidate to drop. An expression frequent in
model text and in baseline output but rare in human text is a candidate to add. Nothing
is changed automatically: the report is input for a human edit of SKILL.md.

Usage:
  python evals/tools/vocab_report.py [--bench ../humanizer-bench] [--top 30]
Author: Alex Camacho Castilho
"""
import argparse
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SUSPECTS = ROOT / "evals" / "suspeitos.md"
STOP = set("a o e de da do das dos em no na nos nas um uma uns umas que se por para com como mais mas "
           "ao aos à às é são foi ser ter tem seu sua seus suas nosso nossa isso essa esse este esta "
           "já não sim também ou entre sobre até quando onde muito pelo pela pelos pelas lhe eles elas "
           "você vocês nós eu ele ela the of".split())


def suspects():
    terms = []
    for line in SUSPECTS.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- ") or ":" not in line or line.startswith("- Connectors"):
            continue
        body = line.split(":", 1)[1]
        body = re.sub(r"\([^)]*\)", "", body).split(" with no ")[0]
        for t in re.split(r"[,;]", body):
            t = t.strip().strip('"').strip().lower()
            if not t or len(t) >= 40:
                continue
            head, _, alts = t.rpartition(" ")
            for alt in alts.split("/"):  # "vale ressaltar/destacar", "cenário/panorama"
                terms.append(f"{head} {alt}".strip())
    return terms


def stem_rx(term):
    """Loose match: verb and adjective endings vary (mergulhar, mergulhando, robustas)."""
    words = term.split()
    last = words[-1]
    root = re.sub(r"(ar|er|ir|o|a|os|as|e|es)$", "", last) if len(last) > 5 else last
    return re.compile(r"\b" + r"\s+".join(map(re.escape, words[:-1] + [root])) + r"\w*\b", re.I)


def per10k(count, words):
    return round(10000 * count / words, 2) if words else 0.0


def ngrams(text, n):
    toks = re.findall(r"[a-záàâãéêíóôõúç]+", text.lower())
    for i in range(len(toks) - n + 1):
        g = toks[i:i + n]
        if g[0] in STOP or g[-1] in STOP:
            continue
        yield " ".join(g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default=None)
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    gen = [json.loads(l) for l in (ROOT / "evals/corpus/generated.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    sources = collections.defaultdict(list)
    for c in gen:
        # Slop texts were prompted to imitate chatbot habits, so they are counted apart:
        # only the natural ones show what current models do on their own.
        sources[f"gerado {c['origin'][3:]}:{c['generator'].replace('claude-', '')}"].append(c["text"])
    human_dir = ROOT / "evals/corpus/human"
    for f in sorted(human_dir.glob("*.json")) if human_dir.is_dir() else []:
        sources["humano"] += [c["text"] for c in json.loads(f.read_text(encoding="utf-8"))]
    if args.bench:
        for f in pathlib.Path(args.bench, "runs", "baseline").glob("*.json"):
            sources["baseline (após humanizar sem skill)"].append(json.loads(f.read_text(encoding="utf-8")).get("output", ""))

    joined = {k: "\n".join(v) for k, v in sources.items()}
    nwords = {k: len(re.findall(r"\w+", v)) for k, v in joined.items()}
    terms = suspects()
    print(f"# Relatório de vocabulário ({len(terms)} suspeitos lidos de {SUSPECTS.relative_to(ROOT)})\n")
    print("Ocorrências por 10 mil palavras.\n")
    cols = sorted(joined)
    print("| Suspeito | " + " | ".join(cols) + " |")
    print("|---|" + "---|" * len(cols))
    unused = []
    for t in terms:
        rx = stem_rx(t)
        vals = [per10k(len(rx.findall(joined[c])), nwords[c]) for c in cols]
        if not any(vals[i] for i, c in enumerate(cols) if c.startswith("gerado natural") or c.startswith("baseline")):
            unused.append(t)
        print(f"| {t} | " + " | ".join(str(v) for v in vals) + " |")
    print(f"\nSuspeitos que nenhum modelo atual usou por conta própria neste corpus (texto natural e saída do baseline) ({len(unused)}): {', '.join(unused) or 'nenhum'}")
    print("Candidatos a sair da lista, se o mesmo acontecer em outro corpus.\n")

    ai = collections.Counter()
    for k, v in joined.items():
        if k.startswith("gerado") or k.startswith("baseline"):
            for n in (2, 3):
                ai.update(ngrams(v, n))
    hum = collections.Counter()
    if "humano" in joined:
        for n in (2, 3):
            hum.update(ngrams(joined["humano"], n))
    known = [stem_rx(t) for t in terms]
    print(f"## Expressões frequentes em texto de modelo e ausentes da lista (top {args.top})\n")
    if not hum:
        print("Sem textos humanos em evals/corpus/human/: a lista abaixo não tem referência e pode incluir expressões comuns do tema.\n")
    shown = 0
    for g, c in ai.most_common(2000):
        if c < 4 or any(rx.search(g) for rx in known) or hum.get(g, 0) >= c / 4:
            continue
        print(f"- {g} ({c} no texto de modelo, {hum.get(g, 0)} no humano)")
        shown += 1
        if shown >= args.top:
            break


if __name__ == "__main__":
    main()
