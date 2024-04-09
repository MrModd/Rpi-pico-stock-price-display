import machine

from connection import Connection
from internet_getter import InternetGetter
import secrets
import epaper2in13b

class entry_point:
    REFRESH_MS = 60 * 60 * 1000  # 60 minutes
    REFRESH_MS_WHEN_FAILED = 1 * 60 * 1000  # 1 minute
    MAX_RETRIES = 3

    def __init__(self):
        self._display = epaper2in13b.EPD_2in13_B_V4_Landscape()
        self._connection = Connection(secrets.SSID, secrets.PASSWORD)
        self._led = machine.Pin("LED", mode=machine.Pin.OUT)

    def die(self):
        print("FATAL ERROR - The board is going to shut down")

        self._display.imagered.text(f"Device is off", 130, 110, 0x00)
        self._display.display()

        self.set_devices_low_power()
        while True:
            # Go in low power mode
            machine.lightsleep(self.REFRESH_MS)

    def set_devices_low_power(self):
        print("Shutting down devices")
        self._connection.disconnect()
        self._display.sleep()
        self._led.value(0)

    def wake_up_devices(self):
        self._led.value(1)
        self._display.reset()

    def init_devices(self):
        print("Init devices")
        self._led.value(1)
        self._display.Clear(0xff, 0xff)
        self._display.display()

    def prepare_screen_layout(self):
        self._display.imageblack.fill(0x00)
        self._display.imagered.fill(0x00)
        self._display.imageblack.fill(0xff)
        self._display.imagered.fill(0xff)
        self._display.imageblack.rect(5, 10, 240, 115, 0x00)

    def _wait(self, for_failure):
        # Go in low power mode
        print("Going to sleep")
        self.set_devices_low_power()
        machine.lightsleep(self.REFRESH_MS_WHEN_FAILED if for_failure else self.REFRESH_MS)

        print("Waking up")
        self.wake_up_devices()

    def run(self):
        self.init_devices()

        failure_retries = self.MAX_RETRIES
        while True:
            failed = False

            print("Preparing screen")
            self.prepare_screen_layout()
            self._display.imageblack.text(f"Connecting...", 80, 60, 0x00)
            self._display.display()

            print("Connecting")
            self._connection.connect()

            if not self._connection.wait_connection():
                print("Connection error")

                self.prepare_screen_layout()
                self._display.imagered.text(f"Connection error", 62, 60, 0x00)
                self._display.display()

                if failure_retries > 0:
                    failure_retries -= 1
                    print(f"Remaining retries {failure_retries}")
                    self._wait(for_failure=True)
                    continue
                else:
                    self.die()

            print("Connected")
            price, change, change_percent, last_trading_day = InternetGetter.get_stock_price(self._connection)
            current_time = InternetGetter.get_current_time(self._connection)
            if price == 0.0 and change == 0.0 and change_percent == 0.0:
                print("API Error")

                self.prepare_screen_layout()
                self._display.imagered.text(f"API error", 95, 60, 0x00)
                self._display.display()

                if failure_retries > 0:
                    failure_retries -= 1
                    self._wait(for_failure=True)
                    continue
                else:
                    self.die()

            # No failures, restore the original value in case it has been decremented
            failure_retries = self.MAX_RETRIES

            self.prepare_screen_layout()
            if (change_percent < 0):
                fb = self._display.imagered
            else:
                fb = self._display.imageblack
            self._display.imageblack.text(f"NASDAQ: ARM", 80, 15, 0x00)
            self._display.imageblack.hline(15, 25, 220, 0x00)
            fb.text(f"Last closure     {price:.2f}$", 10, 30, 0x00)
            fb.text(f"Difference       {change:.2f}$", 10, 40, 0x00)
            fb.text(f"Variation        {change_percent:.2f}%", 10, 50, 0x00)
            fb.text(f"Last trading day {last_trading_day}", 10, 60, 0x00)
            self._display.imageblack.text(f"Last lookup", 10, 80, 0x00)
            self._display.imageblack.text(f"{current_time[:10]}", 10, 90, 0x00)
            self._display.imageblack.text(f"{current_time[11:]}", 10, 100, 0x00)
            self._display.display()

            self._wait(for_failure=False)

if __name__ == "__main__":
    entry_point = entry_point()
    print("Starting")
    entry_point.run()
