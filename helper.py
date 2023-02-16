import math
from enum import Enum

Month = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC"        
]

class Day(Enum):
    FRIDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4

weekDaysMap = [
    "FRIDAY",
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
]

def roundUp(number, base):
    return base * math.ceil(number / base)

def roundDown(number, base):
    return base * math.floor(number / base)
