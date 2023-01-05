"""
sciopy: Python based interface module for ScioSpec Electrical Impedance Tomography device.
"""

__author__ = "Jacob Peter Thönes"
__author_email__ = "jacob.thoenes@uni-rostock.de"
APP_NAME = "sciopy"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A Python Package for ScioSpec EIT (electrical impedance tomography) system with 16, 32, 64, 128 or 256 channels"


from .communication_info import (
    print_syntax,
    print_general_system_messages,
    print_acknowledge_messages,
    print_command_list,
)

from .connect import (
    available_serial_ports,
    connect_COM_port,
    serial_write,
    disconnect_COM_port,
)

__all__ = [
    # communication_info
    "print_syntax",
    "print_general_system_messages",
    "print_acknowledge_messages",
    "print_command_list",
    # connect
    "available_serial_ports",
    "connect_COM_port",
    "serial_write",
    "disconnect_COM_port",
]
