import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def set_global_plot_style():
    sns.set_theme(style="whitegrid")  # or 'darkgrid', 'ticks', etc.
    sns.set_palette("crest")
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.titlesize': 16,
        'axes.titleweight': 'bold',
        'axes.labelsize': 12,
        'axes.labelweight': 'medium',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'axes.edgecolor': 'lightgray',
        'axes.linewidth': 0.8,
        'grid.alpha': 0.4,
        # Using a generic sans-serif font for better compatibility
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Liberation Sans', 'sans-serif'],
    })


def plot_null_counts(df) -> plt:
    null_counts = df.isna().sum()
    null_counts = null_counts[null_counts > 0].sort_values()

    if null_counts.empty:
        print("✅ No missing values.")
        return

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        x=null_counts.values,
        y=null_counts.index,
        palette="crest",
    )

    # Annotate each bar with its value
    for i, (value, label) in enumerate(zip(null_counts.values, null_counts.index)):
        ax.text(
            # small offset to the right
            value + max(null_counts.values) * 0.01,
            i,
            str(value),
            va='center',
            ha='left',
            fontsize=10,
            color='black'
        )

    plt.title("Missing Values per Column", loc='left')
    plt.xlabel("Number of Missing Entries")
    plt.ylabel("Column")
    plt.grid(axis='x', linestyle=':', linewidth=0.5)
    plt.tight_layout()

    return plt
