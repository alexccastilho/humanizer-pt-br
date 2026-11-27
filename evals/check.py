"""Deterministic checks for one rewrite: what a script can verify without a judge.

check(source, output, case) returns a dict of findings. Nothing here calls a model,
so it runs in CI and gives the same answer every time.

What it checks:
  protected   every protected span (declared in the case, plus URLs, e-mails, @mentions,
              #hashtags, inline code and quoted text found in the source) appears verbatim
              in the rewritten text (the trailing "Falta fonte:" line does not count)
  numbers     every number in the source is still there, and no new number appeared;
              a number repeated fewer times than in the source is reported, not failed
  dashes      dashes used as an aside or pause in prose, list items and headings
              (travessão, meia-risca, spaced hyphen); with the [TRAVESSAO: OK] tag, the
              output may not have more than the source
  preamble    chatbot opening or closing ("Aqui está", "Se quiser, posso...")
  punctuation "!!", "?!", more than one "!" per block, arrows, inline bullets and "&"
              standing in for "e" in prose
  falta_fonte the "Falta fonte:" line, when the case expects it
  length      word ratio output/source; similarity for texts that should barely change

Standard library only, Python 3.8+.
Author: Alex Camacho Castilho
"""
import collections
import difflib
import re

DASHES = "—–"  # travessão, meia-risca

URL = re.compile(r"https?://\S+|www\.\S+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MENTION = re.compile(r"(?<![\w@])@\w[\w.]*\w|(?<![\w@])@\w")
HASHTAG = re.compile(r"(?<![\w&])#\w+")
CODE = re.compile(r"`[^`\n]+`")
FENCE = re.compile(r"```.*?```", re.S)
QUOTE = re.compile(r"“[^”\n]{3,}”|\"[^\"\n]{3,}\"")
NUMBER = re.compile(r"(?<![\w])\d+(?:[.,:]\d+)*(?:\s?%)?")

PREAMBLE_START = re.compile(
    r"^\s*(aqui est[áa]|segue(m)?\b|claro[!,.]|pronto[!,.]|com certeza|ótim[oa]|excelente|"
    r"vou (reescrever|humanizar)|reescrevi|abaixo|versão humanizada|texto humanizado)",
    re.I)
PREAMBLE_END = re.compile(
    r"(se quiser[^\n]{0,80}(posso|ajust|é só)|posso ajustar|espero ter ajudado|quer que eu|"
    r"me (diga|avise) se|caso queira|fico à disposição para ajustar)[^\n]*\s*$",
    re.I)

LIST_MARKER = re.compile(r"^\s*([-*•]|\d+[.)])\s")
DIALOGUE = re.compile(r"^\s*[—–]\s*\S")
# "Nome - Cargo", "Assessoria – Empresa", "Contato - 11 9999-0000": a single dash, and
# what follows starts with a capital or a digit. A lowercase continuation is prose.
LABEL = re.compile(r"^[^.!?\n–—]{1,60}\s[-–—]\s[A-ZÀ-Ý0-9][^.!?\n–—]{0,60}$")
HEADING = re.compile(r"^#{1,6}\s+")
AMPERSAND = re.compile(r"\S\s&\s[a-zà-ÿ]")  # "vendas & marketing"; "Johnson & Johnson" is a name
URL_TRAIL = ".,;:!?)"
RANGE = re.compile(r"\d\s?[-–—]\s?\d")


def _strip_fences(text):
    return FENCE.sub(" ", text)


def protected_spans(source, case=None):
    """Spans that must be copied verbatim: declared ones plus those found by pattern."""
    spans = list((case or {}).get("protected", []))
    body = _strip_fences(source)
    for rx in (URL, EMAIL, CODE, QUOTE):
        spans += [m.group(0).rstrip(URL_TRAIL) if rx is URL else m.group(0) for m in rx.finditer(body)]
    for rx in (MENTION, HASHTAG):
        spans += [m.group(0) for m in rx.finditer(EMAIL.sub(" ", URL.sub(" ", body)))]
    for block in FENCE.findall(source):
        spans.append(block.strip("`").strip())
    seen, out = set(), []
    for s in spans:
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _norm_quotes(text):
    return (text.replace("“", '"').replace("”", '"')
            .replace("‘", "'").replace("’", "'").replace("…", "..."))


def missing_protected(source, output, case=None):
    """Protected spans absent from the output. Curly vs straight quotes and the ellipsis
    character count as the same span, since the skill may normalize them on digital
    channels; everything else must match exactly."""
    out_n = _norm_quotes(output)
    return [s for s in protected_spans(source, case) if s not in output and _norm_quotes(s) not in out_n]


def numbers(text):
    vals = []
    for m in NUMBER.finditer(_strip_fences(text)):
        v = m.group(0).replace(" ", "")
        vals.append(v)
    return vals


def number_diff(source, output):
    """(missing, added): numbers of the source not in the output, and new ones."""
    src, out = numbers(source), numbers(output)
    missing = [n for n in dict.fromkeys(src) if n not in out]
    added = [n for n in dict.fromkeys(out) if n not in src]
    return missing, added


def number_count_changed(source, output):
    """Numbers kept in the output but repeated fewer times than in the source ("10 e 10"
    -> "10"). Reported for review, not failed: merging a repeated year is often a fair
    edit, losing one of two equal quantities is not, and only a reader can tell."""
    src, out = collections.Counter(numbers(source)), collections.Counter(numbers(output))
    return [n for n in src if 0 < out[n] < src[n]]


def _prose_lines(text, case=None, lists=True):
    """Lines of prose, with list markers and heading marks taken off so the text of a
    list item or heading is checked too (lists=False leaves list items out). Skipped:
    code, tables, block quotes, fiction dialogue and labels ("Nome - Cargo")."""
    lines = []
    for line in _strip_fences(text).splitlines():
        s = line.strip()
        if not s or DIALOGUE.match(s) or s.startswith(("|", ">")):
            continue
        if not lists and LIST_MARKER.match(s):
            continue
        s = HEADING.sub("", LIST_MARKER.sub("", s, count=1), count=1).strip()
        if not s or LABEL.match(s):
            continue
        lines.append(s)
    return lines


def aside_dashes(text, case=None, spans=None):
    """Dashes used as aside, pause or emphasis in prose. Ranges (10-20, 2020–2024),
    compounds (segunda-feira) and protected spans do not count. Pass the spans of the
    source when checking an output, so text the output itself puts in quotes is not
    exempted."""
    hits = []
    spans = protected_spans(text, case) if spans is None else spans
    for line in _prose_lines(text, case):
        clean = line
        for s in spans:
            clean = clean.replace(s, " ")
        clean = RANGE.sub(" ", clean)
        for m in re.finditer(r"\s[-–—]\s|[–—]", clean):
            hits.append(clean[max(0, m.start() - 15):m.end() + 15].strip())
    return hits


def preamble(output):
    lines = [l for l in output.strip().splitlines() if l.strip()]
    if not lines:
        return []
    found = []
    if PREAMBLE_START.search(lines[0]):
        found.append(lines[0][:80])
    last = lines[-1]
    if len(lines) == 1:
        # One-line answer: only a closing sentence after the text counts, so a text that
        # is itself one sentence ("Caso queira participar, ...") is not flagged.
        sentences = re.split(r"(?<=[.!?])\s+", last.strip())
        last = sentences[-1] if len(sentences) > 1 else ""
    if last and PREAMBLE_END.search(last):
        found.append(last[:80])
    return found


def punctuation(output, spans=()):
    """Punctuation the skill removes from prose (§3). List items are left out, since an
    arrow in a step list ("Arquivo → Salvar") is not prose. Protected spans are taken out
    first, so a quote with "!" or a brand like "P&D" does not count."""
    blocks = []
    for b in re.split(r"\n\s*\n", _strip_fences(output)):
        text = "\n".join(_prose_lines(b, lists=False))
        for s in spans:
            text = text.replace(s, " ")
        blocks.append(text)
    prose = "\n".join(blocks)
    found = [t.strip() for t in ("!!", "?!", "→", " • ") if t in prose]
    if "!!" not in found and any(b.count("!") > 1 for b in blocks):
        found.append("!")
    if AMPERSAND.search(prose):
        found.append("&")
    return found


def words(text):
    return len(re.findall(r"\w+", text))


def similarity(a, b):
    return round(difflib.SequenceMatcher(None, a.split(), b.split()).ratio(), 3)


def check(source, output, case=None):
    """All deterministic findings for one rewrite. `failures` lists the hard ones."""
    case = case or {}
    tags = case.get("tags", [])
    expect = case.get("expect", {})
    # "Falta fonte:" counts only as trailing lines after the text, not anywhere inside it.
    m = re.search(r"(?:\n\s*Falta fonte:[^\n]*)+\s*$", output)
    body = output[:m.start()] if m else output
    missing, added = number_diff(source, body)
    # Spans must survive in the rewrite itself: one that only shows up in the trailing
    # "Falta fonte:" line was still dropped from the text.
    miss_prot = missing_protected(source, body, case)
    src_spans = protected_spans(source, case)
    src_d, out_d = aside_dashes(source, case, src_spans), aside_dashes(body, case, src_spans)
    pre = preamble(body)
    punct = punctuation(body, src_spans)
    has_ff = bool(m)
    r = {
        "protected_missing": miss_prot,
        "numbers_missing": missing,
        "numbers_added": added,
        "numbers_count_changed": number_count_changed(source, body),
        "dashes_source": len(src_d),
        "dashes_output": len(out_d),
        "dash_examples": out_d[:3],
        "preamble": pre,
        "punctuation": punct,
        "falta_fonte": has_ff,
        "words_source": words(source),
        "words_output": words(body),
        "length_ratio": round(words(body) / max(words(source), 1), 3),
        "similarity": similarity(source, body),
    }
    fails = []
    if miss_prot:
        fails.append("protected")
    if missing:
        fails.append("numbers_missing")
    if added:
        fails.append("numbers_added")
    keep = "[TRAVESSAO: OK]" in tags or expect.get("keep_dashes")
    if (keep and len(out_d) > len(src_d)) or (not keep and out_d):
        fails.append("dashes")
    if pre:
        fails.append("preamble")
    if punct:
        fails.append("punctuation")
    if expect.get("falta_fonte") and not has_ff:
        fails.append("falta_fonte_missing")
    if expect.get("falta_fonte") is False and has_ff:
        fails.append("falta_fonte_spurious")
    r["failures"] = fails
    return r
