# This sadly doesn´t work

# https://stackoverflow.com/questions/17589942/using-pyserial-to-send-binary-data
# from connect import connect_COM_port
from time import sleep


def GeneralSystemMessages(serial):
    """Reads the message buffer of a serial connection. Also prints out the general system message."""
    msg_dict = {
        "0x02": "Timeout: Communication-timeout (less data than expected)",
        "0x04": "Wake-Up Message: System boot ready",
        "0x11": "TCP-Socket: Valid TCP client-socket connection",
        "0x81": "Not-Acknowledge: Command has not been executed",
        "0x82": "Not-Acknowledge: Command could not be recognized",
        "0x83": "Command-Acknowledge: Command has been executed successfully",
        "0x84": "System-Ready Message: System is operational and ready to receive data",
        "0x91": "Data holdup: Measurement data could not be sent via the master interface",
    }
    msg = [serial.read() + "," for i in range(4)]  # optimize to lenth
    print(msg)


def SaveSettings(serial) -> None:
    serial.write(bytearray([0x90, 0x00, 0x90]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def SoftwareReset(serial) -> None:
    serial.write(bytearray([0xA1, 0x00, 0xA1]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def ResetMeasurementSetup(serial):
    serial.write(bytearray([0xB0, 0x01, 0x01, 0xB0]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def SetMeasurementSetup(
    serial,
    burst_count: int,
    frame_rate: int = 1,
    exc_freq: list = [100, 100, 1, 0],
    exc_amp: float = 0.01,
) -> None:
    """
    serial      ... Serial connection to the ScioSpecEIT device.
    burst_count ... Number of frames generated before measurement stops automatically.
    frame_rate  ... Number of EIT-frames per second.
    exc_freq    ... Add excitation frequency block in Hz: [fmin, fmax, fcount, ftype]
    exc_amp     ... Set excitation amplitude in ampere.

    Further information:

    [fmin]
        • minimum frequency fmin
        • 4 Byte floating point single precision value
        • range = 100 Hz - 10 MHz
        • Default: fmin = 100 kHz
    [fmax]
        • maximum frequency fmax
        • 4 Byte floating point single precision value
        • range = 100 Hz - 10 MHz
        • Default: fmax = 100 kHz
    [fcount]
        • frequency count fcount
        • 2 Byte unsigned integer value
        • range = 1 - 128
        • Default: fcount = 1
    [ftype]
        • frequency type ftype
        • 1 Byte unsigned interger value
        • ftype = 0: linear frequency distribution | 1: logarithmic frequency distribution
        • Default: ftype = 0
    [excitation amplitude]
        • 8 Byte Floating Point double precision value.
        • Amin = 100 nA
        • Amax = 10 mA
        • Step size see Chapter “Technical Specification”
        • Default: A = 0.01 A
    """

    def write_part(serial, msg):
        serial.write(msg)
        print(GeneralSystemMessages(serial))

    burst_count = bytearray([0xB0, 0x03, 0x02, burst_count, 0xB0])
    write_part(serial, burst_count)

    frame_rate = bytearray([0xB0, 0x05, 0x03, frame_rate, 0xB0])
    write_part(serial, frame_rate)

    exc_freq = bytearray(
        [0xB0, 0x0C, 0x04, exc_freq[0], exc_freq[1], exc_freq[2], exc_freq[3], 0xB0]
    )
    write_part(serial, exc_freq)

    # exc_amp = bytearray([0xB0, 0x05, 0x05, exc_amp, 0xB0])
    # write_part(serial, exc_amp)

    print("Setup done")


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
