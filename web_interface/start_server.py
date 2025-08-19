#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地开发静态服务器（含反向代理，解决浏览器跨域/CORS 问题）。
"""
from __future__ import annotations

import argparse
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urljoin

try:
    import requests
except Exception as e:
    print("缺少 requests 依赖，请先安装: pip install requests", file=sys.stderr)
    raise


class ProxyingHandler(SimpleHTTPRequestHandler):
    server_version = "DevServer/1.0"

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/proxy"):
            return self._proxy("GET")
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        if self.path.startswith("/proxy"):
            return self._proxy("POST")
        return super().do_POST()

    def _proxy(self, method: str) -> None:
        target_base = "http://172.16.0.114:8080/chat/api"  # 硬编码目标地址
        
        # 将 /proxy/... 映射到目标，如 /proxy/open -> {target_base}/open
        upstream_path = self.path[len("/proxy"):]
        if not upstream_path:
            upstream_path = "/"
        upstream_url = urljoin(target_base + "/", upstream_path.lstrip("/"))

        # 读取请求体
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else None

        # 透传必要请求头
        headers = {
            "accept": self.headers.get("accept", "application/json"),
            "content-type": self.headers.get("content-type", "application/json"),
        }
        for k in ("authorization", "AUTHORIZATION", "x-api-key", "X-API-Key", "x-csrftoken", "X-CSRFTOKEN"):
            if k in self.headers:
                headers[k] = self.headers[k]

        try:
            resp = requests.request(method, upstream_url, headers=headers, data=body, stream=True, timeout=300)
        except requests.RequestException as e:
            self.send_error(502, f"上游请求失败: {e}")
            return

        try:
            # 透传状态码与部分头
            self.send_response(resp.status_code)
            ct = resp.headers.get("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Type", ct)
            # SSE 需要保持传输流
            if resp.headers.get("Transfer-Encoding"):
                self.send_header("Transfer-Encoding", resp.headers["Transfer-Encoding"])
            self.end_headers()

            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
        finally:
            resp.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="本地静态服务器（含反向代理）")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = ThreadingHTTPServer(("0.0.0.0", args.port), ProxyingHandler)
    print(f"Serving on http://localhost:{args.port}")
    print(f"Proxy enabled: /proxy -> http://172.16.0.114:8080/chat/api")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
