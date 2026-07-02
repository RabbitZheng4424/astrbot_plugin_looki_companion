from __future__ import annotations

import re
import zipfile
from pathlib import Path


PLUGIN_DIR = Path(__file__).resolve().parent
IGNORED_PARTS = {"__pycache__", ".git", ".pytest_cache", ".ruff_cache", ".venv", "venv"}
EXCLUDED_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "build_portable_zip.py",
}


def load_plugin_version() -> str:
    metadata_path = PLUGIN_DIR / "metadata.yaml"
    try:
        content = metadata_path.read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    match = re.search(r"^version:\s*([^\r\n]+)\s*$", content, re.MULTILINE)
    if not match:
        return "unknown"
    return match.group(1).strip().strip("\"'")


PLUGIN_VERSION = load_plugin_version()
OUTPUT_NAME = f"astrbot_plugin_looki_companion_{PLUGIN_VERSION}_server_flat_portable.zip"
OUTPUT_PATH = PLUGIN_DIR.parent / OUTPUT_NAME


def should_include(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORED_PARTS:
        return False
    if path.name in EXCLUDED_FILES:
        return False
    return path.is_file()


def build_zip() -> Path:
    if OUTPUT_PATH.exists():
        OUTPUT_PATH.unlink()

    with zipfile.ZipFile(OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PLUGIN_DIR.rglob("*")):
            if not should_include(path):
                continue
            archive.write(path, path.relative_to(PLUGIN_DIR).as_posix())

    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_zip())
