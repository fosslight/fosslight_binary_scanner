#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


import hashlib
import logging
import os
import tempfile
import zipfile
import defusedxml.ElementTree as ET
import requests
import fosslight_util.constant as constant
from fosslight_util.get_pom_license import get_license_from_pom
from fosslight_binary._binary import BinaryItem
from fosslight_util.oss_item import OssItem

logger = logging.getLogger(constant.LOGGER_NAME)

_CENTRAL_SEARCH_URL = "https://search.maven.org/solrsearch/select"
_REQUEST_TIMEOUT = 10          # seconds – used for HEAD / POM download
_CENTRAL_SEARCH_TIMEOUT = 2.5  # seconds – tight timeout for Search API (retried on timeout)
_MAX_RETRY = 3                 # maximum Central API retry attempts per JAR
_central_network_warned = False  # Flag to suppress repeated network-unavailable warnings within one run


def _sha1_of_file(filepath):
    h = hashlib.sha1()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
    except Exception as ex:
        logger.debug(f"SHA-1 computation failed for {filepath}: {ex}")
        return ""
    return h.hexdigest()


def _parse_pom_bytes(pom_bytes):
    try:
        root = ET.fromstring(pom_bytes)
        ns = root.tag.split('}')[0] + '}' if root.tag.startswith('{') else ''
        groupId = root.findtext(f'{ns}groupId') or root.findtext(f'{ns}parent/{ns}groupId') or ''
        artifactId = root.findtext(f'{ns}artifactId') or ''
        version = root.findtext(f'{ns}version') or root.findtext(f'{ns}parent/{ns}version') or ''
        project_url = root.findtext(f'{ns}url') or ''
        return groupId, artifactId, version, project_url
    except Exception as ex:
        logger.debug(f"POM parse error: {ex}")
        return '', '', '', ''


def _parse_manifest_bytes(manifest_bytes):
    info = {}
    for line in manifest_bytes.decode('utf-8', errors='replace').splitlines():
        if ':' in line:
            k, _, v = line.partition(':')
            info[k.strip()] = v.strip()
    return info


def _read_pom_from_jar(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            pom_candidates = [n for n in jar.namelist()
                              if n.startswith('META-INF/maven') and n.endswith('pom.xml')]
            if not pom_candidates:
                return '', '', '', '', None
            pom_bytes = jar.open(pom_candidates[0]).read()
            groupId, artifactId, version, project_url = _parse_pom_bytes(pom_bytes)
            with tempfile.NamedTemporaryFile(suffix='.pom', delete=False, mode='wb') as tmp:
                tmp.write(pom_bytes)
                pom_tmp_path = tmp.name
            return groupId, artifactId, version, project_url, pom_tmp_path
    except Exception as ex:
        logger.debug(f"JAR pom.xml read failed for {jar_path}: {ex}")
        return '', '', '', '', None


def _read_manifest_from_jar(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            if 'META-INF/MANIFEST.MF' not in jar.namelist():
                return '', '', '', ''
            mf = _parse_manifest_bytes(jar.open('META-INF/MANIFEST.MF').read())
            groupId = mf.get('Bundle-Vendor', '') or mf.get('Implementation-Vendor', '')
            artifactId = mf.get('Bundle-SymbolicName', '') or mf.get('Implementation-Title', '')
            version = mf.get('Bundle-Version', '') or mf.get('Implementation-Version', '')
            project_url = mf.get('Bundle-DocURL', '') or mf.get('Implementation-URL', '')
            return groupId, artifactId, version, project_url
    except Exception as ex:
        logger.debug(f"JAR MANIFEST.MF read failed for {jar_path}: {ex}")
        return '', '', '', ''


def _is_network_error(ex):
    return isinstance(ex, (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.SSLError,
    ))


def _warn_network_once(context=""):
    global _central_network_warned
    if not _central_network_warned:
        msg = "Maven Central API에 접속할 수 없어 분석에 실패했습니다"
        if context:
            msg += f" ({context})"
        logger.warning(msg)
        _central_network_warned = True


def _search_central_by_sha1(sha1, timeout=None):
    if not sha1:
        return {}, False
    _timeout = timeout if timeout is not None else _CENTRAL_SEARCH_TIMEOUT
    try:
        params = {"q": f"1:{sha1}", "rows": 1, "wt": "json"}
        resp = requests.get(_CENTRAL_SEARCH_URL, params=params, timeout=_timeout)
        resp.raise_for_status()
        docs = resp.json().get("response", {}).get("docs", [])
        if not docs:
            return {}, False
        doc = docs[0]
        return {
            "groupId": doc.get("g", ""),
            "artifactId": doc.get("a", ""),
            "version": doc.get("v") or doc.get("latestVersion", ""),
        }, False
    except requests.exceptions.Timeout:
        logger.debug(f"Maven Central SHA-1 search timed out ({sha1}) – will retry")
        return {}, True
    except Exception as ex:
        if _is_network_error(ex):
            _warn_network_once(f"SHA-1 search: {sha1[:10]}...")
        else:
            logger.debug(f"Maven Central SHA-1 search failed ({sha1}): {ex}")
        return {}, False


def _download_pom_to_tempfile(group_id, artifact_id, version, timeout=None):
    _timeout = timeout if timeout is not None else _REQUEST_TIMEOUT
    group_path = group_id.replace('.', '/')
    pom_name = f"{artifact_id}-{version}.pom"
    urls = [
        f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/{version}/{pom_name}",
        f"https://dl.google.com/android/maven2/{group_path}/{artifact_id}/{version}/{pom_name}",
    ]
    any_timeout = False
    for url in urls:
        try:
            resp = requests.get(url, timeout=_timeout)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix='.pom', delete=False, mode='wb') as tmp:
                tmp.write(resp.content)
                logger.debug(f"POM downloaded to {tmp.name} from {url}")
                return tmp.name, False
        except requests.exceptions.Timeout:
            logger.debug(f"POM download timed out from {url} – will retry")
            any_timeout = True
        except Exception as ex:
            if _is_network_error(ex):
                _warn_network_once(f"POM download: {group_id}:{artifact_id}:{version}")
            else:
                logger.debug(f"POM download failed from {url}: {ex}")
    return None, any_timeout


def _build_central_jar_url(group_id, artifact_id, version):
    if not (group_id and artifact_id and version):
        return ""
    group_path = group_id.replace('.', '/')
    return f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.jar"


def _exists_in_central(group_id, artifact_id, version):
    if not (group_id and artifact_id and version):
        return False
    url = _build_central_jar_url(group_id, artifact_id, version)
    try:
        resp = requests.head(url, timeout=_REQUEST_TIMEOUT, allow_redirects=True)
        return resp.status_code == 200
    except Exception as ex:
        if _is_network_error(ex):
            _warn_network_once(f"existence check: {group_id}:{artifact_id}:{version}")
        else:
            logger.debug(f"Central existence check failed ({group_id}:{artifact_id}:{version}): {ex}")
        return False


def _process_one_jar(jar_path, rel_path, sha1, search_timeout=None, skip_central=False):
    groupId = artifactId = version = project_url = license_str = ''
    confirmed_in_central = False
    source = ''

    if skip_central:
        central_info = {}
        timed_out = False
    else:
        central_info, timed_out = _search_central_by_sha1(sha1, timeout=search_timeout)
        if timed_out:
            logger.debug(f"{rel_path}: Central SHA-1 search timed out – will retry")
            return None, True

    g2, a2, v2, url2, pom_tmp_path = _read_pom_from_jar(jar_path)

    if central_info:
        c_groupId = central_info['groupId']
        c_artifactId = central_info['artifactId']
        c_version = central_info['version']

        jar_oss_name = f"{g2}:{a2}"
        central_oss_name = f"{c_groupId}:{c_artifactId}"
        names_match = (central_oss_name == jar_oss_name and c_version == v2)

        if names_match:
            logger.debug(f"{rel_path}: Central and JAR pom.xml match ({central_oss_name} {c_version}) – using JAR pom.xml for license")
            groupId, artifactId, version, project_url = g2, a2, v2, url2
            source = 'pom.xml'
            confirmed_in_central = True

            if pom_tmp_path:
                try:
                    license_str = get_license_from_pom(
                        group_id=groupId, artifact_id=artifactId, version=version,
                        pom_path=pom_tmp_path, check_parent=True)
                    logger.debug(f"{rel_path}: license from JAR pom.xml (matched Central)={license_str!r}")
                except Exception as ex:
                    logger.debug(f"get_license_from_pom (jar pom_path) failed: {ex}")
                finally:
                    try:
                        os.remove(pom_tmp_path)
                    except Exception:
                        pass
                pom_tmp_path = None
        else:
            logger.debug(f"{rel_path}: Central ({central_oss_name} {c_version}) differs from JAR pom ({jar_oss_name} {v2})")
            groupId, artifactId, version = c_groupId, c_artifactId, c_version
            source = 'Maven Central'
            confirmed_in_central = True

            tmp_path, timed_out = _download_pom_to_tempfile(
                groupId, artifactId, version, timeout=search_timeout)
            if timed_out:
                logger.debug(f"{rel_path}: POM download timed out – will retry")
                if pom_tmp_path:
                    try:
                        os.remove(pom_tmp_path)
                    except Exception:
                        pass
                return None, True
            if tmp_path:
                try:
                    license_str = get_license_from_pom(
                        group_id=groupId, artifact_id=artifactId, version=version,
                        pom_path=tmp_path, check_parent=True)
                    logger.debug(f"{rel_path}: license from Central POM={license_str!r}")
                except Exception as ex:
                    logger.debug(f"get_license_from_pom (Central pom_path) failed: {ex}")
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

        if pom_tmp_path:
            try:
                os.remove(pom_tmp_path)
            except Exception:
                pass

    else:
        logger.debug(f"{rel_path}: not found in Maven Central – falling back to JAR internals")

        if g2 or a2:
            groupId, artifactId, version, project_url = g2, a2, v2, url2
            source = 'pom.xml'

        if pom_tmp_path:
            try:
                if not license_str:
                    license_str = get_license_from_pom(
                        group_id=groupId, artifact_id=artifactId, version=version,
                        pom_path=pom_tmp_path, check_parent=True)
                    logger.debug(f"{rel_path}: license from JAR pom.xml={license_str!r}")
            except Exception as ex:
                logger.debug(f"get_license_from_pom (jar pom_path) failed: {ex}")
            finally:
                try:
                    os.remove(pom_tmp_path)
                except Exception:
                    pass
            if not confirmed_in_central and not skip_central:
                confirmed_in_central = _exists_in_central(groupId, artifactId, version)

    if not (groupId and artifactId):
        g3, a3, v3, url3 = _read_manifest_from_jar(jar_path)
        if g3 or a3:
            groupId = g3
            artifactId = a3
            version = version or v3
            project_url = project_url or url3
            source = 'MANIFEST.MF'

    if not (groupId or artifactId):
        return None, False

    oss_name = f"{groupId}:{artifactId}" if groupId and artifactId else (artifactId or groupId)
    dl_url = _build_central_jar_url(groupId, artifactId, version) if confirmed_in_central else ""

    oss = OssItem(oss_name, version, license_str, dl_url)
    oss.comment = source

    logger.debug(
        f"Result: {rel_path} | {oss_name} {version} | [{license_str}] | dl={dl_url} | source={source}")

    return {"oss_list": [oss], "sha1": sha1}, False


def analyze_jar_file(path_to_find_bin, path_to_exclude):
    global _central_network_warned
    _central_network_warned = False
    jar_items = {}
    success = True
    retry_queue = []

    jar_files = []
    for root_dir, _dirs, files in os.walk(path_to_find_bin):
        for fname in files:
            if fname.endswith('.jar'):
                jar_files.append(os.path.join(root_dir, fname))

    if not jar_files:
        logger.info("No .jar files found – skipping JAR OSS analysis.")
        return jar_items, success

    for jar_path in jar_files:
        rel_path = os.path.relpath(jar_path, path_to_find_bin)
        if rel_path in path_to_exclude:
            continue

        sha1 = _sha1_of_file(jar_path)
        result, needs_retry = _process_one_jar(
            jar_path, rel_path, sha1, search_timeout=_CENTRAL_SEARCH_TIMEOUT)

        if needs_retry:
            logger.debug(f"{rel_path}: Central API timed out – queued for retry (attempt 1/{_MAX_RETRY})")
            retry_queue.append((jar_path, rel_path, sha1, 1))
        elif result is not None:
            jar_items[rel_path] = result

    while retry_queue:
        next_queue = []
        for jar_path, rel_path, sha1, attempt in retry_queue:
            if attempt >= _MAX_RETRY:
                logger.warning(
                    f"{rel_path}: Maven Central API timed out after {_MAX_RETRY} attempts"
                    " – falling back to JAR internals")
                result, _ = _process_one_jar(jar_path, rel_path, sha1, skip_central=True)
                if result is not None:
                    jar_items[rel_path] = result
                continue

            logger.debug(f"{rel_path}: retrying Central API (attempt {attempt + 1}/{_MAX_RETRY})")
            result, needs_retry = _process_one_jar(
                jar_path, rel_path, sha1, search_timeout=_CENTRAL_SEARCH_TIMEOUT)

            if needs_retry:
                next_queue.append((jar_path, rel_path, sha1, attempt + 1))
            elif result is not None:
                jar_items[rel_path] = result

        retry_queue = next_queue

    return jar_items, success


def merge_binary_list(jar_items, bin_list):
    not_found_bin = []

    for key, value in jar_items.items():
        found = False
        oss_list = value["oss_list"]
        sha1 = value.get("sha1", "")
        for bin in bin_list:
            if bin.source_name_or_path == key:
                found = True
                for oss in oss_list:
                    if oss.name and oss.license:
                        bin.found_in_jar_analysis = True
                        break
                bin.set_oss_items(oss_list)
            else:
                if bin.checksum == sha1:
                    bin.set_oss_items(oss_list)

        if not found:
            bin_item = BinaryItem(os.path.abspath(key))
            bin_item.binary_name_without_path = os.path.basename(key)
            bin_item.source_name_or_path = key
            bin_item.set_oss_items(oss_list)
            not_found_bin.append(bin_item)

    bin_list += not_found_bin
    return bin_list
