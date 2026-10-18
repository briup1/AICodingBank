#!/usr/bin/env python3
"""Serve only explicitly published files; no directory browsing or upload API."""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import signal
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from urllib.request import ProxyHandler, build_opener
import uuid


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def handler_for(config_path, root, instance):
    class Handler(BaseHTTPRequestHandler):
        server_version = "VisualArtifactShare/1"
        sys_version = ""

        def respond(self, status, body=b"", content_type="text/plain; charset=utf-8", location=None):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            if location:
                self.send_header("Location", location)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path == "/favicon.ico":
                self.respond(204)
                return
            if path == "/_health":
                self.respond(200, json.dumps({"instance": instance}).encode(), "application/json")
                return
            try:
                routes = load(config_path)["routes"]
                entry = routes.get(path)
                if not entry:
                    self.respond(404)
                    return
                if "redirect" in entry:
                    target = entry["redirect"]
                    if target not in routes or not target.startswith("/") or target.startswith("//"):
                        raise ValueError("invalid redirect")
                    self.respond(302, location=target)
                    return
                relative = Path(entry["file"])
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("invalid file")
                candidate = root / relative
                if any(p.is_symlink() for p in [candidate, *candidate.parents]):
                    raise ValueError("symlink")
                candidate.resolve().relative_to(root)
                body = candidate.read_bytes()
                if hashlib.sha256(body).hexdigest() != entry["sha256"]:
                    self.respond(409)
                    return
                mime = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
                self.respond(200, body, mime + ("; charset=utf-8" if mime.startswith("text/") else ""))
            except (OSError, ValueError, KeyError):
                self.respond(404)

        do_HEAD = do_GET

    return Handler


def live_runtime(config_path):
    runtime = load(config_path.with_name("runtime.json"))
    opener = build_opener(ProxyHandler({}))
    with opener.open(f"http://{runtime['host']}:{runtime['port']}/_health", timeout=2) as response:
        health = json.load(response)
    if health.get("instance") != runtime["instance"]:
        raise ValueError("服务实例已变化，拒绝使用旧记录")
    return runtime


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["serve", "status", "stop"])
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.action != "serve":
        try:
            runtime = live_runtime(config_path)
            if args.action == "stop":
                command = subprocess.check_output(["ps", "-p", str(runtime["pid"]), "-o", "command="], text=True)
                config_argument = runtime.get("config_argument", str(config_path))
                if Path(config_argument).resolve() != config_path or str(Path(__file__).resolve()) not in command or config_argument not in command:
                    raise ValueError("进程不匹配，拒绝停止")
                os.kill(runtime["pid"], signal.SIGTERM)
            print(json.dumps({"action": args.action, **runtime}, ensure_ascii=False))
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
            parser.exit(1, f"服务未运行或记录不匹配：{exc}\n")
        return
    config = load(config_path)
    root = Path(config["publish_root"]).resolve(strict=True)
    instance = uuid.uuid4().hex
    runtime_path = config_path.with_name("runtime.json")
    with ThreadingHTTPServer((config["host"], config["port"]), handler_for(config_path, root, instance)) as server:
        runtime = {"pid": os.getpid(), "host": config["host"], "port": server.server_port, "instance": instance, "config_argument": str(args.config)}
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
        def stop_server(*_):
            raise SystemExit(0)

        signal.signal(signal.SIGTERM, stop_server)
        print(json.dumps(runtime), flush=True)
        try:
            server.serve_forever()
        finally:
            if runtime_path.exists() and load(runtime_path).get("instance") == instance:
                runtime_path.unlink()


if __name__ == "__main__":
    main()
