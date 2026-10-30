"""Parse the Cyber-Practice repo into trackable items.

Sources of truth (so the tracker never drifts from the guides):
  projects/NN-*/README.md              title, planned hours, "Checkpoints" and
                                       "Definition of done" checkbox lines
  projects/NN-*/deliverables/README.md deliverable rows + the file each one should create
Results are cached and re-parsed automatically when any source file changes (e.g. git pull).
"""
from __future__ import annotations

import hashlib
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

TRACKED_SECTIONS = {"Checkpoints": "checkpoint", "Definition of done": "done"}
CHECKBOX_RE = re.compile(r"^\s*- \[[ xX]\]\s+(?P<text>.+?)\s*$")
HEADING_RE = re.compile(r"^##\s+(?:\d+[A-Za-z]?\.\s+)?(?P<name>.+?)\s*$")
HOURS_RE = re.compile(r"\*\*(\d+(?:\.\d+)?)\s+hours", re.I)
DELIV_ROW_RE = re.compile(r"^\|\s*[☐☑✅x ]?\s*\|\s*(?P<desc>.+?)\s*\|\s*`(?P<cmd>scripts/new-doc\.sh[^`]*)`\s*\|\s*$")


@dataclass
class Item:
    key: str
    project: str
    kind: str          # checkpoint | done | deliverable
    text: str
    file: str = ""     # deliverables: expected path relative to the repo
    file_exists: bool = False


@dataclass
class Project:
    id: str            # "01"
    slug: str          # "01-lab-foundation"
    title: str
    hours_planned: float
    items: list[Item] = field(default_factory=list)


def item_key(project: str, kind: str, text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha1(f"{project}|{kind}|{norm}".encode()).hexdigest()[:16]


def _parse_readme(path: Path, pid: str) -> tuple[str, float, list[Item]]:
    title, hours, items = path.parent.name, 0.0, []
    section = None
    in_hours = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and title == path.parent.name:
            title = re.sub(r"^#\s+Project\s+\d+:\s*", "", line).strip()
            continue
        m = HEADING_RE.match(line)
        if m and line.startswith("## "):
            name = m.group("name")
            section = TRACKED_SECTIONS.get(name)
            in_hours = name.lower().startswith("estimated time")
            continue
        if in_hours and not hours:
            hm = HOURS_RE.search(line)
            if hm:
                hours = float(hm.group(1))
        if section:
            cm = CHECKBOX_RE.match(line)
            if cm:
                text = cm.group("text")
                items.append(Item(item_key(pid, section, text), pid, section, text))
    return title, hours, items


def _expected_file(cmd: str) -> str:
    # scripts/new-doc.sh <project> <template> [suffix]  ->  projects/<project>/deliverables/<template>[-suffix].md
    parts = cmd.split()
    if len(parts) < 3:
        return ""
    project, template = parts[1], parts[2]
    suffix = parts[3] if len(parts) > 3 else ""
    name = f"{template}-{suffix}.md" if suffix else f"{template}.md"
    return f"projects/{project}/deliverables/{name}"


def _parse_deliverables(path: Path, pid: str, repo: Path) -> list[Item]:
    items = []
    if not path.exists():
        return items
    for line in path.read_text(encoding="utf-8").splitlines():
        m = DELIV_ROW_RE.match(line)
        if not m:
            continue
        desc, cmd = m.group("desc"), m.group("cmd")
        rel = _expected_file(cmd)
        items.append(Item(item_key(pid, "deliverable", desc), pid, "deliverable", desc,
                          file=rel, file_exists=bool(rel) and (repo / rel).exists()))
    return items


def parse_repo(repo: Path) -> list[Project]:
    projects = []
    for readme in sorted((repo / "projects").glob("[0-9][0-9]-*/README.md")):
        slug = readme.parent.name
        pid = slug[:2]
        title, hours, items = _parse_readme(readme, pid)
        items += _parse_deliverables(readme.parent / "deliverables" / "README.md", pid, repo)
        projects.append(Project(pid, slug, title, hours, items))
    return projects


class RepoCache:
    """Re-parse only when a source file's mtime (or the set of deliverable files) changes."""

    def __init__(self, repo: Path):
        self.repo = repo
        self._lock = threading.Lock()
        self._sig: tuple | None = None
        self._projects: list[Project] = []

    def _signature(self) -> tuple:
        paths = list((self.repo / "projects").glob("[0-9][0-9]-*/README.md"))
        paths += list((self.repo / "projects").glob("[0-9][0-9]-*/deliverables/*.md"))
        return tuple(sorted((str(p), p.stat().st_mtime_ns) for p in paths if p.exists()))

    def projects(self) -> list[Project]:
        sig = self._signature()
        with self._lock:
            if sig != self._sig:
                self._projects = parse_repo(self.repo)
                self._sig = sig
            return self._projects

    def project(self, pid: str) -> Project | None:
        return next((p for p in self.projects() if p.id == pid), None)

    def item_keys(self) -> dict[str, Item]:
        return {i.key: i for p in self.projects() for i in p.items}
