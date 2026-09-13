"""2026-09-13: two evenings lost to normal launches without the web server."""

import errno
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from default_address import default_address
from interrupt_launch import interrupt_launch
from launch import main
from listener_pids import listener_pids
from notify import notify
from offline_workspace import offline_workspace
from pioneer_guard import pioneer_guard
from reserve_port import reserve_port
from stop_process import stop_process
from wait_ready import wait_ready


class LauncherTests(unittest.TestCase):
    """Exercise real bind conflicts and the safety boundaries around launch."""

    @patch("launch.signal.signal")
    @patch("launch.notify")
    @patch("launch.subprocess.Popen")
    @patch("launch.os.access", return_value=False)
    @patch("sys.argv", ["launch.py"])
    def test_missing_binary_does_not_spawn(self, access, spawn, message, signal):
        self.assertEqual(main(), 1)
        spawn.assert_not_called()
        self.assertIn("executable is missing", message.call_args.args[0])

    @patch("launch.signal.signal")
    @patch("launch.notify")
    @patch("launch.subprocess.Popen")
    @patch("launch.os.access", return_value=True)
    @patch("launch.Path.is_file", side_effect=[True, False])
    @patch("sys.argv", ["launch.py"])
    def test_missing_workspace_does_not_spawn(self, is_file, access, spawn, message, signal):
        self.assertEqual(main(), 1)
        spawn.assert_not_called()
        self.assertIn("workspace is missing", message.call_args.args[0])

    def test_termination_enters_cleanup_path(self):
        with self.assertRaises(KeyboardInterrupt):
            interrupt_launch(15, None)

    def test_unreapable_child_still_gets_a_visible_error(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch("sys.argv", ["launch.py"]), \
                patch("launch.signal.signal"), \
                patch("launch.Path.home", return_value=Path(directory)), \
                patch("launch.Path.is_file", return_value=True), \
                patch("launch.os.access", return_value=True), \
                patch("launch.pioneer_guard"), \
                patch("launch.default_address", return_value="10.20.30.40"), \
                patch("launch.reserve_port") as reservation, \
                patch("launch.subprocess.Popen", return_value=MagicMock(pid=123)), \
                patch("launch.wait_ready", side_effect=RuntimeError("startup timed out")), \
                patch("launch.stop_process", side_effect=subprocess.TimeoutExpired("child", 5)), \
                patch("launch.notify") as message:
            reservation.return_value.__enter__.return_value.getsockname.return_value = ("::", 9999)
            self.assertEqual(main(), 1)
            self.assertIn("startup timed out", message.call_args.args[0])
            self.assertIn("Could not stop new QLC+ PID 123", message.call_args.args[0])
            self.assertTrue(message.call_args.kwargs["error"])

    def test_reservation_excludes_ipv4_and_ipv6_competitors(self):
        with reserve_port((0,)) as reservation:
            port = reservation.getsockname()[1]
            for family, address in ((socket.AF_INET, "0.0.0.0"), (socket.AF_INET6, "::")):
                with socket.socket(family, socket.SOCK_STREAM) as rival:
                    with self.assertRaises(OSError) as result:
                        rival.bind((address, port))
                    self.assertEqual(result.exception.errno, errno.EADDRINUSE)

    def test_busy_first_port_falls_back(self):
        with reserve_port((0,)) as busy:
            with reserve_port((busy.getsockname()[1], 0)) as free:
                self.assertNotEqual(busy.getsockname()[1], free.getsockname()[1])

    def test_all_ports_busy_refuses(self):
        with reserve_port((0,)) as busy:
            with self.assertRaisesRegex(RuntimeError, "both in use"):
                reserve_port((busy.getsockname()[1], busy.getsockname()[1]))

    @patch("default_address.subprocess.run")
    def test_address_comes_only_from_default_interface(self, run):
        run.side_effect = [MagicMock(stdout=" interface: en7\n"), MagicMock(stdout="10.20.30.40\n")]
        self.assertEqual(default_address(), "10.20.30.40")
        self.assertEqual(run.call_args.args[0], ["/usr/sbin/ipconfig", "getifaddr", "en7"])

    @patch("default_address.subprocess.run")
    def test_missing_route_refuses_to_guess(self, run):
        run.return_value.stdout = "no route"
        with self.assertRaisesRegex(RuntimeError, "No default-route"):
            default_address()

    @patch("default_address.subprocess.run")
    def test_missing_interface_address_refuses_to_guess(self, run):
        run.side_effect = [MagicMock(stdout=" interface: en7\n"), MagicMock(stdout="")]
        with self.assertRaisesRegex(RuntimeError, "No IPv4 address"):
            default_address()

    @patch("pioneer_guard.subprocess.run")
    def test_pioneer_running_refuses(self, run):
        run.return_value.stdout = "123 /Library/Pioneer/com.pioneerdj.FwUpdateManagerd\n"
        with self.assertRaisesRegex(RuntimeError, "Pioneer.*PID 123"):
            pioneer_guard()

    @patch("pioneer_guard.subprocess.run")
    def test_unrelated_executables_do_not_trigger_pioneer_guard(self, run):
        run.return_value.stdout = "123 /bin/zsh\n456 /usr/bin/python3\n"
        pioneer_guard()

    @patch("wait_ready.listener_pids", return_value={456})
    def test_rival_qlc_listener_is_not_success(self, listeners):
        process = MagicMock(pid=123)
        process.poll.return_value = None
        with self.assertRaisesRegex(RuntimeError, "Another process took"):
            wait_ready(process, 12345)

    @patch("wait_ready.listener_pids", return_value={123})
    @patch("wait_ready.urllib.request.build_opener")
    def test_http_content_and_pid_both_required(self, build, listeners):
        process = MagicMock(pid=123)
        process.poll.return_value = None
        response = build.return_value.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b"<title>QLC+ Web Interface</title>"
        wait_ready(process, 12345)
        self.assertEqual(listeners.call_count, 2)

    @patch("wait_ready.time.sleep")
    @patch("wait_ready.listener_pids", return_value={123})
    @patch("wait_ready.urllib.request.build_opener")
    def test_wrong_http_body_times_out(self, build, listeners, sleep):
        process = MagicMock(pid=123)
        process.poll.return_value = None
        response = build.return_value.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b"unrelated server"
        with self.assertRaisesRegex(RuntimeError, "did not serve"):
            wait_ready(process, 12345, timeout=0.01)

    def test_exited_process_is_failure(self):
        process = MagicMock(returncode=2)
        process.poll.return_value = 2
        with self.assertRaisesRegex(RuntimeError, "exited"):
            wait_ready(process, 12345)

    def test_timeout_cleanup_only_signals_child(self):
        process = MagicMock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("child", 5), 0]
        stop_process(process)
        process.terminate.assert_called_once()
        process.kill.assert_called_once()

    @patch("listener_pids.subprocess.run")
    def test_listener_inspection_failure_is_not_an_empty_port(self, run):
        run.return_value = MagicMock(returncode=1, stderr="permission failure", stdout="")
        with self.assertRaisesRegex(RuntimeError, "Cannot verify"):
            listener_pids(12345)

    @patch("notify.subprocess.run")
    def test_notification_message_is_an_argument_not_code(self, run):
        message = 'QLC+ Vibra on "quoted" address'
        notify(message)
        command = run.call_args.args[0]
        self.assertEqual(command[-1], message)
        self.assertNotIn(message, command[-2])

    def test_verification_copy_cannot_drive_hardware_or_modify_show(self):
        source = Path(__file__).resolve().parents[3] / "QLC+ Setups" / "Vibra.qxw"
        original = source.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = offline_workspace(source, Path(directory) / "Vibra.qxw")
            self.assertIn(b"<!DOCTYPE Workspace>", output.read_bytes())
            root = ET.parse(output).getroot()
            self.assertEqual(root.findall(".//{*}InputOutputMap"), [])
            self.assertEqual(root.findall(".//{*}Output"), [])
            self.assertTrue(root.findall(".//{*}Function"))
        self.assertEqual(source.read_bytes(), original)
