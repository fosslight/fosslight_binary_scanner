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

from fosslight_binary._binary import TLSH_CHECKSUM_NULL
from fosslight_util.oss_item import OssItem
import fosslight_util.constant as constant

logger = logging.getLogger(constant.LOGGER_NAME)

DEFAULT_KB_URL = "http://fosslight-kb.lge.com/"
_BINARY_MATCH_PATH = "/binary/match"
_HTTP_TIMEOUT_SEC = 120
_CHUNK_SIZE = int(os.environ.get("BINARY_MATCH_CHUNK_SIZE", "3000"))

MatchKey = Tuple[str, str]


def resolve_kb_config(kb_url: str = "", kb_token: str = "") -> Tuple[str, str]:
    url = (kb_url or os.environ.get("KB_URL", DEFAULT_KB_URL)).strip() or DEFAULT_KB_URL
    token = (kb_token or "").strip() or (os.environ.get("KB_TOKEN") or "").strip()
    return f"{url.rstrip('/')}/", token


def _match_key(filename: str, checksum: str) -> MatchKey:
    return filename, checksum or ""


def _build_deduped_payload(
    bin_info_list,
    tlsh_null: str,
) -> Tuple[List[dict], Dict[MatchKey, str]]:
    """Deduplicate by filename+checksum; return API payload and key→api_id map."""
    key_to_id: Dict[MatchKey, str] = {}
    items_payload: List[dict] = []

    for item in bin_info_list:
        filename = item.binary_name_without_path
        checksum = item.checksum or ""
        key = _match_key(filename, checksum)
        if key in key_to_id:
            continue
        api_id = str(len(items_payload))
        key_to_id[key] = api_id
        items_payload.append({
            "id": api_id,
            "filename": filename,
            "checksum": checksum,
            "tlsh": item.tlsh or tlsh_null,
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
    Returns (bin_info_list, matched_count).
    """
    _cnt_auto_identified = 0
    if not bin_info_list:
        return bin_info_list, _cnt_auto_identified

    base_url, token = resolve_kb_config(kb_url, kb_token)
    items_payload, key_to_id = _build_deduped_payload(bin_info_list, TLSH_CHECKSUM_NULL)
    if not items_payload:
        return bin_info_list, _cnt_auto_identified

    results_by_id = {}
    try:
        for chunk_start in range(0, len(items_payload), _CHUNK_SIZE):
            chunk = items_payload[chunk_start: chunk_start + _CHUNK_SIZE]
            response = _post_binary_match(base_url, token, chunk)
            if response is None:
                return bin_info_list, _cnt_auto_identified
            for result in response.get("results", []):
                results_by_id[str(result.get("id"))] = result
    except Exception as ex:
        logger.warning(f"Binary match API failed: {ex}")
        return bin_info_list, _cnt_auto_identified

    for item in bin_info_list:
        key = _match_key(item.binary_name_without_path, item.checksum or "")
        api_id = key_to_id.get(key)
        if api_id is None:
            continue
        result = results_by_id.get(api_id)
        if _apply_match_result_to_item(item, result):
            _cnt_auto_identified += 1

    return bin_info_list, _cnt_auto_identified


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
        logger.warning(f"Binary match HTTP {ex.code}: {body or ex.reason}")
        return None
    except urllib.error.URLError as ex:
        logger.debug(f"Binary match unreachable: {ex}")
        return None
