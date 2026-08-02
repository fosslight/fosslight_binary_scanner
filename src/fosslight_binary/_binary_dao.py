#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
"""Binary DB lookup via ldb_service POST /binary/match."""

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from fosslight_binary._binary import TLSH_CHECKSUM_NULL
from fosslight_util.oss_item import OssItem
import fosslight_util.constant as constant

logger = logging.getLogger(constant.LOGGER_NAME)

DEFAULT_KB_URL = "http://fosslight-kb.lge.com/"
_BINARY_MATCH_PATH = "/binary/match"
_HTTP_TIMEOUT_SEC = 120
_PROBE_TIMEOUT_SEC = 10
_DEFAULT_CHUNK_SIZE = 3000


def _get_chunk_size() -> int:
    raw = os.environ.get("BINARY_MATCH_CHUNK_SIZE", str(_DEFAULT_CHUNK_SIZE))
    try:
        chunk_size = int(raw)
    except ValueError:
        logger.warning(f"Invalid BINARY_MATCH_CHUNK_SIZE={raw!r}; using {_DEFAULT_CHUNK_SIZE}")
        return _DEFAULT_CHUNK_SIZE
    if chunk_size <= 0:
        logger.warning(
            f"BINARY_MATCH_CHUNK_SIZE must be > 0 (got {chunk_size}); using {_DEFAULT_CHUNK_SIZE}"
        )
        return _DEFAULT_CHUNK_SIZE
    return chunk_size


_CHUNK_SIZE = _get_chunk_size()

MatchKey = Tuple[str, str]


def resolve_kb_config(kb_url: str = "", kb_token: str = "") -> Tuple[str, str]:
    url = (kb_url or os.environ.get("KB_URL", DEFAULT_KB_URL)).strip() or DEFAULT_KB_URL
    token = (kb_token or "").strip() or (os.environ.get("KB_TOKEN") or "").strip()
    return f"{url.rstrip('/')}/", token


def _is_valid_kb_url_format(kb_url: str) -> bool:
    parsed = urlparse(kb_url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def check_binary_match_endpoint(kb_url: str, kb_token: str = "") -> Tuple[bool, str]:
    """
    Return (available, cover_comment).

    cover_comment is ``KB({kb_url}) Unreachable`` when the host cannot be reached
    (URLError / connection failure). Empty for other skip cases (invalid URL, HTTP 404).
    """
    if not _is_valid_kb_url_format(kb_url):
        logger.warning(f"Invalid KB URL format: {kb_url}")
        return False, ""

    endpoint = f"{kb_url.rstrip('/')}{_BINARY_MATCH_PATH}"
    data = json.dumps({"items": []}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=data, method="POST")
    request.add_header("Accept", "application/json")
    request.add_header("Content-Type", "application/json")
    if kb_token:
        request.add_header("Authorization", f"Bearer {kb_token}")

    try:
        with urllib.request.urlopen(request, timeout=_PROBE_TIMEOUT_SEC) as response:
            response.read()
            return True, ""
    except urllib.error.HTTPError as ex:
        if ex.code == 404:
            logger.warning(
                f"KB binary match endpoint not found (HTTP 404): {endpoint}. "
                "Skipping binary match API."
            )
            return False, ""
        logger.debug(
            f"KB binary match endpoint responded with HTTP {ex.code}; treated as available"
        )
        return True, ""
    except urllib.error.URLError as ex:
        logger.warning(f"KB binary match endpoint unreachable: {ex}. Skipping binary match API.")
        return False, f"KB({kb_url}) Unreachable"
    except Exception as ex:
        logger.warning(
            f"Failed to check KB binary match endpoint: {ex}. Skipping binary match API."
        )
        return False, f"KB({kb_url}) Unreachable"


def _is_unknown_checksum(checksum: str) -> bool:
    """True when checksum was not computed (empty or TLSH_CHECKSUM_NULL)."""
    return (not checksum) or checksum == TLSH_CHECKSUM_NULL


def _is_unknown_tlsh(tlsh: str) -> bool:
    """True when tlsh was not computed (empty or TLSH_CHECKSUM_NULL)."""
    return (not tlsh) or tlsh == TLSH_CHECKSUM_NULL


def _match_key(filename: str, checksum: str, index: int) -> MatchKey:
    """Dedupe key. Unknown checksums stay unique per list index (no filename-only merge)."""
    if _is_unknown_checksum(checksum):
        return filename, f"__unknown_{index}"
    return filename, checksum


def _build_deduped_payload(
    bin_info_list,
    tlsh_null: str,
) -> Tuple[List[dict], Dict[MatchKey, str]]:
    """Deduplicate by filename+checksum; return API payload and key→api_id map.

    Items with empty/\"0\" checksum are not deduped — each keeps its own API entry
    (and its own tlsh) so distinct files that share a basename are not conflated.
    Items with both checksum and tlsh unknown are omitted (nothing to match).
    """
    key_to_id: Dict[MatchKey, str] = {}
    items_payload: List[dict] = []

    for index, item in enumerate(bin_info_list):
        if item.exclude:
            continue
        filename = item.binary_name_without_path
        checksum = item.checksum or ""
        tlsh = item.tlsh or tlsh_null
        if _is_unknown_checksum(checksum) and _is_unknown_tlsh(tlsh):
            continue
        key = _match_key(filename, checksum, index)
        if not _is_unknown_checksum(checksum) and key in key_to_id:
            continue
        api_id = str(len(items_payload))
        key_to_id[key] = api_id
        items_payload.append({
            "id": api_id,
            "filename": filename,
            "checksum": checksum,
            "tlsh": tlsh,
        })

    return items_payload, key_to_id


def _apply_match_result_to_item(item, result: dict) -> bool:
    """Apply a /binary/match result to one binary item. Returns True if matched."""
    if not result or not result.get("matched"):
        return False
    oss_rows = result.get("oss_items") or []
    if not oss_rows:
        return False

    if not item.found_in_jar_analysis and item.oss_items:
        item.oss_items = []

    bin_oss_items = []
    for row in oss_rows:
        if item.found_in_jar_analysis:
            break
        oss_from_db = OssItem(
            row.get("oss_name") or "",
            row.get("oss_version") or "",
            row.get("license") or "",
        )
        if bin_oss_items:
            if not any(
                oss_item.name == oss_from_db.name
                and oss_item.version == oss_from_db.version
                and oss_item.license == oss_from_db.license
                for oss_item in bin_oss_items
            ):
                bin_oss_items.append(oss_from_db)
        else:
            bin_oss_items.append(oss_from_db)

    if bin_oss_items:
        item.set_oss_items(bin_oss_items)
        item.comment = "Binary DB result"
        item.found_in_bin_db = True
        return True
    return False


def get_oss_info_from_db(bin_info_list, kb_url: str = "", kb_token: str = ""):
    """
    Call ldb_service /binary/match and attach OSS info to binary items.
    Deduplicates by filename+checksum before the API call and maps results back.
    Returns (bin_info_list, matched_count, kb_cover_comment).
    """
    _cnt_auto_identified = 0
    if not bin_info_list:
        return bin_info_list, _cnt_auto_identified, ""

    base_url, token = resolve_kb_config(kb_url, kb_token)
    available, kb_cover_comment = check_binary_match_endpoint(base_url, token)
    if not available:
        return bin_info_list, _cnt_auto_identified, kb_cover_comment

    items_payload, key_to_id = _build_deduped_payload(bin_info_list, TLSH_CHECKSUM_NULL)
    if not items_payload:
        return bin_info_list, _cnt_auto_identified, ""

    results_by_id = {}
    try:
        for chunk_start in range(0, len(items_payload), _CHUNK_SIZE):
            chunk = items_payload[chunk_start: chunk_start + _CHUNK_SIZE]
            response = _post_binary_match(base_url, token, chunk)
            if response is None:
                logger.warning(
                    f"Binary match chunk failed "
                    f"({chunk_start}:{chunk_start + len(chunk)}); "
                    "keeping results so far and continuing with next chunks."
                )
                continue
            for result in response.get("results", []):
                results_by_id[str(result.get("id"))] = result
    except Exception as ex:
        logger.warning(f"Binary match API failed: {ex}")

    for index, item in enumerate(bin_info_list):
        if item.exclude:
            continue
        key = _match_key(item.binary_name_without_path, item.checksum or "", index)
        api_id = key_to_id.get(key)
        if api_id is None:
            continue
        result = results_by_id.get(api_id)
        if _apply_match_result_to_item(item, result):
            _cnt_auto_identified += 1

    return bin_info_list, _cnt_auto_identified, ""


def _post_binary_match(kb_url: str, kb_token: str, items: list) -> Optional[dict]:
    data = json.dumps({"items": items}).encode("utf-8")
    request = urllib.request.Request(
        f"{kb_url.rstrip('/')}{_BINARY_MATCH_PATH}",
        data=data,
        method="POST",
    )
    request.add_header("Accept", "application/json")
    request.add_header("Content-Type", "application/json")
    if kb_token:
        request.add_header("Authorization", f"Bearer {kb_token}")

    try:
        with urllib.request.urlopen(request, timeout=_HTTP_TIMEOUT_SEC) as response:
            body = response.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as ex:
        body = ""
        try:
            body = ex.read().decode()
        except Exception:
            pass
        if ex.code == 404:
            logger.warning(
                f"Binary match endpoint not found (HTTP 404): "
                f"{kb_url.rstrip('/')}{_BINARY_MATCH_PATH}"
            )
        else:
            logger.warning(f"Binary match HTTP {ex.code}: {body or ex.reason}")
        return None
    except urllib.error.URLError as ex:
        logger.debug(f"Binary match unreachable: {ex}")
        return None
