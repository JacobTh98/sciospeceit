from .print_command_info import (
    print_syntax,
    print_general_system_messages,
    print_acknowledge_messages,
    print_command_list,
)

from .com_handling import (
    available_serial_ports,
    connect_COM_port,
    serial_write,
    disconnect_COM_port,
)

"""
from .doteit import (
    doteit_in_SingleEitFrame,
    list_eit_files,
    list_all_files,
    single_eit_in_pickle,
    load_pickle_to_dict,
    convert_fulldir_doteit_to_pickle,
    convert_fulldir_doteit_to_npz,
)
"""

from .setup_m import (
    SystemMessageCallback,
    SaveSettings,
    SoftwareReset,
    ResetMeasurementSetup,
    SetMeasurementSetup,
    GetMeasurementSetup,
    SetOutputConfiguration,
    GetOutputConfiguration,
    StartStopMeasurement,
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

from .default_configurations import configuration_01


__all__ = [
    # print_command_info
    "print_syntax",
    "print_general_system_messages",
    "print_acknowledge_messages",
    "print_command_list",
    # com_handling
    "available_serial_ports",
    "connect_COM_port",
    "serial_write",
    "disconnect_COM_port",
    # doteit
    # "doteit_in_SingleEitFrame",
    # "list_eit_files",
    # "list_all_files",
    # "single_eit_in_pickle",
    # "load_pickle_to_dict",
    # "convert_fulldir_doteit_to_pickle",
    # "convert_fulldir_doteit_to_npz",
    # setup_m
    "SystemMessageCallback",
    "SaveSettings",
    "SoftwareReset",
    "ResetMeasurementSetup",
    "SetMeasurementSetup",
    "GetMeasurementSetup",
    "SetOutputConfiguration",
    "GetOutputConfiguration",
    "StartStopMeasurement",
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
    # default_configurations
    "configuration_01",
]
