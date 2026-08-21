#!/usr/bin/env python3
"""Read-only structural audit for a repository's PRD.md document tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "dist",
    "build",
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line: int


@dataclass(frozen=True)
class BrokenLink:
    line: int
    target: str


@dataclass
class PrdInfo:
    path: str
    parent_prd: str | None
    indexed_by_parent: bool | None
    line_count: int
    nonblank_line_count: int
    heading_count: int
    h2_headings: list[str]
    has_implemented_section: bool
    has_unimplemented_section: bool
    outgoing_prd_links: list[str]
    broken_markdown_links: list[BrokenLink]
    review_flags: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit PRD.md files without modifying the repository."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository or directory root to scan (default: current directory).",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--review-lines",
        type=int,
        default=500,
        help="Line-count threshold used only to flag documents for review.",
    )
    return parser.parse_args()


def is_excluded(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in relative.parts)


def find_prd_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("PRD.md")
        if path.is_file() and not is_excluded(path, root)
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_markdown_lines(text: str) -> Iterable[tuple[int, str, bool]]:
    """Yield line number, line text, and whether the line is inside a code fence."""
    in_fence = False
    fence_token: str | None = None
    for line_no, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            token = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_token = token
            elif token == fence_token:
                in_fence = False
                fence_token = None
            yield line_no, line, True
            continue
        yield line_no, line, in_fence


def parse_headings(text: str) -> list[Heading]:
    headings: list[Heading] = []
    for line_no, line, in_fence in iter_markdown_lines(text):
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                Heading(level=len(match.group(1)), title=match.group(2).strip(), line=line_no)
            )
    return headings


def normalize_heading(title: str) -> str:
    normalized = re.sub(r"^[\d一二三四五六七八九十]+[.、)）\s-]+", "", title.strip())
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def has_implemented_section(headings: list[Heading]) -> bool:
    for heading in headings:
        if heading.level != 2:
            continue
        title = normalize_heading(heading.title)
        if "已实现" in title or title in {"implemented", "implemented requirements"}:
            return True
    return False


def has_unimplemented_section(headings: list[Heading]) -> bool:
    for heading in headings:
        if heading.level != 2:
            continue
        title = normalize_heading(heading.title)
        if "未实现" in title or title in {
            "unimplemented",
            "not implemented",
            "future requirements",
        }:
            return True
    return False


def clean_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        quote_positions = [pos for pos in (target.find(' "'), target.find(" '")) if pos >= 0]
        if quote_positions:
            target = target[: min(quote_positions)]
    return unquote(target.strip())


def resolve_markdown_links(path: Path, text: str, root: Path) -> tuple[list[str], list[BrokenLink]]:
    outgoing_prds: set[str] = set()
    broken: list[BrokenLink] = []

    for line_no, line, in_fence in iter_markdown_lines(text):
        if in_fence:
            continue
        for match in LINK_RE.finditer(line):
            target = clean_link_target(match.group(1))
            if not target or target.startswith("#"):
                continue
            parsed = urlparse(target)
            if parsed.scheme or parsed.netloc:
                continue

            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue

            candidate = (path.parent / path_part).resolve()
            if candidate.is_dir():
                candidate = candidate / "PRD.md"

            if candidate.name == "PRD.md":
                try:
                    outgoing_prds.add(candidate.relative_to(root).as_posix())
                except ValueError:
                    outgoing_prds.add(str(candidate))

            if path_part.lower().endswith(".md") and not candidate.exists():
                broken.append(BrokenLink(line=line_no, target=target))

    return sorted(outgoing_prds), broken


def nearest_parent_prd(path: Path, root: Path, prd_set: set[Path]) -> Path | None:
    current = path.parent
    while current != root:
        current = current.parent
        candidate = (current / "PRD.md").resolve()
        if candidate in prd_set:
            return candidate
    return None


def extract_paragraphs(text: str) -> list[tuple[int, str]]:
    paragraphs: list[tuple[int, str]] = []
    current: list[str] = []
    start_line = 0

    def flush() -> None:
        nonlocal current, start_line
        if not current:
            return
        paragraph = " ".join(part.strip() for part in current if part.strip())
        normalized = re.sub(r"\s+", " ", paragraph).strip()
        if len(normalized) >= 60:
            paragraphs.append((start_line, normalized))
        current = []
        start_line = 0

    for line_no, line, in_fence in iter_markdown_lines(text):
        stripped = line.strip()
        if in_fence or not stripped or HEADING_RE.match(line) or stripped.startswith("|"):
            flush()
            continue
        if start_line == 0:
            start_line = line_no
        current.append(stripped)
    flush()
    return paragraphs


def paragraph_fingerprint(paragraph: str) -> str:
    normalized = paragraph.lower()
    normalized = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", normalized)
    normalized = re.sub(r"[`*_>#~-]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def build_audit(root: Path, review_lines: int) -> dict[str, object]:
    prd_files = find_prd_files(root)
    resolved_prds = {path.resolve() for path in prd_files}
    texts = {path: read_text(path) for path in prd_files}
    outgoing_by_path: dict[Path, list[str]] = {}
    broken_by_path: dict[Path, list[BrokenLink]] = {}

    for path, text in texts.items():
        outgoing, broken = resolve_markdown_links(path, text, root)
        outgoing_by_path[path] = outgoing
        broken_by_path[path] = broken

    infos: list[PrdInfo] = []
    for path in prd_files:
        text = texts[path]
        lines = text.splitlines()
        headings = parse_headings(text)
        parent = nearest_parent_prd(path, root, resolved_prds)
        parent_rel = parent.relative_to(root).as_posix() if parent else None
        indexed: bool | None = None
        if parent:
            child_rel = path.relative_to(root).as_posix()
            indexed = child_rel in outgoing_by_path.get(parent, [])

        implemented = has_implemented_section(headings)
        unimplemented = has_unimplemented_section(headings)
        flags: list[str] = []
        if len(lines) >= review_lines:
            flags.append(f"line count >= {review_lines}; review semantic split candidates")
        if len(lines) >= max(review_lines + 300, 800):
            flags.append("very long PRD; strong manual review candidate")
        if not implemented:
            flags.append("missing level-2 implemented section")
        if not unimplemented:
            flags.append("missing level-2 unimplemented section")
        if parent and not indexed:
            flags.append("not linked from nearest parent PRD")
        if broken_by_path[path]:
            flags.append("contains broken relative Markdown links")

        infos.append(
            PrdInfo(
                path=path.relative_to(root).as_posix(),
                parent_prd=parent_rel,
                indexed_by_parent=indexed,
                line_count=len(lines),
                nonblank_line_count=sum(1 for line in lines if line.strip()),
                heading_count=len(headings),
                h2_headings=[heading.title for heading in headings if heading.level == 2],
                has_implemented_section=implemented,
                has_unimplemented_section=unimplemented,
                outgoing_prd_links=outgoing_by_path[path],
                broken_markdown_links=broken_by_path[path],
                review_flags=flags,
            )
        )

    duplicates: dict[str, list[dict[str, object]]] = defaultdict(list)
    paragraph_text: dict[str, str] = {}
    for path, text in texts.items():
        for line_no, paragraph in extract_paragraphs(text):
            fingerprint = paragraph_fingerprint(paragraph)
            paragraph_text.setdefault(fingerprint, paragraph)
            duplicates[fingerprint].append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "line": line_no,
                }
            )

    duplicate_groups: list[dict[str, object]] = []
    for fingerprint, occurrences in duplicates.items():
        unique_paths = {str(item["path"]) for item in occurrences}
        if len(unique_paths) < 2:
            continue
        duplicate_groups.append(
            {
                "fingerprint": fingerprint,
                "preview": paragraph_text[fingerprint][:180],
                "occurrences": occurrences,
            }
        )
    duplicate_groups.sort(key=lambda item: (-len(item["occurrences"]), item["preview"]))

    root_prd = (root / "PRD.md").resolve()
    root_prd_present = root_prd in resolved_prds
    orphan_count = sum(1 for info in infos if info.parent_prd and info.indexed_by_parent is False)
    broken_count = sum(len(info.broken_markdown_links) for info in infos)

    return {
        "root": str(root),
        "root_prd_present": root_prd_present,
        "summary": {
            "prd_count": len(infos),
            "total_lines": sum(info.line_count for info in infos),
            "missing_implemented_sections": sum(
                not info.has_implemented_section for info in infos
            ),
            "missing_unimplemented_sections": sum(
                not info.has_unimplemented_section for info in infos
            ),
            "unindexed_children": orphan_count,
            "broken_markdown_links": broken_count,
            "exact_duplicate_paragraph_groups": len(duplicate_groups),
        },
        "files": [asdict(info) for info in infos],
        "exact_duplicate_paragraphs": duplicate_groups,
    }


def render_markdown(audit: dict[str, object]) -> str:
    summary = audit["summary"]
    files = audit["files"]
    duplicate_groups = audit["exact_duplicate_paragraphs"]

    lines = [
        "# PRD Tree Audit",
        "",
        f"Root: `{audit['root']}`",
        "",
        "## Summary",
        "",
        f"- PRD files: {summary['prd_count']}",
        f"- Total lines: {summary['total_lines']}",
        f"- Root `PRD.md` present: {'yes' if audit['root_prd_present'] else 'no'}",
        f"- Missing implemented sections: {summary['missing_implemented_sections']}",
        f"- Missing unimplemented sections: {summary['missing_unimplemented_sections']}",
        f"- Children not linked from nearest parent: {summary['unindexed_children']}",
        f"- Broken relative Markdown links: {summary['broken_markdown_links']}",
        f"- Exact duplicate paragraph groups: {summary['exact_duplicate_paragraph_groups']}",
        "",
        "## Files",
        "",
        "| PRD | Lines | Parent | Indexed | Status sections | Flags |",
        "|---|---:|---|---|---|---|",
    ]

    for info in files:
        parent = f"`{info['parent_prd']}`" if info["parent_prd"] else "—"
        indexed_value = info["indexed_by_parent"]
        indexed = "—" if indexed_value is None else ("yes" if indexed_value else "no")
        status = (
            f"implemented={'yes' if info['has_implemented_section'] else 'no'}, "
            f"unimplemented={'yes' if info['has_unimplemented_section'] else 'no'}"
        )
        flags = "; ".join(info["review_flags"]) or "—"
        lines.append(
            f"| `{info['path']}` | {info['line_count']} | {parent} | {indexed} | {status} | {flags} |"
        )

    broken_entries: list[tuple[str, dict[str, object]]] = []
    for info in files:
        for broken in info["broken_markdown_links"]:
            broken_entries.append((info["path"], broken))
    if broken_entries:
        lines.extend(["", "## Broken links", ""])
        for path, broken in broken_entries:
            lines.append(f"- `{path}:{broken['line']}` -> `{broken['target']}`")

    if duplicate_groups:
        lines.extend(["", "## Exact duplicate long paragraphs", ""])
        for index, group in enumerate(duplicate_groups[:20], start=1):
            occurrence_text = ", ".join(
                f"`{item['path']}:{item['line']}`" for item in group["occurrences"]
            )
            lines.append(f"{index}. {occurrence_text}")
            lines.append(f"   - Preview: {group['preview']}")
        if len(duplicate_groups) > 20:
            lines.append(f"- {len(duplicate_groups) - 20} additional groups omitted from Markdown output.")

    lines.extend(
        [
            "",
            "> Line-count and duplicate flags are review signals only. Use semantic module boundaries before changing the tree.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2
    if args.review_lines < 1:
        print("error: --review-lines must be positive", file=sys.stderr)
        return 2

    audit = build_audit(root, args.review_lines)
    if args.format == "json":
        json.dump(audit, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
