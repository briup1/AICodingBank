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


def check_decision(meta: object, require_executable: bool = False) -> str:
    """Validate decision shape, not the truth of user records or technical evidence."""
    if not isinstance(meta, dict):
        fail("wl-design-meta must be an object")
    for key in ("requirement_id", "status", "created", "updated", "chosen", "approval_evidence"):
        if key not in meta:
            fail(f"missing metadata key: {key}")
    mode = meta.get("decision_mode", "manual")  # Legacy human-approved documents.
    status = meta["status"]
    if mode not in {"manual", "delegated"}:
        fail("invalid decision_mode")
    if status not in {"draft", "reviewing", "approved", "adopted"}:
        fail("invalid design status")
    if mode == "delegated" and (status == "approved" or meta["approval_evidence"] is not None):
        fail("delegation is not human approval; use adopted and null approval_evidence")
    if status == "adopted" and mode != "delegated":
        fail("adopted requires delegated decision_mode")
    if status == "approved" and not meta["approval_evidence"]:
        fail("approved document has no approval_evidence")
    executable = status in {"approved", "adopted"}
    if require_executable and not executable:
        fail("candidate document is not executable")
    # New decision metadata is stricter; old approved artifacts remain readable.
    if executable and ("decision_mode" in meta or "critical_validation" in meta):
        validation = meta.get("critical_validation")
        if not isinstance(validation, dict) or validation.get("status") != "verified" or not validation.get("evidence"):
            fail("executable design requires verified critical_validation evidence")
    if executable and "decision_mode" in meta:
        for key in ("requirement_version", "design_version", "recommendation", "recommendation_reason"):
            if not isinstance(meta.get(key), str) or not meta[key].strip():
                fail(f"missing decision field: {key}")
        cases = meta.get("source_test_cases")
        if not isinstance(cases, dict) or not all(isinstance(cases.get(k), str) and cases[k].strip() for k in ("path", "version")):
            fail("missing source_test_cases path/version")
    if status == "adopted":
        if meta.get("chosen") != meta.get("recommendation"):
            fail("adopted chosen must match recommendation")
        evidence = meta.get("delegation_evidence")
        keys = ("record", "requirement_version", "design_version", "scope", "data_boundary", "cost_boundary", "operation_boundary")
        if not isinstance(evidence, dict) or not all(isinstance(evidence.get(k), str) and evidence[k].strip() for k in keys):
            fail("missing delegation_evidence record/version/boundaries")
        for key in ("requirement_version", "design_version"):
            if evidence[key] != meta[key]:
                fail(f"delegation_evidence {key} does not match this version")
    return f"{mode}/{status}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--require-executable", action="store_true", help="reject undecided candidates at ticket handoff")
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
    decision = check_decision(meta, args.require_executable)
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
        f"PASS: {html_path} | meta={decision} (structure only) | ids={len(p.ids)} "
        f"links={len(p.links)} embedded={len(p.embedded_resources)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
