"""Bound startup by HTTP content and listener ownership, not process liveness."""

import time
import urllib.error
import urllib.request

from listener_pids import listener_pids


def wait_ready(process, port, timeout=45):
    """Accept only our child's QLC+ HTTP response; detect a lost bind handoff."""
    deadline = time.monotonic() + timeout
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"QLC+ exited before its web server was ready (exit {process.returncode}).")
        owners = listener_pids(port)
        if owners and owners != {process.pid}:
            raise RuntimeError(f"Another process took port {port} during startup. This QLC+ instance will stop.")
        if owners == {process.pid}:
            try:
                with opener.open(f"http://127.0.0.1:{port}/", timeout=1) as response:
                    body = response.read(1024 * 1024)
                    if response.status == 200 and b"QLC+" in body:
                        if process.poll() is None and listener_pids(port) == {process.pid}:
                            return
            except (OSError, urllib.error.URLError):
                pass
        time.sleep(0.2)
    raise RuntimeError(f"QLC+ did not serve its web interface on port {port} within {timeout} seconds.")
