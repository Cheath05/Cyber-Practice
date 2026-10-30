"""Anything with a checkbox in a project is tracked automatically (README, deliverables, TASKS.md)."""
import os

import pytest

from conftest import HDR
from cyber_tracker.repo_parser import RepoCache, item_key, parse_repo

README_01 = """# Project 01: Test Project
## 3. Estimated time
**5 hours.**
## 5. Prerequisites
- [ ] Have a laptop
- [x] Read the network reference
## 7. Build steps
```
- [ ] this is an example inside a code block and must be ignored
```
## 8. Checkpoints
- [ ] Ping works
- [ ] Same text twice
- [ ] Same text twice
## 14. Definition of done
- [ ] Docs written
## 17. My extra section
- [ ] A task I added myself
"""

DELIV_01 = """# Deliverables
| Done | Document | Create with |
|---|---|---|
| ☐ | Design doc | `scripts/new-doc.sh 01-test network-design` |
| ☑ | Runbook | `scripts/new-doc.sh 01-test runbook-sop build` |
| ☐ | Plain row without a command | |
"""

TASKS_01 = """# My tasks
- [ ] Watch the VLAN video
## Stretch
- [x] Try AdGuard Home
"""

README_15 = """# Project 15: Brand New Project
## 3. Estimated time
**7 hours.**
## 8. Checkpoints
- [ ] First checkpoint
"""


@pytest.fixture
def repo(tmp_path):
    p1 = tmp_path / "projects" / "01-test"
    (p1 / "deliverables").mkdir(parents=True)
    (p1 / "README.md").write_text(README_01)
    (p1 / "deliverables" / "README.md").write_text(DELIV_01)
    (p1 / "deliverables" / "runbook-sop-build.md").write_text("# runbook\n")
    (p1 / "TASKS.md").write_text(TASKS_01)
    p15 = tmp_path / "projects" / "15-brand-new"
    p15.mkdir(parents=True)
    (p15 / "README.md").write_text(README_15)
    return tmp_path


def by_text(project):
    return {i.text: i for i in project.items}


def test_every_section_is_tracked(repo):
    p = parse_repo(repo)[0]
    items = by_text(p)
    assert "Have a laptop" in items and items["Have a laptop"].group == "Prerequisites"
    assert items["A task I added myself"].group == "My extra section"
    assert not any("code block" in t for t in items)
    assert [g[1] for g in p.groups()] == ["Prerequisites", "Checkpoints", "Definition of done",
                                          "My extra section", "Deliverables",
                                          "My tasks (TASKS.md)", "My tasks · Stretch"]


def test_existing_keys_unchanged(repo):
    items = by_text(parse_repo(repo)[0])
    assert items["Ping works"].key == item_key("01", "checkpoint", "Ping works")
    assert items["Docs written"].key == item_key("01", "done", "Docs written")
    assert items["Design doc"].key == item_key("01", "deliverable", "Design doc")


def test_duplicates_get_distinct_keys(repo):
    dups = [i for i in parse_repo(repo)[0].items if i.text == "Same text twice"]
    assert len(dups) == 2 and dups[0].key != dups[1].key


def test_repo_ticks_count_as_done(repo):
    items = by_text(parse_repo(repo)[0])
    assert items["Read the network reference"].repo_done
    assert items["Runbook"].repo_done and items["Runbook"].file_exists
    assert items["Try AdGuard Home"].repo_done
    assert not items["Have a laptop"].repo_done
    assert items["Plain row without a command"].file == ""


def test_new_project_folder_is_picked_up(repo):
    projects = parse_repo(repo)
    assert [p.id for p in projects] == ["01", "15"]
    assert projects[1].title == "Brand New Project" and projects[1].hours_planned == 7


def test_cache_sees_new_tasks_file(repo):
    cache = RepoCache(repo)
    before = len(cache.project("15").items)
    (repo / "projects" / "15-brand-new" / "TASKS.md").write_text("- [ ] new task\n")
    assert len(cache.project("15").items) == before + 1


@pytest.fixture
def client(repo, tmp_path, monkeypatch):
    monkeypatch.setenv("CT_DB", str(tmp_path / "default.db"))
    monkeypatch.setenv("CT_TODAY", "2026-11-20")
    from fastapi.testclient import TestClient
    from cyber_tracker.main import create_app
    return TestClient(create_app(repo=repo, db_path=tmp_path / "t.db"))


def test_summary_counts_repo_ticks_and_flags_unscheduled(client):
    s = client.get("/api/summary").json()
    p01 = next(p for p in s["projects"] if p["id"] == "01")
    assert p01["done"] == 3                       # [x] prereq + ☑ runbook + [x] TASKS item
    assert [p["id"] for p in s["unscheduled"]] == ["15"]
    assert s["overall"]["hours_planned"] == 68 + 5 + 7     # buffer + each project's estimate
    page = client.get("/").text
    assert "Not on the schedule yet" in page and "Brand New Project" in page


def test_cannot_untick_item_ticked_in_repo(client, repo):
    item = by_text(parse_repo(repo)[0])["Read the network reference"]
    r = client.post("/api/check", json={"key": item.key, "checked": False}, headers=HDR)
    assert r.status_code == 409


def test_project_page_shows_sources_and_hints(client):
    page = client.get("/project/01").text
    assert "TASKS.md" in page and "ticked in README.md" in page and "My extra section" in page
    page15 = client.get("/project/15").text
    assert "No due date yet" in page15 and "Create <code>projects/15-brand-new/TASKS.md</code>" in page15
