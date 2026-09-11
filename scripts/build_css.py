#!/usr/bin/env python3
"""Generate theme/static/css/main.css with the Tailwind standalone CLI.

    python3 scripts/build_css.py            # regenerate the stylesheet
    python3 scripts/build_css.py --watch    # rebuild on template changes
    python3 scripts/build_css.py --check    # fail if the committed CSS is stale

The CLI is a single self-contained binary -- no Node, no npm, no node_modules.
It is fetched once into .cache/tailwind/ (gitignored) and checksum-verified
against the release's own sha256sums.txt.

main.css is committed because the deploy workflow has no way to build it. That
means adding a utility class to a template is only half the change: regenerate
and commit the CSS too, or the class will silently do nothing in production.
"""
import argparse
import hashlib
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

VERSION = "3.4.19"
BASE_URL = f"https://github.com/tailwindlabs/tailwindcss/releases/download/v{VERSION}"

ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = ROOT / ".cache" / "tailwind"
SCAN_DIR = ROOT / ".cache" / "css-scan"
CONFIG = ROOT / "scripts" / "tailwind" / "tailwind.config.js"
INPUT = ROOT / "scripts" / "tailwind" / "input.css"
OUTPUT = ROOT / "theme" / "static" / "css" / "main.css"


def asset_name():
    """Map this machine to a release asset."""
    system, machine = platform.system(), platform.machine().lower()
    arch = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(machine)
    if arch is None:
        sys.exit(f"unsupported architecture: {platform.machine()}")
    if system == "Darwin":
        return f"tailwindcss-macos-{arch}"
    if system == "Linux":
        return f"tailwindcss-linux-{arch}"
    if system == "Windows":
        return f"tailwindcss-windows-{arch}.exe"
    sys.exit(f"unsupported platform: {system}")


def expected_sha(name):
    """Pull the official checksum for this asset from the release."""
    with urllib.request.urlopen(f"{BASE_URL}/sha256sums.txt") as r:
        for line in r.read().decode().splitlines():
            digest, _, path = line.partition("  ")
            if path.strip().lstrip("./") == name:
                return digest.strip()
    sys.exit(f"no checksum published for {name}")


def ensure_cli():
    """Download and verify the binary once; reuse it after that."""
    name = asset_name()
    # Version in the filename so a bump fetches cleanly instead of reusing a stale binary.
    dest = BIN_DIR / f"{name}-{VERSION}"
    if dest.exists():
        return dest

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    print(f"fetching tailwindcss {VERSION} ({name})...")
    tmp = dest.with_suffix(".part")
    urllib.request.urlretrieve(f"{BASE_URL}/{name}", tmp)

    want = expected_sha(name)
    got = hashlib.sha256(tmp.read_bytes()).hexdigest()
    if got != want:
        tmp.unlink(missing_ok=True)
        sys.exit(f"checksum mismatch for {name}\n  expected {want}\n  got      {got}")
    print(f"  verified sha256 {got[:16]}...")

    tmp.chmod(0o755)
    tmp.rename(dest)
    return dest


def build_scan_site():
    """Build the site so the CLI can scan generated HTML, not just templates."""
    if SCAN_DIR.exists():
        shutil.rmtree(SCAN_DIR)
    subprocess.run(
        ["uv", "run", "pelican", "content", "-o", str(SCAN_DIR), "-s", "pelicanconf.py", "-q"],
        cwd=ROOT,
        check=True,
    )


def run_cli(cli, out, watch=False):
    cmd = [str(cli), "build", "-c", str(CONFIG), "-i", str(INPUT), "-o", str(out)]
    if watch:
        cmd.append("--watch")
    # cwd must be the repo root: the config's content globs are relative to it.
    subprocess.run(cmd, cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--watch", action="store_true",
                   help="rebuild as templates change (does not re-run Pelican)")
    g.add_argument("--check", action="store_true",
                   help="exit non-zero if the committed CSS is out of date")
    args = ap.parse_args()

    cli = ensure_cli()
    build_scan_site()

    if args.check:
        with tempfile.TemporaryDirectory() as td:
            fresh = Path(td) / "main.css"
            run_cli(cli, fresh)
            current = OUTPUT.read_text() if OUTPUT.exists() else ""
            if fresh.read_text() != current:
                sys.exit(f"{OUTPUT.relative_to(ROOT)} is out of date -- "
                         f"run: python3 scripts/build_css.py")
        print(f"{OUTPUT.relative_to(ROOT)} is up to date")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    run_cli(cli, OUTPUT, watch=args.watch)
    if not args.watch:
        raw = OUTPUT.stat().st_size
        print(f"\nwrote {OUTPUT.relative_to(ROOT)} -- {raw // 1024}KB")


if __name__ == "__main__":
    main()
