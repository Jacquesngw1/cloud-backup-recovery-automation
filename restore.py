#!/usr/bin/env python3
"""Cloud Restore Script - Restore from a backup folder.

Restores files from a previously created backup to the original source
directory or a specified target directory.

Usage:
    python restore.py backup_folder
    python restore.py backup_folder --target /path/to/restore
"""

import argparse
import json
import logging
import os
import shutil
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def read_manifest(backup_folder):
    """Read and return the backup manifest.

    Args:
        backup_folder: Path to the backup folder containing manifest.json.

    Returns:
        Dictionary with manifest data, or None if manifest is missing/invalid.
    """
    manifest_path = os.path.join(backup_folder, "manifest.json")
    if not os.path.isfile(manifest_path):
        logger.error("Manifest not found: %s", manifest_path)
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    logger.info(
        "Manifest loaded: %d file(s) from backup at %s",
        manifest.get("total_files", 0),
        manifest.get("timestamp", "unknown"),
    )
    return manifest


def restore_files(backup_folder, target_dir, manifest):
    """Restore files from a backup folder to the target directory.

    Args:
        backup_folder: Path to the backup folder.
        target_dir: Path to the directory where files will be restored.
        manifest: Dictionary with backup metadata including file list.

    Returns:
        List of files that were restored.
    """
    restored_files = []
    for rel_file in manifest.get("files", []):
        src_file = os.path.join(backup_folder, rel_file)
        dst_file = os.path.join(target_dir, rel_file)

        if not os.path.isfile(src_file):
            logger.warning("File missing from backup: %s", rel_file)
            continue

        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)
        restored_files.append(rel_file)
        logger.info("Restored: %s", rel_file)

    return restored_files


def run_restore(backup_folder, target_dir=None):
    """Execute the full restore process.

    Args:
        backup_folder: Path to the backup folder to restore from.
        target_dir: Optional target directory. If None, uses the original
                    source path recorded in the manifest.

    Returns:
        List of restored files, or None if restore failed.
    """
    if not os.path.isdir(backup_folder):
        logger.error("Backup folder does not exist: %s", backup_folder)
        return None

    manifest = read_manifest(backup_folder)
    if manifest is None:
        return None

    if target_dir is None:
        target_dir = manifest.get("source", "restored_data")

    logger.info(
        "Starting restore from '%s' to '%s'", backup_folder, target_dir
    )
    os.makedirs(target_dir, exist_ok=True)
    restored_files = restore_files(backup_folder, target_dir, manifest)

    logger.info(
        "Restore complete: %d file(s) restored to '%s'",
        len(restored_files),
        target_dir,
    )
    return restored_files


def main():
    """Parse arguments and run the restore."""
    parser = argparse.ArgumentParser(description="Cloud Restore Script")
    parser.add_argument(
        "backup_folder",
        help="Path to the backup folder to restore from",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Target directory for restore (default: original source path)",
    )
    args = parser.parse_args()

    result = run_restore(args.backup_folder, args.target)
    if result is None:
        sys.exit(1)
    return result


if __name__ == "__main__":
    main()
