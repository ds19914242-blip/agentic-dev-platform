# CLI Layout

Target CLI structure:

agentic.py
  -> orchestrator/application/command_registry.py
  -> cli/commands/*.py

## Rules

- `agentic.py` is the only stable root executable.
- New commands should be added to `cli/commands/`.
- Old root scripts remain as compatibility wrappers until migrated.
- Deprecated latest-run scripts move to `cli/legacy/`.
- Developer-only helpers move to `tools/`.

## Target root

The repository root should eventually contain:

- agentic.py
- README.md
- docs/
- orchestrator/
- products/
- cli/
- tools/

No new root-level workflow scripts should be added.
