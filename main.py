from files import load_csv_to_df
from visualizer import visualize_nulls

df = load_csv_to_df(
    r'd:\Learning\Machine Learning\notebooks\titanic\train.csv')
visualize_nulls(df)
