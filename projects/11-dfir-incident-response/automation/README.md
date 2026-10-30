# ⚠️ Solution: use only if stuck

**Spoilers.** If you're the investigator, don't read `incident-sim.sh` or `answer-key.md` until
your report is done. Have a friend run the simulation.

| File | Run where | What it does |
|---|---|---|
| `incident-sim.sh` | victim VM (guarded) | Simulates an intrusion with **inert** artifacts to investigate |
| `triage-collect.sh` | victim VM | Collects volatile state + key logs into a timestamped, hashed tarball |
| `answer-key.md` | — | Every simulated artifact and where to find it |
| `python/build_timeline.py` | analysis box | Python exercise: mini super-timeline from a mounted image |
| `cpp/carver.cpp` + `Makefile` | analysis box | C++ exercise: JPEG carver; `make test` builds a test image and carves it |
| `cpp/make_test_image.py` | analysis box | Builds a fake "disk image" with embedded JPEGs for testing the carver |
