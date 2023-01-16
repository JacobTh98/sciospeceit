# This sadly doesn´t work

# https://stackoverflow.com/questions/17589942/using-pyserial-to-send-binary-data
# from connect import connect_COM_port
from time import sleep


def GeneralSystemMessages(serial):
    msg = [serial.read() for i in range(4)]
    print(msg)


def SaveSettings(serial) -> None:
    serial.write(bytearray([0x90, 0x00, 0x90]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def SoftwareReset(serial) -> None:
    serial.write(bytearray([0xA1, 0x00, 0xA1]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def SetMeasurementSetup():
    pass


def GetMeasurementSetup():
    pass


def SetOutputConfiguration():
    pass


def GetOutputConfiguration():
    pass


def Start_StopMeasurement():
    pass


def GetTemperature() -> None:
    print("Not temperature sensor available")


def SetBatteryControll():
    pass


def GetBatteryControll():
    pass


def SetLEDControl(led: int, mode: str, serial) -> None:
    """
    Disable or enable auto mode.
    led: number of led 1,2,3 or 4
        #1 ... Ready
        #2 ... Measure
        #3 ... ---
        #4 ... Status
    mode: "enable" or "disable"
    serial: serial connection
    """
    if mode == "disable":
        MODE = 0x00
    elif mode == "enable":
        MODE = 0x01

    byte_arr = bytearray([0xC8, 0x03, 0x01, led, MODE, 0xC8])
    serial.write(byte_arr)
    # Enable Auto mode
    # ser.write(bytearray([0xC8, 0x03, 0x01, 0x04,0x01, 0xC8]))
    # Disable Auto mode
    # ser.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x00, 0xC8]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def GetLEDControl(led: int, mode: str, serial) -> None:
    """
    Set a defined led to mode off, on or blink.
    led: number of led 1,2,3 or 4
        #1 ... Ready
        #2 ... Measure
        #3 ... ---
        #4 ... Status
    mode: "enable", "disable" or "blink"
    serial: serial connection
    """
    if mode == "disable":
        MODE = 0x00
    elif mode == "enable":
        MODE = 0x01
    elif mode == "blink":
        MODE = 0x02

    byte_arr = bytearray([0xC8, 0x03, 0x02, led, MODE, 0xC8])
    print("sent:", byte_arr)
    serial.write(byte_arr)
    callback = GeneralSystemMessages(serial)
    print(callback)


def SetLED_Mode(led: int, mode: str, serial) -> None:
    """
    led: number of led 1,2,3 or 4
        #1 ... Ready
        #2 ... Measure
        #3 ... ---
        #4 ... Status
    mode: "enable", "disable" or "blink"
    serial: serial connection
    """
    # Disable automode
    serial.write(bytearray([0xC8, 0x03, 0x01, led, 0x00, 0xC8]))
    if mode == "disable":
        MODE = 0x00
    elif mode == "enable":
        MODE = 0x01
    elif mode == "blink":
        MODE = 0x02
    serial.write(bytearray([0xC8, 0x03, 0x02, led, MODE, 0xC8]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def DisableLED_AutoMode(serial) -> None:
    """Disable automode of all LEDs."""
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x01, 0x00, 0xC8]))
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x02, 0x00, 0xC8]))
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x03, 0x00, 0xC8]))
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x00, 0xC8]))


def EnableLED_AutoMode(serial) -> None:
    """Enable automode of all LEDs."""
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x01, 0x01, 0xC8]))
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x02, 0x01, 0xC8]))
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x03, 0x01, 0xC8]))
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x01, 0xC8]))


def FrontIOs():
    pass


def PowerPlugDetect():
    pass


def GetDevideInfo():
    pass


def TCP_ConnectionWatchdog():
    pass


def GetFirmwareIDs():
    pass
