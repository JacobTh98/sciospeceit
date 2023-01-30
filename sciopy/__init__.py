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

from .doteit import (
    list_eit_files,
    list_all_files,
    single_eit_in_pickle,
    load_pickle_to_dict,
    convert_fulldir_doteit_to_pickle,
    convert_fulldir_doteit_to_npz,
)

from .setup_m import (
    SystemMessageCallback,
    SaveSettings,
    SoftwareReset,
    ResetMeasurementSetup,
    SetMeasurementSetup,
    GetMeasurementSetup,
    SetOutputConfiguration,
    GetOutputConfiguration,
    Start_StopMeasurement,
    GetTemperature,
    SetBatteryControll,
    GetBatteryControll,
    SetLEDControl,
    GetLEDControl,
    SetLED_Mode,
    DisableLED_AutoMode,
    EnableLED_AutoMode,
    FrontIOs,
    PowerPlugDetect,
    GetDevideInfo,
    TCP_ConnectionWatchdog,
    GetFirmwareIDs,
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
    # doteit
    "list_eit_files",
    "list_all_files",
    "single_eit_in_pickle",
    "load_pickle_to_dict",
    "convert_fulldir_doteit_to_pickle",
    "convert_fulldir_doteit_to_npz",
    # setup_m
    "GeneralSystemMessages",
    "SaveSettings",
    "SoftwareReset",
    "ResetMeasurementSetup",
    "SetMeasurementSetup",
    "GetMeasurementSetup",
    "SetOutputConfiguration",
    "GetOutputConfiguration",
    "Start_StopMeasurement",
    "GetTemperature",
    "SetBatteryControll",
    "GetBatteryControll",
    "SetLEDControl",
    "GetLEDControl",
    "SetLED_Mode",
    "DisableLED_AutoMode",
    "EnableLED_AutoMode",
    "FrontIOs",
    "PowerPlugDetect",
    "GetDevideInfo",
    "TCP_ConnectionWatchdog",
    "GetFirmwareIDs",
]
