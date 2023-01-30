import numpy as np
import time
import sys
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ender_sciospec_classes import Ender5Stat, mmPerStep, CircleDrivePattern

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
    messagebox,
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
)

try:
    import serial
except ImportError:
    print("Could not import module: serial")

plt.rcParams["font.size"] = 9
# if youre monitor resolution is 4k set "plt.rcParams["font.size"]=6"
plt.rcParams["figure.autolayout"] = True
label_settings = {"font": ("Arial", 25), "borderwidth": "10", "background": "lightblue"}


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

        self.clear_button = Button(app, text="Clear Log", command=self.clear_log)
        self.clear_button.place(x=520, y=740, height=50, width=150)

    def write(self, text):
        self.log.insert(END, text)

    def flush(self):
        pass

    def clear_log(self):
        self.log.delete("1.0", END)


detected_com_ports = available_serial_ports()  # ["COM3", "COM4"]
tank_architectures = ["select tank", "medium", "high"]
step_width = [0.1, 1, 10]

center_x_y = 180
center_z = 0


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
    abs_x_posis=compute_abs_x_y_from_r_phi(100, 10)[0],
    abs_y_posis=compute_abs_x_y_from_r_phi(100, 10)[1],
    abs_z_posis=enderstat.abs_z_pos,
    motion_speed=enderstat.motion_speed,
    n_points=len(compute_abs_x_y_from_r_phi(100, 10)[0]),
    actual_point=0,
)


class ConnectEnder5:
    """
    The initialization has to be added here.
    init_ender5 function -> Move to center/home, whatever and inserts the positional date inside the corresponding dataclass
    """

    def __init__(self, app) -> None:

        self.com_dropdown_ender = ttk.Combobox(values=detected_com_ports)
        self.com_dropdown_ender.bind("<<ComboboxSelected>>", self.dropdown_callback)
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
            x=3 * spacer + btn_width, y=spacer, width=x_0ff - spacer, height=btn_height
        )

    def dropdown_callback(self, event=None):
        if event:
            print("dropdown opened and selected:", self.com_dropdown_ender.get())
            self.connect_interact_button["state"] = "normal"
        else:
            pass

    def connect_interact(self):
        global enderstat, COM_Ender

        self.connect_interact_button["text"] = "Connecting ..."
        print("Connection to ", str(self.com_dropdown_ender.get()), "established.")
        try:
            COM_Ender = serial.Serial(self.com_dropdown_ender.get(), 115200)
            time.sleep(1)
            # if condition, if serial connection is established !!!
            self.connect_interact_button["text"] = "Connection established"
            self.connect_interact_button["bg"] = "green"
            self.connect_interact_button["fg"] = "black"
            self.connect_interact_button["state"] = "disabled"
            self.com_dropdown_ender["state"] = "disabled"
            # print(type(COM_Ender))
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


class ConnectScioSpec:
    def __init__(self, app) -> None:
        self.com_dropdown_sciospec = ttk.Combobox(
            values=detected_com_ports,
        )
        self.com_dropdown_sciospec.bind("<<ComboboxSelected>>", self.dropdown_callback)
        self.com_dropdown_sciospec.place(
            x=spacer,
            y=2 * spacer + btn_height,
            width=btn_width + spacer,
            height=btn_height,
        )

        self.connect_interact_button = Button(
            app,
            text="Connect ScioSpec",
            bg="#FBC86C",
            state="disabled",
            command=self.connect_interact,
        )
        self.connect_interact_button.place(
            x=3 * spacer + btn_width,
            y=2 * spacer + btn_height,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def dropdown_callback(self, event=None):
        if event:
            print("dropdown opened and selected:", self.com_dropdown_sciospec.get())
            self.connect_interact_button["state"] = "normal"
        else:
            pass

    def connect_interact(self):

        self.connect_interact_button["text"] = "Connecting ..."
        print("Connection to ", str(self.com_dropdown_sciospec.get()), "established.")
        # if condition, if serial connection is established !!!
        self.connect_interact_button["text"] = "Connection established"
        self.connect_interact_button["bg"] = "green"
        self.connect_interact_button["fg"] = "black"
        self.connect_interact_button["state"] = "disabled"
        self.com_dropdown_sciospec["state"] = "disabled"
        # Probably a callback message from the ScioSpec device.


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
            print("Sinking z level.")
            if tnk == "medium":
                enderstat.abs_z_tgt = 200
            if tnk == "high":
                enderstat.abs_z_tgt = 250
            if tnk == "select tank":
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
        self.stp_wdth_dropdown.bind("<<ComboboxSelected>>", self.dropdown_callback)
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
        self.x_set_btn.place(x=spacer, y=y_0ff, width=btn_width, height=btn_height)
        self.x_set_entry = Entry(app)
        self.x_set_entry.place(
            x=2 * spacer + btn_width, y=y_0ff, width=btn_width, height=btn_height
        )
        self.x_set_unit = Label(app, text="mm").place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff,
            width=btn_width // 2,
            height=btn_height,
        )

        self.y_set_btn = Button(app, text="Set y=", command=self.set_y)
        self.y_set_btn.place(
            x=spacer, y=y_0ff + btn_height + spacer, width=btn_width, height=btn_height
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
            x=x_0ff + btn_width + spacer, y=y_0ff, width=btn_width, height=btn_height
        )

        self.y_down_btn = Button(app, text="y-", command=self.move_y_down)
        self.y_down_btn.place(
            x=x_0ff + btn_width + spacer,
            y=y_0ff + 2 * spacer + 2 * btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.x_y_center_btn = Button(app, text="center\nx,y", command=self.x_y_center)
        self.x_y_center_btn.place(
            x=x_0ff + btn_width + spacer,
            y=y_0ff + spacer + btn_height,
            width=btn_width,
            height=btn_height,
        )

        self.x_up_btn = Button(app, text="x+", command=self.move_x_down)
        self.x_up_btn.place(
            x=x_0ff, y=y_0ff + spacer + btn_height, width=btn_width, height=btn_height
        )

        self.x_down_btn = Button(app, text="x-", command=self.move_x_up)
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

        self.z_center_btn = Button(app, text="center\nz", command=self.z_center)
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
            x=x_0ff + 5 * btn_width + 3 * spacer,
            y=y_0ff,
            height=3 * btn_height + 2 * spacer,
            width=2 * btn_width,
        )
        self.motion_speed_label = Label(app, text="M\no\nt\ni\no\nn\n\ns\np\ne\ne\nd")
        self.motion_speed_label.place(
            x=x_0ff + 7 * btn_width + 3 * spacer,
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
        plot(enderstat)
        move_to_absolute_z(COM_Ender, enderstat)
        enderstat.abs_z_pos = enderstat.abs_z_tgt
        enderstat.abs_z_tgt = None
        plot(enderstat)

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
        print("Set motion speed to", float(self.motion_speed.get()), "[mm/min]")


class CreateCircularTrajectory:
    def __init__(self, app) -> None:
        self.traj_label = Label(
            app, text="Create a circular trajectory around the center point"
        )
        self.traj_label.place(
            x=spacer,
            y=y_0ff + 4 * btn_height + 1 * spacer,
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
        self.phi_unit = Label(app, text="step/360°").place(
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

        self.next_step_btn = Button(
            app, text="Next step", command=self.next_trajectory_step, state="disabled"
        )
        self.next_step_btn.place(
            x=spacer,
            y=y_0ff + 6 * btn_height + 3 * spacer,
            width=2 * btn_width,
            height=btn_height,
        )

        self.auto_step_btn = Button(
            app, text="Auto drive", command=self.auto_trajectory_drive, state="disabled"
        )
        self.auto_step_btn.place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff + 6 * btn_height + 3 * spacer,
            width=2 * btn_width,
            height=btn_height,
        )

    def compute_trajectory(self):
        """Computes rajectory"""
        circledrivepattern.radius = int(self.radius_entry.get())
        circledrivepattern.phi_steps = int(self.phi_entry.get())
        self.next_step_btn["state"] = "normal"
        self.auto_step_btn["state"] = "normal"

        circledrivepattern.active = True
        circledrivepattern.wait_at_pos = 1
        x, y = compute_abs_x_y_from_r_phi(
            circledrivepattern.radius, circledrivepattern.phi_steps
        )
        circledrivepattern.abs_x_posis = x
        circledrivepattern.abs_y_posis = y
        circledrivepattern.abs_z_posis = enderstat.abs_z_pos
        circledrivepattern.motion_speed = enderstat.motion_speed
        plot(enderstat, circledrivepattern)

    def next_trajectory_step(self):
        print(circledrivepattern.actual_point)
        enderstat.abs_x_tgt = circledrivepattern.abs_x_posis[0]
        enderstat.abs_y_tgt = circledrivepattern.abs_y_posis[0]
        move_to_absolute_x_y(COM_Ender, enderstat)
        circledrivepattern.abs_x_posis = circledrivepattern.abs_x_posis[1:]
        circledrivepattern.abs_y_posis = circledrivepattern.abs_y_posis[1:]
        enderstat.abs_x_pos = enderstat.abs_x_tgt
        enderstat.abs_y_pos = enderstat.abs_y_tgt
        plot(enderstat, circledrivepattern)
        circledrivepattern.actual_point += 1

    def auto_trajectory_drive(self):
        while len(circledrivepattern.abs_x_posis) != 0:
            time.sleep(circledrivepattern.wait_at_pos)
            self.next_trajectory_step()
            time.sleep(circledrivepattern.wait_at_pos)
            plot(enderstat, circledrivepattern)


def plot(enderstat: Ender5Stat, cdp: CircleDrivePattern = circledrivepattern) -> None:
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 5))

    ax1.set_title("Top view")
    ax1.scatter(enderstat.abs_x_pos, enderstat.abs_y_pos, marker=".")
    if enderstat.abs_x_tgt is not None or enderstat.abs_y_tgt is not None:
        ax1.scatter(enderstat.abs_x_tgt, enderstat.abs_y_tgt, marker="*")
    if cdp.active is True:
        ax1.scatter(cdp.abs_x_posis, cdp.abs_y_posis, marker="*")
    ax1.set_ylabel("absolute y[mm]")
    ax1.set_xlabel("absolute x[mm]")
    ax1.set_xlim((0, 350))
    ax1.set_ylim((0, 350))
    ax1.grid()
    if enderstat.abs_x_pos == 180 and enderstat.abs_y_pos == 180:
        ax1.vlines(180, 0, 500, linestyles="dotted", color="black", alpha=0.5)
        ax1.hlines(180, 0, 500, linestyles="dotted", color="black", alpha=0.5)

    ax2.set_title("Front view")

    if enderstat.tank_architecture is not None:
        if enderstat.tank_architecture == "medium":
            tank_archtctrs = [
                Rectangle((100, 400 - enderstat.abs_z_pos), width=150, height=100)
            ]
            pc = PatchCollection(
                tank_archtctrs, facecolor="lightsteelblue", alpha=0.8, edgecolor="black"
            )
            ax2.add_collection(pc)
        if enderstat.tank_architecture == "high":
            tank_archtctrs = [
                Rectangle((100, 400 - enderstat.abs_z_pos), width=150, height=150)
            ]
            pc = PatchCollection(
                tank_archtctrs, facecolor="lightsteelblue", alpha=0.8, edgecolor="black"
            )
            ax2.add_collection(pc)
        if enderstat.tank_architecture == "select tank":
            tank_archtctrs = [Rectangle((0, 0), width=0, height=0)]  # delete tank
            pc = PatchCollection(
                tank_archtctrs, facecolor="lightsteelblue", alpha=0.8, edgecolor="black"
            )
            ax2.add_collection(pc)

    ax2.hlines(
        400 - enderstat.abs_z_pos,
        50,
        300,
        linestyles="solid",
        color="black",
        label="z-table",
    )
    ax2.scatter(enderstat.abs_x_pos, 0, marker=".", label="Currently")
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
    # ax2.hlines(180, 0, 200, linestyles="dotted", color="black")

    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().place(x=750, y=0, width=400, height=800)
    plt.close(fig)


def action_get_info_dialog():
    m_text = "\
************************\n\
Autor: Jacob Thönes\n\
Date: January 2023\n\
Version: 1.00\n\
Contct: jacob.thoenes@uni-rostock.de \n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


def action_get_info_dialog_traj():
    m_text = "\
************************\n\
TBD\n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


grid_dict = {"sticky": "we", "ipadx": "10"}

"""Main Init"""
app = Tk()
app.title("Ender 5 Interface")
app.configure(background="#1A5175")
app.grid()

connect_ender_5 = ConnectEnder5(app)
connect_sciospec = ConnectScioSpec(app)
movement_xyz = MovementXYZ(app)
tankselect = TankSelect()
stepwidthselect = StepWidthSelect(app)
create_circular_trajectory = CreateCircularTrajectory(app)
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
app.geometry("1150x800")
app.mainloop()
