# This sadly doesn´t work

# https://stackoverflow.com/questions/17589942/using-pyserial-to-send-binary-data
# from connect import connect_COM_port
from time import sleep


def GeneralSystemMessages(serial) -> str:
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
    return msg


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

    def write_part(serial, msg) -> None:
        serial.write(msg)
        callback = GeneralSystemMessages(serial)
        print(callback)

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


def GetMeasurementSetup(serial) -> None:
    """Get information about:
    - Burst Count
    - Frame Rate
    - Excitation Frequencies
    - Excitation Amplitude
    - Excitation Sequence
    - Single-Ended or Differential Measure Mode
    - Gain Settings
    - Excitation Switch Type
    """
    burst_count = bytearray([0xB1, 0x01, 0x02, 0xB1])
    serial.write(burst_count)
    print("Burst Count:")
    callback = GeneralSystemMessages(serial)  # [CT] 03 02 [burst count] [CT]
    print(callback)

    frame_rate = bytearray([0xB1, 0x01, 0x03, 0xB1])
    serial.write(frame_rate)
    print("Frame Rate:")
    callback = GeneralSystemMessages(serial)  # [CT] 05 03 [frame rate] [CT]
    print(callback)

    exc_freq = bytearray([0xB1, 0x01, 0x04, 0xB1])
    serial.write(exc_freq)
    print("Excitation Frequencies:")
    callback = GeneralSystemMessages(
        serial
    )  # [CT] [LE] 04 [fmin 1st block] [fmax 1st block] [fcount 1st block] [ftype 1st block] [fmin 2nd block] [fmax 2nd block] [fcount 2nd block] [ftype 2nd block] ... [CT]
    print(callback)

    exc_amp = bytearray(
        [0xB1, 0x01, 0x05, 0xB1]
    )  # [CT] 05 05 [excitation amplitude] [CT]
    serial.write(exc_amp)
    print("Excitation Amplitude:")
    callback = GeneralSystemMessages(serial)
    print(callback)

    exc_seq = bytearray([0xB1, 0x01, 0x06, 0xB1])
    serial.write(exc_seq)
    print("Excitation Sequence:")
    callback = GeneralSystemMessages(serial)  # [CT] [LE] 06 [excitation sequence] [CT]
    print(callback)

    meas_mode = bytearray([0xB1, 0x01, 0x08, 0xB1])
    serial.write(meas_mode)
    print("Measure Mode:")
    callback = GeneralSystemMessages(serial)  # [CT] 03 08 [Mode] [Boundary] [CT]
    print(callback)

    gain = bytearray([0xB1, 0x01, 0x09, 0xB1])
    serial.write(gain)
    print("Gain Settings:")
    callback = GeneralSystemMessages(serial)  # [CT] [LE] 09 [Mode] [Data] [CT]
    print(callback)

    exc_switch = bytearray([0xB1, 0x01, 0x0C, 0xB1])
    serial.write(exc_switch)
    print("Excitation switch type:")
    callback = GeneralSystemMessages(serial)  # [CT] 02 0C [Type] [CT]
    print(callback)


def SetOutputConfiguration(
    serial, exc_settings: int, curr_row_freq_stack: int, timestamp: int
) -> None:
    """
    This command is used to enable or disable additional information in output data stream of measured data (see
    section "Measured Data"). This command is only valid while no measurement is ongoing. In this case a not
    acknowledge (NACK) is returned.

    Excitation setting
        Enable or disable Excitation setting (additional 2 Byte in output stream).

        Syntax
        • Syntax set: [CT] 02 01 [enable/disable] [CT] [enable/disable]
        • 1 Byte unsigned integer value
        • 0 - disable, 1 - enable
    Current row in the frequency stack
        Enable or disable current row in the frequency stack (additional 2 Byte in output stream)

        Syntax
        • Syntax set: [CT] 02 02 [enable/disable] [CT] [enable/disable]
        • 1 Byte unsigned integer value
        • 0 - disable, 1 - enable
    Timestamp
        Enable or disable timestamp (additional 4 Byte in output stream).

        Syntax
        • Syntax set: [CT] 02 03 [enable/disable] [CT]
    """
    # write excitation setting
    serial.write(bytearray([0xB2, 0x02, 0x01, exc_settings, 0xB2]))
    callback = GeneralSystemMessages(serial)
    print(callback)
    # write current row in the frequency stack
    serial.write(bytearray([0xB2, 0x02, 0x02, curr_row_freq_stack, 0xB2]))
    callback = GeneralSystemMessages(serial)
    print(callback)
    # write timestamp
    serial.write(bytearray([0xB2, 0x02, 0x03, timestamp, 0xB2]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def GetOutputConfiguration(serial) -> None:
    """Returns the display option in the data stream of measured date."""
    pass


def Start_StopMeasurement(serial, command: int) -> None:
    """
    A new measurement can only be started when no other measurement is ongoing. A description is can be found in
    section "Measured Data".
        command = 1 for start
        command = 0 for stop
    """
    if command == 1:
        serial.write(bytearray([0xB4, 0x01, 0x01, 0xB4]))
    else:
        serial.write(bytearray([0xB4, 0x01, 0x00, 0xB4]))
    callback = GeneralSystemMessages(serial)
    print(callback)


def GetTemperature() -> None:
    print("Not temperature sensor available")


def SetBatteryControll():
    """TBD"""


def GetBatteryControll():
    """TBD"""


def SetLEDControl(serial, led: int, mode: str) -> None:
    """
    Disable or enable auto mode.
    serial: serial connection
    led: number of led 1,2,3 or 4
        #1 ... Ready
        #2 ... Measure
        #3 ... ---
        #4 ... Status
    mode: "enable" or "disable"
    """
    if mode == "disable":
        MODE = 0x00
    elif mode == "enable":
        MODE = 0x01

    byte_arr = bytearray([0xC8, 0x03, 0x01, led, MODE, 0xC8])
    serial.write(byte_arr)
    callback = GeneralSystemMessages(serial)
    print(callback)


def GetLEDControl(serial, led: int, mode: str) -> None:
    """
    Set a defined led to mode off, on or blink.
    serial: serial connection
    led: number of led 1,2,3 or 4
        #1 ... Ready
        #2 ... Measure
        #3 ... ---
        #4 ... Status
    mode: "enable", "disable" or "blink"
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


def SetLED_Mode(serial, led: int, mode: str) -> None:
    """
    serial: serial connection
    led: number of led 1,2,3 or 4
        #1 ... Ready
        #2 ... Measure
        #3 ... ---
        #4 ... Status
    mode: "enable", "disable" or "blink"
    """
    # Disable automode
    serial.write(bytearray([0xC8, 0x03, 0x01, led, 0x00, 0xC8]))
    GeneralSystemMessages(serial)
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
    GeneralSystemMessages(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x02, 0x00, 0xC8]))
    GeneralSystemMessages(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x03, 0x00, 0xC8]))
    GeneralSystemMessages(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x00, 0xC8]))
    GeneralSystemMessages(serial)


def EnableLED_AutoMode(serial) -> None:
    """Enable automode of all LEDs."""
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x01, 0x01, 0xC8]))
    GeneralSystemMessages(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x02, 0x01, 0xC8]))
    GeneralSystemMessages(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x03, 0x01, 0xC8]))
    GeneralSystemMessages(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x01, 0xC8]))
    GeneralSystemMessages(serial)


def FrontIOs():
    """TBD"""
    pass


def PowerPlugDetect():
    """TBD"""
    pass


def GetDevideInfo():
    """TBD"""
    pass


def TCP_ConnectionWatchdog():
    """TBD"""
    pass


def GetFirmwareIDs():
    """TBD"""
    pass
