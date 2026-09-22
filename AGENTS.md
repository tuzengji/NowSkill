# NowSkill agent instructions

This public repository is the desired set of the user's non-built-in skills.

## When the user hands you this repository to set up or sync their Agent

Treat that request as authorization to install, update, and reconcile user-level skills. Do not ask again for each replacement or removal. A request only to read, review, or edit this repository does not authorize changing the current machine's installed skills.

1. Clone this repository, or update an existing clean checkout using `git pull --ff-only` before syncing. Never discard local work to update it; report conflicts. Read `skills.lock.json` and identify the receiving Agent's user-level skill roots. For Codex, the default command covers `~/.agents/skills` and `$CODEX_HOME/skills` (or `~/.codex/skills`). The manifest is authoritative: do not import the receiving machine's extra skills into it before syncing.
2. Run `python3 scripts/sync.py` from this repository. This checks the latest upstream revisions, stages and validates every required skill, installs or updates all manifest entries, and removes non-built-in skills absent from the manifest. Existing local modifications are backed up and replaced. Duplicates in the legacy root are removed after the canonical copy is installed.
3. For another Agent, use `--dest /path/to/its/user/skills` and repeat `--root /path/to/another/user/skills` as needed. Explicit `--dest` scopes cleanup to that destination plus explicit `--root` paths; it does not scan Codex's default directories. Never pass a home directory, repository root, system directory, or plugin cache as a skill root.
4. Preserve Codex system skills, bundled runtime skills, project/admin skills, unrelated files, and the source targets of skill symlinks. Official means built-in/system/runtime, not merely an OpenAI-authored standalone skill. OpenAI curated skills in the manifest are managed like other manually installed skills.
5. Audit the receiving Agent's actual skill inventory after the script. User-installed third-party plugin skills may require that Agent's supported uninstall mechanism; do not delete cache folders as an uninstall, or remove unrelated connectors/configuration. Report any extra skills that could not safely be removed and do not claim full reconciliation while extras remain. Respect higher-priority host approval rules.
6. Keep the updated Git revisions and well-known content hashes written to `skills.lock.json`. Third-party source code must never enter this repository. After successful synchronization, commit and push lockfile changes when the user has repository write access; otherwise retain the local lockfile and report that it was not pushed. Do not request new credentials or discard unrelated changes just to push.
7. Report actual installed/updated, removed, unchanged, failed, and out-of-scope items, plus backup locations. If the command fails, stop: do not manually prune the remaining skills. Skills are normally detected automatically; restart the Agent only if needed.

`--dry-run` performs upstream checks and downloads into temporary storage but changes neither installed skills nor the repository. Do not run simultaneous syncs or modify skill roots while syncing. `scripts/install.py` remains a pinned, additive restore tool; it does **not** satisfy a full synchronization request.

## Ongoing synchronization

On the user's primary machine, this repository is also a live mirror of the installed non-built-in skill set. An explicit local installation or removal changes the desired set: update `skills.lock.json`, the README inventory, and owned source files in the same task, then commit and push. An explicit skill update must likewise update the recorded revision or content hash. Receiving-machine synchronization flows from the repository to the machine, not in the opposite direction.

These are Agent workflow rules, not a background filesystem watcher. Apply them whenever handling skill changes; do not promise automatic detection of changes made outside an Agent task.

## Repository policy

- Keep `https://github.com/tuzengji/NowSkill` public.
- Commit source code only for skills marked `owned` in `skills.lock.json`.
- Keep `third-party` skills as source links, paths, revisions, and content hashes only.
- Exclude Codex system and bundled runtime skills.
- Never commit credentials, tokens, local configuration, caches, downloaded third-party code, backups, or install logs.
- Preserve unrelated working-tree changes. Run `python3 -m unittest discover -s tests -v` after changing synchronization behavior.
