"""Convert termination into the launcher's child cleanup path."""


def interrupt_launch(signum, frame):
    """Let the orchestrator reap its child before reporting interruption."""
    raise KeyboardInterrupt("launcher interrupted")
