"""
Data Quality Scoring Engine for Vizzy

Provides comprehensive data quality assessment with scoring across multiple dimensions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


class DataQualityEngine:
    """
    Comprehensive data quality assessment engine.

    Evaluates data across multiple quality dimensions:
    - Completeness: Missing values assessment
    - Consistency: Data type and format consistency
    - Accuracy: Outliers and range validation
    - Uniqueness: Duplicate detection
    - Validity: Data format validation
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.n_rows, self.n_cols = df.shape
        self.numeric_cols = df.select_dtypes(
            include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(
            include=['object', 'category']).columns.tolist()
        self.datetime_cols = df.select_dtypes(
            include=['datetime64']).columns.tolist()

    def calculate_overall_score(self) -> Dict[str, Any]:
        """Calculate overall data quality score and detailed breakdown."""

        # Calculate individual dimension scores
        completeness_score = self._calculate_completeness_score()
        consistency_score = self._calculate_consistency_score()
        accuracy_score = self._calculate_accuracy_score()
        uniqueness_score = self._calculate_uniqueness_score()
        validity_score = self._calculate_validity_score()

        # Weighted overall score
        weights = {
            'completeness': 0.25,
            'consistency': 0.20,
            'accuracy': 0.25,
            'uniqueness': 0.15,
            'validity': 0.15
        }

        overall_score = (
            completeness_score['score'] * weights['completeness'] +
            consistency_score['score'] * weights['consistency'] +
            accuracy_score['score'] * weights['accuracy'] +
            uniqueness_score['score'] * weights['uniqueness'] +
            validity_score['score'] * weights['validity']
        )

        return {
            'overall_score': round(overall_score, 1),
            'grade': self._get_quality_grade(overall_score),
            'dimensions': {
                'completeness': completeness_score,
                'consistency': consistency_score,
                'accuracy': accuracy_score,
                'uniqueness': uniqueness_score,
                'validity': validity_score
            },
            'summary': self._generate_summary(overall_score),
            'recommendations': self._generate_recommendations({
                'completeness': completeness_score,
                'consistency': consistency_score,
                'accuracy': accuracy_score,
                'uniqueness': uniqueness_score,
                'validity': validity_score
            })
        }

    def _calculate_completeness_score(self) -> Dict[str, Any]:
        """Calculate completeness score based on missing values."""
        missing_counts = self.df.isnull().sum()
        missing_percentages = (missing_counts / self.n_rows) * 100

        # Column-level completeness
        column_completeness = 100 - missing_percentages

        # Overall completeness (weighted by column importance)
        # Give more weight to columns with less missing data
        weights = 1 / (1 + missing_percentages / 100)
        weighted_completeness = (
            column_completeness * weights).sum() / weights.sum()

        # Issues
        issues = []
        critical_missing = missing_percentages[missing_percentages > 50]
        if len(critical_missing) > 0:
            issues.append(
                f"{len(critical_missing)} columns have >50% missing values")

        moderate_missing = missing_percentages[(
            missing_percentages > 20) & (missing_percentages <= 50)]
        if len(moderate_missing) > 0:
            issues.append(
                f"{len(moderate_missing)} columns have 20-50% missing values")

        return {
            'score': round(weighted_completeness, 1),
            'details': {
                'total_missing_cells': missing_counts.sum(),
                'missing_percentage': round((missing_counts.sum() / (self.n_rows * self.n_cols)) * 100, 2),
                'columns_with_missing': len(missing_counts[missing_counts > 0]),
                'worst_columns': missing_percentages.nlargest(3).to_dict()
            },
            'issues': issues
        }

    def _calculate_consistency_score(self) -> Dict[str, Any]:
        """Calculate consistency score based on data type and format consistency."""
        consistency_issues = []
        consistency_score = 100

        # Check mixed data types in object columns
        mixed_type_columns = []
        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                # Check if column contains mixed types (numbers as strings, etc.)
                non_null_values = self.df[col].dropna()
                if len(non_null_values) > 0:
                    # Check for numeric strings
                    try:
                        pd.to_numeric(non_null_values, errors='raise')
                        mixed_type_columns.append(col)
                    except:
                        pass

        if mixed_type_columns:
            consistency_score -= len(mixed_type_columns) * 5
            consistency_issues.append(
                f"{len(mixed_type_columns)} columns may have mixed data types")

        # Check for inconsistent string formatting
        format_issues = []
        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                non_null_values = self.df[col].dropna().astype(str)
                if len(non_null_values) > 0:
                    # Check for leading/trailing whitespace
                    has_whitespace = (non_null_values !=
                                      non_null_values.str.strip()).any()
                    if has_whitespace:
                        format_issues.append(col)

        if format_issues:
            consistency_score -= len(format_issues) * 3
            consistency_issues.append(
                f"{len(format_issues)} columns have formatting issues (whitespace)")

        # Check for case inconsistency
        case_issues = []
        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                non_null_values = self.df[col].dropna().astype(str)
                if len(non_null_values) > 0:
                    unique_values = non_null_values.unique()
                    lower_values = [v.lower() for v in unique_values]
                    if len(set(lower_values)) < len(unique_values):
                        case_issues.append(col)

        if case_issues:
            consistency_score -= len(case_issues) * 3
            consistency_issues.append(
                f"{len(case_issues)} columns have case inconsistencies")

        consistency_score = max(0, consistency_score)

        return {
            'score': round(consistency_score, 1),
            'details': {
                'mixed_type_columns': mixed_type_columns,
                'format_issue_columns': format_issues,
                'case_issue_columns': case_issues
            },
            'issues': consistency_issues
        }

    def _calculate_accuracy_score(self) -> Dict[str, Any]:
        """Calculate accuracy score based on outliers and data validation."""
        accuracy_issues = []
        accuracy_score = 100

        # Outlier detection for numeric columns
        outlier_columns = {}
        for col in self.numeric_cols:
            if self.df[col].notna().sum() > 0:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = self.df[(self.df[col] < lower_bound) | (
                    self.df[col] > upper_bound)][col]
                outlier_percentage = (
                    len(outliers) / len(self.df[col].dropna())) * 100

                if outlier_percentage > 5:
                    outlier_columns[col] = round(outlier_percentage, 2)
                    # Cap deduction at 20 points
                    accuracy_score -= min(outlier_percentage * 2, 20)

        if outlier_columns:
            accuracy_issues.append(
                f"{len(outlier_columns)} columns have significant outliers (>5%)")

        # Check for impossible values (negative values where they shouldn't be)
        negative_issues = []
        for col in self.numeric_cols:
            if 'age' in col.lower() or 'count' in col.lower() or 'quantity' in col.lower():
                if (self.df[col] < 0).any():
                    negative_issues.append(col)
                    accuracy_score -= 10

        if negative_issues:
            accuracy_issues.append(
                f"{len(negative_issues)} columns have impossible negative values")

        # Check for suspicious patterns in categorical data
        suspicious_categories = []
        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                value_counts = self.df[col].value_counts()
                if len(value_counts) > 0:
                    # Check if one value dominates (>95% of data)
                    if value_counts.iloc[0] / len(self.df) > 0.95:
                        suspicious_categories.append(col)
                        accuracy_score -= 5

        if suspicious_categories:
            accuracy_issues.append(
                f"{len(suspicious_categories)} columns are dominated by single values")

        accuracy_score = max(0, accuracy_score)

        return {
            'score': round(accuracy_score, 1),
            'details': {
                'outlier_columns': outlier_columns,
                'negative_value_columns': negative_issues,
                'suspicious_categorical_columns': suspicious_categories
            },
            'issues': accuracy_issues
        }

    def _calculate_uniqueness_score(self) -> Dict[str, Any]:
        """Calculate uniqueness score based on duplicate detection."""
        uniqueness_issues = []
        uniqueness_score = 100

        # Overall duplicate rows
        duplicate_rows = self.df.duplicated().sum()
        duplicate_percentage = (duplicate_rows / self.n_rows) * 100

        if duplicate_percentage > 0:
            # Cap at 30 points
            uniqueness_score -= min(duplicate_percentage * 3, 30)
            uniqueness_issues.append(
                f"{duplicate_percentage:.1f}% duplicate rows found")

        # Check for potential ID columns with duplicates
        id_columns_with_duplicates = []
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in ['id', 'key', 'identifier']):
                if self.df[col].duplicated().any():
                    id_columns_with_duplicates.append(col)
                    uniqueness_score -= 15

        if id_columns_with_duplicates:
            uniqueness_issues.append(
                f"{len(id_columns_with_duplicates)} ID columns have duplicates")

        # Check for columns with very low uniqueness
        low_uniqueness_columns = {}
        for col in self.df.columns:
            if self.df[col].dtype in ['object', 'category'] or col in self.numeric_cols:
                unique_ratio = self.df[col].nunique(
                ) / len(self.df[col].dropna())
                # Very low uniqueness but not constant
                if unique_ratio < 0.1 and self.df[col].nunique() > 1:
                    low_uniqueness_columns[col] = round(unique_ratio * 100, 1)
                    uniqueness_score -= 5

        if low_uniqueness_columns:
            uniqueness_issues.append(
                f"{len(low_uniqueness_columns)} columns have very low uniqueness (<10%)")

        uniqueness_score = max(0, uniqueness_score)

        return {
            'score': round(uniqueness_score, 1),
            'details': {
                'duplicate_rows': duplicate_rows,
                'duplicate_percentage': round(duplicate_percentage, 2),
                'id_columns_with_duplicates': id_columns_with_duplicates,
                'low_uniqueness_columns': low_uniqueness_columns
            },
            'issues': uniqueness_issues
        }

    def _calculate_validity_score(self) -> Dict[str, Any]:
        """Calculate validity score based on data format validation."""
        validity_issues = []
        validity_score = 100

        # Check for proper email format
        email_columns = []
        for col in self.categorical_cols:
            if 'email' in col.lower() or 'mail' in col.lower():
                if self.df[col].dtype == 'object':
                    non_null_values = self.df[col].dropna()
                    if len(non_null_values) > 0:
                        # Simple email validation
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        valid_emails = non_null_values.str.match(
                            email_pattern, na=False)
                        invalid_percentage = (
                            1 - valid_emails.sum() / len(non_null_values)) * 100
                        if invalid_percentage > 10:
                            email_columns.append(
                                (col, round(invalid_percentage, 1)))
                            validity_score -= min(invalid_percentage, 20)

        if email_columns:
            validity_issues.append(
                f"{len(email_columns)} email columns have invalid formats")

        # Check for reasonable date ranges
        date_issues = []
        for col in self.datetime_cols:
            min_date = self.df[col].min()
            max_date = self.df[col].max()
            if pd.notna(min_date) and pd.notna(max_date):
                # Check for dates in the future (beyond reasonable range)
                current_year = pd.Timestamp.now().year
                if max_date.year > current_year + 10:
                    date_issues.append(col)
                    validity_score -= 10
                # Check for dates too far in the past
                if min_date.year < 1900:
                    date_issues.append(col)
                    validity_score -= 10

        if date_issues:
            validity_issues.append(
                f"{len(date_issues)} date columns have unrealistic values")

        # Check for numeric columns with string values that should be numeric
        numeric_format_issues = []
        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                non_null_values = self.df[col].dropna().astype(str)
                if len(non_null_values) > 0:
                    # Check if most values are numeric strings
                    numeric_like = non_null_values.str.replace(
                        ',', '').str.replace('$', '').str.replace('%', '')
                    try:
                        pd.to_numeric(numeric_like, errors='raise')
                        # If we get here, the column is mostly numeric strings
                        numeric_format_issues.append(col)
                        validity_score -= 5
                    except:
                        pass

        if numeric_format_issues:
            validity_issues.append(
                f"{len(numeric_format_issues)} columns contain numeric data as strings")

        validity_score = max(0, validity_score)

        return {
            'score': round(validity_score, 1),
            'details': {
                'email_format_issues': email_columns,
                'date_range_issues': date_issues,
                'numeric_format_issues': numeric_format_issues
            },
            'issues': validity_issues
        }

    def _get_quality_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_summary(self, score: float) -> str:
        """Generate a summary description of data quality."""
        if score >= 90:
            return "Excellent data quality. Your dataset is well-structured and ready for analysis."
        elif score >= 80:
            return "Good data quality with minor issues. The dataset is suitable for analysis with minimal preprocessing."
        elif score >= 70:
            return "Fair data quality. Some data cleaning recommended before analysis."
        elif score >= 60:
            return "Poor data quality with significant issues. Substantial preprocessing required."
        else:
            return "Very poor data quality. Major data cleaning and validation needed before use."

    def _generate_recommendations(self, dimensions: Dict[str, Dict]) -> List[str]:
        """Generate actionable recommendations based on quality assessment."""
        recommendations = []

        # Completeness recommendations
        if dimensions['completeness']['score'] < 80:
            recommendations.append(
                "📋 Address missing values through imputation or removal strategies")

        # Consistency recommendations
        if dimensions['consistency']['score'] < 80:
            recommendations.append(
                "🔧 Standardize data formats and fix type inconsistencies")

        # Accuracy recommendations
        if dimensions['accuracy']['score'] < 80:
            recommendations.append(
                "🎯 Investigate and handle outliers and suspicious values")

        # Uniqueness recommendations
        if dimensions['uniqueness']['score'] < 80:
            recommendations.append(
                "🔍 Remove duplicate records and review ID column integrity")

        # Validity recommendations
        if dimensions['validity']['score'] < 80:
            recommendations.append("✅ Validate and correct data format issues")

        if not recommendations:
            recommendations.append(
                "🎉 Your data quality is excellent! No major issues detected.")

        return recommendations


def get_column_quality_details(df: pd.DataFrame) -> pd.DataFrame:
    """Get detailed quality metrics for each column."""
    quality_details = []

    for col in df.columns:
        col_data = df[col]

        # Basic metrics
        total_count = len(col_data)
        missing_count = col_data.isnull().sum()
        missing_percentage = (missing_count / total_count) * 100
        unique_count = col_data.nunique()
        unique_percentage = (unique_count / total_count) * 100

        # Data type
        dtype = str(col_data.dtype)

        # Memory usage
        memory_usage = col_data.memory_usage(deep=True) / 1024  # KB

        # Quality score for this column
        column_score = 100

        # Deduct for missing values
        column_score -= missing_percentage * 0.5

        # Deduct for low uniqueness (if not categorical)
        if dtype not in ['object', 'category'] and unique_percentage < 10:
            column_score -= 20

        # Deduct for inconsistencies
        if dtype == 'object':
            # Check for whitespace issues
            non_null_str = col_data.dropna().astype(str)
            if len(non_null_str) > 0:
                has_whitespace = (
                    non_null_str != non_null_str.str.strip()).any()
                if has_whitespace:
                    column_score -= 10

        column_score = max(0, column_score)

        quality_details.append({
            'Column': col,
            'Data Type': dtype,
            'Missing %': round(missing_percentage, 1),
            'Unique Values': unique_count,
            'Unique %': round(unique_percentage, 1),
            'Memory (KB)': round(memory_usage, 1),
            'Quality Score': round(column_score, 1),
            'Issues': _get_column_issues(col_data, missing_percentage, unique_percentage, dtype)
        })

    return pd.DataFrame(quality_details)


def _get_column_issues(col_data, missing_percentage: float, unique_percentage: float, dtype: str) -> str:
    """Identify specific issues for a column."""
    issues = []

    if missing_percentage > 50:
        issues.append("High missing data")
    elif missing_percentage > 20:
        issues.append("Moderate missing data")

    if dtype not in ['object', 'category'] and unique_percentage < 5:
        issues.append("Very low uniqueness")

    if dtype == 'object':
        non_null_str = col_data.dropna().astype(str)
        if len(non_null_str) > 0:
            has_whitespace = (non_null_str != non_null_str.str.strip()).any()
            if has_whitespace:
                issues.append("Formatting issues")

    # Check for outliers in numeric data
    if dtype in ['int64', 'float64'] and col_data.notna().sum() > 0:
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = col_data[(col_data < Q1 - 1.5 * IQR) |
                            (col_data > Q3 + 1.5 * IQR)]
        outlier_percentage = len(outliers) / len(col_data.dropna()) * 100
        if outlier_percentage > 10:
            issues.append("Many outliers")

    return ", ".join(issues) if issues else "No major issues"
