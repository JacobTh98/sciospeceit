try:
    import serial
except ImportError:
    print("Could not import module: serial")

from typing import Union
import time
import numpy as np
import sys
import glob

from ender_sciospec_classes import Ender5Stat, HitBoxTank

# https://reprap.org/wiki/G-code#M17:_Enable.2FPower_all_stepper_motors


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


# Commands for Ender 5


def move_to_absolute_x(ser, enderstat: Ender5Stat) -> None:
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(ser, f"G0 X{enderstat.abs_x_tgt} F{enderstat.motion_speed}\r\n")
    print(enderstat)


def move_to_absolute_y(ser, enderstat: Ender5Stat) -> None:
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(ser, f"G0 Y{enderstat.abs_y_tgt} F{enderstat.motion_speed}\r\n")
    print(enderstat)


def move_to_absolute_z(ser, enderstat: Ender5Stat) -> None:
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(ser, f"G0 Z{enderstat.abs_z_tgt} F{enderstat.motion_speed}\r\n")
    print(enderstat)


def move_to_absolute_x_y(ser, enderstat: Ender5Stat) -> None:
    """
    enderstat.abs_x_tgt : absolute x position
    enderstat.abs_y_tgt : absolute y position
    enderstat.motion_speed : movement speed in [mm/min]
    """
    command(
        ser,
        f"G0 X{enderstat.abs_x_tgt} Y{enderstat.abs_y_tgt} F{enderstat.motion_speed}\r\n",
    )
    print(enderstat)


def disable_steppers(ser) -> None:
    command(ser, "M18 X Y Z E\r\n")


def enable_steppers(ser) -> None:
    command(ser, "M17 X Y Z E\r\n")


def x_y_home(ser, enderstat: Ender5Stat) -> None:
    command(ser, f"G28 X0 Y0 F{enderstat.motion_speed}\r\n")
    command(ser, f"G28 Z0 F{enderstat.motion_speed}\r\n")
    print(enderstat)


def x_y_center(ser, enderstat: Ender5Stat) -> None:
    command(ser, f"G0 X180 Y180 F{enderstat.motion_speed}\r\n")
    print(enderstat)


def turn_off_fan(ser) -> None:
    command(ser, "M106 S0\r\n")


def init_axis(ser) -> None:
    x_y_home(ser)
    x_y_center(ser)
    turn_off_fan(ser)
    print("X,Y axis are centered at X(180), Y(180)")


def circle_clockwise(
    ser, X, Y, enderstat: Ender5Stat, I=180, J=180, clock: bool = True
) -> None:
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


def command(ser, command) -> None:
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
        x,y : Arrays with corresponding x,y steps
    """
    x0, y0 = 180, 180
    angles = np.radians(np.arange(0, 360, phi_step))
    x = r * np.cos(angles) + x0
    y = r * np.sin(angles) + y0

    return x, y


def compute_abs_x_y_from_x_y(
    x_start, y_start, x_stop, y_stop, x_steps, y_steps, hbt: HitBoxTank
) -> np.ndarray:
    """
    Returns a mesh of evenly distributed measurement points
    x_start : Start of the grid at x
    y_start : Start of the grid at y
    x_stop : Stop of the grid at x
    y_stop : Stop of the grid at x
    x_steps : Number of steps on the x-axis including endpoint
    y_steps : Number of steps on the y-axis including endpoint
    hbt : Hitbox of the placed tank

    returns:
        x,y : Arrays with corresponding x,y steps

    """
    x_sigle_vals = np.linspace(x_start, x_stop, num=x_steps, endpoint=True)
    y_sigle_vals = np.linspace(y_start, y_stop, num=y_steps, endpoint=True)
    x = np.repeat(x_sigle_vals, y_steps)
    y = np.concatenate(np.stack([y_sigle_vals for _ in range(x_steps)], axis=0))

    X = []
    Y = []
    if hbt.tank_architecture is not None:
        for xs, ys in zip(
            x - 175, y - 175
        ):  # TBD: Add MeasurementObject class for hitbox of the object itself.
            r = np.sqrt(xs**2 + ys**2)
            if r <= hbt.r_max:
                X.append(xs)
                Y.append(ys)
            else:
                pass
        x = np.array(X) + 175
        y = np.array(Y) + 175
        return x, y
    else:
        return x, y


def calculate_moving_time(enderstat: Ender5Stat, tol: int = 1) -> Union[int, float]:
    """
    Computes the time that the Ender5 needs for moving from one point to another in seconds including a time tolerance of 1s.
    """
    dx = enderstat.abs_x_tgt - enderstat.abs_x_pos
    dy = enderstat.abs_y_tgt - enderstat.abs_y_pos
    if enderstat.abs_z_tgt is None:
        dz = 0
    else:
        dz = enderstat.abs_z_tgt - enderstat.abs_z_pos
    s = np.sqrt(dx**2 + dy**2 + dz**2)
    print("")
    v = enderstat.motion_speed / 60.0
    return np.round(s / v + tol, 2)


def read_temperature(ser) -> float:  # TB-checked
    """
    Read the bed temperature of the Ender 5

    Parameters
    ----------
    ser : _type_
        serial connection

    Returns
    -------
    float
        temperature value
    """
    command(ser, f"M105\r\n")
    temperature = ser.read()
    return temperature
