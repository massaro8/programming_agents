# Module placement workflow

Input: a proposed new or moved source module and its responsibility. Inspect
`docs/generated/CODEBASE_MAP.md`, identify the owning domain or capability, and inspect the nearby
architecture pattern. Classify it as domain, application, adapter, entrypoint, platform, shared, or
composition/configuration. Choose the narrowest coherent location; avoid package-root dumping and
speculative directories. Update architecture or map inputs only when structure materially changes,
then run `python scripts/architecture_check.py`. Done when the location follows dependency
direction and the structural check passes; explain any justified exception.
For a new capability, create only its package root and knowledge card with
`python scripts/module_knowledge.py new <capability> --responsibility "..."`. Record public surface,
external boundaries, and tests in `docs/modules/<capability>.md` only when known. Verify the card
inventory with `python scripts/module_knowledge.py check` and regenerate the map.
