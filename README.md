# Community AI Projects

Field notes on AI projects in the UK, published as a simple web page.

Each project is one Markdown file in [`projects/`](projects), written in [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) (YAML frontmatter at the top, prose underneath). A small script turns those files into one JSON feed, and a single web page displays it.

This is a working prototype. The notes are drafts, not endorsements or ratings.

## How it fits together

```
projects/*.md   ->   scripts/build.py   ->   site/projects.json   ->   site/index.html
(the notes)          (checks and compiles)   (generated feed)         (the page)
```

`site/projects.json` is generated, never edited by hand, and isn't saved in the repository. A GitHub Action rebuilds it and republishes the site every time something changes on `main`.

## Add or edit a project

1. Copy an existing file in `projects/` and rename it, using lowercase and hyphens (`my-project.md`).
2. Edit the frontmatter and the text under `## Principles fit`.
3. Commit to `main`. The site updates a minute or two later.

`product_type` must be one of the types listed at the top of `scripts/build.py`. If a file is missing a field or uses a new type, the build stops, lists the problem in the Actions tab, and the live site stays as it was.

## Preview on your own computer

You'll need Python 3.

```
pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server -d site
```

Then open http://localhost:8000. Opening `index.html` directly won't work, because the page has to fetch the feed from a server.
