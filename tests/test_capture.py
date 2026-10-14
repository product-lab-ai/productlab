"""Source capture must preserve local edits and refuse unsafe destinations."""

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "trials/workings/capture.py"
SPEC = importlib.util.spec_from_file_location("workings_capture", SCRIPT)
capture_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture_module)


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        (self.source / "tracked.txt").write_text("original\n")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "Initial fixture",
        )
        (self.source / "tracked.txt").write_text("local edit\n")
        (self.source / "new.txt").write_text("new work\n")
        self.output = self.root / "review"

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.source), *args])

    def test_capture_keeps_dirty_and_untracked_work_without_source_changes(self):
        before = capture_module.source_manifest(self.source)
        status = self.git("status", "--porcelain")
        record = capture_module.capture(self.source, self.output)
        self.assertEqual(record["status"], "verified")
        self.assertEqual(record["files"], before)
        self.assertEqual((self.output / "source/tracked.txt").read_text(), "local edit\n")
        self.assertEqual((self.output / "source/new.txt").read_text(), "new work\n")
        self.assertEqual(capture_module.source_manifest(self.source), before)
        self.assertEqual(self.git("status", "--porcelain"), status)

    def test_capture_refuses_existing_output_and_nested_source(self):
        self.output.mkdir()
        marker = self.output / "evidence.txt"
        marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            capture_module.capture(self.source, self.output)
        self.assertEqual(marker.read_text(), "keep")
        with self.assertRaises(ValueError):
            capture_module.capture(self.source, self.source / "nested")

    def test_capture_refuses_source_symlinks(self):
        (self.source / "link").symlink_to(self.source / "new.txt")
        with self.assertRaisesRegex(ValueError, "symlinks"):
            capture_module.capture(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_capture_preserves_failed_copy_when_source_changes(self):
        copy = capture_module.shutil.copy2

        def changed(source, target, **kwargs):
            result = copy(source, target, **kwargs)
            Path(source).write_text("changed during capture")
            return result

        with patch.object(capture_module.shutil, "copy2", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "Source changed"):
                capture_module.capture(self.source, self.output)
        record = json.loads((self.output / "source-manifest.json").read_text())
        self.assertEqual(record["status"], "failed")
        self.assertTrue((self.output / "source/new.txt").exists())


if __name__ == "__main__":
    unittest.main()
