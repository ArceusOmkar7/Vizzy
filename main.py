from files import load_csv_to_df
from visualizer import plot_null_counts

df = load_csv_to_df(
    r'd:\Learning\Machine Learning\notebooks\titanic\train.csv')
plot_null_counts(df)
