#!/usr/bin/env python3
"""Valida as imagens estáticas referenciadas pelo catálogo SOLVERO."""
from pathlib import Path
from html.parser import HTMLParser
import sys

ROOT = Path(__file__).resolve().parents[1]

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            src = dict(attrs).get("src", "")
            if src and not src.startswith(("https://", "http://", "data:")):
                self.sources.append(src.split("?", 1)[0])

def valid_signature(path: Path) -> bool:
    with path.open("rb") as f:
        head = f.read(16)
    ext = path.suffix.lower()
    if ext == ".png":
        return head.startswith(bytes.fromhex('89504e470d0a1a0a'))
    if ext in (".jpg", ".jpeg"):
        return head.startswith(bytes.fromhex('ffd8ff'))
    if ext == ".webp":
        return head.startswith(b"RIFF") and head[8:12] == b"WEBP"
    if ext == ".svg":
        return b"<svg" in path.read_bytes()[:1024]
    return False

parser = Images()
parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
issues = []
for src in sorted(set(parser.sources)):
    p = (ROOT / src).resolve()
    if not p.is_relative_to(ROOT):
        issues.append(f"Caminho fora do repositório: {src}")
    elif not p.is_file():
        issues.append(f"Ficheiro em falta: {src}")
    elif p.stat().st_size == 0:
        issues.append(f"Ficheiro vazio: {src}")
    elif not valid_signature(p):
        issues.append(f"Assinatura/formato inválido: {src}")

print(f"Capas locais verificadas: {len(set(parser.sources))}")
for issue in issues:
    print("ERRO:", issue)
if issues:
    sys.exit(1)
print("OK: todas as capas locais referenciadas existem e têm formato reconhecível.")
