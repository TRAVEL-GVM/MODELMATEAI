import os
import pandas as pd
from config import nmd_data_path


def get_mm_data():
    df = pd.read_excel(nmd_data_path)

    return df