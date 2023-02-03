import struct
from dataclasses import dataclass
import os


from sciopy import (
    SystemMessageCallback,
    configuration_01,
    connect_COM_port,
    StartStopMeasurement,
    del_hex_in_list,
    GetFirmwareIDs,
)

import numpy as np

import pickle
from typing import Union

from ender_sciospec_classes import CircleDrivePattern, KartesianDrivePattern
from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig


def split_pickle_to_classes(
    pkl_data: list,
) -> Union[ScioSpecMeasurementConfig, CircleDrivePattern, KartesianDrivePattern]:

    return pkl_data[0], pkl_data[1], pkl_data[2]


try:
    with open("meas_cnf.pkl", "rb") as f:
        meas_cnf = pickle.load(f)
    accessed = True

except BaseException:
    accessed = False
    print("Import Error")
    # TBD-> Handshake that something went wrong.

if accessed:
    (
        scio_spec_measurement_config,
        circledrivepattern,
        kartesiandrivepattern,
    ) = split_pickle_to_classes(meas_cnf)

    scio_spec_measurement_config.actual_sample

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
            circledrivepattern=circledrivepattern,
            kartesiandrivepattern=kartesiandrivepattern,
        )
        scio_spec_measurement_config.actual_sample += 1

    SystemMessageCallback(COM_ScioSpec, prnt_msg=False)
    print("Finished Measurement.")
