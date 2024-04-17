import network
import time

class Connection:
    def __init__(self, ssid, password):
        self._ssid = ssid
        self._password = password
        self._wlan = network.WLAN(network.STA_IF)

    def connect(self) -> None:
        self._wlan.active(True)
        self._wlan.connect(self._ssid, self._password)

    def wait_connection(self, max_wait: int = 10) -> bool:
        """
        It blocks until the WiFi link is established or there is a failure.
        @return True if the WiFi is connected and there is an IP
        """
        while(max_wait > 0):
            if self._wlan.status() < 0 or self._wlan.status() >= 3:
                break
            max_wait -= 1
            time.sleep(1)

        return self._wlan.status() == 3

    def disconnect(self) -> None:
        self._wlan.disconnect()
        self._wlan.active(False)

    def get_ip(self) -> str:
        if self._wlan.isconnected():
            return self._wlan.ifconfig()[0]
        return ""
