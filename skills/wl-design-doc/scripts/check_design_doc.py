#!/usr/bin/env python3
"""Check structural invariants of one wl-design-doc HTML artifact."""
from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.embedded_resources: list[tuple[str, str]] = []
        self.meta_text: list[str] = []
        self._in_meta = False
        self.meta_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(str(values["id"]))
        if tag == "script" and values.get("id") == "wl-design-meta":
            self.meta_count += 1
            self._in_meta = True
        if tag in {"script", "link", "img", "iframe", "video", "audio"}:
            attr = "src" if tag != "link" else "href"
            value = values.get(attr)
            if value:
                self.embedded_resources.append((tag, str(value)))
        if tag == "a" and values.get("href"):
            self.links.append(("a", str(values["href"])))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_meta:
            self._in_meta = False

    def handle_data(self, data: str) -> None:
        if self._in_meta:
            self.meta_text.append(data)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    html_path = args.html.resolve()
    if not html_path.is_file():
        fail(f"file not found: {html_path}")
    p = DocumentParser()
    p.feed(html_path.read_text(encoding="utf-8"))
    duplicates = sorted({item for item in p.ids if p.ids.count(item) > 1})
    if duplicates:
        fail(f"duplicate ids: {', '.join(duplicates)}")
    if p.meta_count != 1:
        fail(f"expected exactly one #wl-design-meta, found {p.meta_count}")
    try:
        meta = json.loads("".join(p.meta_text))
    except json.JSONDecodeError as exc:
        fail(f"invalid wl-design-meta JSON: {exc}")
    for key in ("requirement_id", "status", "created", "updated", "chosen", "approval_evidence"):
        if key not in meta:
            fail(f"missing metadata key: {key}")
    if meta["status"] == "approved" and not meta["approval_evidence"]:
        fail("approved document has no approval_evidence")
    for tag, resource in p.embedded_resources:
        if resource.startswith(("http://", "https://", "//")):
            fail(f"external embedded resource: <{tag}> {resource}")
    for _, href in p.links:
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        target = html_path.parent / unquote(parts.path)
        if not target.exists():
            fail(f"missing local link target: {href}")
    print(
        f"PASS: {html_path} | meta=draft-safe | ids={len(p.ids)} "
        f"links={len(p.links)} embedded={len(p.embedded_resources)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
