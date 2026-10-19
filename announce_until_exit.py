#!/usr/bin/env python3
"""Announce a verified QLC+ web port over Bonjour for exactly as long as that QLC+ runs."""

import argparse
import signal
import subprocess

from interrupt_launch import interrupt_launch
from stop_process import stop_process
from wait_for_exit import wait_for_exit


def main():
    """Keep `dns-sd -R` alive until QLC+ exits, then withdraw it, so no announce outlives the show."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="The Bonjour service name, the show's app name.")
    parser.add_argument("--port", type=int, required=True, help="QLC+'s verified web port.")
    parser.add_argument("--pid", type=int, required=True, help="The QLC+ process the announce belongs to.")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupt_launch)
    announce = subprocess.Popen(["/usr/bin/dns-sd", "-R", args.name, "_http._tcp", "local", str(args.port)],
                                stdin=subprocess.DEVNULL)
    try:
        exited = wait_for_exit([args.pid, announce.pid])
        print(f"{'QLC+ PID' if exited == args.pid else 'dns-sd PID'} {exited} exited; announce withdrawn.", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        stop_process(announce)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
