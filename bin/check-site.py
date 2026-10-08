#!/usr/bin/env python3
"""Validate published content and local references without making network requests."""

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = Counter()
        self.references = []
        self.tabs = []
        self.panels = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids[attrs["id"]] += 1
        for attr in ("href", "src"):
            if attr in attrs:
                self.references.append((attrs[attr], self.getpos()[0]))
        if "srcset" in attrs:
            for candidate in attrs["srcset"].split(","):
                parts = candidate.strip().split()
                if parts:
                    self.references.append((parts[0], self.getpos()[0]))
        if attrs.get("role") == "tab":
            self.tabs.append(attrs)
        if attrs.get("role") == "tabpanel":
            self.panels.append(attrs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", nargs="?", default="_site", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent
    site = args.site_dir.resolve()
    errors = []

    def error(message):
        errors.append(message)

    if not (site / "index.html").is_file():
        parser.error(f"{site} has no index.html; build the site first")

    # Use the project's Ruby YAML parser; Python needs no additional packages.
    yaml_reader = (
        "require 'yaml'; require 'json'; "
        "puts JSON.generate(ARGV.map { |path| YAML.safe_load(File.read(path)) })"
    )
    result = subprocess.run(
        ["ruby", "-e", yaml_reader, str(source / "_config.yml"),
         str(source / "_data/publications.yaml"), str(source / "_data/news.yaml")],
        check=True, capture_output=True, text=True,
    )
    config, publication_data, news_data = json.loads(result.stdout)
    def records(data, key, filename):
        if not isinstance(data, dict) or not isinstance(data.get(key), list):
            error(f"{filename}: {key} must be a list")
            return []
        return data[key]

    papers = records(publication_data, "papers", "publications.yaml")
    news = records(news_data, "items", "news.yaml")
    types = {"preprint", "journal", "ml_conference", "book_chapter"}

    def required(record, fields, label):
        if not isinstance(record, dict):
            error(f"{label}: expected a mapping")
            return False
        valid = True
        for field in fields:
            if not isinstance(record.get(field), str) or not record[field].strip():
                error(f"{label}: missing or empty {field}")
                valid = False
        return valid

    def valid_url(value, label):
        if not isinstance(value, str) or not value or any(c.isspace() for c in value):
            error(f"{label}: invalid URL {value!r}")
            return
        try:
            parsed = urlsplit(value)
            if parsed.scheme and (parsed.scheme not in {"http", "https"} or not parsed.netloc):
                error(f"{label}: invalid URL {value!r}")
        except ValueError:
            error(f"{label}: invalid URL {value!r}")

    for index, paper in enumerate(papers, start=1):
        label = f"publications.yaml paper {index}"
        if not required(paper, ("title", "authors", "venue", "publication_type", "selected"), label):
            continue
        if paper.get("publication_type") not in types:
            error(f"{label}: unknown publication_type {paper.get('publication_type')!r}")
        if paper.get("selected") not in {"y", "n"}:
            error(f"{label}: selected must be y or n")
        for field in ("paper_pdf", "slides", "poster", "video", "code", "website", "data"):
            if field in paper:
                valid_url(paper[field], f"{label} {field}")

    for index, item in enumerate(news, start=1):
        label = f"news.yaml item {index}"
        if not required(item, ("date", "text", "archived"), label):
            continue
        if item.get("archived") not in {"y", "n"}:
            error(f"{label}: archived must be y or n")
        links = item.get("links", [])
        if not isinstance(links, list):
            error(f"{label}: links must be a list")
            continue
        for link_index, link in enumerate(links, start=1):
            link_label = f"{label} link {link_index}"
            if required(link, ("label", "url"), link_label):
                valid_url(link.get("url"), link_label)

    pages = {path.resolve(): Page(path) for path in sorted(site.rglob("*.html"))}
    hostname = urlsplit(config.get("url", "")).hostname
    baseurl = config.get("baseurl", "").rstrip("/")

    for path, page in pages.items():
        label = str(path.relative_to(site))
        for identifier, count in page.ids.items():
            if not identifier or count > 1:
                error(f"{label}: empty or duplicate id {identifier!r}")
        panel_ids = {panel.get("id") for panel in page.panels}
        tab_ids = {tab.get("id") for tab in page.tabs}
        for tab in page.tabs:
            if not tab.get("id") or tab.get("aria-controls") not in panel_ids:
                error(f"{label}: tab {tab.get('id')!r} must control an existing tabpanel")
        for panel in page.panels:
            if not panel.get("id") or panel.get("aria-labelledby") not in tab_ids:
                error(f"{label}: tabpanel {panel.get('id')!r} must be labelled by an existing tab")

        for value, line in page.references:
            reference_label = f"{label}:{line}"
            if value is None or not value.strip():
                error(f"{reference_label}: empty local reference")
                continue
            try:
                url = urlsplit(value)
            except ValueError:
                error(f"{reference_label}: malformed reference {value!r}")
                continue
            if url.scheme and url.scheme not in {"http", "https"}:
                continue
            if url.netloc and url.hostname != hostname:
                continue
            target_path = unquote(url.path)
            if baseurl and (target_path == baseurl or target_path.startswith(baseurl + "/")):
                target_path = target_path[len(baseurl):] or "/"
            if target_path.startswith("/"):
                target = site / target_path.lstrip("/")
            elif target_path:
                target = path.parent / target_path
            else:
                target = path
            target = target.resolve()
            if not target.is_relative_to(site):
                error(f"{reference_label}: reference leaves the built site: {value!r}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                error(f"{reference_label}: missing local target {value!r}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                error(f"{reference_label}: missing fragment in {value!r}")

    if errors:
        print("Site content checks failed:", file=sys.stderr)
        for message in errors:
            print(f"- {message}", file=sys.stderr)
        return 1
    print(f"Site content checks passed: {len(papers)} publications, {len(news)} news items, {len(pages)} HTML pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
