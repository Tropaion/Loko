from time import sleep, sleep_ms

from loko_led_driver import loko_led_driver
from loko_ble_driver import loko_ble_driver

# Main functionality
if __name__ == "__main__":
    # Create led object
    rgb_led = loko_led_driver()

    # Create ble object
    ble_driver = loko_ble_driver("LOCO", rgb_led)

    # Main loop
    while True:
        # Timeout
        sleep_ms(500)


