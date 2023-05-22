import time
import os
import numpy as np

# import sys
import pickle
from typing import Union
import requests
import json

from sciopy import (
    SystemMessageCallback,
    SetBurstCount,
    conf_n_el_16_adjacent,
    conf_n_el_16_opposite,
    connect_COM_port,
    StartStopMeasurement,
    reshape_full_message_in_bursts,
    del_hex_in_list,
    split_bursts_in_frames,
    reduce_burst_to_available_parts,
    SoftwareReset,
)

from ender_sciospec_classes import (
    CircleDrivePattern,
    KartesianDrivePattern,
    Ender5Stat,
)
from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig


def read_telegram_json(json_path: str = "telegram_config.json") -> dict:
    """
    Insert the "token", "chat_id" inside the 'telegram_config.json'
    and set "state":True for using the telegram progress bar.

    Parameters
    ----------
    json_path : str, optional
        path to configuration file, by default 'telegram_config.json'

    Returns
    -------
    dict
        configuration
    """
    conf_file = open(json_path)
    telegram_config = json.load(conf_file)
    return telegram_config


def telegram_KI_bot(bot_message: str, bot_cnf: dict) -> None:
    """
    telegram_KI_bot sends a message string to a configured telegram bot.

    Parameters
    ----------
    bot_message : str
        message to send
    bot_cnf : dict
        bot configuration
    """
    send_text = (
        "https://api.telegram.org/bot"
        + bot_cnf["token"]
        + "/sendMessage?chat_id="
        + bot_cnf["chat_id"]
        + "&parse_mode=Markdown&text="
        + bot_message
    )
    requests.get(send_text)


try:
    telegram_config = read_telegram_json(json_path="telegram_config.json")
except BaseException:
    print("Error 404: No telegram config found")


def check_for_content(
    measurement_data: np.ndarray,
) -> np.ndarray:
    """Checks the data for content. If data is available continues measurement, else abort script.

    Parameters
    ----------
    measurement_data : np.ndarray
        measured data content
    COM_ScioSpec : _type_
        serial connection
    scio_spec_measurement_config : ScioSpecMeasurementConfig
        measurement configuration
    ch_n : int, optional
        number function was called, by default 0

    Returns
    -------
    np.ndarray
        measurement data
    """
    # ch_n = ch_n
    if len(measurement_data[0]) == 0:
        telegram_KI_bot("Message is empty", telegram_config)
        print("empty buffer")
    else:
        return measurement_data


start_time = time.time()


def split_pickle_to_classes(
    pkl_data: list,
) -> Union[
    ScioSpecMeasurementConfig,
    CircleDrivePattern,
    KartesianDrivePattern,
    Ender5Stat,
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
    override_burst_count = scio_spec_measurement_config.burst_count
    # print(
    #    scio_spec_measurement_config,
    #    circledrivepattern,
    #    kartesiandrivepattern,
    #    enderstat,
    # )
    # Check if the measurement before was saved:
    if (
        scio_spec_measurement_config.actual_sample != 0
        and len(os.listdir(scio_spec_measurement_config.s_path)) == 0
    ):
        print("\tNo data was saved!")

    files_offset = len(os.listdir(scio_spec_measurement_config.s_path))
    scio_spec_measurement_config.actual_sample = files_offset

    try:
        COM_ScioSpec = connect_COM_port(
            scio_spec_measurement_config.com_port, timeout=1
        )
    except ConnectionError:
        print("Cant connect to port.")

    # if files_offset % 500 == 0:
    #    telegram_KI_bot("preventive reset", telegram_config)
    #    print("Preventive SoftwareReset")
    #    SoftwareReset(COM_ScioSpec)
    #    time.sleep(5)
    #    COM_ScioSpec = connect_COM_port()
    #    SystemMessageCallback(COM_ScioSpec)

    # Send configuration an read answer
    scio_spec_measurement_config = conf_n_el_16_opposite(
        COM_ScioSpec, scio_spec_measurement_config
    )
    print("\tConfig 4", scio_spec_measurement_config)
    SystemMessageCallback(COM_ScioSpec, prnt_msg=False)

    scio_spec_measurement_config.burst_count = override_burst_count
    splittet_burst_count = reduce_burst_to_available_parts(
        scio_spec_measurement_config.burst_count
    )
    print("Settet burst count:", override_burst_count)
    print("Splittet in::", splittet_burst_count)

    for splitted_bursts in splittet_burst_count:
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
        print(f"\tlen of {len(measurement_data[0])=}.")

        reset_num = 0
        while len(measurement_data[0]) == 0:
            telegram_KI_bot(f"empty measurement->reset {reset_num}", telegram_config)
            SystemMessageCallback(COM_ScioSpec)
            time.sleep(5)
            SoftwareReset(COM_ScioSpec)
            time.sleep(10)
            COM_ScioSpec = connect_COM_port(COM_ScioSpec.name)
            time.sleep(2)
            SystemMessageCallback(COM_ScioSpec)
            scio_spec_measurement_config = conf_n_el_16_opposite(
                COM_ScioSpec, scio_spec_measurement_config
            )
            time.sleep(1)
            SystemMessageCallback(COM_ScioSpec)
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
            reset_num += 1

        for bursts in measurement_data:
            # Check if burst is zero:

            np.savez(
                scio_spec_measurement_config.s_path
                + "sample_{0:06d}.npz".format(files_offset),
                config=scio_spec_measurement_config,
                data=bursts,
                enderstat=enderstat.__dict__,
                circledrivepattern=circledrivepattern.__dict__,
                kartesiandrivepattern=kartesiandrivepattern.__dict__,
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
