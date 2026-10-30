"""Parse the Cyber-Practice repo into trackable items.

Everything with a checkbox in a project is tracked automatically:
  projects/NN-*/README.md               every "- [ ]" line in any section (Prerequisites, Checkpoints,
                                        Definition of done, or any section you add), grouped by heading
  projects/NN-*/deliverables/README.md  every row of the deliverables table (☐ / ☑)
  projects/NN-*/TASKS.md                optional: your own extra tasks for that project ("- [ ]" lines,
                                        grouped by "## " headings if you use them)
A new project folder (projects/15-something/README.md) is picked up too.

Ticks written in the files themselves ("- [x]", or ☑/✅ in the deliverables table) count as done.
Checkboxes inside ``` code blocks are ignored (they're examples, not tasks).
Results are cached and re-parsed automatically when any source file changes (e.g. git pull).
"""
from __future__ import annotations

import hashlib
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

# Section names whose item keys must stay stable (they predate the "track every section" change)
LEGACY_KINDS = {"Checkpoints": "checkpoint", "Definition of done": "done"}
CHECKBOX_RE = re.compile(r"^\s*[-*] \[(?P<mark>[ xX])\]\s+(?P<text>.+?)\s*$")
HEADING_RE = re.compile(r"^##\s+(?:\d+[A-Za-z]?\.\s+)?(?P<name>.+?)\s*$")
HOURS_RE = re.compile(r"\*\*(\d+(?:\.\d+)?)\s+hours", re.I)
TABLE_ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")
NEW_DOC_RE = re.compile(r"scripts/new-doc\.sh\s+[^`|]+")
DONE_MARKS = {"☑", "✅", "✔", "✔️", "x", "X"}
OPEN_MARKS = {"☐", ""}


@dataclass
class Item:
    key: str
    project: str
    kind: str            # machine id of the group: checkpoint | done | prerequisites | deliverable | tasks | ...
    group: str           # display label, e.g. "Prerequisites", "Deliverables", "My tasks (TASKS.md)"
    text: str
    source: str          # file it came from, relative to the project folder
    file: str = ""       # deliverables: expected path relative to the repo
    file_exists: bool = False
    repo_done: bool = False   # ticked in the Markdown file itself


@dataclass
class Project:
    id: str              # "01"
    slug: str            # "01-lab-foundation"
    title: str
    hours_planned: float
    items: list[Item] = field(default_factory=list)

    def groups(self) -> list[tuple[str, str, list[Item]]]:
        """(kind, label, items) in the order they first appear."""
        order: dict[str, tuple[str, list[Item]]] = {}
        for i in self.items:
            order.setdefault(i.kind, (i.group, []))[1].append(i)
        return [(k, label, items) for k, (label, items) in order.items()]


def item_key(project: str, kind: str, text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha1(f"{project}|{kind}|{norm}".encode()).hexdigest()[:16]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "general"


class _KeyMaker:
    """Stable keys; identical text in the same group gets #2, #3... so duplicates don't collide."""

    def __init__(self):
        self.seen: dict[tuple[str, str, str], int] = {}

    def __call__(self, project: str, kind: str, text: str) -> str:
        norm = re.sub(r"\s+", " ", text.strip().lower())
        n = self.seen.get((project, kind, norm), 0)
        self.seen[(project, kind, norm)] = n + 1
        return item_key(project, kind, text if n == 0 else f"{text} #{n + 1}")


def _checkbox_items(path: Path, pid: str, keys: _KeyMaker, *, kind_for, label_for, source: str) -> list[Item]:
    items, heading, in_code = [], None, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADING_RE.match(line)
        if m and line.startswith("## "):
            heading = m.group("name")
            continue
        cm = CHECKBOX_RE.match(line)
        if cm:
            kind, text = kind_for(heading), cm.group("text")
            items.append(Item(keys(pid, kind, text), pid, kind, label_for(heading), text, source,
                              repo_done=cm.group("mark") in "xX"))
    return items


def _readme(path: Path, pid: str, keys: _KeyMaker) -> tuple[str, float, list[Item]]:
    title, hours, in_hours = path.parent.name, 0.0, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and title == path.parent.name:
            title = re.sub(r"^#\s+Project\s+\d+:\s*", "", line).strip()
        m = HEADING_RE.match(line)
        if m and line.startswith("## "):
            in_hours = m.group("name").lower().startswith("estimated time")
        elif in_hours and not hours and (hm := HOURS_RE.search(line)):
            hours = float(hm.group(1))
    items = _checkbox_items(
        path, pid, keys, source="README.md",
        kind_for=lambda h: LEGACY_KINDS.get(h, slugify(h or "general")),
        label_for=lambda h: h or "General")
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


def _deliverables(path: Path, pid: str, repo: Path, keys: _KeyMaker) -> list[Item]:
    items = []
    if not path.exists():
        return items
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TABLE_ROW_RE.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group("cells").split("|")]
        if len(cells) < 2 or set(cells[0]) <= {"-", ":"} and cells[0] or cells[0].lower() == "done":
            continue                                   # separator or header row
        mark, desc = cells[0], cells[1]
        if mark not in DONE_MARKS | OPEN_MARKS or not desc:
            continue
        cmd = NEW_DOC_RE.search(" | ".join(cells[2:]))
        rel = _expected_file(cmd.group(0)) if cmd else ""
        items.append(Item(keys(pid, "deliverable", desc), pid, "deliverable", "Deliverables", desc,
                          "deliverables/README.md", file=rel,
                          file_exists=bool(rel) and (repo / rel).exists(), repo_done=mark in DONE_MARKS))
    return items


def _tasks_file(path: Path, pid: str, keys: _KeyMaker) -> list[Item]:
    if not path.exists():
        return []
    return _checkbox_items(
        path, pid, keys, source="TASKS.md",
        kind_for=lambda h: "tasks" if not h else f"tasks-{slugify(h)}",
        label_for=lambda h: "My tasks (TASKS.md)" if not h else f"My tasks · {h}")


def parse_repo(repo: Path) -> list[Project]:
    projects = []
    for readme in sorted((repo / "projects").glob("[0-9][0-9]-*/README.md")):
        folder = readme.parent
        pid = folder.name[:2]
        keys = _KeyMaker()
        title, hours, items = _readme(readme, pid, keys)
        items += _deliverables(folder / "deliverables" / "README.md", pid, repo, keys)
        items += _tasks_file(folder / "TASKS.md", pid, keys)
        projects.append(Project(pid, folder.name, title, hours, items))
    return projects


def repo_version(repo: Path) -> dict:
    """Current commit and last pull time, read straight from .git (no git binary needed)."""
    git = repo / ".git"
    info = {"commit": None, "branch": None, "last_pull": None}
    try:
        head = (git / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = head[5:]
            info["branch"] = ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
            ref_file = git / ref
            if ref_file.exists():
                info["commit"] = ref_file.read_text().strip()[:7]
            elif (git / "packed-refs").exists():
                for line in (git / "packed-refs").read_text().splitlines():
                    if line.endswith(" " + ref):
                        info["commit"] = line[:7]
        else:
            info["commit"] = head[:7]
        fetch_head = git / "FETCH_HEAD"
        if fetch_head.exists():
            info["last_pull"] = fetch_head.stat().st_mtime
    except OSError:
        pass
    return info


class RepoCache:
    """Re-parse only when a tracked file is added, removed or modified."""

    def __init__(self, repo: Path):
        self.repo = repo
        self._lock = threading.Lock()
        self._sig: tuple | None = None
        self._projects: list[Project] = []

    def _signature(self) -> tuple:
        base = self.repo / "projects"
        paths = list(base.glob("[0-9][0-9]-*/README.md"))
        paths += list(base.glob("[0-9][0-9]-*/TASKS.md"))
        paths += list(base.glob("[0-9][0-9]-*/deliverables/*.md"))   # new deliverable files flip "file created"
        sig = []
        for p in paths:
            try:
                sig.append((str(p), p.stat().st_mtime_ns))
            except OSError:
                continue
        return tuple(sorted(sig))

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
