from enum import Enum


#define the simulation approach - these will be used for the tasks_test.py file
class DataType(Enum):
    STANDARD = "1"
    CUSTOM = "2"


class DataSource(str, Enum):
    DSSAT = "DSSAT"
    OUTDSSAT= "DSSAT_Output"
