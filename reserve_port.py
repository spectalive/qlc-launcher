"""Reserve the first available IPv4/IPv6 web port without address reuse."""

import errno
import socket


def reserve_port(ports=(9998, 9999)):
    """Return a held dual-stack socket; the caller releases it at spawn."""
    for port in ports:
        reservation = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        try:
            reservation.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            reservation.bind(("::", port))
            reservation.listen(1)
            return reservation
        except OSError as error:
            reservation.close()
            if error.errno != errno.EADDRINUSE:
                raise
    raise RuntimeError("Ports 9998 and 9999 are both in use. QLC+ was not started.")
