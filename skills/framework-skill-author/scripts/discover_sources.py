#!/usr/bin/env python3
"""发现框架官方文档入口的常见索引，并生成可复现的来源清单。"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_MAX_BYTES = 2_000_000
USER_AGENT = "framework-skill-author/1.0 (+source-discovery; read-only)"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError(f"不是有效的 HTTP(S) URL: {value}")
    return value


def candidate_urls(entry: str) -> list[tuple[str, str]]:
    parsed = urlparse(entry)
    origin = f"{parsed.scheme}://{parsed.netloc}/"
    path = parsed.path or "/"
    directory = path if path.endswith("/") else path.rsplit("/", 1)[0] + "/"

    candidates = [
        (entry, "docs-entry"),
        (urljoin(origin, "llms.txt"), "llms-index"),
        (urljoin(origin, "llms-full.txt"), "llms-full"),
        (urljoin(origin, "sitemap.xml"), "sitemap"),
    ]
    if directory != "/":
        candidates.extend(
            [
                (urljoin(origin, directory.lstrip("/") + "llms.txt"), "llms-index"),
                (urljoin(origin, directory.lstrip("/") + "sitemap.xml"), "sitemap"),
            ]
        )

    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for url, source_type in candidates:
        normalized = url.split("#", 1)[0]
        if normalized not in seen:
            seen.add(normalized)
            result.append((normalized, source_type))
    return result


def blocked_network_reason(url: str) -> str | None:
    host = urlparse(url).hostname
    if not host:
        return "URL 缺少主机名"
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
    except socket.gaierror:
        return None
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_unspecified
            or ip.is_multicast
        ):
            return f"主机 {host} 解析到非公网地址 {address}"
    return None


class SafeRedirectHandler(HTTPRedirectHandler):
    def __init__(self, allow_private_network: bool) -> None:
        super().__init__()
        self.allow_private_network = allow_private_network

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if not self.allow_private_network:
            reason = blocked_network_reason(newurl)
            if reason:
                raise URLError(f"拒绝重定向到私网或特殊地址: {reason}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_metadata(
    url: str, timeout: float, max_bytes: int, allow_private_network: bool
) -> dict[str, object]:
    if not allow_private_network:
        reason = blocked_network_reason(url)
        if reason:
            return {
                "url": url,
                "status": None,
                "available": False,
                "blocked": True,
                "error": f"拒绝访问私网或特殊地址: {reason}",
            }

    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain,text/html,application/xml,*/*;q=0.1"})
    opener = build_opener(SafeRedirectHandler(allow_private_network))
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            truncated = len(body) > max_bytes
            if truncated:
                body = body[:max_bytes]
            final_url = response.geturl()
            return {
                "url": url,
                "final_url": final_url,
                "status": getattr(response, "status", 200),
                "available": True,
                "content_type": response.headers.get("Content-Type", ""),
                "etag": response.headers.get("ETag", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
                "bytes_hashed": len(body),
                "truncated": truncated,
                "sha256": hashlib.sha256(body).hexdigest(),
                "redirected_cross_host": urlparse(url).netloc != urlparse(final_url).netloc,
            }
    except HTTPError as exc:
        return {"url": url, "status": exc.code, "available": False, "error": str(exc)}
    except (URLError, TimeoutError, OSError) as exc:
        return {"url": url, "status": None, "available": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="发现官方文档索引并记录状态、响应元数据和内容哈希。")
    parser.add_argument("--framework", required=True, help="框架名称")
    parser.add_argument("--docs", required=True, action="append", type=validate_url, help="官方文档入口，可重复")
    parser.add_argument("--repo", action="append", type=validate_url, default=[], help="官方源码仓库，可重复")
    parser.add_argument("--version", default="unspecified", help="目标版本、tag 或 commit")
    parser.add_argument("--output", required=True, type=Path, help="输出 JSON 文件")
    parser.add_argument("--timeout", type=float, default=10.0, help="单请求超时秒数")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="单来源最多参与哈希的字节数")
    parser.add_argument("--allow-private-network", action="store_true", help="显式允许访问 localhost、私网或特殊地址；仅用于已授权的内部文档")
    args = parser.parse_args()

    if args.timeout <= 0 or args.max_bytes <= 0:
        parser.error("--timeout 和 --max-bytes 必须大于 0")

    sources: list[dict[str, object]] = []
    seen: set[str] = set()
    for docs_entry in args.docs:
        for url, source_type in candidate_urls(docs_entry):
            if url in seen:
                continue
            seen.add(url)
            item = fetch_metadata(url, args.timeout, args.max_bytes, args.allow_private_network)
            item["source_type"] = source_type
            item["official_entry"] = docs_entry
            sources.append(item)

    for repo in args.repo:
        if repo in seen:
            continue
        seen.add(repo)
        item = fetch_metadata(repo, args.timeout, args.max_bytes, args.allow_private_network)
        item["source_type"] = "repository"
        item["official_entry"] = repo
        sources.append(item)

    payload = {
        "schema_version": "1",
        "framework": args.framework,
        "target_version": args.version,
        "retrieved_at": utc_now(),
        "docs_entries": args.docs,
        "repository_entries": args.repo,
        "sources": sources,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    available = sum(1 for item in sources if item.get("available"))
    print(f"已写入 {args.output}：{available}/{len(sources)} 个候选来源可访问。")
    return 0 if available else 2


if __name__ == "__main__":
    sys.exit(main())
