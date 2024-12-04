import os
import pandas as pd


def get_mm_data():
    path = os.path.join("data", "mmd.xlsx")
    df = pd.read_excel(path)

    return df