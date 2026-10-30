#!/usr/bin/env python3
"""Generate CTF challenge material (Project 09 Python exercise, solution).

Creates:
  - a multi-layer crypto string (base64(rot13(flag))) + the flag, for a crypto challenge
  - an image with the flag stored in an EXIF/PNG text field, for an OSINT/forensics challenge
  - challenges.csv for CTFd bulk import

    python3 make_challenges.py --out ./build
    (Pillow is only needed for the image: pip install pillow)
"""
import argparse
import base64
import codecs
import csv
import os
import secrets


def make_flag(name):
    return f"homelab{{{name}_{secrets.token_hex(4)}}}"


def crypto_challenge():
    flag = make_flag("crypto_layers")
    rot = codecs.encode(flag, "rot_13")
    encoded = base64.b64encode(rot.encode()).decode()
    prompt = ("Peel back the layers. We intercepted this string:\n\n"
              f"{encoded}\n\nThe flag is in there.")
    return flag, prompt


def exif_challenge(out_dir):
    flag = make_flag("look_closer")
    path = os.path.join(out_dir, "vacation.png")
    try:
        from PIL import Image, PngImagePlugin
    except ImportError:
        with open(path + ".txt", "w", encoding="utf-8") as fh:
            fh.write(f"(install Pillow to generate the real image)\nflag would be: {flag}\n")
        return flag, path + ".txt"
    img = Image.new("RGB", (320, 200), (40, 90, 160))
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Comment", f"Nice photo! {flag}")
    img.save(path, pnginfo=meta)
    return flag, path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="build")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

    c_flag, c_prompt = crypto_challenge()
    e_flag, e_path = exif_challenge(args.out)

    with open(os.path.join(args.out, "crypto_prompt.txt"), "w", encoding="utf-8") as fh:
        fh.write(c_prompt)

    rows = [
        {"name": "Layers", "category": "crypto", "value": 100,
         "description": "See crypto_prompt.txt", "flag": c_flag},
        {"name": "Look Closer", "category": "forensics", "value": 100,
         "description": f"Inspect the attached image ({os.path.basename(e_path)}).", "flag": e_flag},
    ]
    with open(os.path.join(args.out, "challenges.csv"), "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "category", "value", "description", "flag"])
        writer.writeheader()
        writer.writerows(rows)

    print("Generated in", args.out)
    print("ANSWER KEY (keep private):")
    for r in rows:
        print(f"  {r['name']:<14} {r['flag']}")


if __name__ == "__main__":
    main()
