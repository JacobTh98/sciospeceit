def print_syntax() -> None:
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


def print_acknowledge_messages() -> None:
    """List acknowledge messages."""
    print(
        "- Communication-frames with incorrect syntax will cause a “Frame-Not-Acknowledge” message"
    )
    print(
        "- If the transmission of a communication-frame is interrupted for more than 10 ms a “Timeout” message is send"
    )
    print("- Every invalid command-tag will cause a “Not-Acknowledge” message")
    print("- Every valid command is acknowledged with an acknowledge command [ACK]")
    print(
        "- For commands with a return value the returning frame comes before the acknowledge message"
    )
    print(
        "- When commands are sent during the current measurements, measurement data can be transmitted between the command and the following returning frame and the acknowledge-message (commands are handled asynchronously)"
    )
    print(
        "- Before sending a new command, the resulting acknowledge or not acknowledge of the previous command has to be awaited."
    )


def print_general_system_messages() -> None:
    """Print general system messages."""
    print("0x01    Frame-Not-Acknowledge: Incorrect syntax")
    print("0x02    Timeout: Communication-timeout (less data than expected)")
    print("0x04    Wake-Up Message: System boot ready")
    print("0x11    TCP-Socket: Valid TCP client-socket connection")
    print("0x81    Not-Acknowledge: Command has not been executed")
    print("0x82    Not-Acknowledge: Command could not be recognized")
    print("0x83    Command-Acknowledge: Command has been executed successfully")
    print(
        "0x84    System-Ready Message: System is operational and ready to receive data"
    )
    print(
        "0x91    Data holdup: Measurement data could not be sent via the master interface"
    )


def print_command_list() -> None:
    """Print out command list."""
    print(
        "The leading hex code of each command heading represents the [command code] of the respective function."
    )
    print("\t GS = General Syntax\n")
    print("0x90 - Save settings                GS=[CT] 00 [CT]")
    print("0xA1 - Software Reset               GS=[CT] 00 [CT]")
    print("0xB0 - Set Measurement Setup        GS=[CT] [LE] [OB] [CD] [CT]")
    print("0xB1 - Get Measurement Setup        GS=[CT] [LE] [OB] [CT]")
    print("0xB2 - Set Output Configuration     GS=[CT] [LE] [OB] [CD] [CT]")
    print("0xB3 - Get Output Configuration     GS=[CT] [LE] [OB] [CT]")
    print("0xB4 - Start/Stop Measurement       GS=[CT] [LE] [OB] [CT]")
    print("0xB5 - Get temperature              GS=[CT] 01 [TempSensor] [CT]")
    print("0xC6 - Set Battery Control          GS=[CT] [LE] [OB] [CD] [CT]")
    print("0xC7 - Get Battery Control          GS=[CT] [LE] [OB] [CT]")
    print("0xC8 - Set LED Control              GS=[CT] [LE] [OB] [CD] [CT]")
    print("0xC9 - Get LED Control              GS=[CT] [LE] [OB] [LED#] [CT]")
    print("0xCB - FrontIOs                     GS=[CT] [LE] [OB] [CG] [IO] [ST] [CT]")
    print("0xCC - Power Plug Detect            GS=[CT] [LE] [OB] [CT]")
    print("0xD1 - Get Device Info              GS=[CT] 00 [CT]")
    print("0xCF - TCP connection watchdog      GS=[CT] 05 00 [interval] [CT]")
    print("0xD2 - Get firmware IDs             GS=D2 00 D2")
