"""
Demo script to generate sample data for testing the Data Visualizer app.

This script creates various types of datasets to test different visualization features.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def create_sample_datasets():
    """
    Create sample datasets for testing the Data Visualizer app.
    """
    # Create data directory if it doesn't exist
    data_dir = "sample_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Dataset 1: Sales data with various data types
    np.random.seed(42)
    n_rows = 1000

    sales_data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=n_rows, freq='D'),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Books', 'Sports'], n_rows),
        'sales_amount': np.random.normal(100, 30, n_rows).round(2),
        'quantity': np.random.randint(1, 20, n_rows),
        'discount_percent': np.random.uniform(0, 25, n_rows).round(1),
        'customer_age': np.random.normal(35, 12, n_rows).round(),
        'customer_gender': np.random.choice(['Male', 'Female', 'Other'], n_rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_rows),
        'is_weekend': None,  # Will fill this based on date
        'customer_satisfaction': np.random.choice([1, 2, 3, 4, 5], n_rows, p=[0.05, 0.1, 0.2, 0.4, 0.25])
    })

    # Add weekend flag
    sales_data['is_weekend'] = sales_data['date'].dt.weekday >= 5

    # Introduce some missing values
    missing_indices = np.random.choice(
        sales_data.index, size=int(0.1 * n_rows), replace=False)
    sales_data.loc[missing_indices[:50], 'customer_age'] = np.nan
    sales_data.loc[missing_indices[50:100], 'discount_percent'] = np.nan
    sales_data.loc[missing_indices[100:120], 'customer_satisfaction'] = np.nan

    # Add some correlations
    sales_data.loc[sales_data['product_category']
                   == 'Electronics', 'sales_amount'] *= 1.5
    sales_data.loc[sales_data['is_weekend'], 'sales_amount'] *= 0.8

    sales_data.to_csv(f"{data_dir}/sales_data.csv", index=False)
    print(f"✓ Created sales_data.csv ({len(sales_data)} rows)")

    # Dataset 2: Student performance data
    n_students = 500

    student_data = pd.DataFrame({
        'student_id': range(1, n_students + 1),
        'gender': np.random.choice(['Male', 'Female'], n_students),
        'race_ethnicity': np.random.choice(['Group A', 'Group B', 'Group C', 'Group D', 'Group E'], n_students),
        'parental_education': np.random.choice(['High School', 'Some College', 'Bachelor', 'Master', 'Associate'], n_students),
        'lunch_type': np.random.choice(['Standard', 'Free/Reduced'], n_students, p=[0.6, 0.4]),
        'test_prep': np.random.choice(['None', 'Completed'], n_students, p=[0.7, 0.3]),
        'math_score': np.random.normal(65, 15, n_students).round().astype(int),
        'reading_score': np.random.normal(68, 14, n_students).round().astype(int),
        'writing_score': np.random.normal(67, 15, n_students).round().astype(int)
    })

    # Add correlations between scores
    correlation_noise = np.random.normal(0, 5, n_students)
    student_data['reading_score'] = (student_data['math_score'] * 0.7 +
                                     student_data['reading_score'] * 0.3 + correlation_noise).round().astype(int)
    student_data['writing_score'] = (student_data['reading_score'] * 0.8 +
                                     student_data['writing_score'] * 0.2 + correlation_noise).round().astype(int)

    # Ensure scores are in valid range
    for col in ['math_score', 'reading_score', 'writing_score']:
        student_data[col] = student_data[col].clip(0, 100)

    # Add some missing values
    missing_indices = np.random.choice(
        student_data.index, size=int(0.05 * n_students), replace=False)
    student_data.loc[missing_indices[:10], 'test_prep'] = np.nan
    student_data.loc[missing_indices[10:15], 'parental_education'] = np.nan

    student_data.to_csv(f"{data_dir}/student_performance.csv", index=False)
    print(f"✓ Created student_performance.csv ({len(student_data)} rows)")

    # Dataset 3: Small dataset with high missing values
    n_small = 200

    messy_data = pd.DataFrame({
        'id': range(1, n_small + 1),
        'category_a': np.random.choice(['Type1', 'Type2', 'Type3', None], n_small, p=[0.3, 0.3, 0.2, 0.2]),
        'category_b': np.random.choice(['Alpha', 'Beta', 'Gamma', None], n_small, p=[0.25, 0.25, 0.25, 0.25]),
        'numeric_1': np.random.normal(50, 20, n_small),
        'numeric_2': np.random.exponential(10, n_small),
        'binary_flag': np.random.choice([0, 1, None], n_small, p=[0.4, 0.4, 0.2]),
        'text_data': np.random.choice(['Short', 'Medium length text', 'Very long descriptive text here', None],
                                      n_small, p=[0.3, 0.3, 0.2, 0.2])
    })

    # Make numeric_2 missing when category_a is None (correlated missingness)
    messy_data.loc[messy_data['category_a'].isna(), 'numeric_2'] = np.nan

    # Add more missing values
    messy_data.loc[np.random.choice(
        messy_data.index, 30, replace=False), 'numeric_1'] = np.nan

    messy_data.to_csv(f"{data_dir}/messy_data.csv", index=False)
    print(f"✓ Created messy_data.csv ({len(messy_data)} rows)")

    # Dataset 4: High cardinality categorical data
    n_large = 2000

    high_card_data = pd.DataFrame({
        'transaction_id': [f"TXN_{i:06d}" for i in range(1, n_large + 1)],
        'user_id': [f"USER_{i:04d}" for i in np.random.randint(1, 500, n_large)],
        'product_sku': [f"SKU_{i:05d}" for i in np.random.randint(1, 1000, n_large)],
        'amount': np.random.lognormal(mean=4, sigma=1, size=n_large).round(2),
        'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Cash'], n_large),
        'country': np.random.choice(['USA', 'UK', 'Germany', 'France', 'Canada', 'Australia'], n_large),
        'transaction_hour': np.random.randint(0, 24, n_large),
        'is_fraud': np.random.choice([0, 1], n_large, p=[0.95, 0.05])
    })

    # Make fraud cases have higher amounts on average
    fraud_mask = high_card_data['is_fraud'] == 1
    high_card_data.loc[fraud_mask, 'amount'] *= 2

    high_card_data.to_csv(f"{data_dir}/high_cardinality_data.csv", index=False)
    print(f"✓ Created high_cardinality_data.csv ({len(high_card_data)} rows)")

    # Dataset 5: Time series data for testing time series analysis
    np.random.seed(42)

    # Create 2 years of daily data
    date_range = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
    n_ts_points = len(date_range)

    # Generate realistic time series with trend, seasonality, and noise
    # Base trend (slightly increasing)
    trend = np.linspace(100, 120, n_ts_points)

    # Seasonal patterns (yearly and weekly)
    yearly_season = 10 * np.sin(2 * np.pi * np.arange(n_ts_points) / 365.25)
    weekly_season = 5 * np.sin(2 * np.pi * np.arange(n_ts_points) / 7)

    # Random noise
    noise = np.random.normal(0, 3, n_ts_points)

    # Combine components
    values = trend + yearly_season + weekly_season + noise

    # Add some outliers
    outlier_indices = np.random.choice(n_ts_points, size=10, replace=False)
    values[outlier_indices] += np.random.choice(
        [-1, 1], size=10) * np.random.uniform(20, 40, size=10)

    # Create additional time series with different patterns
    ts_data = pd.DataFrame({
        'date': date_range,
        'website_visits': np.maximum(values, 0).round().astype(int),
        'revenue': (values * 12.5 + np.random.normal(0, 50, n_ts_points)).round(2),
        'temperature': 20 + 15 * np.sin(2 * np.pi * np.arange(n_ts_points) / 365.25) + np.random.normal(0, 2, n_ts_points),
        'sales_volume': np.maximum(values * 0.8 + np.random.normal(0, 5, n_ts_points), 0).round().astype(int),
        'customer_count': np.maximum((values * 0.6 + np.random.normal(0, 3, n_ts_points)).round().astype(int), 0),
        'day_of_week': date_range.day_name(),
        'month': date_range.month,
        'quarter': date_range.quarter,
        'is_holiday': np.random.choice([0, 1], n_ts_points, p=[0.95, 0.05])
    })

    # Add some missing values randomly
    missing_indices = np.random.choice(
        n_ts_points, size=int(0.02 * n_ts_points), replace=False)
    ts_data.loc[missing_indices[:10], 'revenue'] = np.nan
    ts_data.loc[missing_indices[10:15], 'temperature'] = np.nan

    # Add weekend effect to some metrics
    weekend_mask = ts_data['date'].dt.weekday >= 5
    ts_data.loc[weekend_mask, 'website_visits'] *= 0.7
    ts_data.loc[weekend_mask, 'customer_count'] *= 0.8

    ts_data.to_csv(f"{data_dir}/time_series_data.csv", index=False)
    print(f"✓ Created time_series_data.csv ({len(ts_data)} rows)")

    print(f"\n🎉 Sample datasets created in '{data_dir}/' directory!")
    print("\nDataset descriptions:")
    print("1. sales_data.csv - E-commerce sales with mixed data types and missing values")
    print("2. student_performance.csv - Academic performance with correlated scores")
    print("3. messy_data.csv - Small dataset with high missing value percentage")
    print("4. high_cardinality_data.csv - Transaction data with many unique values")
    print("5. time_series_data.csv - Multi-variate time series with trends and seasonality")
    print("\nTo test the app:")
    print("1. Run: streamlit run app.py")
    print("2. Upload any of these CSV files")
    print("3. Explore the visualizations!")


if __name__ == "__main__":
    create_sample_datasets()
