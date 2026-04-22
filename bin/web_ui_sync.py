#!/usr/bin/env python3
"""Sync Web UI assets into data/static for firmware builds.

Behavior:
- If MESHTASTIC_WEB_SOURCE is set, build/copy from that local checkout.
- Otherwise, fetch the pinned meshtastic/web release referenced by bin/web.version.
- Skip re-downloading the release when the local cache already matches the pin.

The script is intentionally conservative:
- It keeps .gitkeep in data/static.
- It copies the built site output into data/static as plain files.
- It leaves compression decisions to the source web build pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.request import urlopen


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def state_file(root: Path) -> Path:
    return root / ".cache" / "web-ui-sync.json"


def read_web_version(root: Path) -> str:
    return (root / "bin" / "web.version").read_text(encoding="utf-8").strip()


def has_web_content(dest: Path) -> bool:
    if not dest.exists():
        return False
    for entry in dest.iterdir():
        if entry.name != ".gitkeep":
            return True
    return False


def clear_dir(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for entry in list(dest.iterdir()):
        if entry.name == ".gitkeep":
            continue
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def copy_tree(src: Path, dest: Path) -> None:
    clear_dir(dest)
    for entry in src.iterdir():
        if entry.name == ".gitkeep":
            continue
        target = dest / entry.name
        if entry.is_dir() and not entry.is_symlink():
            shutil.copytree(entry, target, symlinks=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry, target)
    (dest / ".gitkeep").touch(exist_ok=True)


def resolve_site_root(base: Path, dist_dir: str) -> Path:
    candidates = [base, base / dist_dir, base / "build", base / "web", base / "public"]
    for candidate in candidates:
        if (candidate / "index.html").exists() or (candidate / "index.html.gz").exists():
            return candidate
    for index_name in ("index.html", "index.html.gz"):
        matches = sorted(base.rglob(index_name))
        if matches:
            return matches[0].parent
    return base


def detect_build_cmd(source: Path) -> str | None:
    override = os.environ.get("MESHTASTIC_WEB_BUILD_CMD", "").strip()
    if override:
        return override

    if not (source / "package.json").exists():
        return None

    if (source / "pnpm-lock.yaml").exists():
        return "pnpm build"
    if (source / "yarn.lock").exists():
        return "yarn build"
    return "npm run build"


def run_build(source: Path) -> None:
    if os.environ.get("MESHTASTIC_WEB_SKIP_BUILD", "").strip().lower() in {"1", "true", "yes", "on"}:
        return

    cmd = detect_build_cmd(source)
    if not cmd:
        return

    print(f"[web-ui] building source at {source} with: {cmd}")
    subprocess.run(cmd, cwd=source, shell=True, check=True)


def sync_from_local_source(source: Path, dest: Path, dist_dir: str, dist_dir_explicit: bool) -> None:
    source = source.expanduser().resolve()
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"Web source directory not found: {source}")

    run_build(source)

    if dist_dir_explicit:
        explicit_root = source / dist_dir
        if not explicit_root.exists():
            raise FileNotFoundError(
                f"MESHTASTIC_WEB_DIST_DIR points to a missing directory: {explicit_root}"
            )
        if not (explicit_root / "index.html").exists() and not (explicit_root / "index.html.gz").exists():
            raise FileNotFoundError(
                f"MESHTASTIC_WEB_DIST_DIR does not look like a web output root: {explicit_root}"
            )
        site_root = explicit_root
    else:
        site_root = resolve_site_root(source, dist_dir)

    if site_root == source and not (site_root / "index.html").exists() and not (site_root / "index.html.gz").exists():
        raise FileNotFoundError(
            f"Could not find a web build output under {source}. "
            f"Set MESHTASTIC_WEB_DIST_DIR if your build output is elsewhere."
        )

    print(f"[web-ui] syncing local web UI from {site_root} -> {dest}")
    copy_tree(site_root, dest)


def download_release_tar(repo: str, version: str, tempdir: Path) -> Path:
    url = f"https://github.com/{repo}/releases/download/v{version}/build.tar"
    tar_path = tempdir / "build.tar"
    print(f"[web-ui] downloading {url}")
    with urlopen(url) as response, tar_path.open("wb") as out:
        shutil.copyfileobj(response, out)
    return tar_path


def extract_tarball(tar_path: Path, tempdir: Path) -> Path:
    extract_dir = tempdir / "extract"
    extract_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path) as archive:
        archive.extractall(extract_dir)
    return resolve_site_root(extract_dir, "dist")


def sync_from_release(root: Path, dest: Path, repo: str, version: str) -> None:
    cache = state_file(root)
    cache_data = None
    if cache.exists():
        try:
            cache_data = json.loads(cache.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache_data = None

    if has_web_content(dest) and cache_data == {"mode": "release", "repo": repo, "version": version}:
        print("[web-ui] release assets already synced")
        return

    with tempfile.TemporaryDirectory() as td:
        tempdir = Path(td)
        tar_path = download_release_tar(repo, version, tempdir)
        site_root = extract_tarball(tar_path, tempdir)
        if not site_root.exists():
            raise FileNotFoundError(
                f"Downloaded release tarball from {repo} did not contain a usable web root. "
                "If the release layout changed, set MESHTASTIC_WEB_SOURCE to a local checkout."
            )
        print(f"[web-ui] syncing release web UI from {site_root} -> {dest}")
        copy_tree(site_root, dest)

    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"mode": "release", "repo": repo, "version": version}, indent=2), encoding="utf-8")


def normalize_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", default=None, help="Firmware repository root; defaults to the script location.")
    parser.add_argument("--output-dir", default=None, help="Destination directory under the firmware repo.")
    parser.add_argument("--source", default=None, help="Local web checkout to build/copy from.")
    parser.add_argument("--dist-dir", default=None, help="Build output subdirectory under the local web checkout.")
    parser.add_argument("--build-cmd", default=None, help="Override build command for the local web checkout.")
    parser.add_argument("--release-repo", default=None, help="Release repository to download from.")
    parser.add_argument("--release-version", default=None, help="Pinned release version to download.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_dir).expanduser().resolve() if args.project_dir else repo_root()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (root / "data" / "static")
    env_dist_dir = os.environ.get("MESHTASTIC_WEB_DIST_DIR")
    dist_dir = args.dist_dir or env_dist_dir or "dist"
    dist_dir_explicit = args.dist_dir is not None or env_dist_dir is not None
    source = normalize_path(args.source or os.environ.get("MESHTASTIC_WEB_SOURCE"))
    build_cmd = args.build_cmd or os.environ.get("MESHTASTIC_WEB_BUILD_CMD", "")
    release_repo = args.release_repo or os.environ.get("MESHTASTIC_WEB_RELEASE_REPO", "meshtastic/web")
    release_version = args.release_version or os.environ.get("MESHTASTIC_WEB_RELEASE_VERSION")
    if not release_version:
        release_version = read_web_version(root)

    if source is not None:
        if build_cmd:
            os.environ["MESHTASTIC_WEB_BUILD_CMD"] = build_cmd
        sync_from_local_source(source, output_dir, dist_dir, dist_dir_explicit)
        return 0

    sync_from_release(root, output_dir, release_repo, release_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
