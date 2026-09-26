"""2026-09-26 review: the installer's refusal to overwrite was only ever checked by hand."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install import main


class InstallTests(unittest.TestCase):
    """An existing bundle is the operator's; the installer never replaces it."""

    def test_existing_bundle_is_refused_and_left_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            workspace = home / "Show.qxw"
            workspace.write_text("<Workspace/>")
            bundle = home / "Applications" / "Club.app"
            marker = bundle / "Contents" / "Info.plist"
            marker.parent.mkdir(parents=True)
            marker.write_text("the old install")
            argv = ["install.py", "--workspace", str(workspace), "--qlcplus", sys.executable, "--name", "Club"]
            with patch("install.Path.home", return_value=home), patch("sys.argv", argv), \
                    patch("install.subprocess.run") as run, patch("install.find_python") as python:
                with self.assertRaisesRegex(SystemExit, "Already installed"):
                    main()
            run.assert_not_called()
            python.assert_not_called()
            self.assertEqual(marker.read_text(), "the old install")
            self.assertEqual([path.name for path in bundle.rglob("*")], ["Contents", "Info.plist"])
            self.assertFalse((home / "Library" / "Application Support" / "Club").exists())


if __name__ == "__main__":
    unittest.main()
