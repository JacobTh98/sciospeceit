import os
import numpy as np
import time
from dataclasses import dataclass
from typing import Union, List
import sys
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# import serial.tools.list_ports
from tkinter import (
    RIGHT,
    LEFT,
    HORIZONTAL,
    END,
    ttk,
    Button,
    Label,
    Entry,
    Menu,
    Scale,
    Text,
    filedialog,
    Toplevel,
    IntVar,
    Checkbutton,
    Tk,
    messagebox,
)

label_settings = {"font": ("Arial", 25), "borderwidth": "10", "background": "lightblue"}


""" Constant design/layout values"""

x_0ff = 200
y_0ff = 100
spacer = 20
btn_width = 50
btn_height = 50


""" Functions and Classes """


class Log:
    def __init__(self, app):
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


detected_com_ports = ["COM3", "COM4"]


@dataclass
class Ender5Position:
    """Class for keeping x,y,z, and motion speed together"""

    abs_x_pos: Union[int, float]
    abs_y_pos: Union[int, float]
    abs_z_pos: Union[int, float]
    motion_speed: Union[int, float]


@dataclass
class CircleDrivePattern:
    radius: Union[int, float]
    phi_steps: Union[int, float]
    abs_x_pos: List[Union[int, float]]
    abs_y_pos: List[Union[int, float]]
    abs_z_pos: List[Union[int, float]]
    motion_speed: List[Union[int, float]]


@dataclass
class MultipleCircleDrivePattern:
    radius: List[Union[int, float]]
    phi_steps: List[Union[int, float]]
    abs_x_pos: List[Union[int, float]]
    abs_y_pos: List[Union[int, float]]
    abs_z_pos: List[Union[int, float]]
    motion_speed: List[Union[int, float]]


class ConnectEnder5:
    """
    The initialization has to be added here.
    init_ender5 function -> Move to center/home, whatever and inserts the positional date inside the corresponding dataclass
    """

    def __init__(self, app) -> None:

        self.com_dropdown = ttk.Combobox(
            values=detected_com_ports,
        )
        self.com_dropdown.bind("<<ComboboxSelected>>", self.dropdown_callback)
        self.com_dropdown.place(x=spacer, y=spacer, width=btn_width, height=btn_height)

        self.connect_interact_button = Button(
            app,
            text="Establish connection",
            bg="yellow",
            state="disabled",
            command=self.connect_interact,
        )
        self.connect_interact_button.place(
            x=2 * spacer + btn_width, y=spacer, width=x_0ff - spacer, height=btn_height
        )

    def dropdown_callback(self, event=None):
        if event:
            print("dropdown opened and selected:", self.com_dropdown.get())
            self.connect_interact_button["state"] = "normal"
        else:
            print("Nothing")

    def connect_interact(self):

        self.connect_interact_button["text"] = "Connecting ..."
        print("Connection to ", str(self.com_dropdown.get()), "established.")
        time.sleep(3)
        # if condition, if serial connection is established !!!
        self.connect_interact_button["text"] = "Connection established"
        self.connect_interact_button["bg"] = "green"
        self.connect_interact_button["state"] = "disabled"
        self.com_dropdown["state"] = "disabled"
        plot()


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

        self.x_up_btn = Button(app, text="x+", command=self.move_x_up)
        self.x_up_btn.place(
            x=x_0ff, y=y_0ff + spacer + btn_height, width=btn_width, height=btn_height
        )

        self.x_down_btn = Button(app, text="x-", command=self.move_x_down)
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

        self.z_center_btn = Button(app, text="center\nz")
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
        self.motion_speed.set(1000)
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
        print(self.x_set_entry.get())

    def set_y(self):
        print(self.y_set_entry.get())

    def set_z(self):
        print(self.z_set_entry.get())

    def x_y_center(self):
        pass

    def move_x_up(self):
        pass

    def move_x_down(self):
        pass

    def move_y_up(self):
        pass

    def move_y_down(self):
        pass

    def move_z_up(self):
        pass

    def move_z_down(self):
        pass

    def motion_speed_callback(self, event):
        print("Set motion speed to", self.motion_speed.get(), "[mm/min]")


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

        self.radius_input_btn = Button(app, text="r=", command=self.set_r_values)
        self.radius_input_btn.place(
            x=spacer,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )

        self.radius_entry = Entry(app)
        self.radius_entry.place(
            x=2 * spacer + btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.radius_unit = Label(app, text="mm").place(
            x=2 * spacer + 2 * btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width // 2,
            height=btn_height,
        )

        self.phi_input_btn = Button(app, text="phi=", command=self.set_phi_values)
        self.phi_input_btn.place(
            x=3 * spacer + 2 * btn_width + btn_width // 2,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.phi_entry = Entry(app)
        self.phi_entry.place(
            x=5 * spacer + 2 * btn_width + btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width,
            height=btn_height,
        )
        self.phi_unit = Label(app, text="step/360°").place(
            x=5 * spacer + 3 * btn_width + btn_width,
            y=y_0ff + 5 * btn_height + 2 * spacer,
            width=btn_width + btn_width // 2,
            height=btn_height,
        )

        self.compute_trajectory = Button(app, text="Info", command=compute_trajectory)
        self.compute_trajectory.place(
            x=x_0ff + 4 * btn_width + spacer,
            y=y_0ff + 4 * btn_height + 1 * spacer,
            width=btn_width,
            height=btn_height,
        )

    def set_r_values(self):
        print("r=", self.radius_entry.get())

    def set_phi_values(self):
        print("r=", self.phi_entry.get())


def compute_trajectory():
    # Already implemented.
    """Connection between dataclasses and the object oriented classes in tkkinter has to be done."""
    print("computation has to be substituted... (TBD)")


"""
def plot_x_y_circle(x,y):

    plt.scatter(x,y, label="Measurement points", marker='*')
    plt.legend()
    plt.show()
"""


def plot(x=180, y=180, z=100) -> None:
    plt.rcParams["font.size"] = 5
    plt.rcParams["figure.autolayout"] = True
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 5))

    ax1.set_title("Top view")
    ax1.scatter(x, y, marker=".", label="Currently")
    ax1.scatter(x + 10, y + 10, marker="*", label="Target")
    ax1.set_ylabel("absolute y[mm]")
    ax1.set_xlabel("absolute x[mm]")
    ax1.set_xlim((0, 350))
    ax1.set_ylim((0, 350))
    ax1.grid()
    ax1.legend(
        loc="upper center",
        bbox_to_anchor=(0.6, 1.00),
        fancybox=True,
        ncol=5,
    )
    if x == 180 and y == 180:
        ax1.vlines(180, 0, 500, linestyles="dotted", color="black")
        ax1.hlines(180, 0, 500, linestyles="dotted", color="black")

    ax2.set_title("Front view")
    errorboxes = [Rectangle((100, z), width=150, height=100)]
    pc = PatchCollection(
        errorboxes, facecolor="lightsteelblue", alpha=0.8, edgecolor="black"
    )
    ax2.add_collection(pc)
    ax2.hlines(z, 50, 300, linestyles="solid", color="black", label="z-table")
    ax2.scatter(x, z + 10, marker=".")
    ax2.scatter(x + 10, z + 10, marker="*")
    ax2.set_ylabel("absolute z[mm]")
    ax2.set_xlabel("absolute x[mm]")
    ax2.set_xlim((0, 350))
    ax2.set_ylim((0, 350))
    ax2.grid()
    ax2.legend()
    # ax2.hlines(180, 0, 200, linestyles="dotted", color="black")

    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().place(x=750, y=spacer, width=400, height=800)
    toolbar = NavigationToolbar2Tk(canvas, app)
    toolbar.update()


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
Add infos regarding the trajectory definition here...\n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


grid_dict = {"sticky": "we", "ipadx": "10"}

"""Main Init"""
app = Tk()
app.title("Ender 5 Interface")
app.configure(background="white")
app.grid()

connect_ender_5 = ConnectEnder5(app)
movement_xyz = MovementXYZ(app)
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


plot()

app.config(menu=dropdown)
app.geometry("1200x900")
app.mainloop()
