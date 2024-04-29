import machine

from connection import Connection
from internet_getter import InternetGetter, RequestException
import secrets
import epaper2in13b
import ina219

class entry_point:
    REFRESH_MS = 30 * 60 * 1000  # 30 minutes
    REFRESH_MS_WHEN_FAILED = 1 * 60 * 1000  # 1 minute
    MAX_RETRIES = 3

    STOCK_SYMBOL = "ARM"
    STOCK_NAME   = "NASDAQ: ARM"
    TIMEZONE = "Europe/Paris"

    def __init__(self):
        self._display = epaper2in13b.EPD_2in13_B_V4_Landscape()
        self._connection = Connection(secrets.WIFI_CREDENTIALS)
        self._led = machine.Pin("LED", mode=machine.Pin.OUT)
        try:
            self._ups = ina219.INA219(addr=0x43)
        except Exception as e:
            # UPS not connected
            print(f"Exception on I2C bus: {e}")
            self._ups = None

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

    def display_battery(self):
        if self._ups is None:
            print("No battery detected")
            return

        bus_voltage = self._ups.getBusVoltage_V()  # voltage on V- (load side)
        current = self._ups.getCurrent_mA()  # current in mA

        P = (bus_voltage -3)/1.2*100
        if (P < 0):
            P=0
        elif (P > 100):
            P=100

        # INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
        print(f"Voltage:  {bus_voltage:6.3f} V")
        print(f"Current:  {current/1000:6.3f} A")
        print(f"Percent:  {P:5.1f} %")

        if (P < 30):  # Charge state under 30%
            fb = self._display.imagered
        else:
            fb = self._display.imageblack

        # Battery symbol is 20px long
        fill_px = int((P // 10) * 2)  # How many px to fill based on the battery charge
        if fill_px > 0:
            fb.fill_rect(10, 108, fill_px, 10, 0x00)
        if fill_px < 20:
            fb.rect(10+fill_px, 108, 20-fill_px, 10, 0x00)
        fb.fill_rect(30, 110, 2, 6, 0x00)  # This is the positive terminal bump
        fb.text(f"{P:5.1f}%", 34, 110, 0x00)

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
            self.display_battery()
            self._display.imageblack.text(f"Connecting...", 80, 60, 0x00)
            self._display.display()

            print("Connecting")
            if not self._connection.connect():
                print("Connection error")

                self.prepare_screen_layout()
                self.display_battery()
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
            try:
                # price, change, change_percent, date = InternetGetter.get_stock_price(self.STOCK_SYMBOL)
                price, change, change_percent, date = InternetGetter.get_terminal_stock_price(self.STOCK_SYMBOL)
                current_time = InternetGetter.get_current_time(self.TIMEZONE)
            except RequestException as e:
                print(f"API Error: {e}")

                self.prepare_screen_layout()
                self.display_battery()
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
            self.display_battery()
            if (change_percent < 0):
                fb = self._display.imagered
            else:
                fb = self._display.imageblack
            self._display.imageblack.text(f"{self.STOCK_NAME}", 80, 15, 0x00)
            self._display.imageblack.hline(15, 25, 220, 0x00)
            fb.text(f"Price  {price:.2f}$", 10, 30, 0x00)
            fb.text(f"Change {change:.2f}$ {change_percent:.2f}%", 10, 40, 0x00)
            fb.text(f"Date   {date}", 10, 50, 0x00)
            self._display.imageblack.text(f"Last lookup", 10, 70, 0x00)
            self._display.imageblack.text(f"{current_time[:10]}", 10, 80, 0x00)
            self._display.imageblack.text(f"{current_time[11:]}", 10, 90, 0x00)
            self._display.display()

            self._wait(for_failure=False)

if __name__ == "__main__":
    entry_point = entry_point()
    print("Starting")
    entry_point.run()
