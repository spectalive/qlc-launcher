"""Stop only the child process owned by this launcher invocation."""

import subprocess


def stop_process(process):
    """Reap the child after TERM, escalating only that child if it hangs."""
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
