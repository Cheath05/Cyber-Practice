// Cyber-Practice Tracker front-end: no frameworks, no inline scripts (CSP: script-src 'self').
(function () {
  "use strict";
  var HEADERS = { "Content-Type": "application/json", "X-Requested-With": "cyber-tracker" };

  // ---- theme toggle (preference kept in localStorage, which may be unavailable) ----
  function storedTheme() { try { return localStorage.getItem("ct-theme"); } catch (e) { return null; } }
  function applyTheme(t) {
    if (t) { document.documentElement.setAttribute("data-theme", t); }
    else { document.documentElement.removeAttribute("data-theme"); }
  }
  applyTheme(storedTheme());
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem("ct-theme", next); } catch (e) { /* private mode */ }
    });
  });

  function toast(msg) {
    var el = document.getElementById("toast");
    if (!el) return;
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.hidden = true; }, 4000);
  }

  function api(method, url, body) {
    return fetch(url, { method: method, headers: HEADERS, body: body ? JSON.stringify(body) : undefined, credentials: "same-origin" })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          if (!r.ok) throw new Error(data.detail || ("HTTP " + r.status));
          return data;
        });
      });
  }

  function updateProgress(project, overall) {
    if (project) {
      document.querySelectorAll('[data-project="' + project.id + '"]').forEach(function (scope) {
        var pct = scope.querySelector("[data-pct]"), done = scope.querySelector("[data-done]");
        if (pct) pct.textContent = project.pct + "%";
        if (done) done.textContent = project.done;
        var fill = scope.querySelector(".bar-fill");
        if (fill) fill.setAttribute("width", project.pct);
      });
    }
    if (overall) {
      var op = document.querySelector("[data-overall-pct]"), od = document.querySelector("[data-overall-done]");
      if (op) op.textContent = overall.pct + "%";
      if (od) od.textContent = overall.done;
    }
  }

  document.addEventListener("change", function (ev) {
    var t = ev.target;
    if (t.matches("input[type=checkbox][data-key]")) {
      var li = t.closest("li");
      api("POST", "/api/check", { key: t.dataset.key, checked: t.checked })
        .then(function (res) {
          if (li) li.classList.toggle("is-done", t.checked);
          updateProgress(res.project, res.overall);
        })
        .catch(function (err) { t.checked = !t.checked; toast("Couldn't save: " + err.message); });
    } else if (t.matches("input[type=checkbox][data-task-id]")) {
      api("POST", "/api/tasks/" + t.dataset.taskId, { done: t.checked })
        .then(function () { var li2 = t.closest("li"); if (li2) li2.classList.toggle("is-done", t.checked); })
        .catch(function (err) { t.checked = !t.checked; toast("Couldn't save: " + err.message); });
    }
  });

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-delete-url]");
    if (!b) return;
    if (!confirm("Delete this entry?")) return;
    api("DELETE", b.dataset.deleteUrl).then(function () { location.reload(); })
      .catch(function (err) { toast("Couldn't delete: " + err.message); });
  });

  document.addEventListener("submit", function (ev) {
    var f = ev.target, data = new FormData(f), body, url;
    if (f.id === "hours-form") {
      url = "/api/hours";
      body = { project: f.dataset.project, day: data.get("day"), hours: data.get("hours"), note: data.get("note") };
    } else if (f.id === "rating-form") {
      url = "/api/rating";
      body = { project: f.dataset.project, enjoyed: data.get("enjoyed"), natural: data.get("natural"),
               want_more: data.get("want_more") === "on", notes: data.get("notes") };
    } else if (f.id === "task-form") {
      url = "/api/tasks";
      body = { text: data.get("text") };
    } else { return; }
    ev.preventDefault();
    api("POST", url, body).then(function () { location.reload(); })
      .catch(function (err) { toast("Couldn't save: " + err.message); });
  });

  // ---- chart tooltips: follow the pointer over any [data-tip] mark ----
  document.addEventListener("pointermove", function (ev) {
    var tip = document.getElementById("tooltip");
    if (!tip) return;
    var g = ev.target.closest && ev.target.closest("[data-tip]");
    if (!g) { tip.hidden = true; return; }
    tip.textContent = g.getAttribute("data-tip");
    tip.hidden = false;
    var x = Math.min(ev.clientX + 12, window.innerWidth - tip.offsetWidth - 8);
    tip.style.left = x + "px";
    tip.style.top = (ev.clientY - tip.offsetHeight - 10) + "px";
  });
})();
