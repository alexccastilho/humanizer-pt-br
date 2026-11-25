"""Gera dist/<skill>.zip para upload no claude.ai.

O ZIP contém a pasta da skill no topo (<skill>/SKILL.md), com separadores "/" e fim de
linha LF em qualquer sistema operacional, para que o pacote gerado no Windows seja igual
ao gerado no Linux.

Uso: python scripts/build_zip.py [--out dist]
Autor: Alex Camacho Castilho
"""
import argparse
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEXT = {".md", ".txt", ".json", ".py", ".yml", ".yaml"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist"))
    args = ap.parse_args()
    skills = [p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()]
    if len(skills) != 1:
        raise SystemExit(f"esperada uma skill em skills/, achei {len(skills)}")
    src = skills[0]
    out = pathlib.Path(args.out) / f"{src.name}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            arc = f"{src.name}/{path.relative_to(src).as_posix()}"
            data = path.read_bytes()
            if path.suffix.lower() in TEXT:
                data = data.replace(b"\r\n", b"\n")
            zf.writestr(arc, data)
    print(out)


if __name__ == "__main__":
    main()
