from time import sleep, sleep_ms

# Import loko drivers
from loko_led_driver import loko_led_driver
from loko_ble_driver import loko_ble_driver
from loko_lora_driver import loko_lora_driver

# Main functionality
if __name__ == "__main__":
    # Create led driver object
    rgb_led = loko_led_driver()

    # Create ble driver object
    ble_driver = loko_ble_driver("LOCO", rgb_led)

    # Create lora driver object
    lora_driver = loko_lora_driver()

    # Run infinitely and check for new messages
    while True:
        # Check if bluetooth is connected
        if ble_driver.is_ble_connected:
            # TODO: Check for battery level
            # battery_level()
            battery_level = 70

            # Check for new lora message
            gps_data = lora_driver.recv_message()

            # Check if data was received
            #if gps_data != 'No signal' and gps_data != 'No data':
            # Send data via bluetooth
            ble_driver.send(gps_data, battery_level)

            # Timeout
            sleep_ms(500)


