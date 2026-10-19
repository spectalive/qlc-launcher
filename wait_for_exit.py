"""Block until one of several processes exits, without polling or owning them."""

import select


def wait_for_exit(pids):
    """Return the first of `pids` to exit; QLC+ is not our child once launch.py has gone."""
    queue = select.kqueue()
    try:
        events = [select.kevent(pid, select.KQ_FILTER_PROC, select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
                                select.KQ_NOTE_EXIT) for pid in pids]
        for event in events:
            try:
                queue.control([event], 0)
            except ProcessLookupError:
                return event.ident
        return queue.control(None, 1)[0].ident
    finally:
        queue.close()
