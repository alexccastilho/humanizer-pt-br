"""Gera dist/humanizer-token-optimizer-pt-br.zip para upload no claude.ai.

O ZIP contém a pasta da skill no topo (humanizer-token-optimizer-pt-br/SKILL.md),
com separadores "/" independentemente do sistema operacional.

Uso: python scripts/build_zip.py
Autor: Alex Camacho Castilho
"""
import pathlib
import zipfile

NAME = "humanizer-token-optimizer-pt-br"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "skills" / NAME
OUT = ROOT / "dist" / f"{NAME}.zip"

OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(SRC.rglob("*")):
        if path.is_file():
            zf.write(path, f"{NAME}/{path.relative_to(SRC).as_posix()}")
print(OUT)
