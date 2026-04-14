"""Tests for restore.py."""

import json
import os
import shutil
import tempfile

from restore import read_manifest, restore_files, run_restore


class TestReadManifest:
    """Tests for read_manifest."""

    def test_reads_valid_manifest(self, tmp_path):
        manifest_data = {
            "timestamp": "2026-01-01T00:00:00",
            "source": "/src",
            "files": ["a.txt"],
            "total_files": 1,
        }
        (tmp_path / "manifest.json").write_text(json.dumps(manifest_data))
        result = read_manifest(str(tmp_path))
        assert result == manifest_data

    def test_missing_manifest_returns_none(self, tmp_path):
        result = read_manifest(str(tmp_path))
        assert result is None


class TestRestoreFiles:
    """Tests for restore_files."""

    def setup_method(self):
        self.backup_dir = tempfile.mkdtemp()
        self.target_dir = tempfile.mkdtemp()
        # Create a backed-up file
        with open(os.path.join(self.backup_dir, "file.txt"), "w") as f:
            f.write("content")
        sub = os.path.join(self.backup_dir, "sub")
        os.makedirs(sub)
        with open(os.path.join(sub, "nested.txt"), "w") as f:
            f.write("nested content")

    def teardown_method(self):
        shutil.rmtree(self.backup_dir)
        shutil.rmtree(self.target_dir)

    def test_restores_files(self):
        manifest = {
            "files": ["file.txt", os.path.join("sub", "nested.txt")]
        }
        restored = restore_files(
            self.backup_dir, self.target_dir, manifest
        )
        assert len(restored) == 2
        assert os.path.isfile(os.path.join(self.target_dir, "file.txt"))

    def test_skips_missing_files(self):
        manifest = {"files": ["missing.txt"]}
        restored = restore_files(
            self.backup_dir, self.target_dir, manifest
        )
        assert len(restored) == 0


class TestRunRestore:
    """Tests for run_restore end-to-end."""

    def test_full_restore_cycle(self, tmp_path):
        # Set up a fake backup folder with manifest
        backup = tmp_path / "backup_20260101_000000"
        backup.mkdir()
        (backup / "data.txt").write_text("important data")
        target = tmp_path / "restored"
        manifest = {
            "timestamp": "2026-01-01T00:00:00",
            "source": str(target),
            "files": ["data.txt"],
            "total_files": 1,
        }
        (backup / "manifest.json").write_text(json.dumps(manifest))

        result = run_restore(str(backup), str(target))
        assert result is not None
        assert len(result) == 1
        assert (target / "data.txt").read_text() == "important data"

    def test_nonexistent_backup_returns_none(self, tmp_path):
        result = run_restore(str(tmp_path / "nope"))
        assert result is None

    def test_backup_without_manifest_returns_none(self, tmp_path):
        folder = tmp_path / "no_manifest"
        folder.mkdir()
        result = run_restore(str(folder))
        assert result is None
