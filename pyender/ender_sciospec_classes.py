from dataclasses import dataclass
import numpy as np
from typing import Union, List


@dataclass
class OperatingSystem:
    system: str
    resolution_width: int
    resolution_height: int


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
    # Probably add a limitbox for a corresponding tank
    # TBD: Write a function that checks the boundary limit box


@dataclass
class mmPerStep:
    mm_per_step: Union[int, float]


@dataclass
class CircleDrivePattern:
    active: bool
    wait_at_pos: int  # [s]
    radius: Union[int, float]  # [mm]
    phi_steps: Union[int, float]  # [degree/step]
    abs_x_posis: np.ndarray
    abs_y_posis: np.ndarray
    abs_z_posis: np.ndarray
    motion_speed: Union[int, float]
    n_points: int
    actual_point: int


@dataclass
class KartesianDrivePattern:
    active: bool
    wait_at_pos: int  # [s]
    motion_speed: Union[int, float]
    x_start: Union[int, float]
    y_start: Union[int, float]
    x_stop: Union[int, float]
    y_stop: Union[int, float]
    x_stp_num: int
    y_stp_num: int
    abs_x_posis: np.ndarray
    abs_y_posis: np.ndarray
    abs_z_posis: np.ndarray
    n_points: int
    actual_point: int


@dataclass
class HitBoxTank:
    tank_architecture: Union[None, str]
    z_lim_height: Union[int, float]
    r_max: Union[int, float]


@dataclass
class MeasurementObject:
    """TBD: Insert in functions"""

    active: bool
    name: Union[None, str]
    x_boundary_width: Union[int, float]
    y_boundary_width: Union[int, float]
