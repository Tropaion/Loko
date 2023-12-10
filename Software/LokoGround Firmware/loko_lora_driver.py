# Import periphery drivers
from machine import UART
from time import sleep, sleep_ms
import ubinascii

# Import constants
from loko_constants import (
    LORA_UART_NUM,
    LORA_UART_BAUD
    )

class loko_lora_driver():
    def __init__(self):
        # Open UART communication with lora module
        self.__loraCom = UART(LORA_UART_NUM, LORA_UART_BAUD)

        # Init LoRa module
        self._lora_init()

    # Initialize LoRa module
    def _lora_init(self):
        self.__loraCom.write("AT+MODE=TEST")
        sleep(1)
        print("LoRa: " + self.__loraCom.read() + "\n")

        # Configure rf communciation
        self.__loraCom.write("AT+TEST=RFCFG,868,SF7,125,12,15,8,ON,OFF,OFF") 
        sleep(1)
        print("LoRa: " + self.__loraCom.read() + "\n")

    # Message parser
    def _parse_message(self, message):
        # Convert to string
        msg = str(message)
        # Split message
        msg = msg.split(" ")
        # Print message to log
        print("LoRa: " + msg + "\n")

        # Check message
        if msg == ['None']:
            return ('No signal')
        # If message type is RX gps data
        elif msg[-2] == 'RX':
            # Extract data from message
            recv_data = msg[-1][1:-6]
            # Convert data to uft-8
            recv_data = ubinascii.unhexlify(recv_data).decode("utf-8")
            # Create dictionary for gps data
            gps = {}
            # Get longitude and convert to float format
            gps["longitude"] = int(recv_data[7:9]) + float(recv_data[9:16]) / 60
            # Get latitude and convert to float format
            gps["latitude"] = int(recv_data[17:19]) + float(recv_data[19:26]) / 60
            # Get altitude
            gps["altitude"] = recv_data[27:]
            # Get timestamp
            gps["timestamp"] = recv_data[:6]
            # Print message to log
            print("LoRa: " + gps + "\n")
            # return gps data
            return gps
        # If no data was received
        else:
            # Print message to log
            print("LoRa: no data" + "\n")
            return ('No data')

    # Receive and parse lora message
    def recv_message(self):
        # RXLRPKT = Receive Lora Packet
        self.__loraCom.write('AT+TEST=RXLRPKT')
        # Timeout
        sleep(0.5)
        # Read data
        data = self.__loraCom.read()
        # Print data to log
        print("LoRa: " + data + "\n")
        # Parse data
        msg = self._parse_message(data)
        # Return data
        return msg

