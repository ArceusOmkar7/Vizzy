import streamlit as st
import pandas as pd
from visualizer import plot_null_counts

uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])


if uploaded_file:
    df = pd.read_csv(uploaded_file)
    plt = plot_null_counts(df)
    st.pyplot(plt)
