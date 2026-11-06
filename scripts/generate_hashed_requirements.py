# -*- coding: utf-8 -*-
"""Build hash-pinned requirements (one package at a time for reliable mapping)."""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(r"c:\Users\USER\OneDrive\Documentos\Proyectos\web_minera")
BE = ROOT / "backend"
ML = ROOT / "ml"
PY = str(BE / ".venv" / "Scripts" / "python.exe")


def clean_freeze(text: str) -> list[str]:
    lines: list[str] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or " @" in ln or ln.startswith("-e "):
            continue
        if re.match(r"^[A-Za-z0-9_.\-]+==", ln):
            lines.append(ln)
    return sorted(set(lines), key=str.lower)


def resolve_freeze(req: Path) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "site"
        target.mkdir()
        subprocess.check_call(
            [PY, "-m", "pip", "install", "-q", "-r", str(req), "--target", str(target)],
        )
        out = subprocess.check_output(
            [PY, "-m", "pip", "freeze", "--path", str(target)], text=True
        )
        return clean_freeze(out)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hashes_for_pin(pin: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        subprocess.check_call(
            [PY, "-m", "pip", "download", "-q", "--no-deps", "-d", str(dest), pin],
        )
        files = [p for p in dest.iterdir() if p.is_file()]
        if not files:
            raise RuntimeError(f"no artifact downloaded for {pin}")
        return sorted({sha256_file(p) for p in files})


def hashed_requirements(pins: list[str], out: Path) -> None:
    lines: list[str] = [
        "# Hash-locked requirements for Docker/CI (Sonar docker:S8544).",
        "# Regenerar: python _tmp_hash_locks.py",
        "",
    ]
    for i, pin in enumerate(pins, 1):
        print(f"[{i}/{len(pins)}] {pin}")
        digests = hashes_for_pin(pin)
        lines.append(f"{pin} \\")
        for j, digest in enumerate(digests):
            cont = " \\" if j < len(digests) - 1 else ""
            lines.append(f"    --hash=sha256:{digest}{cont}")
        lines.append("")
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print("wrote", out.relative_to(ROOT), "pins", len(pins))


def main() -> None:
    base_pins = resolve_freeze(BE / "requirements" / "base.txt")
    hashed_requirements(base_pins, BE / "requirements" / "base.hashed.txt")

    venv_pins = clean_freeze(subprocess.check_output([PY, "-m", "pip", "freeze"], text=True))
    hashed_requirements(venv_pins, BE / "requirements" / "dev.hashed.txt")

    ml_pins = resolve_freeze(ML / "requirements.txt")
    hashed_requirements(ml_pins, ML / "requirements.hashed.txt")


if __name__ == "__main__":
    main()
