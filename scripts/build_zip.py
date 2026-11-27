"""Gera dist/<skill>.zip para upload no claude.ai.

O ZIP contém a pasta da skill no topo (<skill>/SKILL.md), com separadores "/" e fim de
linha LF em qualquer sistema operacional. Cada entrada leva data fixa (1980-01-01) e
permissões fixas: a mesma máquina gera sempre o mesmo arquivo, byte a byte, e no Windows
e no Linux o conteúdo e os metadados são os mesmos. (Os bytes comprimidos dependem da
zlib de cada Python e podem variar entre instalações.)

Uso: python scripts/build_zip.py [--out dist]
Autor: Alex Camacho Castilho
"""
import argparse
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEXT = {".md", ".txt", ".json", ".py", ".yml", ".yaml"}
FIXED_DATE = (1980, 1, 1, 0, 0, 0)  # the earliest date a ZIP entry can hold


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
            info = zipfile.ZipInfo(arc, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix, so the attributes below mean the same everywhere
            info.external_attr = 0o100644 << 16  # regular file, rw-r--r--
            zf.writestr(info, data)
    print(out)


if __name__ == "__main__":
    main()
