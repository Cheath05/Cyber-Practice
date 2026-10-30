"""Cyber-Practice progress tracker (FastAPI).

Run locally:   uvicorn cyber_tracker.main:app --host 127.0.0.1 --port 8002
Config (environment variables):
  CT_REPO            path to the Cyber-Practice checkout (default: the repo containing this app)
  CT_DB              SQLite file (default: ~/.local/share/cyber-tracker/tracker.db)
  CT_ALLOWED_LOGINS  comma-separated Tailscale logins allowed in (empty = anyone who can reach it)
  CT_REPO_URL        GitHub base URL for "open guide" links
  CT_TODAY           override today's date (YYYY-MM-DD), for testing/screenshots
"""
from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape

from . import __version__
from .db import Database
from .repo_parser import RepoCache, repo_version

PKG = Path(__file__).resolve().parent
MUTATION_HEADER = ("x-requested-with", "cyber-tracker")


def _md(text: str) -> Markup:
    """Tiny, safe Markdown subset for checklist text: escape first, then `code`, **bold**, links."""
    s = str(escape(text))
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
               r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1", s)   # relative repo links: keep the text only
    return Markup(s)


def create_app(repo: Path | None = None, db_path: Path | None = None) -> FastAPI:
    repo = Path(repo or os.environ.get("CT_REPO") or PKG.parent.parent).resolve()
    db_path = Path(db_path or os.environ.get("CT_DB")
                   or Path.home() / ".local/share/cyber-tracker/tracker.db")
    allowed = {x.strip().lower() for x in os.environ.get("CT_ALLOWED_LOGINS", "").split(",") if x.strip()}
    repo_url = os.environ.get("CT_REPO_URL", "https://github.com/cheath05/cyber-practice/blob/main").rstrip("/")
    schedule = json.loads((PKG / "schedule.json").read_text(encoding="utf-8"))

    cache = RepoCache(repo)
    db = Database(db_path)
    app = FastAPI(title="Cyber-Practice Tracker", version=__version__, docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=PKG / "static"), name="static")
    templates = Jinja2Templates(directory=PKG / "templates")
    templates.env.filters["md"] = _md

    def today() -> date:
        override = os.environ.get("CT_TODAY")
        return date.fromisoformat(override) if override else date.today()

    # ---------------------------------------------------------------------------- security
    @app.middleware("http")
    async def guard(request: Request, call_next):
        # 1) Only listed Tailscale identities (tailscale serve adds this header for tailnet users)
        if allowed:
            login = request.headers.get("tailscale-user-login", "").lower()
            if login not in allowed and request.url.path != "/healthz":
                return JSONResponse({"detail": "not on the allowlist"}, status_code=403)
        # 2) CSRF: state-changing calls must carry a custom header. Browsers can't add custom
        #    headers to cross-site requests without a CORS preflight, which this app never allows.
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if request.headers.get(MUTATION_HEADER[0], "").lower() != MUTATION_HEADER[1]:
                return JSONResponse({"detail": "missing X-Requested-With header"}, status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
            "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    # ---------------------------------------------------------------------------- summary
    def milestone_key(mid: str) -> str:
        return f"ms-{mid}"

    def build_summary() -> dict:
        t = today()
        checked = db.checked_keys()
        hours = db.hours_by_project()
        ratings = db.ratings()
        projects = []
        total_items = done_items = 0
        for p in cache.projects():
            done = sum(1 for i in p.items if i.key in checked or i.repo_done)
            total = len(p.items)
            total_items += total
            done_items += done
            pct = round(100 * done / total) if total else 0
            dues = [m["due"] for m in schedule["milestones"] if m["project"] == p.id]
            due = max(dues) if dues else None
            logged = round(hours.get(p.id, 0.0), 1)
            if total and done == total:
                status = ("complete", "✓", "Complete")
            elif due and date.fromisoformat(due) < t:
                status = ("behind", "!", "Behind schedule")
            elif due and date.fromisoformat(due) <= t + timedelta(days=7):
                status = ("due-soon", "◷", "Due this week")
            elif done or logged:
                status = ("in-progress", "●", "In progress")
            else:
                status = ("not-started", "○", "Not started")
            r = ratings.get(p.id)
            projects.append({
                "id": p.id, "slug": p.slug, "title": p.title, "hours_planned": p.hours_planned,
                "hours_logged": logged, "done": done, "total": total, "pct": pct, "due": due,
                "status": status[0], "status_icon": status[1], "status_label": status[2],
                "enjoyed": r["enjoyed"] if r else None,
                "guide_url": f"{repo_url}/projects/{p.slug}/README.md",
            })

        ms_items = []
        for m in schedule["milestones"]:
            key = milestone_key(m["id"])
            is_done = key in checked
            overdue = not is_done and date.fromisoformat(m["due"]) < t
            ms_items.append({**m, "key": key, "done": is_done, "overdue": overdue})

        phase = next((ph for ph in schedule["phases"]
                      if date.fromisoformat(ph["start"]) <= t <= date.fromisoformat(ph["end"])), None)
        upcoming_phase = phase or next((ph for ph in schedule["phases"] if date.fromisoformat(ph["start"]) > t), None)
        week = next((w for w in schedule["weeks"]
                     if date.fromisoformat(w["start"]) <= t <= date.fromisoformat(w["end"])), None)
        next_week = None if week else next((w for w in schedule["weeks"] if date.fromisoformat(w["start"]) > t), None)

        total_logged = round(sum(hours.values()), 1)
        # Planned total follows the guides: every project's estimate + the schedule's buffer.
        planned_total = round(schedule.get("buffer_hours", 0) + sum(p["hours_planned"] for p in projects))
        version = repo_version(repo)
        if version["last_pull"]:
            version["last_pull"] = datetime.fromtimestamp(version["last_pull"]).strftime("%Y-%m-%d %H:%M")
        return {
            "today": t.isoformat(),
            "overall": {"done": done_items, "total": total_items,
                        "pct": round(100 * done_items / total_items) if total_items else 0,
                        "projects_complete": sum(1 for p in projects if p["status"] == "complete"),
                        "projects_total": len(projects),
                        "hours_logged": total_logged, "hours_planned": planned_total},
            "unscheduled": [p for p in projects if not p["due"]],
            "repo": version,
            "phase": phase, "upcoming_phase": upcoming_phase,
            "phase_days_left": (date.fromisoformat(phase["end"]) - t).days if phase else None,
            "week": week, "next_week": next_week,
            "projects": projects,
            "milestones": ms_items,
            "weekly_hours": weekly_hours(t),
            "interest": sorted([p for p in projects if p["enjoyed"]], key=lambda p: (-p["enjoyed"], p["id"])),
        }

    def weekly_hours(t: date, weeks: int = 12) -> list[dict]:
        monday = t - timedelta(days=t.weekday())
        buckets = [{"start": (monday - timedelta(weeks=i)).isoformat(), "hours": 0.0} for i in reversed(range(weeks))]
        first = date.fromisoformat(buckets[0]["start"])
        for e in db.hours_entries():
            d = date.fromisoformat(e["day"])
            if first <= d <= monday + timedelta(days=6):
                buckets[(d - first).days // 7]["hours"] += e["hours"]
        for b in buckets:
            b["hours"] = round(b["hours"], 1)
            b["label"] = date.fromisoformat(b["start"]).strftime("%b %-d")
        return buckets

    def require_project(pid: str):
        p = cache.project(pid)
        if not p:
            raise HTTPException(404, "unknown project")
        return p

    async def json_body(request: Request) -> dict:
        if "application/json" not in request.headers.get("content-type", ""):
            raise HTTPException(415, "send JSON")
        try:
            body = await request.json()
        except ValueError as exc:
            raise HTTPException(400, "invalid JSON") from exc
        if not isinstance(body, dict):
            raise HTTPException(400, "expected an object")
        return body

    # ---------------------------------------------------------------------------- pages
    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse(request, "index.html",
                                          {"s": build_summary(), "tasks": db.tasks()})

    @app.get("/project/{pid}", response_class=HTMLResponse)
    def project_page(request: Request, pid: str):
        p = require_project(pid)
        summary = build_summary()
        info = next(x for x in summary["projects"] if x["id"] == pid)
        checked = db.checked_keys()
        groups = []
        for kind, label, group_items in p.groups():
            rows = [{"key": i.key, "text": i.text, "checked": i.key in checked or i.repo_done,
                     "repo_done": i.repo_done, "file": i.file, "file_exists": i.file_exists,
                     "source": i.source} for i in group_items]
            groups.append({"kind": kind, "label": label, "rows": rows,
                           "source": group_items[0].source,
                           "done": sum(1 for r in rows if r["checked"])})
        milestones = [m for m in summary["milestones"] if m["project"] == pid]
        return templates.TemplateResponse(request, "project.html", {
            "p": info, "groups": groups, "milestones": milestones, "today": summary["today"],
            "entries": db.hours_entries(pid), "rating": db.ratings().get(pid),
        })

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "projects": len(cache.projects()), "version": __version__}

    # ---------------------------------------------------------------------------- API
    @app.get("/api/summary")
    def api_summary():
        return build_summary()

    @app.post("/api/check")
    async def api_check(request: Request):
        body = await json_body(request)
        key = str(body.get("key", ""))
        checked = bool(body.get("checked"))
        items = cache.item_keys()
        milestones = {milestone_key(m["id"]): m for m in schedule["milestones"]}
        if key in items:
            project = items[key].project
            if items[key].repo_done and not checked:
                raise HTTPException(409, "This item is ticked in the repo file itself; untick it there.")
        elif key in milestones:
            project = milestones[key]["project"] or "milestone"
        else:
            raise HTTPException(404, "unknown item (the guide text may have changed; reload)")
        db.set_check(key, project, checked)
        summary = build_summary()
        proj = next((p for p in summary["projects"] if p["id"] == project), None)
        return {"ok": True, "project": proj, "overall": summary["overall"]}

    @app.post("/api/hours")
    async def api_add_hours(request: Request):
        body = await json_body(request)
        pid = str(body.get("project", ""))
        require_project(pid)
        try:
            day = date.fromisoformat(str(body.get("day") or today().isoformat()))
            hrs = float(body.get("hours"))
        except (TypeError, ValueError) as exc:
            raise HTTPException(400, "bad day or hours") from exc
        if not 0 < hrs <= 24:
            raise HTTPException(400, "hours must be between 0 and 24")
        note = str(body.get("note", ""))[:500]
        return {"ok": True, "id": db.add_hours(day.isoformat(), pid, round(hrs, 2), note)}

    @app.delete("/api/hours/{entry_id}")
    def api_delete_hours(entry_id: int):
        if not db.delete_hours(entry_id):
            raise HTTPException(404, "no such entry")
        return {"ok": True}

    @app.post("/api/rating")
    async def api_rating(request: Request):
        body = await json_body(request)
        pid = str(body.get("project", ""))
        require_project(pid)

        def score(name):
            v = body.get(name)
            if v in (None, ""):
                return None
            try:
                v = int(v)
            except (TypeError, ValueError) as exc:
                raise HTTPException(400, f"{name} must be 1-5") from exc
            if not 1 <= v <= 5:
                raise HTTPException(400, f"{name} must be 1-5")
            return v

        want = body.get("want_more")
        db.set_rating(pid, score("enjoyed"), score("natural"),
                      None if want in (None, "") else bool(want), str(body.get("notes", ""))[:1000])
        return {"ok": True}

    @app.post("/api/tasks")
    async def api_add_task(request: Request):
        body = await json_body(request)
        text = str(body.get("text", "")).strip()
        if not text or len(text) > 300:
            raise HTTPException(400, "task text must be 1-300 characters")
        return {"ok": True, "id": db.add_task(text)}

    @app.post("/api/tasks/{task_id}")
    async def api_set_task(task_id: int, request: Request):
        body = await json_body(request)
        if not db.set_task(task_id, bool(body.get("done"))):
            raise HTTPException(404, "no such task")
        return {"ok": True}

    @app.delete("/api/tasks/{task_id}")
    def api_delete_task(task_id: int):
        if not db.delete_task(task_id):
            raise HTTPException(404, "no such task")
        return {"ok": True}

    @app.get("/api/export")
    def api_export():
        return JSONResponse(db.export(), headers={"Content-Disposition": "attachment; filename=tracker-backup.json"})

    return app


app = create_app()
