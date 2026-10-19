"""2026-10-19: the show follows what QLC+ opened last instead of a picker (owner: "que se sincronice con lo que tiene QLC")."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from last_qlcplus_workspace import last_qlcplus_workspace
from launch import main


class LastWorkspaceTests(unittest.TestCase):
    """QLC+'s recent list decides the show; the installed one is the fallback."""

    def test_newest_existing_workspace_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            older = Path(directory) / "Vibra.qxw"
            newer = Path(directory) / "Vibra-split.qxw"
            older.touch()
            newer.touch()
            preferences = {"workspace.recent1": str(older), "workspace.recent0": str(newer),
                           "workspace.windowrect": "@Rect(1 62 1920 1018)"}
            self.assertEqual(last_qlcplus_workspace(preferences), newer)

    def test_validation_copies_and_missing_files_are_skipped(self):
        """On the mini the list was full of qlctool's hidden, deleted validation copies."""
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / ".Vibra.qlctool-validate-3881a4b18e6c495988320f8f408c7230.qxw"
            copy.touch()
            show = Path(directory) / "Vibra.qxw"
            show.touch()
            preferences = {"workspace.recent0": str(copy),
                           "workspace.recent1": str(Path(directory) / "gone.qxw"),
                           "workspace.recent2": str(show)}
            self.assertEqual(last_qlcplus_workspace(preferences), show)

    def test_recent10_sorts_after_recent2(self):
        with tempfile.TemporaryDirectory() as directory:
            second = Path(directory) / "second.qxw"
            tenth = Path(directory) / "tenth.qxw"
            second.touch()
            tenth.touch()
            preferences = {"workspace.recent10": str(tenth), "workspace.recent2": str(second)}
            self.assertEqual(last_qlcplus_workspace(preferences), second)

    def test_no_recent_show_returns_none(self):
        self.assertIsNone(last_qlcplus_workspace({}))

    def test_launch_opens_the_recent_show_instead_of_the_installed_one(self):
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / "Vibra.qxw"
            recent = Path(directory) / "Vibra-beats.qxw"
            installed.touch()
            recent.touch()
            binary = Path(directory) / "qlcplus-qml"
            binary.touch(mode=0o755)
            config = {"qlcplus": binary, "workspace": installed}
            with patch("sys.argv", ["launch.py"]), \
                    patch("launch.signal.signal"), \
                    patch("launch.Path.home", return_value=Path(directory)), \
                    patch("launch.read_config", return_value=config), \
                    patch("launch.read_qlcplus_preferences", return_value={"workspace.recent0": str(recent)}), \
                    patch("launch.pioneer_guard"), \
                    patch("launch.default_address", return_value="10.20.30.40"), \
                    patch("launch.reserve_port") as reservation, \
                    patch("launch.subprocess.Popen", return_value=MagicMock(pid=123)) as popen, \
                    patch("launch.wait_ready"), \
                    patch("launch.announce_show"), \
                    patch("launch.notify"):
                reservation.return_value.__enter__.return_value.getsockname.return_value = ("::", 9999)
                self.assertEqual(main(), 0)
            self.assertEqual(popen.call_args.args[0][-1], str(recent))


if __name__ == "__main__":
    unittest.main()
