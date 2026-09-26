#!/usr/bin/env python3
"""Launch the configured QLC+ show with a verified QLC+ web server."""

import argparse
import fcntl
import os
from pathlib import Path
import signal
import subprocess
import tempfile

from default_address import default_address
from interrupt_launch import interrupt_launch
from notify import notify
from offline_workspace import offline_workspace
from pioneer_guard import pioneer_guard
from read_config import read_config
from reserve_port import reserve_port
from stop_process import stop_process
from wait_ready import wait_ready


def main():
    """Serialize starts and keep ownership of the child through verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-no-output", action="store_true",
                        help="Use an I/O-free temporary copy and stop it automatically after 90 seconds.")
    parser.add_argument("--name", default="QLC+ Vibra",
                        help="The installed app's name, which names its state folder (default: %(default)s).")
    parser.add_argument("--workspace-folder", type=Path,
                        help="Where the workspace's folder is now; the Dock app passes its resolved bookmark.")
    args = parser.parse_args()
    state = Path.home() / "Library" / "Application Support" / args.name
    signal.signal(signal.SIGTERM, interrupt_launch)
    process = None
    ready = False
    try:
        config = read_config(state / "launcher.toml")
        binary = config["qlcplus"]
        workspace = config["workspace"]
        if args.workspace_folder is not None:
            workspace = args.workspace_folder / workspace.name
        if not binary.is_file() or not os.access(binary, os.X_OK):
            raise RuntimeError(f"QLC+ executable is missing or not executable: {binary}")
        if not workspace.is_file():
            raise RuntimeError(f"QLC+ workspace is missing: {workspace}. Restore it before launching.")
        pioneer_guard()
        address = default_address()
        state.mkdir(parents=True, exist_ok=True)
        with (state / "launch.lock").open("a") as lock, tempfile.TemporaryDirectory(prefix="qlc-launcher-") as temporary:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError(f"{args.name} is already starting. Wait for its address notification.") from error
            if args.test_no_output:
                workspace = offline_workspace(workspace, Path(temporary) / workspace.name)
                print(f"TEST MODE: temporary copy of {workspace.name}, no hardware I/O, automatic stop after 90 seconds.", flush=True)
            with reserve_port() as reservation:
                port = reservation.getsockname()[1]
                with (state / "qlcplus.log").open("w") as log:
                    # QLC+ has no socket activation. Hold until spawn, then verify
                    # the listener belongs to this exact child before accepting HTTP.
                    reservation.close()
                    process = subprocess.Popen(
                        [str(binary), "-w", "--wp", str(port), "-o", str(workspace)],
                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
                print(f"Started QLC+ PID {process.pid}, port {port}.", flush=True)
                wait_ready(process, port)
                print(f"HTTP check passed: http://127.0.0.1:{port}/ contains QLC+; listener PID {process.pid}.", flush=True)
                notify(f"{args.name} on {address}:{port}" + (" (test: no hardware output)" if args.test_no_output else ""), title=args.name)
                ready = True
                if args.test_no_output:
                    try:
                        process.wait(timeout=90)
                    except subprocess.TimeoutExpired:
                        pass
                    stop_process(process)
                    print(f"Stopped test QLC+ PID {process.pid}.", flush=True)
        return 0
    except (Exception, KeyboardInterrupt) as error:
        cleanup_message = ""
        if process is not None and (not ready or args.test_no_output):
            try:
                stop_process(process)
            except Exception as cleanup_error:
                cleanup_message = f" Could not stop new QLC+ PID {process.pid}: {cleanup_error}."
        message = f"{args.name} could not start: {error or 'interrupted'}.{cleanup_message} See {state / 'qlcplus.log'} if QLC+ started."
        try:
            notify(message, error=True, title=args.name)
        except Exception as notification_error:
            print(f"Native message failed: {notification_error}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
