# Import periphery drivers
from machine import Pin, Timer
from time import sleep, sleep_ms

# Import bluetooth driver
import ubluetooth

# Class to controll bluetooth
class loko_ble_driver():
    def __init__(self, ble_name, rgb_led):
        # Save passed object to control led
        self.__rgb_led = rgb_led
        # Create timer to blink led
        self.__led_timer = Timer(0)

        # Save bluetooth device name
        self.ble_name = ble_name

        # Initialize bluetooth object
        self.__ble = ubluetooth.BLE()
        # Enable bluetooth
        self.__ble.active(True)

        # Set bluetooth to disconnected
        self._disconnected()

        # Register callback function
        self.__ble.irq(self._ble_irq)

        # Configure bluetooth periphery and search for devices
        self._register()
        self._advertiser()
        self.__ble.config(gap_name="Loko")

    # Event when bluetooth connection is established
    def _connected(self):
        # Set connected variable to true
        self.is_ble_connected = True

        # Disable bluetooth search indication
        self.__led_timer.deinit()
        self.__rgb_led.set_brightness("blue", 0)
        sleep_ms(400)
        self.__rgb_led.set_brightness("blue", 50)
        sleep_ms(400)
        self.__rgb_led.set_brightness("blue", 0)
        sleep_ms(400)
        self.__rgb_led.set_brightness("blue", 50)
        sleep_ms(400)
        self.__rgb_led.set_brightness("blue", 0)
    
    # Event when no bluetooth connection
    def _disconnected(self):
        # Set connected variable to false
        self.is_ble_connected = False

        # Start led timer to indicate searching for bluetooth connection
        self.__led_timer.init(period=15, mode=Timer.PERIODIC, callback=lambda t: self.__rgb_led.pulse_helper("blue", 75))

    # Function to configure bluetooth periphery
    def _register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.__ble.gatts_register_services(SERVICES)

    # Interrupt/event handler for bluetooth connection
    def _ble_irq(self, event, data):
        if event == 1:
            #_IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral
            self._connected()

        elif event == 2:
            #_IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            self._advertiser()
            self._disconnected()
        
        elif event == 3:
            #_IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.          
            self.ble_msg = self.__ble.gatts_read(self.rx).decode('UTF-8').strip()
            print("BLE: RX: " + self.ble_msg + "\n")

    # Function to advertise device
    def _advertiser(self):
        # Create advertisement data
        adv_data = bytearray('\x02\x01\x02', 'UTF-8') + bytearray((len(self.ble_name) + 1, 0x09)) + bytes(self.ble_name, 'UTF-8')
        # Send advertisement data   
        self.__ble.gap_advertise(100, adv_data)
        # Additionaly send data to log
        print("BLE: Advertise: " + adv_data + "\n")

    # Funtion to send data to connected device
    def send(self, gps_data, battery_level):
        # Check gps data for error
        if gps_data == 'No signal' or gps_data == 'No data':
            msg = gps_data
        else:
            # Parse message to send
            msg = ("Id:Loko1" + 
                " Lattitude:" + str(gps_data.get("longitude", "Error")) +
                " Longitude:" + str(gps_data.get("latitude", "Error")) +
                " Altitude:" + str(gps_data.get("altitude", "Error")) +
                " Battery:" + str(battery_level) +
                " RSSI:-17")
        # Print message to log
        print("BLE: Message: " + msg + "\n")    
               
        try:
            # Send message
            self.__ble.gatts_notify(0, self.tx, msg + '\n')
        except Exception as inst:
            # Exception occured
            print("BLE: Send error: ", inst)
