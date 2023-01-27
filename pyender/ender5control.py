try:
    import serial
    from serial import Serial
except ImportError:
    print("Could not import module: serial")


import time
from datetime import datetime
import numpy as np
import sys
import glob

# https://reprap.org/wiki/G-code#M17:_Enable.2FPower_all_stepper_motors

from dataclasses import dataclass
from typing import Union


@dataclass
class Ender5Stat:
    """Class for keeping everything together"""

    abs_x_pos: Union[int, float]
    abs_y_pos: Union[int, float]
    abs_z_pos: Union[int, float]
    tank_architecture: Union[None, str]
    motion_speed: Union[int, float]
    abs_x_tgt: Union[None, int, float]
    abs_y_tgt: Union[None, int, float]
    abs_z_tgt: Union[None, int, float]


def available_serial_ports() -> list:
    """Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def connect_COM_port(port: str = "COM4", baudrate: int = 115200, timeout: int = 1):
    """
    Etablishes a serial connection to a given com port.
    Returnes the serial connection
    """

    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
    )

    print("Connection to", ser.name, "is established.")
    return ser


## Commands for Ender 5


def move_to_absolute_x(ser, enderstat: Ender5Stat):
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(ser, f"G0 X{enderstat.abs_x_tgt} F{enderstat.motion_speed}\r\n")


def move_to_absolute_y(ser, enderstat: Ender5Stat):
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(ser, f"G0 Y{enderstat.abs_y_tgt} F{enderstat.motion_speed}\r\n")


def move_to_absolute_z(ser, enderstat: Ender5Stat):
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(ser, f"G0 Z{enderstat.abs_z_tgt} F{enderstat.motion_speed}\r\n")


def move_to_absolute_x_y(ser, enderstat: Ender5Stat):
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.abs_y_tgt : absolute y position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(
        ser,
        f"G0 X{enderstat.abs_x_tgt} Y{enderstat.abs_y_tgt} F{enderstat.motion_speed}\r\n",
    )


def disable_steppers(ser):
    command(ser, "M18 X Y Z E\r\n")


def enable_steppers(ser):
    command(ser, "M17 X Y Z E\r\n")


def x_y_home(ser, enderstat: Ender5Stat):
    command(ser, f"G28 X0 Y0 F{enderstat.motion_speed}\r\n")
    command(ser, f"G28 Z0 F{enderstat.motion_speed}\r\n")


def x_y_center(ser, enderstat: Ender5Stat):
    command(ser, f"G0 X180 Y180 F{enderstat.motion_speed}\r\n")


def turn_off_fan(ser):
    command(ser, "M106 S0\r\n")


def init_axis(ser):
    x_y_home(ser)
    x_y_center(ser)
    turn_off_fan(ser)
    print("X,Y axis are centered at X(180), Y(180)")


def circle_clockwise(X, Y, enderstat: Ender5Stat, I=180, J=180, clock: bool = True):
    """
    clock : True = clockwise, False = counter-clockwise
    X : The position to move to on the X axis
    Y : The position to move to on the Y axis
    I : The point in X space from the current X position to maintain a constant distance from
    J : The point in Y space from the current Y position to maintain a constant distance from
    enderstat.motion_speed : The feedrate per minute of the move between the starting point and ending point (if supplied)
    """
    if clock:
        command(ser, f"G2 X{X} Y{Y} I{I} J{J} F{enderstat.motion_speed}\r\n")
    else:
        command(ser, f"G3 X{X} Y{Y} I{I} J{J} F{enderstat.motion_speed}\r\n")


def command(ser, command):
    ser.write(str.encode(command))
    time.sleep(1)
    while True:
        line = ser.readline()
        print(line)

        if line == b"ok\n":
            break


# Math commands


def compute_abs_x_y_from_r_phi(r, phi_step) -> np.ndarray:
    """
    Returns a P(x,y) array with the relating trajectory positions.
    Fixpoint/start is the Ender 5 center at P(180,180)

    r : absolute radial movement trajectory [mm]
    phi_step : angle step [°]

    returns:
        P_xy : Array with x,y steps
    """
    x0, y0 = 180, 180
    angles = np.radians(np.arange(0, 360, phi_step))
    x = r * np.cos(angles) + x0
    y = r * np.sin(angles) + y0

    return x, y
