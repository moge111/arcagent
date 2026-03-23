"""SSRF prevention — validate URLs against private networks.

Pattern from NemoClaw's runner.py: validate_endpoint_url with
private IP detection and DNS resolution checks.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

_PRIVATE_NETWORKS = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fd00::/8"),
)


def is_private_ip(addr: str) -> bool:
    """Check if an IP address falls within private/internal ranges."""
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return False
    return any(ip in net for net in _PRIVATE_NETWORKS)


def validate_url(url: str) -> str:
    """Validate a URL is safe to fetch (no SSRF).

    Checks:
    1. Scheme must be http or https
    2. Hostname must be present
    3. Resolved IP must not be private/internal

    Raises ValueError on failure. Returns the validated URL.
    """
    parsed = urlparse(url)

    # Scheme whitelist
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme: '{parsed.scheme}://'")

    # Require hostname
    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"No hostname found in URL: {url}")

    # Resolve DNS and check all results
    try:
        addr_infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ValueError(f"Cannot resolve hostname '{hostname}': {exc}") from exc

    for _family, _type, _proto, _canonname, sockaddr in addr_infos:
        ip_str = str(sockaddr[0])
        if is_private_ip(ip_str):
            raise ValueError(
                f"URL resolves to private/internal address {ip_str}. "
                "Connections to internal networks are not allowed."
            )

    return url
