# Copyright (c) 2026 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
"""Tests for KB HTTPS SSL context selection."""

import ssl
from unittest.mock import patch

from fosslight_binary._binary_dao import create_kb_ssl_context, kb_ssl_verify_enabled


def test_kb_ssl_verify_enabled_default(monkeypatch):
    monkeypatch.delenv("KB_SSL_VERIFY", raising=False)
    assert kb_ssl_verify_enabled() is True


def test_kb_ssl_verify_disabled_values(monkeypatch):
    for value in ("false", "0", "no", "OFF"):
        monkeypatch.setenv("KB_SSL_VERIFY", value)
        assert kb_ssl_verify_enabled() is False


def test_create_kb_ssl_context_insecure(monkeypatch):
    monkeypatch.setenv("KB_SSL_VERIFY", "false")
    ctx = create_kb_ssl_context()
    assert ctx.verify_mode == ssl.CERT_NONE
    assert ctx.check_hostname is False


def test_create_kb_ssl_context_uses_truststore_when_verify_on(monkeypatch):
    monkeypatch.setenv("KB_SSL_VERIFY", "true")
    ctx = create_kb_ssl_context()
    assert ctx.verify_mode != ssl.CERT_NONE
    assert ctx.check_hostname is True


def test_probe_passes_ssl_context():
    from fosslight_binary._binary_dao import check_binary_match_endpoint

    class _Resp:
        def read(self):
            return b"{}"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with patch("fosslight_binary._binary_dao.urllib.request.urlopen", return_value=_Resp()) as urlopen:
        available, comment = check_binary_match_endpoint("https://kb.example/", "")
        assert available is True
        assert comment == ""
        assert urlopen.call_args.kwargs["context"] is not None
        assert isinstance(urlopen.call_args.kwargs["context"], ssl.SSLContext)
