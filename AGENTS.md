# NowSkill agent instructions

This repository restores the user's non-built-in Codex skills.

On the user's primary machine, this repository is a live mirror of the installed non-built-in Codex skill set. Any local skill installation or removal must update `skills.lock.json`, the README inventory, and owned source files in the same task, then commit and push the change.

When the user asks you to install or restore the skills in this repository:

1. Read `skills.lock.json` and keep its pinned revisions unless the user asks for upgrades.
2. Run `python3 scripts/install.py` from the repository root.
3. Report the installed, skipped, and failed skills exactly as printed by the installer.
4. If an existing destination was skipped, do not overwrite it unless the user explicitly asks; then rerun with `--force`. Existing directories are backed up before replacement.
5. Tell the user to restart Codex if the newly installed skills do not appear.

Repository policy:

- Source code may be committed only for skills marked `owned` in `skills.lock.json`.
- Skills marked `third-party` must remain references only. Never vendor their source into this repository.
- Do not add Codex system or bundled runtime skills. Codex supplies those itself.
- Do not copy credentials, tokens, local configuration, caches, or install logs into this repository.
