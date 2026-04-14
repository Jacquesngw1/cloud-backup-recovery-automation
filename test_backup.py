"""Tests for backup.py."""

import json
import os
import shutil
import tempfile

from backup import copy_files, create_backup_folder, run_backup, write_manifest


class TestCreateBackupFolder:
    """Tests for create_backup_folder."""

    def test_creates_folder(self, tmp_path):
        folder = create_backup_folder(str(tmp_path))
        assert os.path.isdir(folder)
        assert folder.startswith(str(tmp_path))

    def test_folder_name_has_backup_prefix(self, tmp_path):
        folder = create_backup_folder(str(tmp_path))
        basename = os.path.basename(folder)
        assert basename.startswith("backup_")


class TestCopyFiles:
    """Tests for copy_files."""

    def setup_method(self):
        self.source = tempfile.mkdtemp()
        self.dest = tempfile.mkdtemp()
        # Create sample files
        with open(os.path.join(self.source, "file1.txt"), "w") as f:
            f.write("hello")
        sub = os.path.join(self.source, "subdir")
        os.makedirs(sub)
        with open(os.path.join(sub, "file2.txt"), "w") as f:
            f.write("world")

    def teardown_method(self):
        shutil.rmtree(self.source)
        shutil.rmtree(self.dest)

    def test_copies_all_files(self):
        copied = copy_files(self.source, self.dest)
        assert len(copied) == 2
        assert "file1.txt" in copied
        assert os.path.join("subdir", "file2.txt") in copied

    def test_files_exist_in_dest(self):
        copy_files(self.source, self.dest)
        assert os.path.isfile(os.path.join(self.dest, "file1.txt"))
        assert os.path.isfile(
            os.path.join(self.dest, "subdir", "file2.txt")
        )

    def test_file_contents_preserved(self):
        copy_files(self.source, self.dest)
        with open(os.path.join(self.dest, "file1.txt")) as f:
            assert f.read() == "hello"


class TestWriteManifest:
    """Tests for write_manifest."""

    def test_manifest_created(self, tmp_path):
        files = ["a.txt", "b.txt"]
        path = write_manifest(str(tmp_path), "/src", files)
        assert os.path.isfile(path)

    def test_manifest_contents(self, tmp_path):
        files = ["a.txt", "b.txt"]
        path = write_manifest(str(tmp_path), "/src", files)
        with open(path) as f:
            data = json.load(f)
        assert data["total_files"] == 2
        assert data["files"] == files
        assert "timestamp" in data


class TestRunBackup:
    """Tests for run_backup end-to-end."""

    def test_successful_backup(self, tmp_path):
        source = tmp_path / "src"
        source.mkdir()
        (source / "test.txt").write_text("data")
        dest = tmp_path / "backups"

        result = run_backup(str(source), str(dest))
        assert result is not None
        assert os.path.isdir(result)
        assert os.path.isfile(os.path.join(result, "manifest.json"))
        assert os.path.isfile(os.path.join(result, "test.txt"))

    def test_missing_source_returns_none(self, tmp_path):
        result = run_backup(str(tmp_path / "nonexistent"), str(tmp_path))
        assert result is None

    def test_empty_source_returns_none(self, tmp_path):
        source = tmp_path / "empty"
        source.mkdir()
        result = run_backup(str(source), str(tmp_path / "backups"))
        assert result is None
