""" Convert a .eit file to python sctructured data"""

import os
import numpy as np
from dataclasses import dataclass, asdict

# tmp path

path = "C:/Users/ScioSpecEIT/Desktop/data/20230105 14.36.10/setup/"

src_list = [_ for _ in os.listdir(path) if _.endswith(".eit")]


# @dataclass
class SingleEitFrame:
    number_of_header: int
    file_version_number: int
    setup_name: str
    date_time: str
    f_min: float
    f_max: float
    f_scale: str  # f_scale = 'linear' if val == 0 else 'logarithmic'
    f_count: int
    current_amplitude: float
    framerate: float
    phase_correct_parameter: float
    MeasurementChannels: list
    MeasurementChannelsIndependentFromInjectionPattern: list
    data: dict
    # ...


def single_eit_in_npz(name, l_path, s_path):
    with open(l_path + name, "r") as file:
        read_content = file.read().split("\n")

    frame = SingleEitFrame(
        #
        #
        read_content[2],
        read_content[3],
        read_content[4],
        read_content[5],
        #
        #
        read_content[8],
        #
        #
        #
        #
        #
        #
        #
        read_content[16].split(":")[1],
        read_content[17].split(":")[1],
        # el_data appended later
    )

    for i in range(18, len(read_content) - 1, 2):
        el_cmb = read_content[i].split(" ")
        el_cmb = f"{el_cmb[0]}_{el_cmb[1]}"
        lct = read_content[i + 1].split("\t")
        lct = [ele.replace("E", "e") for ele in lct]
        lct = [float(ele) for ele in lct]
        print("Set")
        setattr(frame, el_cmb, lct)

    sname = s_path + frame.setup_name + ".npz"
    print(sname)
    np.savez(str(sname), frame=frame)
    sname = s_path + frame.setup_name + "dict.npz"
    np.savez(str(sname), frame=asdict(frame))


single_eit_in_npz(src_list[0], path, "C:/Users/ScioSpecEIT/Desktop/sciospeceit/sciopy/")

# Convert the object to dictionary with function asdict()
