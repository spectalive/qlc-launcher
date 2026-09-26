"""2026-09-26: the launcher left the Vibra repository; the show now comes from a config."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bundle_identifier import bundle_identifier
from find_python import find_python
from launch import main
from read_config import read_config
from write_config import write_config


class ConfigTests(unittest.TestCase):
    """The installer's config is the only place the show and QLC+ are named."""

    def test_written_config_reads_back_with_awkward_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "launcher.toml"
            qlcplus = Path("/Applications/QLC+ 5.2.2.app/Contents/MacOS/qlcplus-qml")
            workspace = Path('/Users/me/Shows/Día "uno" \\ back/QLC+ Setups/Vibra.qxw')
            write_config(path, qlcplus, workspace)
            self.assertEqual(read_config(path), {"qlcplus": qlcplus, "workspace": workspace})

    def test_missing_config_names_the_installer(self):
        with self.assertRaisesRegex(RuntimeError, "missing.*install.py"):
            read_config(Path("/nonexistent/launcher.toml"))

    def test_invalid_toml_is_refused(self):
        with tempfile.NamedTemporaryFile("w", suffix=".toml") as file:
            file.write("qlcplus = \n")
            file.flush()
            with self.assertRaisesRegex(RuntimeError, "not valid TOML"):
                read_config(file.name)

    def test_missing_or_relative_paths_are_refused(self):
        for body in ('qlcplus = "/bin/qlcplus"\n', 'qlcplus = "/bin/qlcplus"\nworkspace = "Show.qxw"\n',
                     'qlcplus = 1\nworkspace = "/Show.qxw"\n'):
            with self.subTest(body=body), tempfile.NamedTemporaryFile("w", suffix=".toml") as file:
                file.write(body)
                file.flush()
                with self.assertRaisesRegex(RuntimeError, "absolute path"):
                    read_config(file.name)

    def test_default_name_keeps_the_original_bundle_identifier(self):
        self.assertEqual(bundle_identifier("QLC+ Vibra"), "com.busirocket.qlc-vibra")
        self.assertEqual(bundle_identifier("  Club Night 2 "), "com.busirocket.club-night-2")
        with self.assertRaises(SystemExit):
            bundle_identifier("+++")

    def test_bundle_prefix_is_a_reverse_dns_prefix(self):
        self.assertEqual(bundle_identifier("QLC+ Vibra", "org.example."), "org.example.qlc-vibra")
        for prefix in ("org.example", "", ".org.", "org..example.", "org example."):
            with self.subTest(prefix=prefix), self.assertRaisesRegex(SystemExit, "Bundle prefix"):
                bundle_identifier("QLC+ Vibra", prefix)

    def test_python_without_tomllib_is_skipped(self):
        self.assertEqual(find_python((Path("/nonexistent/python3"), Path(sys.executable))), Path(sys.executable))
        with self.assertRaises(SystemExit):
            find_python((Path("/nonexistent/python3"),))

    @patch("launch.signal.signal")
    @patch("launch.notify")
    @patch("launch.subprocess.Popen")
    @patch("launch.os.access", return_value=True)
    @patch("launch.Path.is_file", side_effect=[True, False])
    def test_state_follows_name_and_workspace_follows_its_folder(self, is_file, access, spawn, message, signal):
        with tempfile.TemporaryDirectory() as directory, \
                patch("launch.Path.home", return_value=Path(directory)), \
                patch("launch.read_config", return_value={
                    "qlcplus": Path("/bin/qlcplus"), "workspace": Path("/old/place/Show.qxw")}) as config, \
                patch("sys.argv", ["launch.py", "--name", "Club", "--workspace-folder", "/new/place"]):
            self.assertEqual(main(), 1)
            config.assert_called_once_with(Path(directory) / "Library/Application Support/Club/launcher.toml")
        spawn.assert_not_called()
        self.assertIn("/new/place/Show.qxw", message.call_args.args[0])
        self.assertEqual(message.call_args.kwargs["title"], "Club")


if __name__ == "__main__":
    unittest.main()
