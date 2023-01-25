import os
import numpy as np
import sys
import serial.tools.list_ports
from tkinter import (
    RIGHT,
    LEFT,
    HORIZONTAL,
    END,
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


# Main Settings
class Settings(object):
    def __init__(self, el_num, el_dist, volts, current, frequency):
        self.el_num = el_num
        self.el_dist = el_dist
        self.volts = volts
        self.current = current
        self.frequency = frequency


settings_upd = Settings(0, 0, 0, 0, 0)


class Log:
    def __init__(self, app):
        self.log = Text(app, height=10, width=70)
        self.log.grid(row=8, column=0, columnspan=2)

        self.clear_button = Button(app, text="Clear Log", command=self.clear_log)
        self.clear_button.grid(row=8, column=2, sticky="we")

    def write(self, text):
        self.log.insert(END, text)

    def flush(self):
        pass

    def clear_log(self):
        self.log.delete("1.0", END)


class ControlButton:
    def __init__(self, app):
        "Generate buttons"
        self.load_conf_button = Button(
            app, text="Load config", command=self.load_config
        )
        self.load_conf_button.grid(row=8, column=2, sticky="wne")
        self.save_conf_button = Button(
            app, text="Save config", command=self.save_config
        )
        self.save_conf_button.grid(row=8, column=3, sticky="wne")
        # Clear log button on row=8, column=2
        self.show_conf_button = Button(
            app, text="Show config", command=self.show_config
        )
        self.show_conf_button.grid(row=8, column=3, sticky="ew")

    def load_config(self):
        global settings_upd
        spath = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a save path",
            # filetypes=(("Text files", "*.txt*"), ("all files", "*.*")),
        )
        print("load path:", spath, "\n")
        tmp = np.load(spath, allow_pickle=True)
        settings_upd = Settings(
            tmp["el_num"].tolist(),
            tmp["el_dist"].tolist(),
            tmp["volts"].tolist(),
            tmp["current"].tolist(),
            tmp["frequency"].tolist(),
        )
        for f in settings_upd.__dict__:
            print(f, ":", tmp[f])

    def save_config(self):
        # generieren vom Ordner
        # Falls der nicht da ist einen erstellen und
        # zum Speicherstandart auswählen
        spath = os.getcwd() + "/data/"
        # checkeh, wie viele dateien da sind
        try:
            num = len(os.listdir(spath))
            np.savez(
                spath + "config_{0:04d}.npz".format(num),
                el_num=settings_upd.el_num,
                el_dist=settings_upd.el_dist,
                volts=settings_upd.volts,
                current=settings_upd.current,
                frequency=settings_upd.frequency,
            )
            print("saved:", spath + "/" + str("config_{0:04d}.npz".format(num)))
        except BaseException:
            print(
                "[Errno 2] No such file or directory:",
                spath,
                "\nSolution: File -> Generate save folder",
            )

    def show_config(self):
        print(settings_upd.__dict__)


class ConnectSerialWindow:
    def __init__(self, app):

        self.ser_cnct_window = Toplevel(app)
        self.ser_cnct_window.grid()
        self.ser_cnct_window.title("Available serial ports")
        # self.ser_cnct_window.geometry("250x100")
        self.cw_label = Label(self.ser_cnct_window, text="Enter port adress:")
        self.cw_label.grid(column=0, row=0, sticky="nesw")

        self.entry = Entry(self.ser_cnct_window, width=25)
        self.entry.grid(column=0, row=1, sticky="nesw")

        self.enter_btn = Button(
            self.ser_cnct_window, text="Submit", command=self.submit_ser_port
        )
        self.enter_btn.grid(column=0, row=2, sticky="nesw")

    def submit_ser_port(self):
        global serial_con_port
        serial_con_port = self.entry.get()
        self.ser_cnct_window.destroy()
        if serial_con_port == "":
            print("Please insert a serial path.")
            ConnectSerialWindow(app)
        else:
            print(serial_con_port)
            self.connect_to_port()

    def connect_to_port(self):
        print("..to continue")


class ConnectAndRunButton:
    def __init__(self, app):

        self.connect_button = Button(
            app, text="Show connections", width=15, command=self.serial_connect
        )
        self.connect_button.grid(row=8, column=2, sticky="esw")

        self.run_conf_button = Button(
            app, text="Run", width=15, background="green", command=self.run_conf
        )
        self.run_conf_button.grid(row=8, column=3, sticky="wse")

    def serial_connect(self):
        if self.connect_button["text"] == "Show connections":
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                print(
                    "Available Connections:\n", "{}: {} [{}]".format(port, desc, hwid)
                )
            self.connect_button["text"] = "Open settings"

        elif self.connect_button["text"] == "Open settings":
            ConnectSerialWindow(app)
            self.connect_button["text"] = "Connect settings"
        else:
            self.connect_button["text"] = "Show connections"

    def run_conf(self):
        if self.run_conf_button["text"] == "Stop":
            self.run_conf_button["text"] = "Run"
            print("Run")
            self.run_conf_button.configure(bg="green", fg="black")
        else:
            self.run_conf_button["text"] = "Stop"
            print("Stop")
            self.run_conf_button.configure(bg="red", fg="white")


def action_get_info_dialog():
    m_text = "\
************************\n\
Autor: Jacob Thönes\n\
Date: Oktober 2022\n\
Version: 1.00\n\
Contct: jacob.thoenes@uni-rostock.de \n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


def gen_save_folder():
    curr_path = os.getcwd()
    existence = False
    for ele in os.listdir(curr_path):
        if str(ele) == "data":
            existence = True
    if not existence:
        os.mkdir("data")
        spath = curr_path + "/data"
        print("Generated save directory: ", spath)
    else:
        print("Directory already exists")


grid_dict = {"sticky": "we", "ipadx": "10"}


class ConfigurationField:
    def __init__(self, app):

        self.el_num_label = Label(
            app,
            justify=LEFT,
            padx=10,
            text="Number of electrodes:\t",
            background="white",
            border=10,
        )
        self.el_num_label.grid(row=2, **grid_dict)

        el_vals = [16, 32, 64, 128, 256]

        for ij, evals in enumerate(el_vals):
            # botching grid
            i = [1, 1, 1, 2, 3]
            j = ["w", "", "e", "we", "we"]
            self.el_num_chbutton = Checkbutton(
                app,
                text=str(evals) + "\t",
                onvalue=evals,
                width=8,
                offvalue=0,
                variable=el_num,
                command=self.set_n_el,
                background="white",
            )
            self.el_num_chbutton.grid(row=2, column=i[ij], padx=5, sticky=j[ij])

        self.EL_DIST_label = Label(
            app,
            justify=LEFT,
            padx=10,
            text="Electrode distance:\t",
            border=10,
        )
        self.EL_DIST_label.grid(row=3, **grid_dict)

        self.voltage_button = Label(
            app,
            justify=LEFT,
            padx=10,
            text="Voltage:\t\t",
            background="white",
            border=10,
        )
        self.voltage_button.grid(row=4, **grid_dict)

        self.VOLTS = Entry(app, width=20)
        self.VOLTS.grid(row=4, column=1, sticky="w", padx=20)
        self.voltage_unit = Label(app, justify=RIGHT, text="[mV]")
        self.voltage_unit.grid(row=4, column=1, sticky="e")

        self.VOLTS_b = Button(app, text="set", command=self.set_volts)
        self.VOLTS_b.grid(row=4, column=2)

        self.current_button = Label(
            app,
            justify=LEFT,
            padx=10,
            text="Current: \t \t",
            border=10,
        )
        self.current_button.grid(row=5, **grid_dict)

        self.CURRENT = Entry(app, width=20)
        self.CURRENT.grid(row=5, column=1, sticky="w", padx=20)
        self.curr_unit = Label(app, justify=RIGHT, text="[mA]")
        self.curr_unit.grid(row=5, column=1, sticky="e")

        self.CURRENT_b = Button(app, text="set", command=self.set_current)
        self.CURRENT_b.grid(row=5, column=2)

        self.frequency_button = Label(
            app,
            justify=LEFT,
            padx=10,
            text="Frequency:\t\t",
            background="white",
            border=10,
        )

        self.frequency_button.grid(row=6, **grid_dict)

        self.FREQ = Entry(app, width=20)
        self.FREQ.grid(row=6, column=1, sticky="w", padx=20)
        self.freq_unit = Label(app, justify=RIGHT, text="[HZ]")
        self.freq_unit.grid(row=6, column=1, sticky="e")
        self.FREQ_b = Button(app, text="set", command=self.set_frequency)
        self.FREQ_b.grid(row=6, column=2)

        # Spacer
        self.spacer = Label(app, text="\n", background="white", border=5)
        self.spacer.grid(row=7)
        # --

    def update_el_dist(self):
        self.EL_DIST = Scale(
            app,
            from_=0,
            to=settings_upd.el_num,
            #   variable=el_dist,
            orient=HORIZONTAL,
            background="white",
            command=self.set_el_dist,
        )
        self.EL_DIST.grid(row=3, column=1, columnspan=3, sticky="ew", padx=20, ipadx=10)
        settings_upd.el_dist = self.EL_DIST.get()

    def set_el_dist(self, el_dist):
        settings_upd.el_dist = el_dist

    def set_volts(self):
        settings_upd.volts = self.VOLTS.get()
        self.VOLTS_b.configure(bg="green", fg="white")
        print(settings_upd.__dict__)

    def set_current(self):
        settings_upd.current = self.CURRENT.get()
        self.CURRENT_b.configure(bg="green", fg="white")
        print(settings_upd.__dict__)

    def set_frequency(self):
        settings_upd.frequency = self.FREQ.get()
        self.FREQ_b.configure(bg="green", fg="white")
        print(settings_upd.__dict__)

    def set_n_el(self):
        settings_upd.el_num = el_num.get()
        self.update_el_dist()
        print(settings_upd.__dict__)


"""Main Init"""
app = Tk()
app.title("Ender 5 Interface")
app.configure(background="white")
app.grid()
Label(app, text="Settings for measurement", **label_settings).grid(
    columnspan=5, ipady=5, sticky="nesw"
)
el_num = IntVar()
el_dist = IntVar()
#CONF_FIELD = ConfigurationField(app)
LOG = Log(app)
sys.stdout = LOG
#CONFIG_BUTTONS = ControlButton(app)
#CON_RUN_BUTTONS = ConnectAndRunButton(app)
dropdown = Menu(app)
datei_menu = Menu(dropdown, tearoff=0)
help_menu = Menu(dropdown, tearoff=0)
datei_menu.add_command(label="Generate save folder", command=gen_save_folder)
datei_menu.add_separator()
datei_menu.add_command(label="Exit", command=app.quit)
help_menu.add_command(label="Info", command=action_get_info_dialog)
dropdown.add_cascade(label="File", menu=datei_menu)
dropdown.add_cascade(label="Help", menu=help_menu)

app.config(menu=dropdown)
app.geometry("762x400")
app.mainloop()
