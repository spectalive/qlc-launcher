"""Report only the IPv4 address of the default-route interface."""

import ipaddress
import subprocess


def default_address():
    """Refuse missing routes instead of guessing from other interfaces."""
    route = subprocess.run(
        ["/sbin/route", "-n", "get", "default"],
        capture_output=True, text=True, check=True, timeout=5,
    ).stdout
    interface = next(
        (line.split(":", 1)[1].strip() for line in route.splitlines()
         if line.strip().startswith("interface:")), None,
    )
    if not interface:
        raise RuntimeError("No default-route interface. Connect the Mac to the tablet network.")
    result = subprocess.run(
        ["/usr/sbin/ipconfig", "getifaddr", interface],
        capture_output=True, text=True, timeout=5,
    )
    try:
        address = ipaddress.IPv4Address(result.stdout.strip())
    except ipaddress.AddressValueError as error:
        raise RuntimeError(f"No IPv4 address on default-route interface {interface}.") from error
    if address.is_loopback or address.is_unspecified or address.is_link_local:
        raise RuntimeError(f"Default-route interface {interface} has no usable LAN address.")
    return str(address)
