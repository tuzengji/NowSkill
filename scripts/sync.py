#!/usr/bin/env python3
"""Reconcile user skills with NowSkill, checking upstream updates first."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import urllib.parse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import install


def within(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def has_skill(path: Path) -> bool:
    return any((path / name).is_file() for name in ("SKILL.md", "SKILL.md.disabled"))


def protected_locations(codex_home: Path) -> list[Path]:
    return [
        (codex_home / "skills" / ".system").resolve(),
        (codex_home / "skills" / "codex-primary-runtime").resolve(),
        (codex_home / "plugins" / "cache" / "openai-bundled").resolve(),
        (codex_home / "plugins" / "cache" / "openai-primary-runtime").resolve(),
    ]


def skill_roots(dest: Path | None, extra: list[Path], codex_home: Path) -> tuple[Path, list[Path]]:
    destination = (dest or Path.home() / ".agents" / "skills").expanduser().resolve()
    candidates = [destination]
    if dest is None:
        candidates.append(codex_home / "skills")
    candidates.extend(extra)
    roots = list(dict.fromkeys(path.expanduser().resolve() for path in candidates))
    for root in roots:
        if root == Path(root.anchor) or within(Path.home(), root) or within(install.REPO_ROOT, root):
            raise ValueError(f"Refusing broad or repository-containing skill root: {root}")
        if any(within(root, protected) for protected in protected_locations(codex_home)):
            raise ValueError(f"Refusing built-in skill root: {root}")
        if within(root, (codex_home / "plugins").resolve()) or within(root, Path("/etc/codex").resolve()):
            raise ValueError(f"Refusing plugin or administrator skill root: {root}")
        if ".system" in root.parts or has_skill(root):
            raise ValueError(f"Expected a user skill collection, not an individual/system skill: {root}")
        if exists(root) and not root.is_dir():
            raise ValueError(f"Skill root is not a directory: {root}")
        if any(root != other and within(root, other) for other in roots):
            raise ValueError("Skill roots must not overlap")
        backup_base = (root.parent / "skill-backups").resolve()
        if any(within(backup_base, other) for other in roots):
            raise ValueError("Backup directories must be outside all skill roots")
        if any(within(backup_base, protected) for protected in protected_locations(codex_home)):
            raise ValueError("Backup directories must not point into built-in locations")
    return destination, roots


def inventory(root: Path, protected: list[Path]) -> tuple[set[Path], set[Path]]:
    skills: set[Path] = set()
    preserved: set[Path] = set()

    def visit(folder: Path) -> None:
        for item in sorted(folder.iterdir()):
            if item.name in install.IGNORED_NAMES:
                continue
            if item.name == ".system" or any(within(item.resolve(), path) for path in protected):
                preserved.add(item)
                continue
            if has_skill(item):
                # Never move a skill parent that would also move a protected subtree.
                if any(child.name == ".system" or (
                    child.is_symlink() and any(within(child.resolve(), path) for path in protected)
                ) for child in item.rglob("*")):
                    raise ValueError(f"Protected directory nested inside skill: {item}")
                skills.add(item)
            elif item.is_symlink():
                if item.is_dir():
                    raise ValueError(f"Linked collection needs individual skill links before syncing: {item}")
                if not item.exists():
                    raise ValueError(f"Broken link needs inspection before syncing: {item}")
            elif item.is_dir():
                visit(item)

    if root.exists():
        visit(root)
    return skills, preserved


def tree_digest(root: Path, *, validate: bool = False) -> str:
    digest = hashlib.sha256()

    def fail(error: OSError) -> None:
        raise error

    for folder, directories, files in os.walk(root, followlinks=False, onerror=fail):
        directories[:] = sorted(name for name in directories if name not in install.IGNORED_NAMES)
        for name in sorted(directories + files):
            if name in install.IGNORED_NAMES:
                continue
            item = Path(folder) / name
            relative = item.relative_to(root).as_posix()
            mode = item.lstat().st_mode
            if item.is_symlink():
                link = os.readlink(item)
                if validate and (Path(link).is_absolute() or not within(item.resolve(), root.resolve())):
                    raise ValueError(f"Skill symlink escapes its directory: {item}")
                value = [relative, "link", link]
            elif item.is_file():
                value = [relative, "file", bool(mode & 0o111), hashlib.sha256(item.read_bytes()).hexdigest()]
            elif item.is_dir():
                value = [relative, "directory"]
            else:
                raise ValueError(f"Unsupported skill file type: {item}")
            digest.update(json.dumps(value, ensure_ascii=True).encode() + b"\n")
    return "sha256:" + digest.hexdigest()


def latest_revision(repository: str, tracking_ref: str) -> str:
    output = install.run(["git", "ls-remote", "--exit-code", repository, tracking_ref])
    revisions = {line.split()[0] for line in output.splitlines() if line.strip()}
    if len(revisions) != 1 or not re.fullmatch(r"[0-9a-f]{40}", next(iter(revisions), "")):
        raise ValueError(f"Cannot resolve a unique upstream revision: {repository} {tracking_ref}")
    return revisions.pop()


def updated_source(source: dict[str, Any], ref: str) -> None:
    source["ref"] = ref
    repository = urllib.parse.urlsplit(source["repository"])
    if repository.hostname == "github.com":
        repo_path = repository.path.removesuffix(".git").rstrip("/")
        suffix = "" if source["path"] == "." else "/" + urllib.parse.quote(source["path"], safe="/")
        source["url"] = urllib.parse.urlunsplit(("https", "github.com", f"{repo_path}/tree/{ref}{suffix}", "", ""))


def stage_all(manifest: dict[str, Any], workdir: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    updated = copy.deepcopy(manifest)
    cache = install.SourceCache(workdir / "sources")
    cache.workdir.mkdir()
    revisions: dict[tuple[str, str], str] = {}
    staged: dict[str, Path] = {}
    for entry in updated["skills"]:
        source = entry["source"]
        if source["type"] == "github":
            key = (source["repository"], source.get("update_ref", "HEAD"))
            if key not in revisions:
                revisions[key] = latest_revision(*key)
            ref = revisions[key]
            previous = source["ref"]
            updated_source(source, ref)
            print(f"CHECK {entry['name']}: {previous[:12]} -> {ref[:12]}")
        else:
            print(f"CHECK {entry['name']}: current {source['type']} content")
        target = workdir / "staged" / entry["name"]
        target.parent.mkdir(exist_ok=True)
        install.stage_skill(entry, cache, target)
        install.validate_staged(entry, target)
        content_digest = tree_digest(target, validate=True)
        if source["type"] == "well-known":
            source["content_sha256"] = content_digest
            source.pop("package_digest", None)
        staged[entry["name"]] = target
    return updated, staged


def plan_actions(destination: Path, roots: list[Path], staged: dict[str, Path], protected: list[Path]) -> tuple[list[tuple[Path, Path]], list[Path], list[Path]]:
    found: set[Path] = set()
    preserved: set[Path] = set()
    for root in roots:
        skills, official = inventory(root, protected)
        found.update(skills)
        preserved.update(official)
    targets = {destination / name for name in staged}
    installs: list[tuple[Path, Path]] = []
    unchanged: list[Path] = []
    for name, source in staged.items():
        target = destination / name
        if any(within(item, target) or within(target, item) for item in preserved):
            raise ValueError(f"Target overlaps an official skill: {target}")
        if exists(target) and target not in found:
            raise ValueError(f"Refusing to replace an unrecognized destination: {target}")
        if target in found and not target.is_symlink() and tree_digest(target) == tree_digest(source):
            unchanged.append(target)
        else:
            installs.append((source, target))
    removals = sorted(found - targets)
    for target in sorted(unchanged):
        print(f"KEEP  {target}")
    for source, target in installs:
        print(f"{'UPDATE' if exists(target) else 'ADD'} {target}")
    for target in removals:
        print(f"REMOVE {target} (recoverable backup)")
    for target in sorted(preserved):
        print(f"SYSTEM {target} (preserved)")
    return installs, removals, unchanged


def apply_actions(installs: list[tuple[Path, Path]], removals: list[Path], roots: list[Path], manifest_path: Path, manifest: dict[str, Any]) -> list[Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    backup_roots: set[Path] = set()
    journal: list[tuple[Path, Path | None, bool]] = []
    original_manifest = manifest_path.read_bytes()
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    temporary_manifest: Path | None = None
    try:
        # Prepare all filesystem copies before moving any installed skill.
        with tempfile.TemporaryDirectory(prefix="nowskill-prepared-") as temp:
            prepared: dict[Path, Path] = {}
            for index, (source, target) in enumerate(installs):
                ready = Path(temp) / str(index)
                install.copy_tree(source, ready)
                prepared[target] = ready
            for target in list(prepared) + removals:
                root = next(root for root in roots if within(target, root))
                backup_root = root.parent / "skill-backups" / f"nowskill-{stamp}" / root.name
                backup = None
                if exists(target):
                    backup = backup_root / target.relative_to(root)
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    if exists(backup):
                        raise FileExistsError(backup)
                    shutil.move(str(target), str(backup))
                    backup_roots.add(backup_root)
                journal.append((target, backup, target in prepared))
                if target in prepared:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(prepared[target]), str(target))
        if manifest_bytes != original_manifest:
            with tempfile.NamedTemporaryFile(dir=manifest_path.parent, prefix=".skills-lock-", delete=False) as handle:
                temporary_manifest = Path(handle.name)
                handle.write(manifest_bytes)
            temporary_manifest.chmod(stat.S_IMODE(manifest_path.stat().st_mode))
            os.replace(temporary_manifest, manifest_path)
    except BaseException as error:
        # Reverse the transaction, including duplicate-root removals, on failure.
        rollback_errors = []
        for target, backup, installed in reversed(journal):
            try:
                if installed and exists(target):
                    if target.is_symlink() or not target.is_dir():
                        target.unlink()
                    else:
                        shutil.rmtree(target)
                if backup is not None:
                    shutil.move(str(backup), str(target))
            except Exception as rollback_error:
                rollback_errors.append(f"{target}: {rollback_error}; backup: {backup}")
        if rollback_errors:
            raise RuntimeError("Rollback incomplete; recover these backups manually: " + "; ".join(rollback_errors)) from error
        raise
    finally:
        if temporary_manifest is not None and temporary_manifest.exists():
            temporary_manifest.unlink()
    return sorted(backup_roots)


def sync(manifest_path: Path, dest: Path | None, extra_roots: list[Path], *, dry_run: bool = False) -> int:
    manifest = install.load_manifest(manifest_path)
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser().resolve()
    destination, roots = skill_roots(dest, extra_roots, codex_home)
    protected = protected_locations(codex_home)
    print(f"Destination: {destination}")
    for root in roots:
        print(f"Scope: {root}")
    # Reject ambiguous local layouts before spending time on downloads.
    for root in roots:
        inventory(root, protected)
    with tempfile.TemporaryDirectory(prefix="nowskill-sync-") as temp:
        updated, staged = stage_all(manifest, Path(temp))
        installs, removals, unchanged = plan_actions(destination, roots, staged, protected)
        if dry_run:
            print("DRY RUN: no installed skills or repository files were changed.")
        else:
            for backup in apply_actions(installs, removals, roots, manifest_path, updated):
                print(f"Backups: {backup}")
        print(f"Summary: {len(installs)} installed/updated, {len(removals)} removed, {len(unchanged)} unchanged" + (" (planned)" if dry_run else ""))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, help="Custom destination; disables automatic scanning of the two default user roots")
    parser.add_argument("--root", type=Path, action="append", default=[], help="Additional user skill collection to reconcile; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="Check upstream and preview exact changes without modifying skills or lockfile")
    args = parser.parse_args()
    try:
        return sync(install.MANIFEST_PATH, args.dest, args.root, dry_run=args.dry_run)
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        print("Sync did not complete. No pruning occurs before all sources validate. Failed applies attempt rollback; inspect any reported backup/recovery errors before retrying.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
