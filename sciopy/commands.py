def print_syntax():
    """List sciospec communication interface syntax."""
    print("The general structure of each communication with a Sciospec device:")
    print("- The communication is done by frames")
    print("- Each communication frame is constructed as follows")
    print("- 1 byte command-Tag (Frame-Start)")
    print("- 1 byte number of data-bytes (0...255)")
    print("- 0...255 data-bytes")
    print("- 1 byte Command-Tag (Frame-End)")
    print("- The command-tag identifies the command (see Command list)")
    print("- Frame-Start and –End must be identical")


def print_acknowledge_messages():
    """List acknowledge messages."""
    print("- Communication-frames with incorrect syntax will cause a “Frame-Not-Acknowledge” message")
    print("- If the transmission of a communication-frame is interrupted for more than 10 ms a “Timeout” message is send")
    print("- Every invalid command-tag will cause a “Not-Acknowledge” message")
    print(
        "- Every valid command is acknowledged with an acknowledge command [ACK]")
    print("- For commands with a return value the returning frame comes before the acknowledge message")
    print("- When commands are sent during the current measurements, measurement data can be transmitted between the command and the following returning frame and the acknowledge-message (commands are handled asynchronously)")
    print("- Before sending a new command, the resulting acknowledge or not acknowledge of the previous command has to be awaited.")


def print_general_system_messages():
    """Print general system messages."""
    pass


def print_command_list():
    """Print out command list."""
    print(
        "The leading hex code of each command heading represents the [command code] of the respective function.")
    print("0x90 - Save settings")
    print("0xA1 - Software Reset")
    print("0xB0 - Set Measurement Setup")
    print("0xB1 - Get Measurement Setup")
    print("0xB2 - Set Output Configuration")
    print("0xB3 - Get Output Configuration")
    print("0xB4 - Start/Stop Measurement")
    print("0xB5 - Get temperature")
    print("0xC6 - Set Battery Control")
    print("0xC7 - Get Battery Control")
    print("0xC8 - Set LED Control")
    print("0xC9 - Get LED Control")
    print("0xCB - FrontIOs")
    print("0xCC - Power Plug Detect")
    print("0xD1 - Get Device Info")
    print("0xCF - TCP connection watchdog")
    print("0xD2 - Get firmware IDs")


def save_settings():
    print("Saved Settings: 0x90")


def software_reset():
    print("Software reset: 0xA1")
