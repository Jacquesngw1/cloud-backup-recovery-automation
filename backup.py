#!/usr/bin/env python3
"""Cloud Backup Script - Automated backup with scheduling support.

Creates timestamped backups of a source directory to a backup storage location.
Supports configurable source and destination paths via environment variables
or command-line arguments.

Usage:
    python backup.py
    python backup.py --source /path/to/source --dest /path/to/backups
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_SOURCE = os.environ.get("BACKUP_SOURCE", "data")
DEFAULT_DEST = os.environ.get("BACKUP_DEST", "backups")


def create_backup_folder(dest_dir):
    """Create a timestamped backup folder inside the destination directory.

    Args:
        dest_dir: Path to the destination directory for backups.

    Returns:
        Path to the newly created timestamped backup folder.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(dest_dir, f"backup_{timestamp}")
    os.makedirs(backup_folder, exist_ok=True)
    logger.info("Created backup folder: %s", backup_folder)
    return backup_folder


def copy_files(source_dir, backup_folder):
    """Copy all files and directories from source to backup folder.

    Args:
        source_dir: Path to the source directory to back up.
        backup_folder: Path to the backup destination folder.

    Returns:
        List of files that were copied.
    """
    copied_files = []
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        dest_path = os.path.join(backup_folder, rel_path)
        os.makedirs(dest_path, exist_ok=True)
        for filename in files:
            src_file = os.path.join(root, filename)
            dst_file = os.path.join(dest_path, filename)
            shutil.copy2(src_file, dst_file)
            copied_files.append(os.path.relpath(src_file, source_dir))
            logger.info("Copied: %s", os.path.relpath(src_file, source_dir))
    return copied_files


def write_manifest(backup_folder, source_dir, copied_files):
    """Write a manifest file with backup metadata.

    Args:
        backup_folder: Path to the backup folder.
        source_dir: Path to the original source directory.
        copied_files: List of files included in the backup.

    Returns:
        Path to the manifest file.
    """
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": os.path.abspath(source_dir),
        "files": copied_files,
        "total_files": len(copied_files),
    }
    manifest_path = os.path.join(backup_folder, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Manifest written to: %s", manifest_path)
    return manifest_path


def run_backup(source_dir, dest_dir):
    """Execute the full backup process.

    Args:
        source_dir: Path to the source directory to back up.
        dest_dir: Path to the destination directory for backups.

    Returns:
        Path to the backup folder, or None if backup failed.
    """
    if not os.path.isdir(source_dir):
        logger.error("Source directory does not exist: %s", source_dir)
        return None

    logger.info("Starting backup from '%s' to '%s'", source_dir, dest_dir)
    backup_folder = create_backup_folder(dest_dir)
    copied_files = copy_files(source_dir, backup_folder)

    if not copied_files:
        logger.warning("No files found to back up in '%s'", source_dir)
        shutil.rmtree(backup_folder)
        return None

    write_manifest(backup_folder, source_dir, copied_files)
    logger.info(
        "Backup complete: %d file(s) copied to '%s'",
        len(copied_files),
        backup_folder,
    )
    return backup_folder


def main():
    """Parse arguments and run the backup."""
    parser = argparse.ArgumentParser(description="Cloud Backup Script")
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help="Source directory to back up (default: %(default)s)",
    )
    parser.add_argument(
        "--dest",
        default=DEFAULT_DEST,
        help="Destination directory for backups (default: %(default)s)",
    )
    args = parser.parse_args()

    result = run_backup(args.source, args.dest)
    if result is None:
        sys.exit(1)
    return result


if __name__ == "__main__":
    main()
