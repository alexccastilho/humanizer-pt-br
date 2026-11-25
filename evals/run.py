"""Run the corpus through Claude Code under each condition ("arm").

Arms:
  baseline   the user's request alone, no skill
  minimal    the request plus a two-line instruction a user could write themselves
  skill      the request, with the skill loaded as a plugin (it must trigger by itself)
  novocab    as skill, but with the vocabulary list of §4 removed (ablation)
  cand       a candidate version of the skill (--cand-dir), to compare with the current one

Every arm gets the exact same user message. The plugin is exported to a folder outside
the repository, so a run cannot read the corpus, the judge prompts or the results.

Usage:
  python evals/run.py --out <folder outside the repo> --split dev|holdout|all
      [--arms baseline,minimal,skill,novocab] [--reps 1] [--model sonnet] [--jobs 4]
      [--skill-dir <released skill folder>] [--cand-dir skills/humanizer-token-optimizer-pt-br]

Results: <out>/runs/<arm>/<case>__r<rep>.json (resumable: finished runs are skipped).
Author: Alex Camacho Castilho
"""
import argparse
import concurrent.futures
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from claude_cli import long_path, run_claude  # noqa: E402
from check import check  # noqa: E402

MINIMAL = ("Ao reescrever texto em português, remova marcas de escrita de IA (travessões usados como aparte, "
           "clichês, fórmulas e enchimento) e use voz natural. Não acrescente, altere nem remova fatos, números, "
           "nomes, citações ou ressalvas, e entregue só o texto reescrito.")

ARMS = ("baseline", "minimal", "skill", "novocab", "cand")


def load_corpus(split):
    cases = []
    gen = HERE / "corpus" / "generated.jsonl"
    if gen.exists():
        cases += [json.loads(l) for l in gen.read_text(encoding="utf-8").splitlines() if l.strip()]
    cases += json.loads((HERE / "corpus" / "handmade.json").read_text(encoding="utf-8"))
    human = HERE / "corpus" / "human"
    if human.is_dir():
        for f in sorted(human.glob("*.json")):
            cases += json.loads(f.read_text(encoding="utf-8"))
    return [c for c in cases if split == "all" or c["split"] == split]


def user_message(case):
    return f"{case['request']}\n\n{case['text']}"


def strip_vocabulary(skill_md):
    """Remove the vocabulary block of §4 (from **Vocabulary.** up to **Structure.**)."""
    out, n = re.subn(r"\*\*Vocabulary\.\*\*.*?(?=\*\*Structure\.\*\*)", "", skill_md, flags=re.S)
    if n != 1:
        raise SystemExit("novocab: vocabulary block not found in SKILL.md")
    return out


def export_plugin(out, skill_dir, arm):
    """Copy manifest and skill to <out>/_plugin_<arm>, outside the repository."""
    dest = pathlib.Path(long_path(out)) / f"_plugin_{arm}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ROOT / ".claude-plugin", dest / ".claude-plugin")
    name = pathlib.Path(skill_dir).name
    shutil.copytree(skill_dir, dest / "skills" / name)
    if arm == "novocab":
        p = dest / "skills" / name / "SKILL.md"
        p.write_text(strip_vocabulary(p.read_text(encoding="utf-8")), encoding="utf-8")
    return dest


def run_one(case, arm, rep, args, plugins):
    dest = pathlib.Path(args.out) / "runs" / arm / f"{case['id']}__r{rep}.json"
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    res = run_claude(user_message(case), model=args.model, plugin_dir=plugins.get(arm),
                     system_append=MINIMAL if arm == "minimal" else None)
    output = (res.get("result") or "").strip()
    rec = {"case": case["id"], "split": case["split"], "arm": arm, "rep": rep, "model": args.model,
           "output": output, "check": check(case["text"], output, case) if output else None, **res}
    rec.pop("result", None)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    u = res.get("usage") or {}
    print(f"{arm:8} {case['id']:24} r{rep} skill={bool(res.get('skill_calls'))} "
          f"out={u.get('output_tokens')} fails={(rec['check'] or {}).get('failures')}", flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="dev", choices=["dev", "holdout", "all"])
    ap.add_argument("--arms", default="baseline,minimal,skill,novocab")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--cases", default="", help="comma-separated case ids (default: all in split)")
    default_skill = next(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
    ap.add_argument("--skill-dir", default=str(default_skill))
    ap.add_argument("--cand-dir", default=str(default_skill))
    args = ap.parse_args()
    out = pathlib.Path(long_path(args.out))
    if ROOT in out.parents or out == ROOT:
        raise SystemExit("--out must be outside the repository")
    out.mkdir(parents=True, exist_ok=True)
    args.out = str(out)
    arms = [a for a in args.arms.split(",") if a]
    dirs = {"skill": args.skill_dir, "novocab": args.skill_dir, "cand": args.cand_dir}
    plugins = {a: str(export_plugin(out, dirs[a], a)) for a in arms if a in dirs}
    cases = load_corpus(args.split)
    if args.cases:
        wanted = set(args.cases.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    jobs = [(c, a, r) for r in range(1, args.reps + 1) for c in cases for a in arms]
    print(f"{len(cases)} casos x {len(arms)} braços x {args.reps} rep = {len(jobs)} execuções", flush=True)
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
        list(ex.map(lambda j: run_one(*j, args, plugins), jobs))


if __name__ == "__main__":
    main()
