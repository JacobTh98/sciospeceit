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
    parse_single_frame,
    connect_COM_port,
    StartStopMeasurement,
    reshape_burst_buffer,
    del_hex_in_list,
    parse_to_full_frame,
    SetBurstCount,
)

import numpy as np
from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig
import pickle
from typing import Union

from ender_sciospec_classes import CircleDrivePattern, KartesianDrivePattern, Ender5Stat


def reshape_full_message_in_bursts(
    lst: list, cnf: ScioSpecMeasurementConfig
) -> np.ndarray:
    """
    Gets the full message buffer.

    Example:- input: n_el=16 -> lst.shape=(44804) | n_el=32 -> lst.shape=(89604,)
            - delete acknowledgement message: lst.shape=(4480,0) | lst.shape=(89600,)
            - split this depending on burst count: split_list.shape=(5, 8960) | split_list.shape=(5, 17920)
    """
    split_list = []
    msg_len = 140
    # delete acknowledgement message
    lst = lst[4:]
    # split in burst count messages
    split_length = lst.shape[0] // cnf.burst_count
    for split in range(cnf.burst_count):
        split_list.append(lst[split * split_length : (split + 1) * split_length])
    return np.array(split_list)


def split_bursts_in_framge(
    split_list: np.ndarray, cnf: ScioSpecMeasurementConfig
) -> np.ndarray:
    """ """
    msg_len = 140  # Constant
    frame = []  # Channel group depending frame
    burst_frame = []  # single burst count frame with channel depending frame
    subframe_length = split_list.shape[1] // msg_len
    for bursts in range(cnf.burst_count):  # Iterate over bursts
        tmp_split_list = np.reshape(split_list[bursts], (subframe_length, msg_len))
        for subframe in range(subframe_length):
            parsed_sgl_frame = parse_single_frame(tmp_split_list[subframe])
            # Select the right channel group data
            if parsed_sgl_frame.channel_group in cnf.channel_group:
                frame.append(parsed_sgl_frame)
        burst_frame.append(frame)
        frame = []  # Reset channel depending single burst frame
    return np.array(burst_frame)


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
    print("\tConfig 4", scio_spec_measurement_config)

    SystemMessageCallback(COM_ScioSpec, prnt_msg=False)

    """
    TBD: Send own configuration
        - [ ] burst count
        - [ ] frequency
    """
    scio_spec_measurement_config.burst_count = 5
    SetBurstCount(COM_ScioSpec, scio_spec_measurement_config)
    SystemMessageCallback(COM_ScioSpec)

    # Measure up to burst count
    measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
    # Delete hex in mesured buffer
    measurement_data = del_hex_in_list(measurement_data_hex)
    # Reshape the full mesaurement buffer. Depending on number of electrodes
    # np.save(
    #    scio_spec_measurement_config.s_path + "meas_ele_32_bc_5.npy", measurement_data
    # )
    # Start insertion: get: Full message buffer. return: shaped and exported information depending on burst count, n_el -> INSERT DATA FROM WORKBENCH

    split_measurement_data = reshape_full_message_in_bursts(
        measurement_data, scio_spec_measurement_config
    )

    measurement_data = split_bursts_in_framge(
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
