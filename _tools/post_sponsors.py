#!/usr/bin/env python3
"""Posting step: validate -> render -> re-validate -> guard checks -> commit -> push.

  python3 _tools/post_sponsors.py            # dry run: validate + render, no commit
  python3 _tools/post_sponsors.py --push -m "Sponsors: add Acme Movers (Featured)"
"""
import argparse, glob, os, subprocess, sys
import sponsors_lib as L

AUTHOR = "Tangent Real Estate <hello@columbuslivingwell.com>"


def run(*cmd):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=L.ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    ap.add_argument("-m", "--message", default="Sponsors: update sponsor listings")
    a = ap.parse_args()
    py = sys.executable
    tools = os.path.join(L.ROOT, "_tools")
    run(py, os.path.join(tools, "validate_sponsors.py"))
    run(py, os.path.join(tools, "render_sponsors.py"))
    # guard: the owner's personal name must never be published
    for p in glob.glob(os.path.join(L.ROOT, "*.html")) + [L.DATA]:
        with open(p, encoding="utf-8") as f:
            low = f.read().lower()
        for w in L.FORBIDDEN_TEXT:
            if w in low:
                sys.exit(f"ABORT: forbidden name '{w}' found in {os.path.basename(p)}")
    if not a.push:
        run("git", "status", "--short")
        print("Dry run complete (no commit). Re-run with --push to publish.")
        return 0
    run("git", "add", "-A", "sponsors.json", "img/sponsors", "*.html")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=L.ROOT).returncode == 0:
        print("Nothing to publish.")
        return 0
    run("git", "-c", "user.name=Tangent Real Estate", "-c", "user.email=hello@columbuslivingwell.com",
        "commit", f"--author={AUTHOR}", "-m", a.message)
    run("git", "push", "origin", "HEAD:main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
