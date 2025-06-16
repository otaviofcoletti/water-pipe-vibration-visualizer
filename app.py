import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

st.title("Water Pipe Vibration & Power Visualization")

# Directory where your data lives inside the repository
DATA_DIR = 'Macro Power Data/Macro Power Data'
PATTERN = re.compile(r'^M(\d+)([A-Z])\.csv$')

# List available pairs
files = os.listdir(DATA_DIR)
acc_files = [f for f in files if PATTERN.match(f)]

pairs = []
for acc_file in acc_files:
    match = PATTERN.match(acc_file)
    prefix_num = match.group(1)
    letter = match.group(2)
    power_file = f"M{prefix_num}{letter}_power.csv"
    if power_file in files:
        pairs.append(f"M{prefix_num}{letter}")

if not pairs:
    st.warning("No valid file pairs found in your data folder.")
else:
    selected_pair = st.selectbox("Select the file pair:", sorted(pairs))

    if selected_pair:
        acc_file = f"{selected_pair}.csv"
        power_file = f"{selected_pair}_power.csv"
        acc_path = os.path.join(DATA_DIR, acc_file)
        power_path = os.path.join(DATA_DIR, power_file)

        n_lines_acc = sum(1 for _ in open(acc_path))
        n_lines_power = sum(1 for _ in open(power_path))
        n_lines = min(n_lines_acc, n_lines_power)

        center = n_lines // 2
        window = 500
        start = max(center - window, 0)
        nrows = min(1000, n_lines - start)

        df_acc = pd.read_csv(acc_path, header=None, skiprows=start, nrows=nrows, usecols=[1, 2, 3])
        acc = df_acc.to_numpy()
        magnitude = np.sqrt(np.sum(acc**2, axis=1))

        df_power = pd.read_csv(power_path, header=None, skiprows=start, nrows=nrows, usecols=[1])
        power = df_power.iloc[:, 0].to_numpy()

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].plot(magnitude)
        axes[0].set_title(f"Acceleration Magnitude - {selected_pair}")
        axes[0].set_xlabel('Sample')
        axes[0].set_ylabel('Acceleration Magnitude')

        axes[1].plot(power, color='orange')
        axes[1].set_title(f"Power - {selected_pair}")
        axes[1].set_xlabel('Sample')
        axes[1].set_ylabel('Power (W)')

        st.pyplot(fig)
