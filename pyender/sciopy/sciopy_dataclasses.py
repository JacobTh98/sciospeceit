from dataclasses import dataclass
from typing import Union, List


@dataclass
class ScioSpecMeasurementConfig:
    sample_per_step: int
    actual_sample: int
    s_path: str
    object: str


@dataclass
class SingleEitFrame:
    pass
