import pandas as pd
from enum import Enum
import os


def directory_up(path: str, n: int):
    for _ in range(n):
        path = directory_up(path.rpartition("/")[0], 0)
    return path


root_path = os.path.dirname(os.path.realpath(__file__))
# Change working directory to root of the project.
os.chdir(directory_up(root_path, 2))


class Filenames(Enum):
    data_with_weather = 'data_with_weather'
    data_cleaned = 'data_cleaned'


def get_route_from_filename(filename: str):
    return './data/{}.csv'.format(filename)


def write_data(data_frame: pd.DataFrame, filename: Filenames):
    data_frame.to_csv(get_route_from_filename(filename), index=False)


def read_data(filename):
    return pd.read_csv(get_route_from_filename(filename))
