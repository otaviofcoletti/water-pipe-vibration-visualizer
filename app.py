import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# === TÍTULO E INTRODUÇÃO ===

st.title("Water Pipe Vibration & Power Visualization")

st.markdown("""
This application allows you to visualize and analyze paired vibration and power measurements collected from a water pipeline monitoring system.

The dataset contains two types of CSV files:

- **Vibration files (MXXXXL.csv):**  
  Contain acceleration data in 3 axes (X, Y, Z). Columns 2, 3, and 4 store the acceleration measurements. The file name includes the flow rate (XXXX) and a letter (L) to distinguish different samples.

- **Power files (MXXXXL_power.csv):**  
  Contain corresponding power measurements for the same flow condition. The power values are stored in column 2.

---

### How to use:

1. All files must be placed inside the `/Macro Power Data/Macro Power Data/` directory (already included in this repository).
2. The app automatically detects valid file pairs based on the filename pattern.
3. Use the selector below to choose which flow condition you wish to visualize.
4. The application will extract a central window from both vibration and power signals to create side-by-side plots.
5. You can select how many samples you want to display.

---
""")

# === CONFIGURAÇÃO DE DIRETÓRIO ===

DATA_DIR = 'Macro Power Data/Macro Power Data'
PATTERN = re.compile(r'^M(\d+)([A-Z])\.csv$')

# === DETECTAR PARES ===

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

# === INTERFACE DE SELEÇÃO ===

if not pairs:
    st.warning("No valid file pairs found in your data folder.")
else:
    selected_pair = st.selectbox("Select the file pair:", sorted(pairs))

    # Novo: permitir selecionar o tamanho da janela
    window_size = st.selectbox("Select number of samples to display:", [1000, 5000, 10000, 15000, 20000], index=0)

    if selected_pair:
        acc_file = f"{selected_pair}.csv"
        power_file = f"{selected_pair}_power.csv"
        acc_path = os.path.join(DATA_DIR, acc_file)
        power_path = os.path.join(DATA_DIR, power_file)

        n_lines_acc = sum(1 for _ in open(acc_path))
        n_lines_power = sum(1 for _ in open(power_path))
        n_lines = min(n_lines_acc, n_lines_power)

        center = n_lines // 2
        window = window_size // 2
        start = max(center - window, 0)
        nrows = min(window_size, n_lines - start)

        df_acc = pd.read_csv(acc_path, header=None, skiprows=start, nrows=nrows, usecols=[1, 2, 3])
        acc = df_acc.to_numpy()
        magnitude = np.sqrt(np.sum(acc**2, axis=1))

        df_power = pd.read_csv(power_path, header=None, skiprows=start, nrows=nrows, usecols=[1])
        power = df_power.iloc[:, 0].to_numpy()

        # Aumentamos o tamanho da figura
        fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)

        axes[0].plot(magnitude)
        axes[0].set_title(f"Acceleration Magnitude - {selected_pair}", fontsize=16)
        axes[0].set_ylabel('Acceleration Magnitude', fontsize=14)
        axes[0].grid(True)

        axes[1].plot(power, color='orange')
        axes[1].set_title(f"Power - {selected_pair}", fontsize=16)
        axes[1].set_xlabel('Sample', fontsize=14)
        axes[1].set_ylabel('Power (W)', fontsize=14)
        axes[1].grid(True)

        plt.tight_layout()
        st.pyplot(fig)
