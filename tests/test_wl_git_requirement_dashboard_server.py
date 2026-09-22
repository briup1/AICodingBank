from __future__ import annotations

import http.client
import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Callable

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/wl-git-flow/scripts/dashboard.py"
SPEC = importlib.util.spec_from_file_location("wl_git_requirement_dashboard_server", MODULE_PATH)
assert SPEC and SPEC.loader
DASHBOARD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DASHBOARD
SPEC.loader.exec_module(DASHBOARD)


TOKEN = "test-dashboard-token"
INITIAL_DATA = {
    "version": 1,
    "generatedAt": "2026-09-21T10:00:00+08:00",
    "summary": {"active": 1},
    "projects": [{"id": "compass"}],
    "requirements": [],
    "anomalies": [],
    "errors": [],
}


class RunningServer:
    def __init__(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        refresh: Callable[[Any], dict[str, Any]],
    ) -> None:
        paths = DASHBOARD.RuntimePaths(
            config_file=tmp_path / "config.json",
            state_file=tmp_path / "state.json",
            html_file=tmp_path / "dashboard.html",
        )
        monkeypatch.setattr(DASHBOARD, "refresh_dashboard", refresh)
        self.server = DASHBOARD.create_dashboard_server(
            paths,
            port=0,
            token=TOKEN,
            initial_data=INITIAL_DATA,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.host = host
        self.port = port
        self.origin = f"http://{host}:{port}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        origin: str | None = None,
        host: str | None = None,
        body: bytes | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        headers = {"Host": host or f"{self.host}:{self.port}"}
        if token is not None:
            headers["X-WL-Dashboard-Token"] = token
        if origin is not None:
            headers["Origin"] = origin
        connection = http.client.HTTPConnection(self.host, self.port, timeout=3)
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        result = response.status, {key.lower(): value for key, value in response.getheaders()}, payload
        connection.close()
        return result


@pytest.fixture
def server_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    servers: list[RunningServer] = []

    def start(refresh: Callable[[Any], dict[str, Any]]) -> RunningServer:
        server = RunningServer(tmp_path, monkeypatch, refresh)
        servers.append(server)
        return server

    yield start

    for server in servers:
        server.close()


def assert_security_headers(headers: dict[str, str]) -> None:
    assert headers["cache-control"] == "no-store"
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["referrer-policy"] == "no-referrer"
    assert "default-src 'none'" in headers["content-security-policy"]
    assert "access-control-allow-origin" not in headers


def decode_json(payload: bytes) -> dict[str, Any]:
    decoded = json.loads(payload)
    assert isinstance(decoded, dict)
    return decoded


def test_each_server_uses_a_fresh_random_session_token(tmp_path: Path) -> None:
    paths = DASHBOARD.RuntimePaths(
        config_file=tmp_path / "config.json",
        state_file=tmp_path / "state.json",
        html_file=tmp_path / "dashboard.html",
    )
    first = DASHBOARD.create_dashboard_server(paths, initial_data=INITIAL_DATA)
    second = DASHBOARD.create_dashboard_server(paths, initial_data=INITIAL_DATA)
    try:
        assert first.dashboard_state.token
        assert second.dashboard_state.token
        assert first.dashboard_state.token != second.dashboard_state.token
    finally:
        first.server_close()
        second.server_close()


def test_server_binds_loopback_random_port_and_injects_stable_live_config(server_factory) -> None:
    server = server_factory(lambda _paths: INITIAL_DATA)
    assert isinstance(server.server, DASHBOARD.http.server.ThreadingHTTPServer)
    assert server.host == "127.0.0.1"
    assert server.port > 0

    status, headers, payload = server.request("GET", "/")
    assert status == 200
    assert_security_headers(headers)
    html = payload.decode("utf-8")
    marker = '<script id="wlDashboardLiveConfig" type="application/json">'
    assert html.count(marker) == 1
    config_text = html.split(marker, 1)[1].split("</script>", 1)[0]
    assert json.loads(config_text) == {
        "mode": "live",
        "api": {
            "state": "/api/state",
            "refresh": "/api/refresh",
            "health": "/api/health",
        },
        "token": TOKEN,
        "refreshIntervals": [0, 15, 30, 60],
    }


def test_state_requires_same_origin_token_and_host(server_factory) -> None:
    server = server_factory(lambda _paths: INITIAL_DATA)

    for token, origin, host in [
        (None, server.origin, None),
        ("wrong", server.origin, None),
        (TOKEN, "http://example.test", None),
        (TOKEN, server.origin, "localhost:1"),
    ]:
        status, headers, payload = server.request(
            "GET", "/api/state", token=token, origin=origin, host=host
        )
        assert status == 403
        assert_security_headers(headers)
        error = decode_json(payload)
        assert error["ok"] is False
        assert error["error"]["code"] == "forbidden"

    status, headers, payload = server.request(
        "GET", "/api/state", token=TOKEN, origin=server.origin
    )
    assert status == 200
    assert_security_headers(headers)
    assert decode_json(payload) == INITIAL_DATA


def test_refresh_rejects_get_invalid_auth_body_unknown_and_write_routes(server_factory) -> None:
    server = server_factory(lambda _paths: INITIAL_DATA)

    status, _, payload = server.request("GET", "/api/refresh")
    assert status == 405
    assert decode_json(payload)["error"]["code"] == "method-not-allowed"

    for token, origin, host in [
        (None, server.origin, None),
        ("wrong", server.origin, None),
        (TOKEN, "null", None),
        (TOKEN, server.origin, "example.test"),
    ]:
        status, _, payload = server.request(
            "POST", "/api/refresh", token=token, origin=origin, host=host
        )
        assert status == 403
        assert decode_json(payload)["error"]["code"] == "forbidden"

    status, _, payload = server.request(
        "POST", "/api/refresh", token=TOKEN, origin=server.origin, body=b"not-empty"
    )
    assert status == 400
    assert decode_json(payload)["error"]["code"] == "request-body-not-allowed"

    for method, path in [
        ("GET", "/missing"),
        ("POST", "/api/git/push"),
        ("POST", "/api/agent/start"),
        ("POST", "/api/merge"),
    ]:
        status, headers, payload = server.request(method, path)
        assert status == 404
        assert_security_headers(headers)
        assert decode_json(payload)["error"]["code"] == "not-found"


def test_valid_refresh_returns_new_snapshot_and_health(server_factory) -> None:
    calls = 0
    updated = {**INITIAL_DATA, "generatedAt": "2026-09-21T10:01:00+08:00"}

    def refresh(_paths) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return updated

    server = server_factory(refresh)
    status, headers, payload = server.request(
        "POST", "/api/refresh", token=TOKEN, origin=server.origin
    )
    assert status == 200
    assert_security_headers(headers)
    response = decode_json(payload)
    assert response["ok"] is True
    assert response["data"] == updated
    assert isinstance(response["durationMs"], int)
    assert response["durationMs"] >= 0
    assert calls == 1

    status, _, payload = server.request("GET", "/api/health")
    assert status == 200
    assert decode_json(payload) == {
        "ok": True,
        "mode": "live",
        "generatedAt": updated["generatedAt"],
        "refreshing": False,
    }


def test_concurrent_refresh_returns_409_without_second_scan(server_factory) -> None:
    entered = threading.Event()
    release = threading.Event()
    calls = 0

    def refresh(_paths) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(timeout=3)
        return INITIAL_DATA

    server = server_factory(refresh)
    first_result: list[tuple[int, dict[str, str], bytes]] = []
    first = threading.Thread(
        target=lambda: first_result.append(
            server.request("POST", "/api/refresh", token=TOKEN, origin=server.origin)
        )
    )
    first.start()
    assert entered.wait(timeout=2)

    status, _, payload = server.request(
        "POST", "/api/refresh", token=TOKEN, origin=server.origin
    )
    assert status == 409
    assert decode_json(payload)["error"]["code"] == "refresh-in-progress"
    assert calls == 1

    release.set()
    first.join(timeout=3)
    assert first_result[0][0] == 200


def test_refresh_failure_is_structured_and_preserves_previous_snapshot(server_factory) -> None:
    def refresh(_paths) -> dict[str, Any]:
        raise DASHBOARD.DashboardError("scanner failed")

    server = server_factory(refresh)
    status, _, payload = server.request(
        "POST", "/api/refresh", token=TOKEN, origin=server.origin
    )
    assert status == 500
    response = decode_json(payload)
    assert response == {
        "ok": False,
        "error": {"code": "refresh-failed", "message": "scanner failed"},
    }
    assert "Traceback" not in payload.decode("utf-8")

    status, _, payload = server.request(
        "GET", "/api/state", token=TOKEN, origin=server.origin
    )
    assert status == 200
    assert decode_json(payload) == INITIAL_DATA


def test_server_close_releases_port(server_factory) -> None:
    server = server_factory(lambda _paths: INITIAL_DATA)
    port = server.port
    server.close()

    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", port), timeout=0.2)


def test_serve_cli_defaults_and_open_only_uses_loopback_url(monkeypatch, tmp_path: Path) -> None:
    args = DASHBOARD.build_parser().parse_args(["serve"])
    assert args.port == 0
    assert args.open is False

    opened: list[str] = []

    class FakeServer:
        server_address = ("127.0.0.1", 54321)
        dashboard_state = type("State", (), {"latest_data": INITIAL_DATA})()

        def serve_forever(self) -> None:
            raise KeyboardInterrupt

        def shutdown(self) -> None:
            pass

        def server_close(self) -> None:
            pass

    monkeypatch.setattr(
        DASHBOARD,
        "create_dashboard_server",
        lambda *_args, **_kwargs: FakeServer(),
    )
    monkeypatch.setattr(DASHBOARD.webbrowser, "open", opened.append)
    paths = DASHBOARD.RuntimePaths(
        config_file=tmp_path / "config.json",
        state_file=tmp_path / "state.json",
        html_file=tmp_path / "dashboard.html",
    )

    DASHBOARD.serve_dashboard(paths, port=0, open_browser=True)
    assert opened == ["http://127.0.0.1:54321/"]



def test_foreground_cli_ctrl_c_closes_socket(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.update(
        PYTHONUNBUFFERED="1",
        XDG_CONFIG_HOME=str(tmp_path / "config"),
        XDG_STATE_HOME=str(tmp_path / "state"),
        XDG_DATA_HOME=str(tmp_path / "data"),
    )
    process = subprocess.Popen(
        [sys.executable, "-u", str(MODULE_PATH), "serve", "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    assert process.stdout is not None
    try:
        url_line = process.stdout.readline().strip()
        assert url_line.startswith("url=http://127.0.0.1:")
        port = int(url_line.rsplit(":", 1)[1].rstrip("/"))
        assert process.stdout.readline().strip() == "projects=0"
        assert "127.0.0.1-only" in process.stdout.readline()
        assert process.stdout.readline().strip() == "stop=Ctrl+C"

        process.send_signal(signal.SIGINT)
        process.wait(timeout=3)
        assert process.returncode == 0
        with pytest.raises(OSError):
            socket.create_connection(("127.0.0.1", port), timeout=0.2)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)


def test_shell_help_lists_serve_command() -> None:
    shell = ROOT / "skills/wl-git-flow/scripts/wl-git-flow.sh"
    result = subprocess.run(
        [str(shell), "--help"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert "dashboard serve [--port 0] [--open]" in result.stdout
    assert "\\n  wl-git-flow.sh dashboard serve" not in result.stdout
