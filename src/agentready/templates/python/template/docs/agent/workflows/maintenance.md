# Maintenance workflow

Select one READY MAINTENANCE item. Identify affected tooling/configuration → establish baseline → check compatibility and risk → make minimum change → targeted validation → required gates → evaluate README/architecture impact → complete record and changelog → DONE → sync registry → stop.

For dependency additions/upgrades, justify each direct dependency; review relevant release notes,
compatibility, and known security impact; choose constraints for supported compatibility; update
`uv.lock`; run focused compatibility tests and required project gates. Remove unused direct
dependencies, avoid intentional transitive imports, and avoid unrelated broad upgrades.
