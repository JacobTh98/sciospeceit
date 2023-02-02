# https://stackoverflow.com/questions/17589942/using-pyserial-to-send-binary-data
# from connect import connect_COM_port
from time import sleep


def SystemMessageCallback(serial, prnt_msg: bool = True, ret_hex_int: int = 0):
    """Reads the message buffer of a serial connection. Also prints out the general system message.
    serial      ... serial connection
    prnt_msg    ... print out the buffer
    ret_hex_int ... Parameters -> ['none','hex', 'int', 'both']
    
    @v=1.0.3
    """
    msg_dict = {
        "0x01": "No message inside the message buffer",
        "0x02": "Timeout: Communication-timeout (less data than expected)",
        "0x04": "Wake-Up Message: System boot ready",
        "0x11": "TCP-Socket: Valid TCP client-socket connection",
        "0x81": "Not-Acknowledge: Command has not been executed",
        "0x82": "Not-Acknowledge: Command could not be recognized",
        "0x83": "Command-Acknowledge: Command has been executed successfully",
        "0x84": "System-Ready Message: System is operational and ready to receive data",
        "0x91": "Data holdup: Measurement data could not be sent via the master interface",
    }
    timeout_count = 0
    received = []
    received_hex = []
    data_count = 0

    while True:
        buffer = serial.read()
        if buffer:
            received.extend(buffer)
            data_count += len(buffer)
            timeout_count = 0
            continue
        timeout_count += 1
        if timeout_count >= 1:
            # Break if we haven't received any data
            break

        received = "".join(str(received))  # If you need all the data
    received_hex = [hex(receive) for receive in received]
    try:
        msg_idx = received_hex.index("0x18")
        print(msg_dict[received_hex[msg_idx + 2]])
    except BaseException:
        print(msg_dict["0x01"])
        prnt_msg = False
    if prnt_msg:
        print("message buffer:\n", received_hex)
        print("message length:\t", data_count)

    if ret_hex_int == "none":
        return
    elif ret_hex_int == "hex":
        return received_hex
    elif ret_hex_int == "int":
        return received
    elif ret_hex_int == "both":
        return received, received_hex


def SaveSettings(serial) -> None:
    serial.write(bytearray([0x90, 0x00, 0x90]))
    SystemMessageCallback(serial)


def SoftwareReset(serial) -> None:
    serial.write(bytearray([0xA1, 0x00, 0xA1]))
    SystemMessageCallback(serial)


def ResetMeasurementSetup(serial):
    serial.write(bytearray([0xB0, 0x01, 0x01, 0xB0]))
    SystemMessageCallback(serial)


def SetMeasurementSetup(
    serial,
    burst_count: int = 10,
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
        SystemMessageCallback(serial)

    if burst_count <= 255:
        burst_count = bytearray([0xB0, 0x03, 0x02, 0x00, burst_count, 0xB0])
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
    SystemMessageCallback(serial)  # [CT] 03 02 [burst count] [CT]

    frame_rate = bytearray([0xB1, 0x01, 0x03, 0xB1])
    serial.write(frame_rate)
    print("Frame Rate:")
    SystemMessageCallback(serial)  # [CT] 05 03 [frame rate] [CT]

    exc_freq = bytearray([0xB1, 0x01, 0x04, 0xB1])
    serial.write(exc_freq)
    print("Excitation Frequencies:")
    SystemMessageCallback(
        serial
    )  # [CT] [LE] 04 [fmin 1st block] [fmax 1st block] [fcount 1st block] [ftype 1st block] [fmin 2nd block] [fmax 2nd block] [fcount 2nd block] [ftype 2nd block] ... [CT]

    exc_amp = bytearray(
        [0xB1, 0x01, 0x05, 0xB1]
    )  # [CT] 05 05 [excitation amplitude] [CT]
    serial.write(exc_amp)
    print("Excitation Amplitude:")
    SystemMessageCallback(serial)

    exc_seq = bytearray([0xB1, 0x01, 0x06, 0xB1])
    serial.write(exc_seq)
    print("Excitation Sequence:")
    SystemMessageCallback(serial)  # [CT] [LE] 06 [excitation sequence] [CT]

    meas_mode = bytearray([0xB1, 0x01, 0x08, 0xB1])
    serial.write(meas_mode)
    print("Measure Mode:")
    SystemMessageCallback(serial)  # [CT] 03 08 [Mode] [Boundary] [CT]

    gain = bytearray([0xB1, 0x01, 0x09, 0xB1])
    serial.write(gain)
    print("Gain Settings:")
    SystemMessageCallback(serial)  # [CT] [LE] 09 [Mode] [Data] [CT]

    exc_switch = bytearray([0xB1, 0x01, 0x0C, 0xB1])
    serial.write(exc_switch)
    print("Excitation switch type:")
    SystemMessageCallback(serial)  # [CT] 02 0C [Type] [CT]


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
    SystemMessageCallback(serial)

    # write current row in the frequency stack
    serial.write(bytearray([0xB2, 0x02, 0x02, curr_row_freq_stack, 0xB2]))
    SystemMessageCallback(serial)

    # write timestamp
    serial.write(bytearray([0xB2, 0x02, 0x03, timestamp, 0xB2]))
    SystemMessageCallback(serial)


def GetOutputConfiguration(serial) -> None:
    """Returns the display option in the data stream of measured date."""
    pass


def StartStopMeasurement(serial, command: int) -> None:
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
    SystemMessageCallback(serial)


def GetTemperature() -> None:
    print("No temperature sensor available")


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
    SystemMessageCallback(serial)


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
    SystemMessageCallback(serial)


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
    SystemMessageCallback(serial)
    if mode == "disable":
        MODE = 0x00
    elif mode == "enable":
        MODE = 0x01
    elif mode == "blink":
        MODE = 0x02
    serial.write(bytearray([0xC8, 0x03, 0x02, led, MODE, 0xC8]))
    SystemMessageCallback(serial)


def DisableLED_AutoMode(serial) -> None:
    """Disable automode of all LEDs."""
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x01, 0x00, 0xC8]))
    SystemMessageCallback(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x02, 0x00, 0xC8]))
    SystemMessageCallback(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x03, 0x00, 0xC8]))
    SystemMessageCallback(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x00, 0xC8]))
    SystemMessageCallback(serial)


def EnableLED_AutoMode(serial) -> None:
    """Enable automode of all LEDs."""
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x01, 0x01, 0xC8]))
    SystemMessageCallback(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x02, 0x01, 0xC8]))
    SystemMessageCallback(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x03, 0x01, 0xC8]))
    SystemMessageCallback(serial)
    serial.write(bytearray([0xC8, 0x03, 0x01, 0x04, 0x01, 0xC8]))
    SystemMessageCallback(serial)


def FrontIOs():
    """TBD"""
    pass


def PowerPlugDetect(serial) -> None:
    serial.write(bytearray([0xCC, 0x01, 0x81, 0xCC]))
    SystemMessageCallback(serial)


def GetDevideInfo(serial) -> None:
    """Get device info"""
    serial.write(bytearray([0xD1, 0x00, 0xD1]))
    SystemMessageCallback(serial)


def TCP_ConnectionWatchdog():
    """TBD"""
    pass


def GetFirmwareIDs(serial) -> None:
    """Get firmware IDs"""
    serial.write(bytearray([0xD2, 0x00, 0xD2]))
    SystemMessageCallback(serial)


def Config_01(serial) -> None:
    serial.write(bytearray([0xB0, 0x01, 0x01, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x02, 0x00, 0x09, 0xB0]))
    serial.write(
        bytearray(
            [0xB0, 0x09, 0x05, 0x3F, 0x50, 0x62, 0x4D, 0xD2, 0xF1, 0xA9, 0xFC, 0xB0]
        )
    )
    serial.write(bytearray([0xB0, 0x02, 0x0D, 0x01, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x09, 0x01, 0x00, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x08, 0x01, 0x01, 0xB0]))
    serial.write(bytearray([0xB0, 0x02, 0x0C, 0x01, 0xB0]))
    serial.write(bytearray([0xB0, 0x05, 0x03, 0x40, 0x00, 0x00, 0x00, 0xB0]))
    serial.write(
        bytearray(
            [
                0xB0,
                0x0C,
                0x04,
                0x44,
                0x7A,
                0x00,
                0x00,
                0x44,
                0x7A,
                0x00,
                0x00,
                0x00,
                0x01,
                0x00,
                0xB0,
            ]
        )
    )
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x01, 0x02, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x02, 0x03, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x03, 0x04, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x04, 0x05, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x05, 0x06, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x06, 0x07, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x07, 0x08, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x08, 0x09, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x09, 0x0A, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x0A, 0x0B, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x0B, 0x0C, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x0C, 0x0D, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x0D, 0x0E, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x0E, 0x0F, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x0F, 0x10, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x10, 0x11, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x11, 0x12, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x12, 0x13, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x13, 0x14, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x14, 0x15, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x15, 0x16, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x16, 0x17, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x17, 0x18, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x18, 0x19, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x19, 0x1A, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x1A, 0x1B, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x1B, 0x1C, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x1C, 0x1D, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x1D, 0x1E, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x1E, 0x1F, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x1F, 0x20, 0xB0]))
    serial.write(bytearray([0xB0, 0x03, 0x06, 0x20, 0x01, 0xB0]))
    serial.write(bytearray([0xB1, 0x01, 0x03, 0xB1]))
    serial.write(bytearray([0xB2, 0x02, 0x01, 0x01, 0xB2]))
    serial.write(bytearray([0xB2, 0x02, 0x03, 0x01, 0xB2]))
    serial.write(bytearray([0xB2, 0x02, 0x02, 0x01, 0xB2]))
    serial.write(bytearray([0xB4, 0x01, 0x01, 0xB4]))
    sleep(10)
    serial.write(bytearray([0xB4, 0x01, 0x00, 0xB4]))
