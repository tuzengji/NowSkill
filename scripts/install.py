#!/usr/bin/env python3
"""Install the skills declared in ../skills.lock.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "skills.lock.json"
IGNORED_NAMES = {".DS_Store", ".git", "__pycache__"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restore the non-built-in Codex skills in skills.lock.json."
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path.home() / ".agents" / "skills",
        help="Skill destination (default: ~/.agents/skills)",
    )
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="Install only this skill; repeat for more than one",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Do not copy entries preserved in a disabled state",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing skills after backing them up",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without downloading or writing",
    )
    return parser.parse_args()


def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported manifest schema")
    names = [entry.get("name") for entry in manifest.get("skills", [])]
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise ValueError("Every skill needs a non-empty name")
    if len(names) != len(set(names)):
        raise ValueError("Skill names must be unique")
    return manifest


def run(command: list[str], cwd: Path | None = None) -> str:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def safe_child(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"Unsafe relative path: {relative}")
    candidate = (root / rel).resolve()
    candidate.relative_to(root.resolve())
    return candidate


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        symlinks=True,
        ignore=shutil.ignore_patterns(*IGNORED_NAMES),
    )


def copy_selected(source: Path, destination: Path, files: list[str]) -> None:
    destination.mkdir(parents=True)
    for relative in files:
        item = safe_child(source, relative)
        if not item.exists():
            raise FileNotFoundError(f"Missing source file: {relative}")
        target = safe_child(destination, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        if item.is_dir():
            shutil.copytree(item, target, symlinks=True)
        else:
            shutil.copy2(item, target)


class SourceCache:
    def __init__(self, workdir: Path) -> None:
        self.workdir = workdir
        self.github_repositories: dict[tuple[str, str], Path] = {}
        self.well_known_indexes: dict[str, dict[str, Any]] = {}

    def github(self, repository: str, ref: str) -> Path:
        key = (repository, ref)
        if key in self.github_repositories:
            return self.github_repositories[key]

        slug = hashlib.sha256(f"{repository}@{ref}".encode()).hexdigest()[:12]
        checkout = self.workdir / f"github-{slug}"
        checkout.mkdir()
        run(["git", "init", "--quiet"], cwd=checkout)
        run(["git", "remote", "add", "origin", repository], cwd=checkout)
        run(["git", "fetch", "--quiet", "--depth", "1", "origin", ref], cwd=checkout)
        run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)

        actual = run(["git", "rev-parse", "HEAD"], cwd=checkout)
        if len(ref) == 40 and actual != ref:
            raise RuntimeError(f"Expected {ref}, fetched {actual} from {repository}")
        self.github_repositories[key] = checkout
        return checkout

    def well_known(self, base_url: str, skill_name: str, destination: Path) -> None:
        base_url = base_url.rstrip("/")
        if base_url not in self.well_known_indexes:
            index_url = f"{base_url}/.well-known/skills/index.json"
            self.well_known_indexes[base_url] = fetch_json(index_url)

        index = self.well_known_indexes[base_url]
        entry = next(
            (item for item in index.get("skills", []) if item.get("name") == skill_name),
            None,
        )
        if entry is None:
            raise RuntimeError(f"{skill_name} is missing from {base_url} skill index")

        files = entry.get("files") or ["SKILL.md"]
        destination.mkdir(parents=True)
        for relative in files:
            target = safe_child(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            quoted_name = urllib.parse.quote(skill_name, safe="")
            quoted_path = urllib.parse.quote(relative, safe="/")
            url = f"{base_url}/.well-known/skills/{quoted_name}/{quoted_path}"
            target.write_bytes(fetch_bytes(url))


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "NowSkill/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def fetch_json(url: str) -> dict[str, Any]:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def stage_skill(entry: dict[str, Any], cache: SourceCache, destination: Path) -> None:
    source = entry["source"]
    source_type = source["type"]

    if source_type == "bundled":
        source_dir = safe_child(REPO_ROOT, source["path"])
    elif source_type == "github":
        checkout = cache.github(source["repository"], source["ref"])
        source_dir = safe_child(checkout, source["path"])
    elif source_type == "well-known":
        cache.well_known(source["base_url"], entry["name"], destination)
        return
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    files = source.get("files")
    if files:
        copy_selected(source_dir, destination, files)
    else:
        copy_tree(source_dir, destination)


def validate_staged(entry: dict[str, Any], staged: Path) -> None:
    expected = "SKILL.md" if entry.get("enabled", True) else "SKILL.md.disabled"
    if not (staged / expected).is_file():
        raise RuntimeError(f"{entry['name']} does not contain {expected}")


def install_staged(staged: Path, target: Path, backup_root: Path | None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{target.name}.nowskill-", dir=target.parent) as temp:
        prepared = Path(temp) / target.name
        copy_tree(staged, prepared)

        backup: Path | None = None
        if target.exists() or target.is_symlink():
            if backup_root is None:
                raise FileExistsError(target)
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = backup_root / target.name
            if backup.exists() or backup.is_symlink():
                raise FileExistsError(f"Backup already exists: {backup}")
            shutil.move(str(target), str(backup))

        try:
            os.replace(prepared, target)
        except Exception:
            if backup is not None and not target.exists():
                shutil.move(str(backup), str(target))
            raise


def describe_source(entry: dict[str, Any]) -> str:
    source = entry["source"]
    if source["type"] == "github":
        return source["url"]
    if source["type"] == "well-known":
        return source["url"]
    return source["path"]


def main() -> int:
    args = parse_args()
    manifest = load_manifest()
    destination = args.dest.expanduser().resolve()
    selected = set(args.skills or [])
    entries = [
        entry
        for entry in manifest["skills"]
        if (not selected or entry["name"] in selected)
        and (not args.active_only or entry.get("enabled", True))
    ]

    known = {entry["name"] for entry in manifest["skills"]}
    unknown = selected - known
    if unknown:
        print(f"Unknown skill(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2

    print(f"Destination: {destination}")
    if args.dry_run:
        for entry in entries:
            state = "active" if entry.get("enabled", True) else "disabled"
            print(f"PLAN  {entry['name']} ({state}) <- {describe_source(entry)}")
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = destination.parent / "skill-backups" / f"nowskill-{timestamp}"
    installed: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []

    with tempfile.TemporaryDirectory(prefix="nowskill-") as temp:
        workdir = Path(temp)
        cache = SourceCache(workdir / "sources")
        cache.workdir.mkdir()

        for entry in entries:
            name = entry["name"]
            target = destination / name
            if (target.exists() or target.is_symlink()) and not args.force:
                print(f"SKIP  {name}: destination exists")
                skipped.append(name)
                continue

            staged = workdir / "staged" / name
            staged.parent.mkdir(exist_ok=True)
            try:
                stage_skill(entry, cache, staged)
                validate_staged(entry, staged)
                install_staged(staged, target, backup_root if args.force else None)
                state = "active" if entry.get("enabled", True) else "disabled"
                print(f"OK    {name} ({state})")
                installed.append(name)
            except Exception as error:
                print(f"FAIL  {name}: {error}", file=sys.stderr)
                failed.append(name)

    print(
        f"Summary: {len(installed)} installed, {len(skipped)} skipped, "
        f"{len(failed)} failed"
    )
    if args.force and installed and backup_root.exists():
        print(f"Backups: {backup_root}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
