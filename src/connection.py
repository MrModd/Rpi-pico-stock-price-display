import network
import time


class Connection:
    def __init__(self, credentials):
        self._credentials = credentials
        self._wlan = None

    def connect(self) -> bool:
        """" @return: True if the WiFi is connected and there's an IP """
        self._wlan = network.WLAN(network.STA_IF)
        self._wlan.active(True)
        for ssid, password in self._credentials:
            print(f"Connection: trying {ssid}...")
            self._wlan.connect(ssid, password)
            if self._wait_connection():
                print(f"Connection: connected to {ssid}")
                return True
            else:
                print(f"Connection: failed to connect to {ssid}")

        return False

    def _wait_connection(self, max_wait: int = 10) -> bool:
        """
        It blocks until the WiFi link is established or there is a failure.
        @return True if the WiFi is connected and there is an IP
        """
        while (max_wait > 0):
            if self._wlan.status() < 0 or self._wlan.status() >= 3:
                break
            max_wait -= 1
            time.sleep(1)

        return self._wlan.status() == 3

    def disconnect(self) -> None:
        self._wlan.disconnect()
        self._wlan.active(False)
        self._wlan.deinit()
        self._wlan = None

    def get_ip(self) -> str:
        if self._wlan.isconnected():
            return self._wlan.ifconfig()[0]
        return ""
