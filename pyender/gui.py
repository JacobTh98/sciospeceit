import numpy as np
import time
import sys
import pickle
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import PatchCollection
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

from dialogs import (
    action_get_info_dialog,
    action_get_info_dialog_kat_traj,
    action_get_info_dialog_traj,
)

from subprocess import call

from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig

try:
    import serial
except ImportError:
    print("Could not import module: serial")


import platform
from screeninfo import get_monitors

from tqdm.contrib.telegram import trange


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


try:
    telegram_config = read_telegram_json(json_path="telegram_config.json")
except BaseException:
    print("Error 404: No telegram config found")

from ender_sciospec_classes import (
    OperatingSystem,
    Ender5Stat,
    mmPerStep,
    CircleDrivePattern,
    KartesianDrivePattern,
    HitBoxTank,
)

from tkinter import (
    END,
    ttk,
    Button,
    Label,
    Entry,
    Menu,
    Scale,
    Text,
    Tk,
    Toplevel,
    filedialog,
)

from ender5control import (
    x_y_home,
    x_y_center,
    turn_off_fan,
    move_to_absolute_x,
    move_to_absolute_y,
    move_to_absolute_z,
    move_to_absolute_x_y,
    available_serial_ports,
    compute_abs_x_y_from_r_phi,
    compute_abs_x_y_from_x_y,
    calculate_moving_time,
    read_temperature,  # TBD
)

"""
Tasks:
-> "run_meas_script" mit json o.ae. ansteuern.
-> Geschwindigkeitstest für Messungen
-> Aufteilung eines BurstCount >1 Skript in einzelne Messungen
-> reshape_measurement_buffer() funktioniert noch nicht im erstgenannten Skript.
-> Anpassen der GUI auf Grund der "call" umstände
"""


""" Read resolution and set for visualization. """

monitor = get_monitors()

if type(monitor) == list:
    monitor = monitor[0]

print(monitor)

op_system = OperatingSystem(
    system=str(platform.system()),
    resolution_width=int(monitor.width),
    resolution_height=int(monitor.height),
)

print(op_system)

if op_system.resolution_width == 3840 or op_system.resolution_height == 3840:
    print("4k system. Setting rcParams to font size = 6.")
    plt.rcParams["font.size"] = 5
else:
    plt.rcParams["font.size"] = 9
plt.rcParams["figure.autolayout"] = True

""" Constant design/layout values"""

x_0ff = 200
y_0ff = 160
spacer = 20
btn_width = 50
btn_height = 50


""" Functions and Classes """


class Log:
    def __init__(self, app) -> None:
        self.log = Text(app, height=10, width=100)
        self.log.place(x=10, y=590, width=500, height=200)

        self.clear_button = Button(
            app, text="Clear Log", command=self.clear_log
        )
        self.clear_button.place(x=520, y=740, height=50, width=150)

    def write(self, text):
        self.log.insert(END, text)

    def flush(self):
        pass

    def clear_log(self):
        self.log.delete("1.0", END)


detected_com_ports = available_serial_ports()  # ["COM3", "COM4"]
tank_architectures = ["select tank", "medium", "high"]
object_architectures = ["none", "circle", "triangle", "square"]
object_sizes = [0.1, 0.2, 0.3, 0.4]
n_el_possibilities = [16, 32, 48, 64]
step_width = [0.1, 1, 10]

center_x_y = 180
center_z = 0


scio_spec_measurement_config = ScioSpecMeasurementConfig(
    com_port="COM3",
    burst_count=10,
    n_el=16,
    channel_group=[1],
    actual_sample=0,
    s_path="tmp_data/",  # TBD: Select savepath with seperate window!
    object="circle",
    size=0.0,
    material="/",
    saline_conductivity=0.0,
    temperature=0.0,
    water_lvl=0.0,
    exc_freq=10000.0,
    datetime=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
)


manual_step = mmPerStep(10)


# First Initialization
enderstat = Ender5Stat(
    abs_x_pos=350,
    abs_y_pos=350,
    abs_z_pos=0,
    tank_architecture=None,
    motion_speed=1500,
    abs_x_tgt=None,
    abs_y_tgt=None,
    abs_z_tgt=None,
)


circledrivepattern = CircleDrivePattern(
    active=False,
    wait_at_pos=1,  # time to wait in [s]
    radius=100,
    phi_steps=10,
    abs_x_posis=np.zeros(1),
    abs_y_posis=np.zeros(1),
    abs_z_posis=enderstat.abs_z_pos,
    motion_speed=enderstat.motion_speed,
    n_points=0,
    actual_point=0,
)

hit_box_tank = HitBoxTank(
    tank_architecture=None,
    z_lim_height=200,
    r_max=85,
)

kartesiandrivepattern = KartesianDrivePattern(
    active=False,
    wait_at_pos=1,
    motion_speed=enderstat.motion_speed,
    x_start=160,
    y_start=160,
    x_stop=center_x_y,
    y_stop=center_x_y,
    x_stp_num=10,
    y_stp_num=10,
    abs_x_posis=np.zeros(1),
    abs_y_posis=np.zeros(1),
    abs_z_posis=enderstat.abs_z_pos,
    n_points=0,
    actual_point=0,
)


class ConnectEnder5:
    """
    The initialization has to be added here.
    init_ender5 function -> Move to center/home, whatever and inserts the positional date inside the corresponding dataclass
    """

    def __init__(self, app) -> None:
        self.com_dropdown_ender = ttk.Combobox(values=detected_com_ports)
        self.com_dropdown_ender.bind(
            "<<ComboboxSelected>>", self.dropdown_callback
        )
        self.com_dropdown_ender.place(
            x=spacer, y=spacer, width=btn_width + spacer, height=btn_height
        )

        self.connect_interact_button = Button(
            app,
            text="Connect Ender 5",
            bg="#FBC86C",
            state="disabled",
            command=self.connect_interact,
        )
        self.connect_interact_button.place(
            x=3 * spacer + btn_width,
            y=spacer,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def dropdown_callback(self, event=None):
        if event:
            print(
                "dropdown opened and selected:", self.com_dropdown_ender.get()
            )
            self.connect_interact_button["state"] = "normal"
        else:
            pass

    def connect_interact(self):
        global enderstat, COM_Ender

        self.connect_interact_button["text"] = "Connecting ..."
        print(
            "Connection to ",
            str(self.com_dropdown_ender.get()),
            "established.",
        )
        try:
            COM_Ender = serial.Serial(self.com_dropdown_ender.get(), 115200)
            time.sleep(1)
            # if condition, if serial connection is established !!!
            self.connect_interact_button["text"] = "Connection established"
            self.connect_interact_button["bg"] = "green"
            self.connect_interact_button["fg"] = "black"
            self.connect_interact_button["state"] = "disabled"
            self.com_dropdown_ender["state"] = "disabled"
            # Init routine
            turn_off_fan(COM_Ender)
            enderstat.abs_x_tgt = 0
            enderstat.abs_y_tgt = 0
            plot(enderstat)
            time.sleep(1)
            print("move home")
            x_y_home(COM_Ender, enderstat)
            enderstat.abs_x_pos = enderstat.abs_x_tgt
            enderstat.abs_y_pos = enderstat.abs_y_tgt
            enderstat.abs_y_tgt = center_x_y
            enderstat.abs_x_tgt = center_x_y
            plot(enderstat)
            x_y_center(COM_Ender, enderstat)
            enderstat.abs_x_pos = enderstat.abs_x_tgt
            enderstat.abs_y_pos = enderstat.abs_y_tgt
            enderstat.abs_x_tgt = None
            enderstat.abs_y_tgt = None
            print("Initialization done.")

        except BaseException:
            print("Can not open", self.com_dropdown_ender.get())


class ScioSpecPort:
    def __init__(self, app) -> None:
        self.com_dropdown_sciospec = ttk.Combobox(
            values=detected_com_ports,
        )
        self.com_dropdown_sciospec.bind(
            "<<ComboboxSelected>>", self.dropdown_callback
        )
        self.com_dropdown_sciospec.place(
            x=spacer,
            y=2 * spacer + btn_height,
            width=btn_width + spacer,
            height=btn_height,
        )

    def dropdown_callback(self, event=None):
        if event:
            scio_spec_measurement_config.com_port = (
                self.com_dropdown_sciospec.get()
            )
            print(
                "dropdown opened and selected:",
                scio_spec_measurement_config.com_port,
            )
        else:
            pass


class ScioSpecConfig:
    def __init__(self, app) -> None:
        self.opnen_cnf_window_btn = Button(
            app, text="ScioSpec Config", command=self.config_window
        )
        self.opnen_cnf_window_btn.place(
            x=3 * spacer + btn_width,
            y=2 * spacer + btn_height,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def config_window(self):
        self.sciospec_cnf_wndow = Toplevel(app)
        self.sciospec_cnf_wndow.title("Configure ScioSpec")
        self.sciospec_cnf_wndow.geometry("800x400")

        def open_path_select():
            scio_spec_measurement_config.s_path = (
                filedialog.askdirectory(title="Select save path") + "/"
            )

        def set_sciospec_settings():
            scio_spec_measurement_config.burst_count = int(
                entry_sample_per_step.get()
            )
            scio_spec_measurement_config.n_el = int(n_el_dropdown.get())
            scio_spec_measurement_config.object = objct_dropdown.get()
            scio_spec_measurement_config.size = float(obj_size.get())

            scio_spec_measurement_config.material = material_dropdown.get()
            scio_spec_measurement_config.saline_conductivity = float(
                entry_sline_cond.get(), str(saline_unit.get())
            )
            scio_spec_measurement_config.water_lvl = float(
                entry_water_lvl.get()
            )
            scio_spec_measurement_config.exc_freq = float(etry_exc_freq.get())
            scio_spec_measurement_config.temperature = read_temperature(
                COM_Ender
            )  # Check this

            scio_spec_measurement_config.actual_sample = 0
            print(scio_spec_measurement_config)
            self.sciospec_cnf_wndow.destroy()

        labels = [
            "Burst count:",
            "Save path:",
            "Object:",
            "size:",
            "Electrodes:",
        ]

        for i in range(len(labels)):
            label = Label(self.sciospec_cnf_wndow, text=labels[i], anchor="w")
            label.place(
                x=0, y=i * btn_width, width=2 * btn_width, height=btn_height
            )

        entry_sample_per_step = Entry(self.sciospec_cnf_wndow)
        entry_sample_per_step.place(x=2 * btn_width, y=18, width=4 * btn_width)
        entry_sample_per_step.insert(0, "10")

        label_saline = Label(
            self.sciospec_cnf_wndow, text="Saline conductivity:", anchor="w"
        )
        label_saline.place(
            x=7 * btn_width + spacer,
            y=0,
            width=3 * btn_width,
            height=btn_height,
        )

        entry_sline_cond = Entry(self.sciospec_cnf_wndow)
        entry_sline_cond.place(x=11 * btn_width, y=18, width=2 * btn_width)
        entry_sline_cond.insert(0, "0.0")

        saline_unit = ttk.Combobox(
            self.sciospec_cnf_wndow, values=["S", "mS", "µS"]
        )
        saline_unit.place(x=13 * btn_width, y=18, width=btn_width)
        saline_unit.current(1)

        entry_water_lvl_label = Label(
            self.sciospec_cnf_wndow, text="Water lvl [mm]:", anchor="w"
        )
        entry_water_lvl_label.place(
            x=7 * btn_width + spacer,
            y=btn_height - 15,
            width=3 * btn_width,
            height=btn_height,
        )
        entry_water_lvl = Entry(self.sciospec_cnf_wndow)
        entry_water_lvl.place(
            x=11 * btn_width, y=btn_height, width=2 * btn_width
        )

        etry_exc_freq_label = Label(
            self.sciospec_cnf_wndow, text="Excitation freq. [HZ]:", anchor="w"
        )
        etry_exc_freq_label.place(
            x=7 * btn_width + spacer,
            y=2 * btn_height,
            width=3 * btn_width + spacer,
            height=btn_height,
        )

        etry_exc_freq = Entry(self.sciospec_cnf_wndow)
        etry_exc_freq.place(
            x=11 * btn_width, y=2 * btn_height + 9, width=2 * btn_width
        )
        etry_exc_freq.insert(0, "10000")

        btn_save_path = Button(
            self.sciospec_cnf_wndow, text="Select", command=open_path_select
        )
        btn_save_path.place(x=2 * btn_width, y=btn_height, height=btn_height)

        objct_dropdown = ttk.Combobox(
            self.sciospec_cnf_wndow, values=object_architectures
        )
        objct_dropdown.current(0)
        objct_dropdown.place(
            x=2 * btn_width, y=2 * btn_height + 18, width=4 * btn_width
        )

        material_dropdown_label = Label(
            self.sciospec_cnf_wndow, text="Material:", anchor="w"
        )
        material_dropdown_label.place(
            x=7 * btn_width + spacer,
            y=3 * btn_height,
            width=3 * btn_width,
            height=btn_height,
        )
        material_dropdown = ttk.Combobox(
            self.sciospec_cnf_wndow, values=["PLA", "Conductor"]
        )
        material_dropdown.place(
            x=11 * btn_width, y=3 * btn_height + 18, width=2 * btn_width
        )
        material_dropdown.current(0)

        obj_size = ttk.Combobox(self.sciospec_cnf_wndow, values=object_sizes)
        obj_size.place(
            x=2 * btn_width, y=3 * btn_height + 18, width=4 * btn_width
        )

        n_el_dropdown = ttk.Combobox(
            self.sciospec_cnf_wndow, values=n_el_possibilities
        )
        n_el_dropdown.place(
            x=2 * btn_width, y=4 * btn_height + 18, width=4 * btn_width
        )
        n_el_dropdown.current(0)

        btn_set_all = Button(
            self.sciospec_cnf_wndow,
            text="Set all selections",
            command=set_sciospec_settings,
        )
        btn_set_all.place(x=2 * btn_width, y=5 * btn_height, height=btn_height)


class TankSelect:
    def __init__(self) -> None:
        self.tnk_dropdown = ttk.Combobox(values=tank_architectures)
        self.tnk_dropdown.current(0)
        self.tnk_dropdown.bind("<<ComboboxSelected>>", self.dropdown_callback)
        self.tnk_dropdown.place(
            x=3 * spacer + btn_width + x_0ff,
            y=spacer,
            width=2 * btn_width + 2 * spacer,
            height=btn_height,
        )

    def dropdown_callback(self, event=None):
        if event:
            tnk = self.tnk_dropdown.get()
            print(tnk, "tank selected.")
            enderstat.tank_architecture = tnk
            hit_box_tank.tank_architecture = tnk
            print("Sinking z level.")
            if tnk == "medium":
                enderstat.abs_z_tgt = 0
            if tnk == "high":
                enderstat.abs_z_tgt = 100
            if tnk == "select tank":
                hit_box_tank.tank_architecture = None
                enderstat.abs_z_tgt = enderstat.abs_z_pos
            move_to_absolute_z(COM_Ender, enderstat)
            enderstat.abs_z_pos = enderstat.abs_z_tgt
            enderstat.abs_z_tgt = None
            plot(enderstat)
        else:
            pass


class StepWidthSelect:
    # global mm_per_step

    def __init__(self, app) -> None:
        self.stp_wdth_dropdown = ttk.Combobox(values=step_width)
        self.stp_wdth_dropdown.current(2)
        self.stp_wdth_dropdown.bind(
            "<<ComboboxSelected>>", self.dropdown_callback
        )
        self.stp_wdth_dropdown.place(
            x=x_0ff + 4 * btn_width + 3 * spacer,
            y=spacer,
            width=btn_width,
            height=btn_height,
        )
        self.mm_ps_label = Label(app, text="mm/step")
        self.mm_ps_label.place(
            x=x_0ff + 5 * btn_width + 3 * spacer,
            y=spacer,
            width=btn_width,
            height=btn_height,
        )

    def dropdown_callback(self, event=None):
        if event:
            manual_step.mm_per_step = float(self.stp_wdth_dropdown.get())
            print("Distance per step:", manual_step.mm_per_step)
        else:
            pass


class MovementXYZ:
    def __init__(self, app) -> None:
        self.x_set_btn = Button(app, text="Set x=", command=self.set_x)
        self.x_set_btn.place(
            x=spacer, y=y_0ff, width=btn_width, height=btn_height
        )
        self.x_set_entry = Entry(app)
        self.x_set_entry.place(
            x=2 * spacer + btn_width,
            y=y_0ff,
            width=btn_width,
            height=btn_height,
        )
        self.x_set_unit = Label(app, text="mm").place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff,
            width=btn_width // 2,
            height=btn_height,
        )

        self.y_set_btn = Button(app, text="Set y=", command=self.set_y)
        self.y_set_btn.place(
            x=spacer,
            y=y_0ff + btn_height + spacer,
            width=btn_width,
            height=btn_height,
        )
        self.y_set_entry = Entry(app)
        self.y_set_entry.place(
            x=2 * spacer + btn_width,
            y=y_0ff + btn_height + spacer,
            width=btn_width,
            height=btn_height,
        )
        self.y_set_unit = Label(app, text="mm").place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff + btn_height + spacer,
            width=btn_width // 2,
            height=btn_height,
        )

        self.z_set_btn = Button(app, text="Set z=", command=self.set_z)
        self.z_set_btn.place(
            x=spacer,
            y=y_0ff + 2 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.z_set_entry = Entry(app)
        self.z_set_entry.place(
            x=2 * spacer + btn_width,
            y=y_0ff + 2 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.z_set_unit = Label(app, text="mm").place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff + 2 * btn_height + 2 * spacer,
            width=btn_width // 2,
            height=btn_height,
        )

        self.y_up_btn = Button(app, text="y+", command=self.move_y_up)
        self.y_up_btn.place(
            x=x_0ff + btn_width + spacer,
            y=y_0ff,
            width=btn_width,
            height=btn_height,
        )

        self.y_down_btn = Button(app, text="y-", command=self.move_y_down)
        self.y_down_btn.place(
            x=x_0ff + btn_width + spacer,
            y=y_0ff + 2 * spacer + 2 * btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.x_y_center_btn = Button(
            app, text="center\nx,y", command=self.x_y_center
        )
        self.x_y_center_btn.place(
            x=x_0ff + btn_width + spacer,
            y=y_0ff + spacer + btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.x_up_btn = Button(app, text="x-", command=self.move_x_down)
        self.x_up_btn.place(
            x=x_0ff,
            y=y_0ff + spacer + btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.x_down_btn = Button(app, text="x+", command=self.move_x_up)
        self.x_down_btn.place(
            x=x_0ff + 2 * btn_width + 2 * spacer,
            y=y_0ff + spacer + btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.z_up_btn = Button(app, text="z+", command=self.move_z_up)
        self.z_up_btn.place(
            x=x_0ff + 4 * btn_width + spacer,
            y=y_0ff,
            width=btn_width,
            height=btn_height,
        )

        self.z_center_btn = Button(
            app, text="center\nz", command=self.z_center
        )
        self.z_center_btn.place(
            x=x_0ff + 4 * btn_width + spacer,
            y=y_0ff + spacer + btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.z_down_btn = Button(app, text="z-", command=self.move_z_down)
        self.z_down_btn.place(
            x=x_0ff + 4 * btn_width + spacer,
            y=y_0ff + 2 * spacer + 2 * btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.motion_speed = Scale(
            app,
            from_=1500,
            to=100,
            tickinterval=200,
            orient="vertical",
        )
        self.motion_speed.set(1500)
        self.motion_speed.bind("<ButtonRelease-1>", self.motion_speed_callback)
        self.motion_speed.place(
            x=x_0ff + 5 * btn_width + 2 * spacer,
            y=y_0ff,
            height=3 * btn_height + 2 * spacer,
            width=2 * btn_width,
        )
        self.motion_speed_label = Label(
            app, text="M\no\nt\ni\no\nn\n\ns\np\ne\ne\nd"
        )
        self.motion_speed_label.place(
            x=x_0ff + 7 * btn_width + 2 * spacer,
            y=y_0ff,
            height=3 * btn_height + 2 * spacer,
            width=btn_width // 2,
        )

    def set_x(self):
        enderstat.abs_x_tgt = float(self.x_set_entry.get())
        plot(enderstat)
        move_to_absolute_x(COM_Ender, enderstat)
        enderstat.abs_x_pos = enderstat.abs_x_tgt
        enderstat.abs_x_tgt = None
        plot(enderstat)

    def set_y(self):
        enderstat.abs_y_tgt = float(self.y_set_entry.get())
        plot(enderstat)
        move_to_absolute_y(COM_Ender, enderstat)
        enderstat.abs_y_pos = enderstat.abs_y_tgt
        enderstat.abs_y_tgt = None
        plot(enderstat)

    def set_z(self):
        enderstat.abs_z_tgt = float(self.z_set_entry.get())
        plot(enderstat)
        move_to_absolute_z(COM_Ender, enderstat)
        enderstat.abs_z_pos = enderstat.abs_z_tgt
        enderstat.abs_z_tgt = None
        plot(enderstat)

    def x_y_center(self):
        enderstat.abs_x_tgt = center_x_y
        enderstat.abs_y_tgt = center_x_y
        plot(enderstat)
        move_to_absolute_x_y(COM_Ender, enderstat)
        enderstat.abs_x_pos = enderstat.abs_x_tgt
        enderstat.abs_y_pos = enderstat.abs_y_tgt
        enderstat.abs_x_tgt = None
        enderstat.abs_y_tgt = None

    def move_x_up(self):
        enderstat.abs_x_tgt = enderstat.abs_x_pos + manual_step.mm_per_step
        plot(enderstat)
        move_to_absolute_x(COM_Ender, enderstat)
        enderstat.abs_x_pos = enderstat.abs_x_tgt
        enderstat.abs_x_tgt = None
        plot(enderstat)

    def move_x_down(self):
        enderstat.abs_x_tgt = enderstat.abs_x_pos - manual_step.mm_per_step
        plot(enderstat)
        move_to_absolute_x(COM_Ender, enderstat)
        enderstat.abs_x_pos = enderstat.abs_x_tgt
        enderstat.abs_x_tgt = None
        plot(enderstat)

    def move_y_up(self):
        print(type(enderstat.motion_speed))
        enderstat.abs_y_tgt = enderstat.abs_y_pos + manual_step.mm_per_step
        print("2", type(enderstat.motion_speed))
        plot(enderstat)
        move_to_absolute_y(COM_Ender, enderstat)
        enderstat.abs_y_pos = enderstat.abs_y_tgt
        enderstat.abs_y_tgt = None
        plot(enderstat)

    def move_y_down(self):
        enderstat.abs_y_tgt = enderstat.abs_y_pos - manual_step.mm_per_step
        plot(enderstat)
        move_to_absolute_y(COM_Ender, enderstat)
        enderstat.abs_y_pos = enderstat.abs_y_tgt
        enderstat.abs_y_tgt = None
        plot(enderstat)

    def move_z_up(self):
        enderstat.abs_z_tgt = enderstat.abs_z_pos - manual_step.mm_per_step
        if enderstat.abs_z_tgt >= 0:
            plot(enderstat)
            move_to_absolute_z(COM_Ender, enderstat)
            enderstat.abs_z_pos = enderstat.abs_z_tgt
            enderstat.abs_z_tgt = None
            plot(enderstat)
        else:
            print("\tcollision prevented")

    def move_z_down(self):
        enderstat.abs_z_tgt = enderstat.abs_z_pos + manual_step.mm_per_step
        plot(enderstat)
        move_to_absolute_z(COM_Ender, enderstat)
        enderstat.abs_z_pos = enderstat.abs_z_tgt
        enderstat.abs_z_tgt = None
        plot(enderstat)

    def z_center(self):
        enderstat.abs_z_tgt = center_z
        plot(enderstat)
        move_to_absolute_z(COM_Ender, enderstat)
        enderstat.abs_z_pos = enderstat.abs_z_tgt
        enderstat.abs_z_tgt = None
        plot(enderstat)

    def motion_speed_callback(self, event):
        enderstat.motion_speed = float(self.motion_speed.get())
        print(
            "Set motion speed to", float(self.motion_speed.get()), "[mm/min]"
        )


class CreateCircularTrajectory:
    def __init__(self, app) -> None:
        self.traj_label = Label(
            app, text="Create a circular trajectory around the center point."
        )
        self.traj_label.place(
            x=spacer,
            y=y_0ff + 4 * btn_height + spacer,
            width=x_0ff + 4 * btn_width,
            height=btn_height,
        )
        self.traj_info_dialog = Button(
            app, text="Info", command=action_get_info_dialog_traj
        )
        self.traj_info_dialog.place(
            x=x_0ff + 4 * btn_width + spacer,
            y=y_0ff + 4 * btn_height + 1 * spacer,
            width=btn_width,
            height=btn_height,
        )

        self.radius_entry = Entry(app)
        self.radius_entry.place(
            x=spacer,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.radius_unit = Label(app, text="mm").place(
            x=spacer + btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width // 2,
            height=btn_height,
        )
        self.phi_entry = Entry(app)
        self.phi_entry.place(
            x=2 * spacer + btn_width + btn_width // 2,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.phi_unit = Label(app, text="°/step").place(
            x=2 * spacer + 2 * btn_width + btn_width // 2,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width + btn_width // 2,
            height=btn_height,
        )

        self.compute_trajectory_btn = Button(
            app, text="Set", command=self.compute_trajectory
        )
        self.compute_trajectory_btn.place(
            x=3 * spacer + 4 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )

    def compute_trajectory(self):
        """Computes rajectory"""
        kartesiandrivepattern.active = False
        circledrivepattern.radius = int(self.radius_entry.get())
        circledrivepattern.phi_steps = int(self.phi_entry.get())
        next_auto_drive.next_step_btn["state"] = "normal"
        next_auto_drive.auto_step_btn["state"] = "normal"
        next_auto_drive.reset_trajectory_btn["state"] = "normal"

        circledrivepattern.active = True
        circledrivepattern.wait_at_pos = 1
        x, y = compute_abs_x_y_from_r_phi(
            circledrivepattern.radius, circledrivepattern.phi_steps
        )
        if circledrivepattern.n_points == 0:
            circledrivepattern.abs_x_posis = x
            circledrivepattern.abs_y_posis = y
            circledrivepattern.abs_z_posis = enderstat.abs_z_pos
            circledrivepattern.n_points += len(x)
        else:
            circledrivepattern.abs_x_posis = np.concatenate(
                (circledrivepattern.abs_x_posis, x)
            )
            circledrivepattern.abs_y_posis = np.concatenate(
                (circledrivepattern.abs_y_posis, y)
            )
            circledrivepattern.abs_z_posis = enderstat.abs_z_pos
            circledrivepattern.n_points = circledrivepattern.n_points + len(x)
            print("circledrivepattern.n_points", circledrivepattern.n_points)
        circledrivepattern.motion_speed = enderstat.motion_speed
        plot(enderstat, circledrivepattern, kartesiandrivepattern)
        save_cnf_file()


class NextAutoDriveResetMeasure:
    def __init__(self, app) -> None:
        self.next_step_btn = Button(
            app,
            text="Next step",
            command=self.next_trajectory_step,
            state="disabled",
        )
        self.next_step_btn.place(
            x=spacer,
            y=y_0ff + 6 * btn_height + 3 * spacer,
            width=2 * btn_width,
            height=btn_height,
        )

        self.auto_step_btn = Button(
            app,
            text="Auto drive",
            command=self.auto_trajectory_drive,
            state="disabled",
        )
        self.auto_step_btn.place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff + 6 * btn_height + 3 * spacer,
            width=2 * btn_width,
            height=btn_height,
        )

        self.reset_trajectory_btn = Button(
            app, text="Reset", command=self.reset_trajectory, state="disabled"
        )
        self.reset_trajectory_btn.place(
            x=3 * spacer + 4 * btn_width,
            y=y_0ff + 6 * btn_height + 3 * spacer,
            width=btn_width,
            height=btn_height,
        )

        self.measure_btn = Button(
            app, text="Measure", command=single_measurement
        )
        self.measure_btn.place(
            x=4 * spacer + 5 * btn_width,
            y=y_0ff + 6 * btn_height + 3 * spacer,
            width=2 * btn_width,
            height=btn_height,
        )

    def next_trajectory_step(self) -> None:
        if circledrivepattern.active is True:
            print(circledrivepattern.actual_point)
            enderstat.abs_x_tgt = circledrivepattern.abs_x_posis[0]
            enderstat.abs_y_tgt = circledrivepattern.abs_y_posis[0]
            move_to_absolute_x_y(COM_Ender, enderstat)
            print("Wait:", calculate_moving_time(enderstat))
            time.sleep(calculate_moving_time(enderstat))
            circledrivepattern.abs_x_posis = circledrivepattern.abs_x_posis[1:]
            circledrivepattern.abs_y_posis = circledrivepattern.abs_y_posis[1:]
            enderstat.abs_x_pos = enderstat.abs_x_tgt
            enderstat.abs_y_pos = enderstat.abs_y_tgt
            # plot(enderstat, circledrivepattern, kartesiandrivepattern)
            circledrivepattern.actual_point += 1

        if kartesiandrivepattern.active is True:
            print(kartesiandrivepattern.actual_point)
            enderstat.abs_x_tgt = kartesiandrivepattern.abs_x_posis[0]
            enderstat.abs_y_tgt = kartesiandrivepattern.abs_y_posis[0]
            move_to_absolute_x_y(COM_Ender, enderstat)
            print("Wait:", calculate_moving_time(enderstat))
            time.sleep(calculate_moving_time(enderstat))
            kartesiandrivepattern.abs_x_posis = (
                kartesiandrivepattern.abs_x_posis[1:]
            )
            kartesiandrivepattern.abs_y_posis = (
                kartesiandrivepattern.abs_y_posis[1:]
            )
            enderstat.abs_x_pos = enderstat.abs_x_tgt
            enderstat.abs_y_pos = enderstat.abs_y_tgt
            # plot(enderstat, circledrivepattern, kartesiandrivepattern)
            kartesiandrivepattern.actual_point += 1
        # Measurement:
        single_measurement()

    def reset_trajectory(self) -> None:
        circledrivepattern.active = False
        kartesiandrivepattern.active = False

        circledrivepattern.abs_x_posis = []
        circledrivepattern.abs_y_posis = []
        circledrivepattern.abs_z_posis = []
        circledrivepattern.n_points = 0

        kartesiandrivepattern.abs_x_posis = []
        kartesiandrivepattern.abs_y_posis = []
        kartesiandrivepattern.abs_z_posis = []
        kartesiandrivepattern.n_points = 0

        plot(enderstat, circledrivepattern, kartesiandrivepattern)
        self.auto_step_btn["state"] = "disabled"
        self.next_step_btn["state"] = "disabled"
        self.reset_trajectory_btn["state"] = "disabled"

    def auto_trajectory_drive(self) -> None:
        if circledrivepattern.active is True:
            if telegram_config["state"]:
                for _ in trange(
                    circledrivepattern.n_points,
                    token=telegram_config["token"],
                    chat_id=telegram_config["chat_id"],
                ):
                    time.sleep(circledrivepattern.wait_at_pos)
                    self.next_trajectory_step()
                    time.sleep(circledrivepattern.wait_at_pos)
            else:
                while len(circledrivepattern.abs_x_posis) != 0:
                    time.sleep(circledrivepattern.wait_at_pos)
                    self.next_trajectory_step()
                    time.sleep(circledrivepattern.wait_at_pos)
        if kartesiandrivepattern.active is True:
            if telegram_config["state"]:
                for _ in trange(
                    kartesiandrivepattern.n_points,
                    token=telegram_config["token"],
                    chat_id=telegram_config["chat_id"],
                ):
                    time.sleep(kartesiandrivepattern.wait_at_pos)
                    self.next_trajectory_step()
                    time.sleep(kartesiandrivepattern.wait_at_pos)
            else:
                while len(kartesiandrivepattern.abs_x_posis) != 0:
                    time.sleep(kartesiandrivepattern.wait_at_pos)
                    self.next_trajectory_step()
                    time.sleep(kartesiandrivepattern.wait_at_pos)


class CreateKartesianTrajectory:
    def __init__(self, app) -> None:
        self.traj_label = Label(app, text="Create a kartesian trajectory.")
        self.traj_label.place(
            x=2 * spacer + x_0ff + 5 * btn_width,
            y=y_0ff + 4 * btn_height + spacer,
            width=x_0ff + 3 * btn_width + spacer,
            height=btn_height,
        )
        self.traj_info_dialog = Button(
            app, text="Info", command=action_get_info_dialog_kat_traj
        )
        self.traj_info_dialog.place(
            x=5 * spacer + x_0ff + 11 * btn_width,
            y=y_0ff + 4 * btn_height + 1 * spacer,
            width=btn_width,
            height=btn_height,
        )

        self.x_start = Entry(app)
        self.x_start.place(
            x=2 * spacer + x_0ff + 5 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.x_start_unit = Label(app, text="x-start").place(
            x=2 * spacer + x_0ff + 6 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )

        self.x_stop = Entry(app)
        self.x_stop.place(
            x=2 * spacer + x_0ff + 5 * btn_width,
            y=y_0ff + 5 * btn_height + btn_height // 2 + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.x_stop_unit = Label(app, text="x-stop").place(
            x=2 * spacer + x_0ff + 6 * btn_width,
            y=y_0ff + 5 * btn_height + btn_height // 2 + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.y_start = Entry(app)
        self.y_start.place(
            x=3 * spacer + x_0ff + 7 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.y_start_unit = Label(app, text="y-start").place(
            x=3 * spacer + x_0ff + 8 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )

        self.y_stop = Entry(app)
        self.y_stop.place(
            x=3 * spacer + x_0ff + 7 * btn_width,
            y=y_0ff + 5 * btn_height + btn_height // 2 + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.y_stop_unit = Label(app, text="y-stop").place(
            x=3 * spacer + x_0ff + 8 * btn_width,
            y=y_0ff + 5 * btn_height + btn_height // 2 + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.x_step = Entry(app)
        self.x_step.place(
            x=4 * spacer + x_0ff + 9 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.x_step_unit = Label(app, text="x-steps").place(
            x=4 * spacer + x_0ff + 10 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )

        self.y_step = Entry(app)
        self.y_step.place(
            x=4 * spacer + x_0ff + 9 * btn_width,
            y=y_0ff + 5 * btn_height + btn_height // 2 + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.y_step_unit = Label(app, text="y-steps").place(
            x=4 * spacer + x_0ff + 10 * btn_width,
            y=y_0ff + 5 * btn_height + btn_height // 2 + 2 * spacer,
            width=btn_width,
            height=btn_height // 2,
        )
        self.compute_trajectory_btn = Button(
            app, text="Set", command=self.compute_trajectory
        )
        self.compute_trajectory_btn.place(
            x=5 * spacer + x_0ff + 11 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )

    def compute_trajectory(self):
        """Computes rajectory"""
        circledrivepattern.active = False
        kartesiandrivepattern.active = True

        kartesiandrivepattern.x_start = int(self.x_start.get())
        kartesiandrivepattern.y_start = int(self.y_start.get())
        kartesiandrivepattern.x_stop = int(self.x_stop.get())
        kartesiandrivepattern.y_stop = int(self.y_stop.get())
        kartesiandrivepattern.x_stp_num = int(self.x_step.get())
        kartesiandrivepattern.y_stp_num = int(self.y_step.get())
        next_auto_drive.next_step_btn["state"] = "normal"
        next_auto_drive.auto_step_btn["state"] = "normal"
        next_auto_drive.reset_trajectory_btn["state"] = "normal"

        circledrivepattern.wait_at_pos = 1
        x, y = compute_abs_x_y_from_x_y(
            kartesiandrivepattern.x_start,
            kartesiandrivepattern.y_start,
            kartesiandrivepattern.x_stop,
            kartesiandrivepattern.y_stop,
            kartesiandrivepattern.x_stp_num,
            kartesiandrivepattern.y_stp_num,
            hit_box_tank,
        )
        kartesiandrivepattern.abs_x_posis = x
        kartesiandrivepattern.abs_y_posis = y
        kartesiandrivepattern.abs_z_posis = enderstat.abs_z_pos
        kartesiandrivepattern.n_points = len(x)
        kartesiandrivepattern.motion_speed = enderstat.motion_speed
        plot(enderstat, circledrivepattern, kartesiandrivepattern)
        save_cnf_file()


def plot_empty(
    enderstat: Ender5Stat,
    cdp: CircleDrivePattern = circledrivepattern,
    kdp: KartesianDrivePattern = kartesiandrivepattern,
) -> None:
    pass


def plot(
    enderstat: Ender5Stat,
    cdp: CircleDrivePattern = circledrivepattern,
    kdp: KartesianDrivePattern = kartesiandrivepattern,
) -> None:
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 5))

    ax1.set_title("Top view")
    if enderstat.tank_architecture is not None:
        if enderstat.tank_architecture == "select tank":
            circle = Circle(
                (center_x_y, center_x_y),
                radius=1,
                color="lightsteelblue",
                alpha=0,
            )
            ax1.add_artist(circle)
        else:
            circle = Circle(
                (center_x_y, center_x_y),
                radius=100,
                color="lightsteelblue",
                alpha=0.7,
            )
            ax1.add_artist(circle)

    ax1.scatter(
        enderstat.abs_x_pos, enderstat.abs_y_pos, marker=".", label="Currently"
    )
    if enderstat.abs_x_tgt is not None or enderstat.abs_y_tgt is not None:
        ax1.scatter(
            enderstat.abs_x_tgt,
            enderstat.abs_y_tgt,
            marker="*",
            s=10,
            label="Targets",
        )
        ax1.legend()
    if cdp.active is True:
        ax1.scatter(
            cdp.abs_x_posis, cdp.abs_y_posis, marker="*", s=10, label="Targets"
        )
        ax1.legend()
    if kdp.active is True:
        ax1.scatter(
            kdp.abs_x_posis, kdp.abs_y_posis, marker="*", s=10, label="Targets"
        )
        ax1.legend()
    ax1.set_ylabel("absolute y[mm]")
    ax1.set_xlabel("absolute x[mm]")
    ax1.set_xlim((0, 350))
    ax1.set_ylim((0, 350))
    ax1.grid()
    if enderstat.abs_x_pos == center_x_y and enderstat.abs_y_pos == center_x_y:
        ax1.vlines(
            center_x_y, 0, 500, linestyles="dotted", color="black", alpha=0.5
        )
        ax1.hlines(
            center_x_y, 0, 500, linestyles="dotted", color="black", alpha=0.5
        )

    ax2.set_title("Front view")

    if enderstat.tank_architecture is not None:
        if enderstat.tank_architecture == "medium":
            tank_archtctrs = [
                Rectangle(
                    (75, hit_box_tank.z_lim_height - enderstat.abs_z_pos),
                    width=200,
                    height=150,
                )
            ]
            pc = PatchCollection(
                tank_archtctrs,
                facecolor="lightsteelblue",
                alpha=0.7,
                edgecolor="black",
            )
            ax2.add_collection(pc)
        if enderstat.tank_architecture == "high":
            tank_archtctrs = [
                Rectangle(
                    (75, hit_box_tank.z_lim_height - enderstat.abs_z_pos),
                    width=200,
                    height=200,
                )
            ]
            pc = PatchCollection(
                tank_archtctrs,
                facecolor="lightsteelblue",
                alpha=0.7,
                edgecolor="black",
            )
            ax2.add_collection(pc)
        if enderstat.tank_architecture == "select tank":
            tank_archtctrs = [
                Rectangle((0, 0), width=0, height=0)
            ]  # delete tank
            pc = PatchCollection(
                tank_archtctrs,
                facecolor="lightsteelblue",
                alpha=0.7,
                edgecolor="black",
            )
            ax2.add_collection(pc)

    ax2.hlines(
        hit_box_tank.z_lim_height - enderstat.abs_z_pos,
        50,
        300,
        linestyles="solid",
        color="black",
        label="z-table",
    )
    if enderstat.abs_z_tgt is not None:
        ax2.hlines(
            enderstat.abs_z_tgt,
            100,
            225,
            linestyles="solid",
            color="black",
            label="z-table",
        )
    ax2.set_ylabel("absolute z[mm]")
    ax2.set_yticks(np.arange(0, 401, 50)[::-1])
    ax2.set_yticklabels(np.arange(0, 401, 50))
    ax2.set_xlabel("absolute x[mm]")
    ax2.set_xlim((0, 350))
    ax2.set_ylim((0, 400))
    ax2.grid()
    ax2.legend()
    # ax2.hlines(center_x_y, 0, hit_box_tank.z_lim_height, linestyles="dotted", color="black")

    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().place(x=950, y=0, width=400, height=800)
    plt.close(fig)


def save_cnf_file() -> None:
    with open("meas_cnf.pkl", "wb") as f:
        tmp_conf = [
            scio_spec_measurement_config,
            circledrivepattern,
            kartesiandrivepattern,
            enderstat,
        ]
        pickle.dump(tmp_conf, f)
    print("Saved meas_cnf.pkl")


def single_measurement() -> None:
    """
    Start measurement script:
    -> Measurement at the current enderstat position.
    """
    scio_spec_measurement_config.temperature = read_temperature(COM_Ender)
    scio_spec_measurement_config.datetime = (
        datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    )
    save_cnf_file()
    call(["python", "run_meas_prototype.py"])


grid_dict = {"sticky": "we", "ipadx": "10"}

"""Main Init"""
app = Tk()
app.title("Ender 5 Interface")
app.configure(background="#1A5175")
app.grid()

app.iconbitmap("../images/ico/ico_sciopy.ico")

connect_ender_5 = ConnectEnder5(app)
connect_sciospec = ScioSpecPort(app)
scio_spec_config = ScioSpecConfig(app)
movement_xyz = MovementXYZ(app)
tankselect = TankSelect()
stepwidthselect = StepWidthSelect(app)
create_circular_trajectory = CreateCircularTrajectory(app)
create_kartesian_trajectory = CreateKartesianTrajectory(app)
next_auto_drive = NextAutoDriveResetMeasure(app)
LOG = Log(app)
sys.stdout = LOG

dropdown = Menu(app)
datei_menu = Menu(dropdown, tearoff=0)
help_menu = Menu(dropdown, tearoff=0)
# datei_menu.add_command(label="Generate save folder", command=gen_save_folder)
datei_menu.add_separator()
datei_menu.add_command(label="Exit", command=app.quit)
help_menu.add_command(label="Info", command=action_get_info_dialog)
dropdown.add_cascade(label="File", menu=datei_menu)
dropdown.add_cascade(label="Help", menu=help_menu)


plot(enderstat)

app.config(menu=dropdown)
app.geometry("1350x800")
app.mainloop()
