from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

logger = logging.getLogger("uvicorn.error")

MAX_RESPONSE_LOG_CHARS = 4_000
SENSITIVE_KEYS = {
    "access_token",
    "authorization",
    "client_secret",
    "id_token",
    "password",
    "refresh_token",
    "secret",
    "token",
}


def log_external_response(
    *,
    source: str,
    method: str,
    url: str,
    response: httpx.Response,
) -> None:
    content_type = response.headers.get("content-type", "")
    logger.info(
        "%s response: %s %s status=%s content_type=%s data=%s",
        source,
        method,
        redact_url(url),
        response.status_code,
        content_type or "unknown",
        summarize_response_data(response, content_type),
    )


def summarize_response_data(response: httpx.Response, content_type: str | None = None) -> str:
    content_type = (content_type or response.headers.get("content-type", "")).lower()
    if is_binary_response(content_type):
        return f"<binary {content_type or 'unknown'} {len(response.content)} bytes>"

    if "json" in content_type:
        try:
            return truncate(json.dumps(redact_data(response.json()), ensure_ascii=True, sort_keys=True))
        except ValueError:
            pass

    text = response.text
    if text:
        return truncate(text)
    return "<empty>"


def is_binary_response(content_type: str) -> bool:
    return (
        content_type.startswith("image/")
        or content_type.startswith("application/octet-stream")
        or content_type.startswith("application/pdf")
    )


def redact_url(url: str) -> str:
    parsed = urlsplit(url)
    query = [
        (key, "[redacted]" if key.lower() in SENSITIVE_KEYS else value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
    ]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def redact_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: "[redacted]" if str(key).lower() in SENSITIVE_KEYS else redact_data(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    return value


def truncate(value: str) -> str:
    if len(value) <= MAX_RESPONSE_LOG_CHARS:
        return value
    return f"{value[:MAX_RESPONSE_LOG_CHARS]}... <truncated {len(value) - MAX_RESPONSE_LOG_CHARS} chars>"
