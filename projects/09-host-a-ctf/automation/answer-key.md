# Answer Key: Project 09 sample challenges

Flags are generated per run by `make_challenges.py` (except the reversing one, which is fixed in
source). Keep this private if you reuse the set.

| Challenge | Category | Intended solution |
|---|---|---|
| Layers | crypto | base64 -d, then ROT13 → `homelab{crypto_layers_...}` |
| Look Closer | forensics/OSINT | `exiftool vacation.png` (or `strings`) reveals the Comment field |
| (reversing) checker | reversing | `strings checker` shows `r3verse_me_2026`; run it to get `flag{homelab_reversing_is_fun}` |

Run `python3 python/make_challenges.py --out build` to (re)generate the per-event flags; it
prints the crypto and forensics flags.
