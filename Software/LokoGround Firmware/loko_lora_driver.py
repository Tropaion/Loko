# Import periphery drivers
from machine import UART

# Import constants
from loko_constants import (
    LORA_UART_NUM,
    LORA_UART_BAUD
    )

class loko_lora_driver():
    def __init__(self):
        # Open UART communication with lora module
