import time
import os
import numpy as np

import pickle
from typing import Union

from sciopy import (
    SystemMessageCallback,
    #    configuration_01,
    #    configuration_02,
    SetBurstCount,
    configuration_04,
    connect_COM_port,
    StartStopMeasurement,
    reshape_full_message_in_bursts,
    del_hex_in_list,
    split_bursts_in_frames,
    reduce_burst_to_available_parts,
)

from ender_sciospec_classes import CircleDrivePattern, KartesianDrivePattern, Ender5Stat
from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig

start_time = time.time()


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

    # Send configuration an read answer
    scio_spec_measurement_config = configuration_04(
        COM_ScioSpec, scio_spec_measurement_config
    )
    print("\tConfig 4", scio_spec_measurement_config)
    SystemMessageCallback(COM_ScioSpec, prnt_msg=False)

    for splitted_bursts in reduce_burst_to_available_parts(
        scio_spec_measurement_config.burst_count
    ):
        # Iterate over splittet bursts
        scio_spec_measurement_config.burst_count = splitted_bursts

        SetBurstCount(COM_ScioSpec, scio_spec_measurement_config)
        SystemMessageCallback(COM_ScioSpec)

        # Measure up to burst count
        measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
        # Delete hex in mesured buffer
        measurement_data = del_hex_in_list(measurement_data_hex)
        # Reshape the full mesaurement buffer. Depending on number of electrodes
        split_measurement_data = reshape_full_message_in_bursts(
            measurement_data, scio_spec_measurement_config
        )
        measurement_data = split_bursts_in_frames(
            split_measurement_data, scio_spec_measurement_config
        )

        for bursts in measurement_data:
            np.savez(
                scio_spec_measurement_config.s_path
                + "sample_{0:06d}.npz".format(files_offset),
                config=scio_spec_measurement_config,
                data=bursts,
                enderstat=enderstat,
                circledrivepattern=circledrivepattern,
                kartesiandrivepattern=kartesiandrivepattern,
            )
            files_offset += 1
            scio_spec_measurement_config.actual_sample = files_offset

        SystemMessageCallback(COM_ScioSpec, prnt_msg=False)

    # os.remove("meas_cnf.pkl")
    print("\t->Finished Measurement.")
    COM_ScioSpec.close()
    total_time = time.time() - start_time
    print(
        "--- Runtime measurement script %s seconds ---"
        % np.round(time.time() - start_time, 2)
    )
