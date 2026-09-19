import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

SCRIPT = Path(__file__).resolve().parents[1] / "skills/visual-artifact-workbench/scripts/serve.py"


class ShareServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        cls.root = cls.base / "public"
        cls.root.mkdir()
        cls.config = cls.base / "config.json"
        cls.body = b"<h1>approved</h1>"
        (cls.root / "page.html").write_bytes(cls.body)
        (cls.root / "unpublished.txt").write_text("not approved")
        (cls.base / "secret.txt").write_text("outside")
        (cls.root / "link.html").symlink_to(cls.base / "secret.txt")
        cls.routes = {
            "/doc/": {"redirect": "/doc/v1/"},
            "/doc/v1/": {"file": "page.html", "sha256": hashlib.sha256(cls.body).hexdigest()},
            "/link/": {"file": "link.html", "sha256": hashlib.sha256(b"outside").hexdigest()},
            "/bad-file/": {"file": "../secret.txt", "sha256": hashlib.sha256(b"outside").hexdigest()},
            "/bad-redirect/": {"redirect": "//example.invalid/"},
        }
        cls.config.write_text(json.dumps({"host": "127.0.0.1", "port": 0, "publish_root": str(cls.root), "routes": cls.routes}))
        cls.proc = subprocess.Popen([sys.executable, str(SCRIPT), "serve", "--config", str(cls.config)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.opener = build_opener(ProxyHandler({}))
        for _ in range(100):
            if (cls.base / "runtime.json").exists():
                cls.runtime = json.loads((cls.base / "runtime.json").read_text())
                cls.url = f"http://127.0.0.1:{cls.runtime['port']}"
                break
            if cls.proc.poll() is not None:
                raise AssertionError("server exited")
            time.sleep(.02)
        else:
            cls.proc.terminate()
            cls.proc.wait(timeout=5)
            raise AssertionError("server failed to start")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        cls.tmp.cleanup()

    def request(self, path, method="GET"):
        try:
            return self.opener.open(Request(self.url + path, method=method), timeout=2)
        except HTTPError as response:
            return response

    def test_published_page_and_redirect(self):
        with self.request("/doc/") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), self.body)
            self.assertTrue(response.url.endswith("/doc/v1/"))

    def test_no_directory_listing_or_unpublished_files(self):
        for path in ["/", "/unpublished.txt", "/config.json", "/runtime.json", "/../secret.txt", "/%2e%2e/secret.txt", "/bad-file/", "/link/", "/bad-redirect/"]:
            with self.request(path) as response:
                self.assertEqual(response.status, 404, path)
                self.assertNotIn(b"outside", response.read())

    def test_mutated_version_is_not_served(self):
        page = self.root / "page.html"
        try:
            page.write_bytes(b"unexpected mutation")
            with self.request("/doc/v1/") as response:
                self.assertEqual(response.status, 409)
        finally:
            page.write_bytes(self.body)

    def test_head_and_no_upload(self):
        with self.request("/doc/v1/", "HEAD") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"")
        with self.request("/doc/v1/", "POST") as response:
            self.assertEqual(response.status, 501)

    def test_status_checks_real_instance(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "status", "--config", str(self.config)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["instance"], self.runtime["instance"])

    def test_zz_stop_targets_this_instance(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "stop", "--config", str(self.config)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.proc.wait(timeout=5)
        self.assertFalse((self.base / "runtime.json").exists())

    def test_status_rejects_stale_instance(self):
        state = self.base / "runtime.json"
        try:
            state.write_text(json.dumps({**self.runtime, "instance": "stale"}))
            result = subprocess.run([sys.executable, str(SCRIPT), "stop", "--config", str(self.config)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIsNone(self.proc.poll())
        finally:
            state.write_text(json.dumps(self.runtime))


if __name__ == "__main__":
    unittest.main()
