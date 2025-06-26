import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def visualize_nulls(df: pd.DataFrame):
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.isna(), cbar=False, cmap='viridis')
    plt.title('Missing Values Heatmap')
    plt.show()
