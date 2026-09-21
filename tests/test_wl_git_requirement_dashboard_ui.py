from __future__ import annotations

import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/wl-git-requirement-flow/assets/dashboard-template.html"


class DashboardMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.external_resources: list[tuple[str, str]] = []
        self.button_depth = 0
        self.button_text: list[str] = []
        self.buttons: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value:
                self.external_resources.append((attribute, value))
        if tag == "button":
            self.button_depth += 1
            self.button_text = []

    def handle_data(self, data: str) -> None:
        if self.button_depth:
            self.button_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self.button_depth:
            self.buttons.append(" ".join("".join(self.button_text).split()))
            self.button_depth -= 1
            self.button_text = []


def template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def executable_javascript(html: str) -> str:
    scripts = re.findall(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", html, re.DOTALL)
    return "\n".join(body for attrs, body in scripts if 'type="application/json"' not in attrs)


def test_template_exposes_live_and_static_refresh_controls() -> None:
    html = template_text()

    assert 'id="dashboardMode"' in html
    assert "本地实时模式" in html
    assert "静态快照" in html
    assert 'id="refreshDashboard"' in html
    assert "刷新状态" in html
    assert 'id="autoRefresh"' in html
    for value, label in (("0", "关闭"), ("15", "15 秒"), ("30", "30 秒"), ("60", "60 秒")):
        assert re.search(rf'<option\s+value="{value}"[^>]*>{re.escape(label)}</option>', html)
    assert re.search(r'<option\s+value="0"\s+selected>关闭</option>', html)


def test_template_exposes_accessible_refresh_feedback_states() -> None:
    html = template_text()

    assert 'id="refreshStatus"' in html
    assert 'aria-live="polite"' in html
    assert 'data-state="idle"' in html
    for state in ("loading", "success", "error"):
        assert f'setRefreshFeedback("{state}"' in html
    assert "dashboard serve --open" in html


def test_live_refresh_uses_frozen_same_origin_contract_and_hot_updates() -> None:
    javascript = executable_javascript(template_text())

    assert "window.__WL_DASHBOARD_LIVE__" in javascript
    assert 'liveConfig.mode === "live"' in javascript
    assert "liveConfig.refreshPath" in javascript
    assert "liveConfig.statePath" in javascript
    assert "liveConfig.origin" in javascript
    assert 'method: "POST"' in javascript
    assert '"X-WL-Dashboard-Token": liveConfig.token' in javascript
    assert 'credentials: "same-origin"' in javascript
    assert "applyDashboardData(payload.data)" in javascript
    assert "window.location.reload()" in javascript

    refresh_body = re.search(
        r"const refreshLiveData\s*=\s*async\s*\(\)\s*=>\s*\{(?P<body>.*?)\n\s*\};",
        javascript,
        re.DOTALL,
    )
    assert refresh_body, "refreshLiveData must be an explicit async function"
    assert "location.reload" not in refresh_body.group("body")


def test_hot_update_preserves_ui_state_and_serializes_auto_refresh() -> None:
    javascript = executable_javascript(template_text())

    for marker in (
        "captureUiState",
        "restoreUiState",
        "window.scrollX",
        "window.scrollY",
        'querySelectorAll("details[data-detail-key][open]")',
        "sessionStorage",
        "document.hidden",
        "setTimeout",
        "refreshInFlight",
        'document.addEventListener("visibilitychange"',
    ):
        assert marker in javascript
    assert "setInterval" not in javascript


def test_template_has_no_external_resources_unsafe_html_or_write_actions() -> None:
    html = template_text()
    parser = DashboardMarkupParser()
    parser.feed(html)

    assert parser.external_resources == []
    assert "innerHTML" not in html
    forbidden_button_words = ("agent", "merge", "push", "delete", "合并", "推送", "删除", "启动")
    assert not [
        label
        for label in parser.buttons
        if any(word in label.lower() for word in forbidden_button_words)
    ]
    for forbidden_route in ("/api/agent", "/api/merge", "/api/push", "/api/delete", "exec(", "/bin/sh", "child_process"):
        assert forbidden_route not in html.lower()


def test_embedded_javascript_has_valid_syntax(tmp_path: Path) -> None:
    script = tmp_path / "dashboard-template.js"
    script.write_text(executable_javascript(template_text()), encoding="utf-8")

    result = subprocess.run(
        ["node", "--check", str(script)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert result.returncode == 0, result.stdout


def test_live_config_supports_server_json_injection_contract() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")
    assert 'getElementById("wlDashboardLiveConfig")' in html
    assert "JSON.parse(embeddedLiveConfig.textContent" in html
    assert "liveCandidate.api.refresh" in html
    assert "liveCandidate.api.state" in html
    assert "liveCandidate.origin || window.location.origin" in html
