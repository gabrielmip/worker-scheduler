from dataclasses import dataclass
from datetime import datetime


@dataclass
class Timeslot:
    start: datetime
    end: datetime


@dataclass
class AvailabilityTuple(Timeslot):
    session_duration: int
