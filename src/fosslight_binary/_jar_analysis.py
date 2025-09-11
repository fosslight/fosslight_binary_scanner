#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0

import logging
import json
import os
import subprocess
import platform
import tempfile
import tarfile
import shutil
import fosslight_util.constant as constant
from ._binary import BinaryItem, VulnerabilityItem, is_package_dir
from fosslight_util.oss_item import OssItem
import urllib.request

logger = logging.getLogger(constant.LOGGER_NAME)


def install_syft():
    """Install syft binary"""
    try:
        system = platform.system().lower()
        arch = platform.machine().lower()

        # Map architecture names
        if arch in ['x86_64', 'amd64']:
            arch = 'amd64'
        elif arch in ['aarch64', 'arm64']:
            arch = 'arm64'
        else:
            logger.error(f"Unsupported architecture: {arch}")
            return False

        # Get Syft version
        version = "v1.29.0"  # Updated to latest version

        # Download URL
        filename = f"syft_{version[1:]}_{system}_{arch}.tar.gz"
        url = f"https://github.com/anchore/syft/releases/download/{version}/{filename}"

        logger.info(f"Downloading syft from {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            tar_path = os.path.join(temp_dir, filename)
            urllib.request.urlretrieve(url, tar_path)

            # Extract tar.gz
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(temp_dir)

            # Find syft binary and copy to local bin
            syft_bin = os.path.join(temp_dir, 'syft')
            local_bin_dir = os.path.expanduser('~/.local/bin')
            os.makedirs(local_bin_dir, exist_ok=True)

            shutil.copy2(syft_bin, os.path.join(local_bin_dir, 'syft'))
            os.chmod(os.path.join(local_bin_dir, 'syft'), 0o755)

        logger.info("Syft installed successfully")
        return True

    except Exception as ex:
        logger.error(f"Failed to install syft: {ex}")
        return False


def install_grype():
    """Install grype binary"""
    try:
        system = platform.system().lower()
        arch = platform.machine().lower()

        # Map architecture names
        if arch in ['x86_64', 'amd64']:
            arch = 'amd64'
        elif arch in ['aarch64', 'arm64']:
            arch = 'arm64'
        else:
            logger.error(f"Unsupported architecture: {arch}")
            return False

        # Grype version
        version = "v0.84.0"  # Updated to latest version

        # Download URL
        filename = f"grype_{version[1:]}_{system}_{arch}.tar.gz"
        url = f"https://github.com/anchore/grype/releases/download/{version}/{filename}"

        logger.info(f"Downloading grype from {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            tar_path = os.path.join(temp_dir, filename)
            urllib.request.urlretrieve(url, tar_path)

            # Extract tar.gz
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(temp_dir)

            # Find grype binary and copy to local bin
            grype_bin = os.path.join(temp_dir, 'grype')
            local_bin_dir = os.path.expanduser('~/.local/bin')
            os.makedirs(local_bin_dir, exist_ok=True)

            shutil.copy2(grype_bin, os.path.join(local_bin_dir, 'grype'))
            os.chmod(os.path.join(local_bin_dir, 'grype'), 0o755)

        logger.info("Grype installed successfully")
        return True

    except Exception as ex:
        logger.error(f"Failed to install grype: {ex}")
        return False


def ensure_grype():
    """Ensure grype is installed and available"""
    try:
        # Try grype in PATH first
        result = subprocess.run(['grype', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # Try local installation
    local_grype = os.path.expanduser('~/.local/bin/grype')
    if os.path.exists(local_grype):
        try:
            result = subprocess.run([local_grype, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except Exception:
            pass

    # Install grype if not found
    logger.info("Grype not found, installing...")
    return install_grype()


def ensure_syft_grype():
    """Ensure syft and grype are installed and available"""
    def check_command(cmd):
        try:
            # Check in PATH first
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Check in ~/.local/bin
            local_bin = os.path.expanduser(f'~/.local/bin/{cmd}')
            if os.path.exists(local_bin):
                try:
                    subprocess.run([local_bin, '--version'], capture_output=True, check=True)
                    return True
                except subprocess.CalledProcessError:
                    pass
            return False

    # Check and install syft
    if not check_command('syft'):
        logger.info("Syft not found. Installing...")
        if not install_syft():
            logger.error("Failed to install syft")
            return False

    # Check and install grype
    if not check_command('grype'):
        logger.info("Grype not found. Installing...")
        if not install_grype():
            logger.error("Failed to install grype")
            return False

    return True


def run_syft_analysis(jar_files, output_dir):
    """Run syft to generate SBOM for multiple jar files"""
    output_file = os.path.join(output_dir, 'syft-report.json')

    # Try syft in PATH first, then local bin
    syft_cmd = 'syft'
    try:
        subprocess.run([syft_cmd, '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        syft_cmd = os.path.expanduser('~/.local/bin/syft')

    try:
        # Create temp dir and copy jar files (symlinks don't work well with new syft version)
        temp_dir = tempfile.mkdtemp()
        try:
            for jar_file in jar_files:
                # Copy jar file
                jar_basename = os.path.basename(jar_file)
                dest_path = os.path.join(temp_dir, jar_basename)
                shutil.copy2(jar_file, dest_path)

            # Use java-archive-cataloger specifically for jar files
            cmd = [syft_cmd, f'dir:{temp_dir}',
                   '--override-default-catalogers', 'java-archive-cataloger',
                   '-o', f'json={output_file}']

            logger.debug(f"Running syft command: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(output_file):
                logger.debug(f"Syft analysis completed: {output_file}")
                return output_file
            else:
                logger.error("Syft analysis failed: output file not created")
                return None
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"Syft analysis failed: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Error running syft analysis: {str(e)}")
        return None


def run_grype_analysis(jar_files, output_dir, syft_report_file=None):
    """Run grype to scan vulnerabilities for multiple jar files using syft SBOM if available"""
    output_file = os.path.join(output_dir, 'grype-report.json')

    # Try grype in PATH first, then local bin
    grype_cmd = 'grype'
    try:
        subprocess.run([grype_cmd, '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        grype_cmd = os.path.expanduser('~/.local/bin/grype')

    try:
        # Use syft SBOM if available, otherwise scan jar files directly
        if syft_report_file and os.path.exists(syft_report_file):
            input_source = f'sbom:{syft_report_file}'
            logger.debug(f"Running grype with syft SBOM: {syft_report_file}")
            cmd = [grype_cmd, input_source, '-o', f'json={output_file}']
        else:
            logger.debug("Can't find syft report file. Scanning jar files directly.")
            # Create temp dir and copy jar files for unified processing
            temp_dir = tempfile.mkdtemp()
            try:
                for jar_file in jar_files:
                    # Copy jar file instead of symlinking
                    jar_basename = os.path.basename(jar_file)
                    dest_path = os.path.join(temp_dir, jar_basename)
                    shutil.copy2(jar_file, dest_path)

                # Scan jar files directly without deprecated flags
                cmd = [grype_cmd, f'dir:{temp_dir}',
                       '-o', f'json={output_file}']

                logger.debug(f"Running grype command: {' '.join(cmd)}")
                subprocess.run(cmd, capture_output=True, text=True, check=True)

                logger.debug(f"Grype analysis completed for {len(jar_files)} jar files")
                return output_file
            finally:
                # Clean up temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)

        # For SBOM case
        logger.debug(f"Running grype command: {' '.join(cmd)}")
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        logger.debug(f"Grype analysis completed for {len(jar_files)} jar files")
        return output_file
    except subprocess.CalledProcessError as ex:
        logger.error(f"Error running grype analysis: {ex.stderr}")
        return None


def merge_oss_and_vul_items(bin, key, oss_list, vulnerability_items):
    bin.set_oss_items(oss_list)
    if vulnerability_items and vulnerability_items.get(key):
        bin.vulnerability_items.extend(vulnerability_items.get(key, []))


def merge_binary_list(syft_grype_items, vulnerability_items, bin_list):
    not_found_bin = []

    # key : file_path / value : {"oss_list": [oss], "sha1": sha1} for one binary
    for key, value in syft_grype_items.items():
        found = False
        oss_list = value["oss_list"]
        sha1 = value.get("sha1", "")
        for bin in bin_list:
            if bin.source_name_or_path == key:
                found = True
                for oss in oss_list:
                    if oss.name and oss.license:
                        bin.found_in_syft = True
                        break
                merge_oss_and_vul_items(bin, key, oss_list, vulnerability_items)
            else:
                if bin.checksum == sha1:
                    merge_oss_and_vul_items(bin, key, oss_list, vulnerability_items)

        if not found:
            bin_item = BinaryItem(os.path.abspath(key))
            bin_item.binary_name_without_path = os.path.basename(key)
            bin_item.source_name_or_path = key

            is_pkg, _ = is_package_dir(bin_item.source_name_or_path, '')
            if is_pkg:
                continue

            bin_item.set_oss_items(oss_list)
            not_found_bin.append(bin_item)

    bin_list += not_found_bin
    return bin_list


def parse_syft_report(syft_json_file):
    """Parse syft SBOM report to extract OSS information"""
    oss_items = {}

    try:
        with open(syft_json_file, 'r') as f:
            syft_data = json.load(f)

        artifacts = syft_data.get('artifacts', [])

        for artifact in artifacts:
            name = artifact.get('name', '')
            version = artifact.get('version', '')
            purl = artifact.get('purl', '')
            licenses = artifact.get('licenses', [])

            # Extract license information
            license_str = ''
            if licenses:
                license_str = ', '.join([lic.get('value', '') for lic in licenses if lic.get('value')])

            # Get download URL from PURL if available
            download_url = ''
            if purl:
                download_url = purl

            # Use locations to map to file paths
            locations = artifact.get('locations', [])
            for location in locations:
                file_path = location.get('path', '')
                if file_path.endswith('.jar'):
                    file_path = os.path.basename(file_path)

                    oss = OssItem(name, version, license_str, download_url)
                    oss.comment = "Syft result"

                    if file_path in oss_items:
                        oss_items[file_path]["oss_list"].append(oss)
                    else:
                        oss_items[file_path] = {
                            "oss_list": [oss],
                            "sha1": ""
                        }

    except Exception as ex:
        logger.error(f"Error parsing syft report: {ex}")

    return oss_items


def parse_grype_report(grype_json_file):
    """Parse grype vulnerability report"""
    vulnerability_items = {}

    try:
        with open(grype_json_file, 'r') as f:
            grype_data = json.load(f)

        matches = grype_data.get('matches', [])

        for match in matches:
            vulnerability = match.get('vulnerability', {})
            artifact = match.get('artifact', {})

            vul_id = vulnerability.get('id', '')

            # Try to get NVD URL from related vulnerabilities first
            nvd_url = ''
            related_vulnerabilities = match.get('relatedVulnerabilities', [])
            for related_vul in related_vulnerabilities:
                related_id = related_vul.get('id', '')
                related_datasource = related_vul.get('dataSource', '')
                if 'cve' in related_id.lower() and 'nvd' in related_datasource.lower():
                    nvd_url = related_datasource
                    vul_id = related_id  # Use CVE ID instead of GHSA
                    break

            # Get artifact location
            locations = artifact.get('locations', [])
            for location in locations:
                file_path = location.get('path', '')
                if file_path.endswith('.jar'):
                    file_path = os.path.basename(file_path)

                    vul_item = VulnerabilityItem(file_path, vul_id, nvd_url)

                    if file_path in vulnerability_items:
                        vulnerability_items[file_path].append(vul_item)
                    else:
                        vulnerability_items[file_path] = [vul_item]

    except Exception as ex:
        logger.error(f"Error parsing grype report: {ex}")

    return vulnerability_items


def analyze_jar_file(path_to_find_bin, path_to_exclude):
    """Analyze jar files using syft and grype"""
    syft_items = {}
    vulnerability_items = {}
    success = True

    # Check if syft and grype are installed
    if not ensure_syft_grype():
        logger.error("Syft or Grype is not installed. Cannot proceed with jar analysis.")
        return syft_items, vulnerability_items, False

    # Find all jar files in the directory
    jar_files = []
    for root, dirs, files in os.walk(path_to_find_bin):
        for file in files:
            if file.endswith('.jar'):
                jar_path = os.path.join(root, file)

                # Check if jar file should be excluded
                should_exclude = False
                for exclude_path in path_to_exclude:
                    # Convert both paths to absolute paths to avoid mixing absolute and relative paths
                    exclude_path_abs = os.path.abspath(exclude_path)
                    jar_path_abs = os.path.abspath(jar_path)

                    try:
                        if os.path.commonpath([jar_path_abs, exclude_path_abs]) == exclude_path_abs:
                            should_exclude = True
                            break
                    except ValueError:
                        # If commonpath fails, try simple path comparison
                        if jar_path_abs == exclude_path_abs:
                            should_exclude = True
                            break

                if not should_exclude:
                    jar_files.append(jar_path)

    if not jar_files:
        logger.info("No jar files found for analysis")
        return syft_items, vulnerability_items, True

    # Create output directory for reports in current working directory
    output_dir = os.path.join(os.getcwd(), 'syft_grype_reports')
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Try jar analysis first for better performance
        logger.info(f"Starting jar analysis of {len(jar_files)} jar files")

        # Run syft analysis
        syft_report = run_syft_analysis(jar_files, output_dir)
        if syft_report:
            jar_oss_items = parse_syft_report(syft_report)
            # Merge OSS items for all jar files
            for file_path, data in jar_oss_items.items():
                # Find matching jar file by basename
                matching_jar = None
                for jar_file in jar_files:
                    if os.path.basename(jar_file) == file_path:
                        matching_jar = jar_file
                        break

                if matching_jar:
                    relative_path = os.path.relpath(matching_jar, path_to_find_bin)
                    if relative_path in syft_items:
                        syft_items[relative_path]["oss_list"].extend(data["oss_list"])
                    else:
                        syft_items[relative_path] = data

        # Run grype analysis using syft SBOM if available
        grype_report = run_grype_analysis(jar_files, output_dir, syft_report)
        if grype_report:
            jar_vul_items = parse_grype_report(grype_report)
            # Merge vulnerability items for all jar files
            for file_path, vul_list in jar_vul_items.items():
                # Find matching jar file by basename
                matching_jar = None
                for jar_file in jar_files:
                    if os.path.basename(jar_file) == file_path:
                        matching_jar = jar_file
                        break

                if matching_jar:
                    relative_path = os.path.relpath(matching_jar, path_to_find_bin)
                    if relative_path in vulnerability_items:
                        vulnerability_items[relative_path].extend(vul_list)
                    else:
                        vulnerability_items[relative_path] = vul_list

        if not syft_report or not grype_report:
            logger.info("Failed to analyze jar files")

    except Exception as ex:
        logger.error(f"Error during jar analysis: {ex}")
        success = False

    finally:
        # Clean up syft_grype_reports directory in current working directory
        try:
            syft_grype_reports_dir = os.path.join(os.getcwd(), 'syft_grype_reports')
            if os.path.exists(syft_grype_reports_dir):
                shutil.rmtree(syft_grype_reports_dir)
                logger.debug(f"Cleaned up report directory: {syft_grype_reports_dir}")
        except Exception as ex:
            logger.debug(f"Error cleaning up report files: {ex}")

    logger.info("Completed jar analysis.")
    return syft_items, vulnerability_items, success
