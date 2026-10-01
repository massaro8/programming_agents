"""Read-only static validation for generated skill contracts and routing."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from skill_routes import EXPECTED_SKILLS, ROUTES, SECURITY_MODES


class SkillCheckError(ValueError):
    """Generated skills or routes violate their static contract."""


LINK = re.compile(r"\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\n(?P<fields>[\s\S]*?)\n---\n(?P<body>[\s\S]*)\Z")


def _read_skill(path: Path) -> tuple[str, str, str]:
    if path.is_symlink() or not path.is_file():
        raise SkillCheckError(f"missing or unsafe skill: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SkillCheckError(f"cannot read {path}: {exc}") from exc
    match = FRONTMATTER.fullmatch(text)
    if not match:
        raise SkillCheckError(f"invalid YAML frontmatter: {path}")
    fields = match.group("fields").splitlines()
    names = [line[6:].strip() for line in fields if line.startswith("name: ")]
    descriptions = [line[13:].strip() for line in fields if line.startswith("description: ")]
    if len(names) != 1 or len(descriptions) != 1 or not names[0] or len(descriptions[0]) < 35:
        raise SkillCheckError(f"frontmatter needs one name and useful description: {path}")
    return names[0], descriptions[0], match.group("body")


def check(root: Path) -> None:
    canonical = root / ".agents" / "skills"
    provider = root / ".claude" / "skills"
    names = set(EXPECTED_SKILLS)
    descriptions: dict[str, str] = {}
    canonical_text: dict[str, str] = {}
    for label, base in (("canonical", canonical), ("provider", provider)):
        if base.is_symlink() or not base.is_dir():
            raise SkillCheckError(f"missing or unsafe {label} skill directory: {base}")
        entries = sorted(base.rglob("SKILL.md"))
        found = [path.parent.name for path in entries]
        if len(found) != len(set(found)) or set(found) != names:
            missing, extra = sorted(names - set(found)), sorted(set(found) - names)
            raise SkillCheckError(
                f"{label} skills differ from expected set; missing {missing}, extra {extra}"
            )
        frontmatter_names: list[str] = []
        for path in entries:
            name, description, body = _read_skill(path)
            frontmatter_names.append(name)
            if name != path.parent.name:
                raise SkillCheckError(f"skill name/path conflict: {path}")
            if label == "canonical":
                descriptions[name] = description
                canonical_text[name] = path.read_text(encoding="utf-8")
                for target in LINK.findall(body):
                    if target.startswith(("https://", "http://", "#", "mailto:")):
                        continue
                    if not (path.parent / target.split("#", 1)[0]).resolve().is_file():
                        raise SkillCheckError(f"broken skill link in {path}: {target}")
            elif path.read_text(encoding="utf-8") != canonical_text.get(name):
                raise SkillCheckError(f"provider skill drift: {name}")
        if len(frontmatter_names) != len(set(frontmatter_names)):
            raise SkillCheckError(f"duplicate frontmatter skill names in {label} tree")
    if len({text.lower() for text in descriptions.values()}) != len(names):
        raise SkillCheckError("skill descriptions must be distinct")
    if set(ROUTES) != {"FEATURE", "BUGFIX", "REFACTOR", "MAINTENANCE", "DOCS", "SECURITY"}:
        raise SkillCheckError("work type routing is incomplete or contains unexpected types")
    for kind, route in ROUTES.items():
        if route["skill"] not in names:
            raise SkillCheckError(f"unknown skill for {kind}: {route['skill']}")
        for target in (route["workflow"], *route["standards"]):
            if not (root / target).is_file():
                raise SkillCheckError(f"missing route context for {kind}: {target}")
    if set(SECURITY_MODES) != {"review-only", "implementation"}:
        raise SkillCheckError("security modes are incomplete")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    try:
        check(root)
    except (SkillCheckError, OSError, UnicodeError) as exc:
        print(f"skill check: {exc}", file=sys.stderr)
        return 1
    print("skill contracts and routes are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
