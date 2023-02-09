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
    n_el: int  # TBD -> Insert in reshape


@dataclass
class SingleFrame:
    # Can be deleted
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
    configuration_04(COM_ScioSpec)
    SystemMessageCallback(COM_ScioSpec)
    scio_spec_measurement_config.burst_count = 5

    """
    TBD: Send own configuration
        - [ ] burst count
        - [ ] frequency
    """
    print("Burst count = 1")
    COM_ScioSpec.write(bytearray([0xB0, 0x03, 0x02, 0x00, 0x05, 0xB0]))
    SystemMessageCallback(COM_ScioSpec)

    # SET BURST COUNT = scio_spec_measurement_config.burst_count
    # SystemMessageCallback(COM_ScioSpec)

    # Insert burst count splitting reduce_burst_to_less_x()

    """
    TBD: Insert "reshape_burst_measurement_buffer()".
        This function is scaleable within the measurement buffer. It returns a list of np.ndarrays.
        Each element inside this list represents the single buffer feedback of "reshape_measurement_buffer()".
        It has to be saved for example in a for-loop to save the single measurements in single samples.
        The advantage is much more speed during the measurement. 

        reshape_burst_measurement_buffer() has also be inserted in the sciopy module too!
    """
    # Measure up to burst count
    measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
    # Delete hex in mesured buffer
    measurement_data = del_hex_in_list(measurement_data_hex)
    # Reshape the full mesaurement buffer
    measurement_data = reshape_burst_buffer(  # -> ANZAHL DER MESSENDEN ELEKTRODEN HAT EINFLUSS. Z.B.: 32 Elektroden: 128*140=17920, 16 Elektroden = 128*70=8960
        measurement_data, scio_spec_measurement_config.burst_count
    )
    # Iterate over the list full of single measurements. The len(measurement_data)=burst_count
    for ele in measurement_data:
        np.savez(
            scio_spec_measurement_config.s_path
            + "sample_{0:06d}.npz".format(files_offset),
            config=scio_spec_measurement_config,
            data=parse_to_full_frame(measurement_data),  # parse_to_full_frame
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
