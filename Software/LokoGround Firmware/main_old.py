import machine
from machine import ADC
from machine import Pin, UART, Timer
from time import sleep_ms
import ubinascii
import ubluetooth
import json
import _thread
import sys

if 1:  # Must be 1 for real hardware
    VBAT_IN = ADC(Pin(39))
    BUTTON = Pin(35, Pin.IN)
    POWER_CTRL = Pin(12, Pin.OUT)
    LED_BLUE = Pin(21, Pin.OUT)
    LED_RED = Pin(18, Pin.OUT)
    LED_GREEN = Pin(19, Pin.OUT)
    LORA_UART = UART(2, 9600)
else:
    # Loko debug board pinout
    VBAT_IN = ADC(Pin(1))
    BUTTON = Pin(0, Pin.IN)
    POWER_CTRL = Pin(12, Pin.OUT)
    LED_BLUE = Pin(47, Pin.OUT)
    LED_RED = Pin(36, Pin.OUT)
    LED_GREEN = Pin(37, Pin.OUT)
    LORA_UART = UART(2, 9600)

use_coommand_line_parser = False

class SETTINGS():

    data = {
        'id2': 0,
        'freq': 868
    }

    def __init__(self, file_name='settings.json'):
        self.file_name = file_name
        self.load()

    def save(self):
        print('Save settings to {}:{}'.format(self.file_name, self.data))
        with open(self.file_name, "w") as fp:
            json.dump(self.data, fp)

    def load(self):
        try:
            with open(self.file_name, "r") as fp:
                self.data = json.load(fp)
        except Exception as inst:
            print(inst)
            print("Settings file not found create new and use default settings")
            self.save()
        print('Load settings from {}:{}'.format(self.file_name, self.data))


class COMMAND_RECEIVER():

    def __init__(self, settings_obj):
        self.exit_request = False
        self.settings = settings_obj
        _thread.start_new_thread(self.receiver_thread, ())

    def set_handler(self, tag, number):
        if tag != 'id2' and tag != 'freq':
            print('Wrong set argument')
            return

        try:
            param = int(number)
        except (ValueError, TypeError):
            print("Expected numeric argument")
        else:
            if tag == 'freq' and param > 1000:
                print('Too big frequency argument, expected value in MHZ < 1000')
                return

            self.settings.data[tag] = param
            self.settings.save()

    def get_info(self, *args):
        print('Settings: ', self.settings.data)

    def print_help(self, *args):
        for cmd in self.commands:
            print('{} - {}'.format(cmd, self.commands[cmd]['info']))
            
    def exit_app(self, *args):
        self.exit_request = True
        sys.exit(1)

    commands = {
        'set': {'handler': set_handler, 'info': '\'set id2 VALUE\' or \'set freq VALUE\''},
        'info': {'handler': get_info, 'info': 'print current settings'},
        'help': {'handler': print_help, 'info': 'show this text'},
        'exit': {'handler': exit_app, 'info': 'test_command'},
    }

    def receiver_thread(self):
        while True:
            try:
                rx_line = input("> ")
            except KeyboardInterrupt:
                print('Ctrl+C pressed')
                exit_app()
            print('!!!' + rx_line)
                
            if not rx_line:
                continue

            cmd, *params = rx_line.split()
            try:
                handler = self.commands[cmd]['handler']
            except KeyError:
                print('Unknown command')               
            else:
                handler(self, *params)


def battery_level():
    # VBAT_IN.atten(ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    # set 9 bit return values (returned range 0-511)
    VBAT_IN.width(ADC.WIDTH_9BIT)
    adc_battery_gnd = VBAT_IN.read()*4.2/511
#     print(adc_battery_gnd)
    return (adc_battery_gnd)


def lora_set(freq_mhz):
    LORA_UART.write("AT+MODE=TEST")
    sleep_ms(1000)
    print('Lora Resp:', LORA_UART.read())
    LORA_UART.write(
        "AT+TEST=RFCFG,{},SF12,125,12,15,14,ON,OFF,OFF".format(freq_mhz))
    sleep_ms(1000)
    print('Lora Resp:', LORA_UART.read())


def lora_data_receive():
    LORA_UART.write('AT+TEST=RXLRPKT')
    sleep_ms(500)
    print('Lora RX:', LORA_UART.read())


def parse_lora_module_message(message):
    # expected packet like: '+TEST: LEN:31, RSSI:-35, SNR:12\r\n+TEST: RX \"30302C3030302C35302E3531313732352C33302E3739313934352C33393936\"\r\n'
    line = str(message).split(" ")
    if len(line) > 2 and line[-2] == 'RX':        
        received_data = line[-1][1:]
        end_hex_data_pos = received_data.find('\"')
        received_data = received_data[0:end_hex_data_pos]
        converted_data = ubinascii.unhexlify(received_data)
        loko_message = converted_data.decode("utf-8")
        return loko_message
    return None


def parse_loko_packet(string):
    # expected packet like: '123,321,40.376123,49.850848,3420'
    values = string.split(',')
    print(values)
    if len(values) == 5:
        id1 = int(values[0])
        id2 = int(values[1])

        # do not use float() result will round to five digit, ex: 50.511725 >>>> 50.51172 and 30.791945 >>>> 30.79195
        lat = (values[2])
        lon = (values[3])

        vbat = int(values[4])
        return {'id1': id1, 'id2': id2, 'lat': lat, 'lon': lon, 'vbat': vbat}
    return None


def button_timer(pin):
    print('Power value:', POWER_CTRL.value())
    if BUTTON.value() == 0:
        print("counting till 3")
        sleep_ms(2000)
        if BUTTON.value() == 0:
            LED_RED.value(not LED_GREEN.value())
            POWER_CTRL.value(not POWER_CTRL.value())
            print('Power value:', POWER_CTRL.value())
        else:
            print('Button released')


def main():

    LED_BLUE.value(0)
    sleep_ms(500)

    LED_BLUE.value(1)
    LED_RED.value(0)
    sleep_ms(500)

    LED_RED.value(1)
    LED_GREEN.value(0)
    sleep_ms(500)

    LED_GREEN.value(1)
    POWER_CTRL.value(1)
    LED_GREEN.value(0)
    sleep_ms(500)

    LED_GREEN.value(1)

    settings = SETTINGS()
    if use_coommand_line_parser == True:
        command_parser = COMMAND_RECEIVER(settings)

    BUTTON.irq(trigger=Pin.IRQ_FALLING, handler=button_timer)
    ble = LOKO_BLE("LOKO")
    lora_set(settings.data['freq'])
    lora_data_receive()
    countr = 0
    g_send = True
    while True:
        sleep_ms(100)
        countr += 1
        if ble.is_connected:
            if(g_send):
                g_bat= battery_level()
                sleep_ms(200)
                print(g_bat)
                ble.send(str(g_bat))
                g_send = False
            if countr >= 150:
                g_send = True
                countr = 0
        else:
            g_send = True
            countr = 0
        if use_coommand_line_parser == True:
            if command_parser.exit_request == True:
               sys.exit(1)
            
        lora_data = LORA_UART.read()
        if lora_data == None:
            continue
        print('LoraRx: ', lora_data)

        loko_string = parse_lora_module_message(lora_data)
        if loko_string == None:
            continue
        print('LokoMessage: '+loko_string+','+str(g_bat))
        
        loko_data = parse_loko_packet(loko_string)
        if loko_data['id2'] == settings.data['id2']:
            if ble.is_connected:
                ble.send(loko_string)
            else:
                print('BLE not connected')
        else:
            print('DEBUG:Received unexpected ID2={}, Expected={}'.format(
                loko_data['id2'], settings.data['id2']))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Ctrl+C pressed, exit from application')
        exit(1)

