#!/usr/bin/env python3
"""Daily GLaDOS check-in script for local runs or GitHub Actions."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


def normalized_base_url() -> str:
    raw = os.getenv("GLADOS_BASE_URL", "https://glados.one").strip().rstrip("/")
    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"
    return raw


def default_token(base_url: str) -> str:
    host = urllib.parse.urlparse(base_url).netloc
    return host or "glados.one"


def request_json(
    method: str,
    url: str,
    cookie: str,
    origin: str,
    referer: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url=url, data=body, method=method.upper())
    request.add_header("Accept", "application/json, text/plain, */*")
    request.add_header("Content-Type", "application/json;charset=UTF-8")
    request.add_header("Cookie", cookie)
    request.add_header("Origin", origin)
    request.add_header("Referer", referer)
    request.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8")
            data = json.loads(text) if text else {}
            return response.status, data
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(text) if text else {}
        except json.JSONDecodeError:
            data = {"message": text}
        return error.code, data


def status_text(status_data: Any) -> str:
    if isinstance(status_data, dict):
        left_days = status_data.get("leftDays")
        email = status_data.get("email")
        plan = status_data.get("plan")
        parts = []
        if email:
            parts.append(f"email={email}")
        if plan:
            parts.append(f"plan={plan}")
        if left_days is not None:
            parts.append(f"leftDays={left_days}")
        if parts:
            return ", ".join(parts)
    return "status fetched"


def main() -> int:
    cookie = env("GLADOS_COOKIE")
    base_url = normalized_base_url()
    token = os.getenv("GLADOS_CHECKIN_TOKEN", default_token(base_url)).strip()
    origin = os.getenv("GLADOS_ORIGIN", base_url).strip().rstrip("/")
    referer = os.getenv("GLADOS_REFERER", f"{origin}/console/checkin").strip()

    status_url = f"{base_url}/api/user/status"
    checkin_url = f"{base_url}/api/user/checkin"

    status_code, status_data = request_json(
        method="GET",
        url=status_url,
        cookie=cookie,
        origin=origin,
        referer=referer,
    )
    if status_code >= 400:
        raise RuntimeError(
            f"Failed to fetch status ({status_code}): "
            f"{json.dumps(status_data, ensure_ascii=False)}"
        )
    print(f"[status] {status_text(status_data)}")

    checkin_code, checkin_data = request_json(
        method="POST",
        url=checkin_url,
        cookie=cookie,
        origin=origin,
        referer=referer,
        payload={"token": token},
    )
    if checkin_code >= 400:
        raise RuntimeError(
            f"Check-in request failed ({checkin_code}): "
            f"{json.dumps(checkin_data, ensure_ascii=False)}"
        )

    print(f"[checkin] {json.dumps(checkin_data, ensure_ascii=False)}")
    message = ""
    if isinstance(checkin_data, dict):
        message = str(checkin_data.get("message") or checkin_data.get("msg") or "")
    if message:
        print(f"[result] {message}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(1)
