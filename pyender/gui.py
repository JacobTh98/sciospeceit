import os
import numpy as np
import time
from dataclasses import dataclass
from typing import Union, List
import sys
from matplotlib.figure import Figure
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


def plot():

    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(4, 2))

    t = np.arange(0, 3, 0.01)
    ax1.plot(t, 2 * np.sin(2 * np.pi * t))
    ax1.set_title("x-y Plane")
    ax2.plot(t, 2 * np.cos(2 * np.pi * t))

    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().place(x=700, y=spacer, width=350, height=700)

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas, app)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    # canvas.get_tk_widget().pack()


class VisualiseXYPlane:
    def __init__(self, app) -> None:
        self.x_y_plane_canvas = FigureCanvasTkAgg(app, figure=fig)


def action_get_info_dialog():
    m_text = "\
************************\n\
Autor: Jacob Thönes\n\
Date: January 2023\n\
Version: 1.00\n\
Contct: jacob.thoenes@uni-rostock.de \n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


grid_dict = {"sticky": "we", "ipadx": "10"}

"""Main Init"""
app = Tk()
app.title("Ender 5 Interface")
app.configure(background="white")
app.grid()


movement_xyz = MovementXYZ(app)
connect_ender_5 = ConnectEnder5(app)
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


# plot()

app.config(menu=dropdown)
app.geometry("1200x800")
app.mainloop()
