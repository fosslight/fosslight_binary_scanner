#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

"""
CLI interface for installing syft and grype tools manually.
"""

import os
import subprocess
import sys


def main():
    """Main entry point for fosslight_install_tools command."""
    print("=== FOSSLight Binary Scanner - Tool Installer ===")
    print("Installing syft and grype tools...")

    try:
        # Find install_tools.py script
        # Get the directory where this module is located
        module_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to the project root
        project_root = os.path.dirname(os.path.dirname(module_dir))
        script_path = os.path.join(project_root, 'install_tools.py')

        if os.path.exists(script_path):
            print(f"Found installer script: {script_path}")
            print("Running installation...")

            # Execute the installer script
            result = subprocess.run([sys.executable, script_path],
                                    capture_output=False, text=True)

            if result.returncode == 0:
                print("\n✅ Installation completed successfully!")
                print("You can now use 'syft' and 'grype' commands.")
            else:
                print(f"\n❌ Installation failed with exit code: {result.returncode}")
                return 1

        else:
            print(f"❌ Installer script not found at: {script_path}")
            print("Please ensure install_tools.py exists in the project root.")
            return 1

    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
