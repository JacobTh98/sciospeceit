import struct
from dataclasses import dataclass
from typing import List, Tuple, Union
import os
import numpy as np

from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig

scio_spec_measurement_config = ScioSpecMeasurementConfig(
    sample_per_step=10,
    actual_sample=0,
    s_path="tmp_data/",
    object="circle",
)

import time
from sciopy import (
    SystemMessageCallback,
    configuration_01,
    connect_COM_port,
    StartStopMeasurement,
    del_hex_in_list,
    reshape_measurement_buffer,
)


def GetFirmwareIDs(serial):
    """Get firmware IDs"""
    serial.write(bytearray([0xD2, 0x00, 0xD2]))
    SystemMessageCallback(serial)


scio_spec_measurement_config.actual_sample = len(
    os.listdir(scio_spec_measurement_config.s_path)
)

## Insert config files...


COM_ScioSpec = connect_COM_port("COM3", timeout=1)

GetFirmwareIDs(COM_ScioSpec)
SystemMessageCallback(COM_ScioSpec)

configuration_01(COM_ScioSpec)

SystemMessageCallback(COM_ScioSpec)

# Measurement:

for i in range(scio_spec_measurement_config.sample_per_step):
    # TBD: Inser an Input JSON, that contain the measurement informaton of any step.
    measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
    measurement_data = del_hex_in_list(measurement_data_hex)
    # measurement_data = reshape_measurement_buffer(measurement_data)
    np.savez(
        scio_spec_measurement_config.s_path
        + f"Sample{scio_spec_measurement_config.actual_sample}.npy",
        config=scio_spec_measurement_config,
        data=measurement_data,
        allow_pickle=True,
    )
    scio_spec_measurement_config.actual_sample += 1

SystemMessageCallback(COM_ScioSpec, prnt_msg=False)
print("Finished Measurement.")
