import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import logging
import sys

from llama_index.experimental.query_engine import PandasQueryEngine
import openai


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

openai.api_key = os.getenv("OPEN_AI_KEY")

from prompts import instruction_str, new_prompt, context

population_path = os.path.join("data", "population.csv")
population_df = pd.read_csv(population_path)


population_query_engine = PandasQueryEngine(df=population_df, verbose=True, instruction_str=instruction_str)
population_query_engine.update_prompts({"pandas_prompt": new_prompt})
population_query_engine.query("What is the population of canada")

