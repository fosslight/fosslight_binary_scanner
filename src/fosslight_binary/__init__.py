#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

# Auto-install syft and grype on first import
import logging
import os

logger = logging.getLogger(__name__)


def _auto_install_dependencies():
    """Auto-install syft and grype if not available"""
    try:
        from ._jar_analysis import ensure_syft_grype
        # Only try to install if we're not in a restricted environment
        if not os.environ.get('FOSSLIGHT_SKIP_AUTO_INSTALL'):
            ensure_syft_grype()
    except Exception as ex:
        # Don't fail package import if auto-install fails
        logger.debug(f"Auto-install failed (this is not critical): {ex}")


# Run auto-install on import
_auto_install_dependencies()
