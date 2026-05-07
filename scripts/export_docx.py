#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor


ACCENT_COLOR = RGBColor(0x1F, 0x4E, 0x79)
DEFAULT_MANIFEST = "docs/docx-manifest.json"
DEFAULT_REFERENCE_DOC = "templates/reference.docx"
DEFAULT_WSL_LIBREOFFICE_PYTHON_PATHS = (
    Path("/mnt/c/Program Files/LibreOffice/program/python.exe"),
    Path("/mnt/c/Program Files (x86)/LibreOffice/program/python.exe"),
)
DEFAULT_WINDOWS_PANDOC_PATHS = (
    Path.home() / "AppData" / "Local" / "Pandoc" / "pandoc.exe",
    Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "pandoc.exe",
    Path("C:/Program Files/Pandoc/pandoc.exe"),
)


def resolve_argument_path(value: str, repo_root: Path) -> Path:
    raw_path = Path(value)
    if raw_path.is_absolute():
        return raw_path.resolve()

    if raw_path.parts and raw_path.parts[0] in {".", ".."}:
        return (Path.cwd() / raw_path).resolve()

    return (repo_root / raw_path).resolve()


def resolve_pandoc_executable() -> str:
    explicit = os.environ.get("PANDOC_EXECUTABLE")
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_absolute() or any(separator in explicit for separator in ("/", "\\")):
            if candidate.exists():
                return str(candidate.resolve())
        else:
            resolved = shutil.which(explicit)
            if resolved:
                return resolved

    resolved = shutil.which("pandoc")
    if resolved:
        return resolved

    if sys.platform == "win32":
        for candidate in DEFAULT_WINDOWS_PANDOC_PATHS:
            if candidate.exists():
                return str(candidate.resolve())

    raise FileNotFoundError(
        "Pandoc executable not found. Install pandoc or set the PANDOC_EXECUTABLE environment variable."
    )


def resolve_wsl_windows_path(path: Path) -> str:
    wslpath = shutil.which("wslpath")
    if not wslpath:
        raise FileNotFoundError("wslpath is required to convert WSL paths for LibreOffice.")

    converted = subprocess.run(
        [wslpath, "-w", str(path.resolve())],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not converted:
        raise RuntimeError(f"wslpath did not return a Windows path for {path}.")

    return converted


def resolve_wsl_libreoffice_python() -> Path | None:
    explicit_python = os.environ.get("LIBREOFFICE_PYTHON")
    if explicit_python:
        candidate = Path(explicit_python).expanduser()
        if candidate.exists():
            return candidate.resolve()

    explicit_program = os.environ.get("LIBREOFFICE_PROGRAM") or os.environ.get("UNO_PATH")
    if explicit_program:
        candidate = Path(explicit_program).expanduser()
        python_executable = candidate / "python.exe" if candidate.is_dir() else candidate
        if python_executable.exists():
            return python_executable.resolve()

    for candidate in DEFAULT_WSL_LIBREOFFICE_PYTHON_PATHS:
        if candidate.exists():
            return candidate.resolve()

    return None


def set_title_style(paragraph) -> None:
    paragraph.style = "Title"
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in paragraph.runs:
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = ACCENT_COLOR


def apply_postprocessing(document_path: Path) -> None:
    document = Document(document_path)

    title_paragraph = next((paragraph for paragraph in document.paragraphs if paragraph.text.strip()), None)
    if title_paragraph is not None:
        set_title_style(title_paragraph)

    document.save(document_path)


def is_excluded_discovery_path(path: Path) -> bool:
    excluded_segments = {".git", ".venv", ".pytest_cache", "__pycache__"}
    return any(segment in excluded_segments or segment.startswith(".") for segment in path.parts)


def discover_source_paths(repo_root: Path, entry: dict) -> list[Path]:
    source_path = (repo_root / entry["source"]).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {entry['source']}")

    explicit_sources = entry.get("sources")
    if explicit_sources:
        sources = [resolve_argument_path(value, repo_root) for value in explicit_sources]
    else:
        sources = [source_path]
        include_root_value = entry.get("include_root")
        if include_root_value:
            include_root = resolve_argument_path(include_root_value, repo_root)
            if not include_root.exists():
                raise FileNotFoundError(f"Include root not found: {include_root_value}")

            suffix = ".en.md" if source_path.name.endswith(".en.md") else ".md"
            discovered = []
            for candidate in include_root.rglob(f"README{suffix}"):
                if is_excluded_discovery_path(candidate):
                    continue
                resolved_candidate = candidate.resolve()
                if resolved_candidate == source_path:
                    continue
                discovered.append(resolved_candidate)

            discovered.sort(key=lambda path: path.relative_to(include_root).as_posix().lower())
            sources.extend(discovered)

    unique_sources: list[Path] = []
    seen = set()
    for source in sources:
        resolved_source = source.resolve()
        if resolved_source in seen:
            continue
        seen.add(resolved_source)
        unique_sources.append(resolved_source)

    return unique_sources


def build_resource_path(repo_root: Path, sources: list[Path]) -> str:
    directories: list[Path] = []
    seen = set()

    for source in sources:
        directory = source.parent.resolve()
        if directory in seen:
            continue
        seen.add(directory)
        directories.append(directory)

    if repo_root not in seen:
        directories.append(repo_root)

    return os.pathsep.join(str(directory) for directory in directories)


def refresh_generated_docx_toc(repo_root: Path, document_paths: list[Path]) -> None:
    if os.name == "nt" or not document_paths:
        return

    libreoffice_python = resolve_wsl_libreoffice_python()
    if libreoffice_python is None:
        print(
            "Warning: LibreOffice Python runtime was not found. Skipping DOCX table-of-contents refresh.",
            file=sys.stderr,
        )
        return

    refresh_script = repo_root / "scripts" / "refresh_docx_toc_libreoffice.py"
    if not refresh_script.exists():
        print(
            "Warning: LibreOffice TOC refresh helper script was not found. Skipping DOCX table-of-contents refresh.",
            file=sys.stderr,
        )
        return

    try:
        command = [str(libreoffice_python)]
        if shutil.which("wslpath"):
            command.extend(
                [
                    resolve_wsl_windows_path(refresh_script),
                    *[resolve_wsl_windows_path(document_path) for document_path in document_paths],
                ]
            )
        else:
            command.extend([str(refresh_script), *[str(document_path) for document_path in document_paths]])
        subprocess.run(command, check=True)
    except Exception as exc:
        print(f"Warning: LibreOffice TOC refresh failed: {exc}", file=sys.stderr)


def export_entry(repo_root: Path, reference_doc: Path, pandoc_executable: str, entry: dict) -> Path:
    source_paths = discover_source_paths(repo_root, entry)
    output_path = (repo_root / entry["output"]).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        pandoc_executable,
        *[str(source_path) for source_path in source_paths],
        "--from=gfm",
        "--to=docx",
        "--toc",
        "--toc-depth=3",
        "--metadata",
        f"toc-title={entry['tocTitle']}",
        f"--reference-doc={reference_doc}",
        f"--resource-path={build_resource_path(repo_root, source_paths)}",
        f"--output={output_path}",
    ]

    included_count = len(source_paths) - 1
    if included_count > 0:
        print(
            f"Exporting {entry['source']} (+{included_count} included sources) -> {output_path.relative_to(repo_root)}"
        )
    else:
        print(f"Exporting {entry['source']} -> {output_path.relative_to(repo_root)}")
    subprocess.run(command, check=True)

    apply_postprocessing(output_path)
    return output_path


def export_entries(
    repo_root: Path,
    reference_doc: Path,
    pandoc_executable: str,
    entries: list[dict],
) -> list[Path]:
    generated_paths = []
    for entry in entries:
        generated_paths.append(export_entry(repo_root, reference_doc, pandoc_executable, entry))

    refresh_generated_docx_toc(repo_root, generated_paths)
    return generated_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Markdown guides to DOCX.")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Manifest path.")
    parser.add_argument("--reference-doc", default=DEFAULT_REFERENCE_DOC, help="Reference DOCX path.")
    parser.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="Optional manifest ids, source paths, or output paths to export.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = resolve_argument_path(args.manifest, repo_root)
    reference_doc = resolve_argument_path(args.reference_doc, repo_root)
    pandoc_executable = resolve_pandoc_executable()

    if not reference_doc.exists():
        template_script = repo_root / "scripts" / "create_reference_template.py"
        subprocess.run(
            [sys.executable, str(template_script), "--output", str(reference_doc)],
            check=True,
        )

    with manifest_path.open(encoding="utf-8") as handle:
        entries = json.load(handle)

    only = set(args.only)
    selected = [
        entry
        for entry in entries
        if not only
        or entry["id"] in only
        or entry["source"] in only
        or entry["output"] in only
    ]

    if not selected:
        raise SystemExit("No manifest entries matched the requested selection.")

    export_entries(repo_root, reference_doc, pandoc_executable, selected)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
