""" Convert a .eit file to python sctructured data"""

import os
import numpy as np

# tmp path

path = "C:/Users/ScioSpecEIT/Desktop/data/20230105 14.36.10/setup/"

src_list = [_ for _ in os.listdir(path) if _.endswith(".eit")]


class SingleEitFrame:
    pass


def single_eit_in_npz(name, l_path, s_path):
    with open(l_path + name, "r") as file:
        read_content = file.read().split("\n")

    frame = SingleEitFrame()
    # read_content[0]
    # read_content[1]
    frame.setup_name = read_content[2]
    frame.date_time = read_content[3]
    frame.f_min = read_content[4]
    frame.f_max = read_content[5]
    # read_content[6]
    # read_content[7]
    frame.current = read_content[8]
    # read_content[9]
    # read_content[10]
    # read_content[11]
    # read_content[12]
    # read_content[13]
    # read_content[14]
    # read_content[15]
    frame.MeasurementChannels = read_content[16].split(":")[1]
    frame.MeasurementChannelsIndependentFromInjectionPattern = read_content[17].split(
        ":"
    )[1]

    for i in range(18, len(read_content) - 1, 2):
        el_cmb = read_content[i].split(" ")
        el_cmb = f"{el_cmb[0]}_{el_cmb[1]}"
        lct = read_content[i + 1].split("\t")
        lct = [ele.replace("E", "e") for ele in lct]
        lct = [float(ele) for ele in lct]
        setattr(frame, el_cmb, lct)

    sname = s_path + frame.setup_name + ".npz"
    print(sname)
    np.savez(str(sname), frame=frame)


single_eit_in_npz(src_list[0], path, "C:/Users/ScioSpecEIT/Desktop/sciospeceit/sciopy/")
