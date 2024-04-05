import network
import requests
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

    def request_json(self, url: str):
        if not self._wlan.isconnected():
            return {}

        request = requests.get(url)
        if request.status_code == 200:
            return request.json()
        else:
            return {}
