import os
import socket

import aiohttp
import requests

__all__ = ('connector', 'timeout')

USE_IPV4_ONLY = bool(os.environ.get('BLREC_IPV4'))

if not USE_IPV4_ONLY:
    family = 0
else:
    requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore
    family = socket.AF_INET


_connector: aiohttp.TCPConnector = None  # type: ignore[assignment]


def connector() -> aiohttp.TCPConnector:
    global _connector
    if _connector is None:
        _connector = aiohttp.TCPConnector(family=family, limit=200)
    return _connector


timeout = aiohttp.ClientTimeout(total=10)
