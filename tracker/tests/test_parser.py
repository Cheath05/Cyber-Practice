from pathlib import Path

from cyber_tracker.repo_parser import RepoCache, _expected_file, item_key, parse_repo

REPO = Path(__file__).resolve().parents[2]


def test_all_projects_parsed_with_items():
    projects = parse_repo(REPO)
    assert [p.id for p in projects] == [f"{i:02d}" for i in range(1, 15)]
    for p in projects:
        kinds = {i.kind for i in p.items}
        assert {"checkpoint", "done", "deliverable"} <= kinds, p.slug
        assert p.hours_planned > 0, p.slug
        assert p.title and not p.title.startswith("#")


def test_planned_hours_match_schedule_doc():
    assert sum(p.hours_planned for p in parse_repo(REPO)) == 174   # docs/schedule.md "Project hours"


def test_item_keys_unique_and_stable():
    items = [i for p in parse_repo(REPO) for i in p.items]
    keys = [i.key for i in items]
    assert len(keys) == len(set(keys))
    assert item_key("01", "done", "  Some   Text ") == item_key("01", "done", "some text")


def test_expected_deliverable_paths():
    assert _expected_file("scripts/new-doc.sh 01-lab-foundation network-design") == \
        "projects/01-lab-foundation/deliverables/network-design.md"
    assert _expected_file("scripts/new-doc.sh 03-wireguard-remote-access adr 003-remote-access") == \
        "projects/03-wireguard-remote-access/deliverables/adr-003-remote-access.md"


def test_cache_reparses_when_files_change(tmp_path):
    proj = tmp_path / "projects" / "01-test"
    (proj / "deliverables").mkdir(parents=True)
    readme = proj / "README.md"
    readme.write_text("# Project 01: Test\n## 3. Estimated time\n**2 hours.**\n## 8. Checkpoints\n- [ ] one\n")
    cache = RepoCache(tmp_path)
    assert len(cache.projects()[0].items) == 1
    import os, time
    readme.write_text(readme.read_text() + "- [ ] two\n")
    st = readme.stat()
    os.utime(readme, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))
    assert len(cache.projects()[0].items) == 2
