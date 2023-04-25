import importlib

try:
    importlib.import_module('pandas')
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'pandas'])

try:
    importlib.import_module('psycopg2')
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'psycopg2'])

try:
    importlib.import_module('matplotlib')
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'matplotlib'])

import pandas as pd
import matplotlib.pyplot as plt

from db_conn import db_connection
from query import query


def builder():
    connection = db_connection()
    df = pd.read_sql(query, connection)

    fig, ax = plt.subplots(figsize=(10, 50))

    ax.plot(df['dt'], df['transaction_balance_change_sum'], label='Transaction Balance Change')
    ax.plot(df['dt'], df['transaction_balance_change_cs_sum'], label='Transaction Balance Change Cumulative Sum')
    ax.plot(df['dt'], df['classes_sum'], label='Classes')
    ax.plot(df['dt'], df['classes_cs_sum'], label='Classes Cumulative Sum')
    ax.plot(df['dt'], df['balance_sum'], label='Balance')

    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.set_title('Graph')
    ax.legend()

    plt.show()


if __name__ == "__main__":
    builder()
