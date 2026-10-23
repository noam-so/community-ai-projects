#!/usr/bin/env python3
"""
Compile every project file in projects/ into site/projects.json.

Each project is a Markdown file with YAML frontmatter (Open Knowledge Format).
This script checks each file, turns its body into HTML, and writes one JSON
feed that site/index.html reads. If any file has a problem, it lists them all
and stops without writing anything, so a broken file never reaches the site.

Run locally:  python3 scripts/build.py
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "projects"
OUTPUT = ROOT / "site" / "projects.json"

# The only product types allowed. Add a new one here first, then use it.
PRODUCT_TYPES = [
    "Automated publishing",
    "Domain assistant",
    "General assistant",
    "Infrastructure",
    "Shared resource",
    "Specialist processing tool",
]

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def read_project(path):
    """Return (project, problems) for one file."""
    problems = []
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        return None, [f"{path.name}: no frontmatter block at the top"]

    meta = yaml.safe_load(match.group(1)) or {}
    extra = meta.get("x-community-ai") or {}

    for key in ("type", "title", "description", "resource"):
        if not meta.get(key):
            problems.append(f"{path.name}: missing '{key}'")
    for key in ("product_type", "creator"):
        if not extra.get(key):
            problems.append(f"{path.name}: missing 'x-community-ai.{key}'")
    if extra.get("product_type") and extra["product_type"] not in PRODUCT_TYPES:
        problems.append(
            f"{path.name}: product type '{extra['product_type']}' is not in the "
            f"list in scripts/build.py"
        )

    # Shift headings down a level: '## Principles fit' becomes <h3> on the page,
    # because each project title is already an <h2> there.
    body_html = markdown.markdown(
        match.group(2).strip(),
        extensions=["toc"],
        extension_configs={"toc": {"baselevel": 2}},
    )

    project = {
        "slug": path.stem,
        "title": meta.get("title"),
        "description": meta.get("description"),
        "url": meta.get("resource"),
        "status": meta.get("status", "stable"),
        "product_type": extra.get("product_type"),
        "creator": extra.get("creator"),
        "creator_url": extra.get("creator_url"),
        "body_html": body_html,
    }
    return project, problems


def main():
    projects, problems = [], []
    for path in sorted(SOURCE.glob("*.md")):
        if path.name in ("index.md", "log.md"):  # reserved names in OKF
            continue
        project, found = read_project(path)
        problems += found
        if project:
            projects.append(project)

    if problems:
        print("Build stopped. Fix these and run it again:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    projects.sort(key=lambda p: p["title"].lower())
    feed = {
        "meta": {
            "name": "Community AI Projects",
            "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": len(projects),
            "product_types": PRODUCT_TYPES,
        },
        "projects": projects,
    }
    OUTPUT.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(projects)} projects to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
