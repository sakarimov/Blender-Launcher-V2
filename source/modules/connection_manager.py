from __future__ import annotations

import ssl
import sys
from typing import TYPE_CHECKING, Union

from modules._platform import get_cwd, get_platform_full, is_frozen
from modules.settings import (
    get_proxy_host,
    get_proxy_password,
    get_proxy_port,
    get_proxy_type,
    get_proxy_user,
    get_use_custom_tls_certificates,
)
from PyQt5.QtCore import QObject, pyqtSignal
from urllib3 import PoolManager, ProxyManager, make_headers
from urllib3.contrib.socks import SOCKSProxyManager

if TYPE_CHECKING:
    from semver import Version

proxy_types_chemes = {
    1: "http://",
    2: "https://",
    3: "socks4a://",
    4: "socks5h://",
}

REQUEST_MANAGER = Union[PoolManager, ProxyManager, SOCKSProxyManager]


# TODO
# It is impossible to kill existing instance of PoolManager
# and create a new one without restarting application


class ConnectionManager(QObject):
    error = pyqtSignal()

    def __init__(self, version: Version, proxy_type=None) -> None:
        super().__init__()
        self.version = version
        if proxy_type is None:
            proxy_type = get_proxy_type()
        self.proxy_type = proxy_type
        self.manager: REQUEST_MANAGER | None = None

        # Basic Headers
        self._headers = {"user-agent": f"Blender-Launcher-v2/{self.version!s} ({get_platform_full()})"}

        # Get custom certificates file path
        if is_frozen() is True:
            self.cacert = sys._MEIPASS + "/files/custom.pem"  # noqa: SLF001
        else:
            self.cacert = (get_cwd() / "source/resources/certificates/custom.pem").as_posix()

    def setup(self):
        if self.proxy_type == 0:  # Use generic requests
            if get_use_custom_tls_certificates():
                # Generic requests with CERT_REQUIRED
                self.manager = PoolManager(
                    num_pools=50,
                    maxsize=10,
                    headers=self._headers,
                    cert_reqs=ssl.CERT_REQUIRED,
                    ca_certs=self.cacert,
                )
            else:
                # Generic requests w/o CERT_REQUIRED
                self.manager = PoolManager(num_pools=50, maxsize=10, headers=self._headers)
        else:  # Use Proxy
            ip = get_proxy_host()
            port = get_proxy_port()
            scheme = proxy_types_chemes[self.proxy_type]

            if self.proxy_type > 2:  # Use SOCKS Proxy
                if get_use_custom_tls_certificates():
                    # SOCKS Proxy with CERT_REQUIRED
                    self.manager = SOCKSProxyManager(
                        proxy_url=f"{scheme}{ip}:{port}",
                        num_pools=50,
                        maxsize=10,
                        headers=self._headers,
                        username=get_proxy_user(),
                        password=get_proxy_password(),
                        cert_reqs=ssl.CERT_REQUIRED,
                        ca_certs=self.cacert,
                    )
                else:
                    # SOCKS Proxy w/o CERT_REQUIRED
                    self.manager = SOCKSProxyManager(
                        proxy_url=f"{scheme}{ip}:{port}",
                        num_pools=50,
                        maxsize=10,
                        headers=self._headers,
                        username=get_proxy_user(),
                        password=get_proxy_password(),
                    )
            else:  # Use HTTP Proxy
                # HTTP Proxy autherification headers
                auth_headers = make_headers(proxy_basic_auth=f"{get_proxy_user()}:{get_proxy_password()}")

                if get_use_custom_tls_certificates():
                    # HTTP Proxy with CERT_REQUIRED
                    self.manager = ProxyManager(
                        proxy_url=f"{scheme}{ip}:{port}",
                        num_pools=50,
                        maxsize=10,
                        headers=self._headers,
                        proxy_headers=auth_headers,
                        cert_reqs=ssl.CERT_REQUIRED,
                        ca_certs=self.cacert,
                    )
                else:
                    # HTTP Proxy w/o CERT_REQUIRED
                    self.manager = ProxyManager(
                        proxy_url=f"{scheme}{ip}:{port}",
                        num_pools=50,
                        maxsize=10,
                        headers=self._headers,
                        proxy_headers=auth_headers,
                    )

    def request(self, _method, _url, fields=None, headers=None, **urlopen_kw):
        try:
            assert self.manager is not None
            return self.manager.request(_method, _url, fields, headers, **urlopen_kw)
        except Exception:
            self.error.emit()
            return None
