import time

start_time = time.time()

from dataclasses import dataclass
from typing import List
import os
import numpy as np


from sciopy import (
    SystemMessageCallback,
    configuration_01,
    configuration_02,
    configuration_04,
    connect_COM_port,
    StartStopMeasurement,
    reshape_burst_buffer,
    del_hex_in_list,
    parse_to_full_frame,
)

import numpy as np

import pickle
from typing import Union

from ender_sciospec_classes import CircleDrivePattern, KartesianDrivePattern, Ender5Stat
from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig


def split_pickle_to_classes(
    pkl_data: list,
) -> Union[
    ScioSpecMeasurementConfig, CircleDrivePattern, KartesianDrivePattern, Ender5Stat
]:

    return pkl_data[0], pkl_data[1], pkl_data[2], pkl_data[3]


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
        enderstat,
    ) = split_pickle_to_classes(meas_cnf)

    print(
        scio_spec_measurement_config,
        circledrivepattern,
        kartesiandrivepattern,
        enderstat,
    )

    files_offset = len(os.listdir(scio_spec_measurement_config.s_path))
    scio_spec_measurement_config.actual_sample = files_offset

    try:
        COM_ScioSpec = connect_COM_port(
            scio_spec_measurement_config.com_port, timeout=1
        )
    except ConnectionError:
        print("Cant connect to port.")

    # GetFirmwareIDs(COM_ScioSpec)
    # SystemMessageCallback(COM_ScioSpec)

    # Send configuration an read answer
    scio_spec_measurement_config = configuration_04(
        COM_ScioSpec, scio_spec_measurement_config
    )

    SystemMessageCallback(COM_ScioSpec)

    """
    TBD: Send own configuration
        - [ ] burst count
        - [ ] frequency
    """

    print("Burst count = 1")
    COM_ScioSpec.write(bytearray([0xB0, 0x03, 0x02, 0x00, 0x05, 0xB0]))
    SystemMessageCallback(COM_ScioSpec)

    # Measure up to burst count
    measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
    # Delete hex in mesured buffer
    measurement_data = del_hex_in_list(measurement_data_hex)
    # Reshape the full mesaurement buffer. Depending on number of electrodes
    measurement_data = reshape_burst_buffer(
        measurement_data, scio_spec_measurement_config
    )
    for ele in measurement_data:
        for bursts in range(scio_spec_measurement_config.burst_count):
            np.savez(
                scio_spec_measurement_config.s_path
                + "sample_{0:06d}.npz".format(files_offset),
                config=scio_spec_measurement_config,
                data=parse_to_full_frame(measurement_data[bursts]),
                enderstat=enderstat,
                circledrivepattern=circledrivepattern,
                kartesiandrivepattern=kartesiandrivepattern,
            )
            files_offset += 1
            scio_spec_measurement_config.actual_sample = files_offset

    SystemMessageCallback(COM_ScioSpec, prnt_msg=False)
    os.remove("meas_cnf.pkl")
    print("\t->Finished Measurement.")
    COM_ScioSpec.close()
    total_time = time.time() - start_time
    print(
        "--- Runtime measurement script %s seconds ---"
        % np.round(time.time() - start_time, 2)
    )
