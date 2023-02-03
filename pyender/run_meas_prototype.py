import time

start_time = time.time()

from dataclasses import dataclass
from typing import List
import os
import numpy as np


from sciopy import (
    SystemMessageCallback,
    configuration_01,
    connect_COM_port,
    StartStopMeasurement,
    bytesarray_to_float,
    bytesarray_to_int,
    bytesarray_to_byteslist,
    parse_single_frame,
    reshape_measurement_buffer,
    del_hex_in_list,
    parse_to_full_frame,
    GetFirmwareIDs,
)

"""
def del_hex_in_list(lst: list) -> list:
    return [
        "0" + ele.replace("0x", "") if len(ele) == 1 else ele.replace("0x", "")
        for ele in lst
    ]


def bytesarray_to_float(bytes_array: np.ndarray) -> float:
    bytes_array = [int(b, 16) for b in bytes_array]
    bytes_array = bytes(bytes_array)
    return struct.unpack("!f", bytes(bytes_array))[0]


def bytesarray_to_int(bytes_array: np.ndarray) -> int:
    bytes_array = bytesarray_to_byteslist(bytes_array)
    return int.from_bytes(bytes_array, "big")


def bytesarray_to_byteslist(bytes_array: np.ndarray) -> list:
    bytes_array = [int(b, 16) for b in bytes_array]
    return bytes(bytes_array)


def reshape_measurement_buffer(lst: list) -> np.ndarray:
    idx_b4 = [i for i, ele in enumerate(lst) if ele == "b4"]
    idx_b4 = np.array(idx_b4)
    step = abs(idx_b4[1] - idx_b4[0]) + 1
    return np.array(
        [lst[i : i + step] for i in range(idx_b4[0], idx_b4[-1] + step, step)],
        dtype=list,
    )[:-1]

"""

# def parse_to_full_frame(
#    measurement_data: np.ndarray, burst_count: int = 1
# ) -> np.ndarray:
#    """Parses any measured byte representation into the dataclass SingleFrame"""
#    if burst_count == 1:
#        data_frame = []
#        for i, sf in enumerate(measurement_data):
#            data_frame.append(parse_single_frame(sf))
#        return np.array(data_frame)
#


@dataclass
class BaseSettingForEstimation:
    active_channel_groups: np.ndarray
    burst_count: int


@dataclass
class SingleFrame:
    start_tag: List[str]
    channel_group: str
    excitation_stgs: List[str]
    frequency_row: List[str]
    timestamp: int  # [ms]
    ch_1: complex
    ch_2: complex
    ch_3: complex
    ch_4: complex
    ch_5: complex
    ch_6: complex
    ch_7: complex
    ch_8: complex
    ch_9: complex
    ch_10: complex
    ch_11: complex
    ch_12: complex
    ch_13: complex
    ch_14: complex
    ch_15: complex
    ch_16: complex
    end_tag: str


"""
def parse_single_frame(lst_ele: np.ndarray) -> SingleFrame:
    channels = {}
    enum = 0
    for i in range(11, 135, 8):
        enum += 1
        channels[f"ch_{enum}"] = complex(
            bytesarray_to_float(lst_ele[i : i + 4]),
            bytesarray_to_float(lst_ele[i + 4 : i + 8]),
        )
    excitation_stgs = np.array([ele for ele in lst_ele[3:5]])

    sgl_frm = SingleFrame(
        start_tag=lst_ele[0],
        channel_group=int(lst_ele[2]),
        excitation_stgs=excitation_stgs,
        frequency_row=lst_ele[5:7],
        timestamp=bytesarray_to_int(lst_ele[7:11]),
        **channels,
        end_tag=lst_ele[139],
    )
    return sgl_frm
"""

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

    try:
        COM_ScioSpec = connect_COM_port(
            scio_spec_measurement_config.com_port, timeout=1
        )
    except ConnectionError:
        print("Cant connect to port.")

    # GetFirmwareIDs(COM_ScioSpec)
    # SystemMessageCallback(COM_ScioSpec)

    configuration_01(COM_ScioSpec)

    SystemMessageCallback(COM_ScioSpec)

    # Measurement:

    # Possible topic of the future:
    # Insert the BurstCount at e.g. 100. Then save the data and in a post processing step the data is converted.

    for i in range(scio_spec_measurement_config.sample_per_step):
        # TBD: Speed opt: Using intern ScioSpec Burst count.

        X = int(enderstat.abs_x_pos)
        Y = int(enderstat.abs_y_pos)
        Z = int(enderstat.abs_z_pos)

        measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
        measurement_data = del_hex_in_list(measurement_data_hex)
        measurement_data = reshape_measurement_buffer(measurement_data)
        np.savez(
            scio_spec_measurement_config.s_path
            + "sample_{0:06d}.npz".format(
                len(os.listdir(scio_spec_measurement_config.s_path))
            ),
            config=scio_spec_measurement_config,
            data=parse_to_full_frame(
                measurement_data, scio_spec_measurement_config.sample_per_step
            ),
            enderstat=enderstat,
            circledrivepattern=circledrivepattern,
            kartesiandrivepattern=kartesiandrivepattern,
        )
        scio_spec_measurement_config.actual_sample += 1
        print("Burst:", scio_spec_measurement_config.actual_sample)

    SystemMessageCallback(COM_ScioSpec, prnt_msg=False)
    os.remove("meas_cnf.pkl")
    print("\t->Finished Measurement.")
    COM_ScioSpec.close()

    print(
        "--- Runtime measurement script %s seconds ---"
        % np.round(time.time() - start_time, 2)
    )
