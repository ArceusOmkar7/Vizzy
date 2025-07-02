"""
Data Preprocessing Suggestions Engine for Vizzy

Provides intelligent recommendations for data cleaning and preprocessing.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import warnings
warnings.filterwarnings('ignore')


class PreprocessingSuggestionEngine:
    """
    Intelligent preprocessing suggestions engine.

    Analyzes data and provides actionable recommendations for:
    - Missing value handling
    - Outlier treatment
    - Feature scaling/normalization
    - Encoding strategies
    - Data type optimization
    - Feature engineering
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

    def generate_all_suggestions(self) -> Dict[str, Any]:
        """Generate comprehensive preprocessing suggestions."""

        suggestions = {
            'missing_values': self._suggest_missing_value_handling(),
            'outliers': self._suggest_outlier_treatment(),
            'scaling': self._suggest_feature_scaling(),
            'encoding': self._suggest_categorical_encoding(),
            'data_types': self._suggest_data_type_optimization(),
            'feature_engineering': self._suggest_feature_engineering(),
            'duplicates': self._suggest_duplicate_handling(),
            'validation': self._suggest_data_validation()
        }

        # Calculate priority scores
        suggestions['priorities'] = self._calculate_priorities(suggestions)
        suggestions['summary'] = self._generate_summary(suggestions)

        return suggestions

    def _suggest_missing_value_handling(self) -> Dict[str, Any]:
        """Suggest strategies for handling missing values."""
        missing_suggestions = []
        column_strategies = {}

        missing_counts = self.df.isnull().sum()
        missing_cols = missing_counts[missing_counts > 0]

        if len(missing_cols) == 0:
            return {
                'suggestions': ["✅ No missing values detected - no action needed"],
                'column_strategies': {},
                'priority': 0,
                'code_snippets': []
            }

        for col in missing_cols.index:
            missing_pct = (missing_cols[col] / len(self.df)) * 100
            col_type = self.df[col].dtype

            # Determine strategy based on missing percentage and data type
            if missing_pct > 70:
                strategy = "Consider removing column (>70% missing)"
                code = f"df = df.drop('{col}', axis=1)  # Remove high-missing column"
            elif missing_pct > 50:
                strategy = "High missing data - use domain knowledge or advanced imputation"
                code = f"# Consider specialized imputation for '{col}' (e.g., KNN, model-based)"
            elif col_type in ['int64', 'float64']:
                if missing_pct < 5:
                    strategy = "Forward fill or median imputation"
                    code = f"df['{col}'].fillna(df['{col}'].median(), inplace=True)  # Median imputation"
                else:
                    strategy = "Median/mean imputation or interpolation"
                    code = f"df['{col}'].interpolate(method='linear', inplace=True)  # Linear interpolation"
            elif col_type == 'object':
                if missing_pct < 10:
                    strategy = "Mode imputation or 'Unknown' category"
                    code = f"df['{col}'].fillna('Unknown', inplace=True)  # Fill with 'Unknown'"
                else:
                    strategy = "Create 'Missing' category or use frequent value"
                    code = f"df['{col}'].fillna(df['{col}'].mode()[0], inplace=True)  # Mode imputation"
            else:
                strategy = "Forward/backward fill for temporal data"
                code = f"df['{col}'].ffill(inplace=True)  # Forward fill"

            column_strategies[col] = {
                'missing_percentage': round(missing_pct, 1),
                'strategy': strategy,
                'code': code
            }

            missing_suggestions.append(
                f"**{col}** ({missing_pct:.1f}% missing): {strategy}")

        # General suggestions
        if len(missing_cols) > 5:
            missing_suggestions.append(
                "📊 Consider using advanced imputation techniques (KNN, MICE) for multiple missing columns")

        priority = min(100, len(missing_cols) * 10 +
                       max(missing_counts) / len(self.df) * 50)

        return {
            'suggestions': missing_suggestions,
            'column_strategies': column_strategies,
            'priority': round(priority, 1),
            'code_snippets': [strategy['code'] for strategy in column_strategies.values()]
        }

    def _suggest_outlier_treatment(self) -> Dict[str, Any]:
        """Suggest strategies for handling outliers."""
        outlier_suggestions = []
        column_strategies = {}

        if not self.numeric_cols:
            return {
                'suggestions': ["ℹ️ No numeric columns for outlier analysis"],
                'column_strategies': {},
                'priority': 0,
                'code_snippets': []
            }

        for col in self.numeric_cols:
            if self.df[col].notna().sum() < 3:
                continue

            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = self.df[(self.df[col] < lower_bound)
                               | (self.df[col] > upper_bound)][col]
            outlier_pct = (len(outliers) / len(self.df[col].dropna())) * 100

            if outlier_pct > 1:  # More than 1% outliers
                if outlier_pct > 15:
                    strategy = "High outlier rate - check data validity, consider log transformation"
                    code = f"# Check '{col}' data validity - high outlier rate ({outlier_pct:.1f}%)\n" + \
                           f"df['{col}_log'] = np.log1p(df['{col}'])  # Log transformation"
                elif outlier_pct > 5:
                    strategy = "Consider capping at percentiles or transformation"
                    code = f"# Cap outliers for '{col}'\n" + \
                           f"q95 = df['{col}'].quantile(0.95)\n" + \
                           f"q05 = df['{col}'].quantile(0.05)\n" + \
                           f"df['{col}'] = df['{col}'].clip(lower=q05, upper=q95)"
                else:
                    strategy = "Remove outliers or use robust scaling"
                    code = f"# Remove outliers for '{col}'\n" + \
                           f"Q1, Q3 = df['{col}'].quantile([0.25, 0.75])\n" + \
                           f"IQR = Q3 - Q1\n" + \
                           f"df = df[~((df['{col}'] < (Q1 - 1.5 * IQR)) | (df['{col}'] > (Q3 + 1.5 * IQR)))]"

                column_strategies[col] = {
                    'outlier_percentage': round(outlier_pct, 1),
                    'outlier_count': len(outliers),
                    'strategy': strategy,
                    'code': code
                }

                outlier_suggestions.append(
                    f"**{col}** ({outlier_pct:.1f}% outliers): {strategy}")

        if not column_strategies:
            outlier_suggestions.append(
                "✅ No significant outliers detected in numeric columns")
            priority = 0
        else:
            priority = min(80, len(column_strategies) * 15)
            if len(column_strategies) > 3:
                outlier_suggestions.append(
                    "🔍 Consider using robust scaling methods for multiple outlier columns")

        return {
            'suggestions': outlier_suggestions,
            'column_strategies': column_strategies,
            'priority': round(priority, 1),
            'code_snippets': [strategy['code'] for strategy in column_strategies.values()]
        }

    def _suggest_feature_scaling(self) -> Dict[str, Any]:
        """Suggest feature scaling strategies."""
        scaling_suggestions = []
        column_strategies = {}

        if not self.numeric_cols:
            return {
                'suggestions': ["ℹ️ No numeric columns for scaling analysis"],
                'column_strategies': {},
                'priority': 0,
                'code_snippets': []
            }

        # Analyze scale differences
        scales = {}
        for col in self.numeric_cols:
            if self.df[col].notna().sum() > 0:
                scales[col] = {
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'range': self.df[col].max() - self.df[col].min(),
                    'std': self.df[col].std()
                }

        if not scales:
            return {
                'suggestions': ["ℹ️ No valid numeric data for scaling analysis"],
                'column_strategies': {},
                'priority': 0,
                'code_snippets': []
            }

        # Check if scaling is needed
        max_range = max([s['range']
                        for s in scales.values() if pd.notna(s['range'])])
        min_range = min([s['range'] for s in scales.values()
                        if pd.notna(s['range']) and s['range'] > 0])

        if max_range / min_range > 100:  # Large scale difference
            scaling_suggestions.append(
                "📏 **High scale variance detected** - scaling recommended for ML algorithms")

            # Suggest appropriate scaling method
            has_negative = any(s['min'] < 0 for s in scales.values())
            has_outliers = any(col in [cs for cs in column_strategies.keys()]
                               for cs in self._suggest_outlier_treatment()['column_strategies'])

            if has_negative or has_outliers:
                method = "StandardScaler (Z-score normalization)"
                code = """from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
numeric_cols = """ + str(self.numeric_cols) + """
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])"""
            else:
                method = "MinMaxScaler (0-1 normalization)"
                code = """from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
numeric_cols = """ + str(self.numeric_cols) + """
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])"""

            scaling_suggestions.append(f"🎯 **Recommended method**: {method}")

            column_strategies['all_numeric'] = {
                'method': method,
                'reason': f"Scale difference ratio: {max_range/min_range:.1f}x",
                'code': code
            }

            priority = 60
        else:
            scaling_suggestions.append(
                "✅ Numeric columns have similar scales - scaling may not be necessary")
            priority = 10

        return {
            'suggestions': scaling_suggestions,
            'column_strategies': column_strategies,
            'priority': priority,
            'code_snippets': [strategy['code'] for strategy in column_strategies.values()]
        }

    def _suggest_categorical_encoding(self) -> Dict[str, Any]:
        """Suggest categorical encoding strategies."""
        encoding_suggestions = []
        column_strategies = {}

        if not self.categorical_cols:
            return {
                'suggestions': ["ℹ️ No categorical columns for encoding analysis"],
                'column_strategies': {},
                'priority': 0,
                'code_snippets': []
            }

        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                unique_count = self.df[col].nunique()
                null_count = self.df[col].isnull().sum()

                # Determine encoding strategy
                if unique_count <= 2:
                    strategy = "Label Encoding (binary categories)"
                    code = f"""from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['{col}_encoded'] = le.fit_transform(df['{col}'].fillna('Missing'))"""
                elif unique_count <= 10:
                    strategy = "One-Hot Encoding (low cardinality)"
                    code = f"""df_encoded = pd.get_dummies(df['{col}'], prefix='{col}', dummy_na=True)
df = pd.concat([df, df_encoded], axis=1)
df = df.drop('{col}', axis=1)"""
                elif unique_count <= 50:
                    strategy = "Target Encoding or Frequency Encoding (medium cardinality)"
                    code = f"""# Frequency encoding for '{col}'
freq_map = df['{col}'].value_counts().to_dict()
df['{col}_freq'] = df['{col}'].map(freq_map)"""
                else:
                    strategy = "High cardinality - consider grouping rare categories"
                    code = f"""# Group rare categories for '{col}'
value_counts = df['{col}'].value_counts()
rare_categories = value_counts[value_counts < 10].index
df['{col}_grouped'] = df['{col}'].replace(rare_categories, 'Other')"""

                column_strategies[col] = {
                    'unique_count': unique_count,
                    'null_count': null_count,
                    'strategy': strategy,
                    'code': code
                }

                encoding_suggestions.append(
                    f"**{col}** ({unique_count} categories): {strategy}")

        if column_strategies:
            priority = min(70, len(column_strategies) * 15)
            encoding_suggestions.append(
                "🤖 **Note**: Encoding is essential for machine learning algorithms")
        else:
            priority = 0

        return {
            'suggestions': encoding_suggestions,
            'column_strategies': column_strategies,
            'priority': priority,
            'code_snippets': [strategy['code'] for strategy in column_strategies.values()]
        }

    def _suggest_data_type_optimization(self) -> Dict[str, Any]:
        """Suggest data type optimizations for memory efficiency."""
        optimization_suggestions = []
        column_strategies = {}

        current_memory = self.df.memory_usage(deep=True).sum() / 1024**2  # MB
        potential_savings = 0

        for col in self.df.columns:
            current_dtype = self.df[col].dtype
            optimization = None

            if current_dtype == 'object':
                # Check if it's actually numeric
                try:
                    numeric_values = pd.to_numeric(
                        self.df[col], errors='coerce')
                    if numeric_values.notna().sum() / len(self.df) > 0.9:  # 90% numeric
                        optimization = {
                            'current': 'object',
                            'suggested': 'float64 or int64',
                            'reason': 'Contains mostly numeric values',
                            'code': f"df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce')"
                        }
                except:
                    pass

                # Check if it should be categorical
                if optimization is None and self.df[col].nunique() / len(self.df) < 0.5:
                    optimization = {
                        'current': 'object',
                        'suggested': 'category',
                        'reason': 'Low cardinality - category saves memory',
                        'code': f"df['{col}'] = df['{col}'].astype('category')"
                    }

            elif current_dtype in ['int64', 'float64']:
                # Check if we can downcast
                min_val = self.df[col].min()
                max_val = self.df[col].max()

                if current_dtype == 'int64':
                    if min_val >= 0 and max_val <= 255:
                        suggested = 'uint8'
                    elif min_val >= -128 and max_val <= 127:
                        suggested = 'int8'
                    elif min_val >= 0 and max_val <= 65535:
                        suggested = 'uint16'
                    elif min_val >= -32768 and max_val <= 32767:
                        suggested = 'int16'
                    elif min_val >= 0 and max_val <= 4294967295:
                        suggested = 'uint32'
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        suggested = 'int32'
                    else:
                        suggested = None

                    if suggested and suggested != current_dtype:
                        optimization = {
                            'current': str(current_dtype),
                            'suggested': suggested,
                            'reason': f'Range fits in smaller type: {min_val} to {max_val}',
                            'code': f"df['{col}'] = df['{col}'].astype('{suggested}')"
                        }

                elif current_dtype == 'float64':
                    # Check if it can be float32
                    if abs(min_val) < 3.4e38 and abs(max_val) < 3.4e38:
                        optimization = {
                            'current': 'float64',
                            'suggested': 'float32',
                            'reason': 'Values fit in float32 precision',
                            'code': f"df['{col}'] = df['{col}'].astype('float32')"
                        }

            if optimization:
                column_strategies[col] = optimization
                current_size = self.df[col].memory_usage(deep=True) / 1024**2
                # Estimate savings (rough approximation)
                if 'int8' in optimization['suggested'] or 'uint8' in optimization['suggested']:
                    potential_savings += current_size * 0.875  # ~87.5% savings
                elif 'int16' in optimization['suggested'] or 'uint16' in optimization['suggested']:
                    potential_savings += current_size * 0.75   # ~75% savings
                elif 'int32' in optimization['suggested'] or 'uint32' in optimization['suggested']:
                    potential_savings += current_size * 0.5    # ~50% savings
                elif 'float32' in optimization['suggested']:
                    potential_savings += current_size * 0.5    # ~50% savings
                elif 'category' in optimization['suggested']:
                    potential_savings += current_size * 0.3    # ~30% savings

                optimization_suggestions.append(
                    f"**{col}**: {optimization['current']} → {optimization['suggested']} ({optimization['reason']})"
                )

        if potential_savings > 0.1:  # More than 0.1 MB savings
            optimization_suggestions.insert(
                0, f"💾 **Potential memory savings**: ~{potential_savings:.1f} MB ({potential_savings/current_memory*100:.1f}%)")
            priority = min(50, potential_savings * 10)
        else:
            optimization_suggestions.append(
                "✅ Data types are already well-optimized")
            priority = 5

        return {
            'suggestions': optimization_suggestions,
            'column_strategies': column_strategies,
            'priority': round(priority, 1),
            'code_snippets': [strategy['code'] for strategy in column_strategies.values()],
            'memory_savings': round(potential_savings, 2)
        }

    def _suggest_feature_engineering(self) -> Dict[str, Any]:
        """Suggest feature engineering opportunities."""
        feature_suggestions = []
        column_strategies = {}

        # DateTime feature engineering
        if self.datetime_cols:
            for col in self.datetime_cols:
                strategies = []
                codes = []

                strategies.append(
                    "Extract date components (year, month, day, weekday)")
                codes.append(f"""# Extract datetime features from '{col}'
df['{col}_year'] = df['{col}'].dt.year
df['{col}_month'] = df['{col}'].dt.month
df['{col}_day'] = df['{col}'].dt.day
df['{col}_weekday'] = df['{col}'].dt.weekday""")

                strategies.append(
                    "Create time-based features (is_weekend, quarter, hour)")
                codes.append(f"""# Create time-based features from '{col}'
df['{col}_is_weekend'] = df['{col}'].dt.weekday >= 5
df['{col}_quarter'] = df['{col}'].dt.quarter
if df['{col}'].dt.hour.notna().any():
    df['{col}_hour'] = df['{col}'].dt.hour""")

                column_strategies[col] = {
                    'type': 'datetime',
                    'strategies': strategies,
                    'code': '\n\n'.join(codes)
                }

                feature_suggestions.append(
                    f"**{col}** (datetime): Extract temporal features")

        # Numeric feature engineering
        skewed_cols = []
        for col in self.numeric_cols:
            if self.df[col].notna().sum() > 0:
                skewness = abs(self.df[col].skew())
                if skewness > 1:  # Highly skewed
                    skewed_cols.append(col)

        if skewed_cols:
            strategies = ["Apply log transformation to reduce skewness"]
            code = f"""# Log transformation for skewed columns
import numpy as np
skewed_cols = {skewed_cols}
for col in skewed_cols:
    df[f'{{col}}_log'] = np.log1p(df[col])  # log1p handles zeros"""

            column_strategies['skewed_numeric'] = {
                'type': 'transformation',
                'columns': skewed_cols,
                'strategies': strategies,
                'code': code
            }

            feature_suggestions.append(
                f"**Skewed columns** ({len(skewed_cols)}): Apply log transformation")

        # Polynomial features for small numeric datasets
        if len(self.numeric_cols) <= 5 and self.n_rows <= 10000:
            strategies = [
                "Create polynomial features for better model performance"]
            code = f"""# Create polynomial features (degree=2)
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
numeric_cols = {self.numeric_cols}
poly_features = poly.fit_transform(df[numeric_cols])
poly_feature_names = poly.get_feature_names_out(numeric_cols)
df_poly = pd.DataFrame(poly_features, columns=poly_feature_names, index=df.index)
df = pd.concat([df, df_poly], axis=1)"""

            column_strategies['polynomial'] = {
                'type': 'polynomial',
                'strategies': strategies,
                'code': code
            }

            feature_suggestions.append(
                "**Numeric columns**: Consider polynomial features for non-linear relationships")

        # Binning for continuous variables
        high_cardinality_numeric = []
        for col in self.numeric_cols:
            if self.df[col].nunique() > 50:
                high_cardinality_numeric.append(col)

        if high_cardinality_numeric:
            strategies = ["Create bins for high-cardinality numeric features"]
            code = f"""# Create bins for high-cardinality numeric columns
high_card_cols = {high_cardinality_numeric}
for col in high_card_cols:
    df[f'{{col}}_binned'] = pd.cut(df[col], bins=5, labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])"""

            column_strategies['binning'] = {
                'type': 'binning',
                'columns': high_cardinality_numeric,
                'strategies': strategies,
                'code': code
            }

            feature_suggestions.append(
                f"**High-cardinality numeric** ({len(high_cardinality_numeric)}): Create categorical bins")

        if not feature_suggestions:
            feature_suggestions.append(
                "ℹ️ Limited feature engineering opportunities with current data structure")
            priority = 5
        else:
            priority = min(40, len(column_strategies) * 10)

        return {
            'suggestions': feature_suggestions,
            'column_strategies': column_strategies,
            'priority': priority,
            'code_snippets': [strategy['code'] for strategy in column_strategies.values()]
        }

    def _suggest_duplicate_handling(self) -> Dict[str, Any]:
        """Suggest strategies for handling duplicates."""
        duplicate_count = self.df.duplicated().sum()
        duplicate_pct = (duplicate_count / len(self.df)) * 100

        if duplicate_count == 0:
            return {
                'suggestions': ["✅ No duplicate rows detected"],
                'strategy': None,
                'priority': 0,
                'code_snippets': []
            }

        suggestions = [
            f"🔍 **{duplicate_count} duplicate rows found** ({duplicate_pct:.1f}% of data)"]

        if duplicate_pct > 20:
            strategy = "High duplicate rate - investigate data collection process"
            code = "# Investigate duplicates\nprint(df[df.duplicated()].head())\n# Remove after investigation\n# df = df.drop_duplicates()"
        elif duplicate_pct > 5:
            strategy = "Moderate duplicates - remove after verification"
            code = "# Remove duplicate rows\ndf = df.drop_duplicates(keep='first')\nprint(f'Removed {duplicate_count} duplicate rows')"
        else:
            strategy = "Remove duplicate rows"
            code = "df = df.drop_duplicates(keep='first')"

        suggestions.append(f"🎯 **Recommended action**: {strategy}")

        priority = min(60, duplicate_pct * 2)

        return {
            'suggestions': suggestions,
            'strategy': strategy,
            'priority': round(priority, 1),
            'code_snippets': [code]
        }

    def _suggest_data_validation(self) -> Dict[str, Any]:
        """Suggest data validation steps."""
        validation_suggestions = []
        validation_checks = {}

        # Check for potential data entry errors
        for col in self.numeric_cols:
            if self.df[col].notna().sum() > 0:
                # Check for impossible values
                if 'age' in col.lower():
                    invalid = self.df[(self.df[col] < 0) |
                                      (self.df[col] > 150)]
                    if len(invalid) > 0:
                        validation_checks[col] = f"Invalid age values: {len(invalid)} rows"
                        validation_suggestions.append(
                            f"**{col}**: Check {len(invalid)} potentially invalid age values")

                elif 'percentage' in col.lower() or 'percent' in col.lower():
                    invalid = self.df[(self.df[col] < 0) |
                                      (self.df[col] > 100)]
                    if len(invalid) > 0:
                        validation_checks[col] = f"Invalid percentage values: {len(invalid)} rows"
                        validation_suggestions.append(
                            f"**{col}**: Check {len(invalid)} percentage values outside 0-100 range")

        # Check for formatting issues in text columns
        for col in self.categorical_cols:
            if self.df[col].dtype == 'object':
                # Check for mixed case
                non_null_values = self.df[col].dropna().astype(str)
                if len(non_null_values) > 0:
                    unique_values = non_null_values.unique()
                    lower_values = [v.lower() for v in unique_values]
                    if len(set(lower_values)) < len(unique_values):
                        validation_checks[col] = "Case inconsistencies detected"
                        validation_suggestions.append(
                            f"**{col}**: Standardize text case (found case inconsistencies)")

                # Check for leading/trailing whitespace
                has_whitespace = (non_null_values !=
                                  non_null_values.str.strip()).any()
                if has_whitespace:
                    validation_checks[col] = "Whitespace issues detected"
                    validation_suggestions.append(
                        f"**{col}**: Remove leading/trailing whitespace")

        if not validation_suggestions:
            validation_suggestions.append(
                "✅ No obvious data validation issues detected")
            priority = 0
        else:
            priority = min(50, len(validation_checks) * 10)
            validation_suggestions.insert(
                0, "🔍 **Data validation recommended**:")

        code_snippets = []
        if validation_checks:
            code_snippets.append("""# Data validation and cleaning
# Remove leading/trailing whitespace from text columns
text_cols = df.select_dtypes(include=['object']).columns
for col in text_cols:
    df[col] = df[col].str.strip()

# Standardize text case (example for specific columns)
# df['column_name'] = df['column_name'].str.title()  # Title case
# df['column_name'] = df['column_name'].str.lower()  # Lower case""")

        return {
            'suggestions': validation_suggestions,
            'validation_checks': validation_checks,
            'priority': round(priority, 1),
            'code_snippets': code_snippets
        }

    def _calculate_priorities(self, suggestions: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Calculate and rank suggestion priorities."""
        priorities = []

        for category, data in suggestions.items():
            if isinstance(data, dict) and 'priority' in data:
                priorities.append(
                    (category.replace('_', ' ').title(), data['priority']))

        # Sort by priority (highest first)
        priorities.sort(key=lambda x: x[1], reverse=True)
        return priorities

    def _generate_summary(self, suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of preprocessing needs."""
        total_issues = 0
        high_priority_issues = []

        for category, data in suggestions.items():
            if isinstance(data, dict) and 'priority' in data:
                priority = data['priority']
                if priority > 50:
                    high_priority_issues.append(
                        category.replace('_', ' ').title())
                if priority > 0:
                    total_issues += 1

        if total_issues == 0:
            summary_text = "🎉 Your data is well-prepared! Only minor optimizations suggested."
            urgency = "Low"
        elif len(high_priority_issues) == 0:
            summary_text = f"✅ Good data quality with {total_issues} minor preprocessing opportunities."
            urgency = "Low"
        elif len(high_priority_issues) <= 2:
            summary_text = f"⚠️ {len(high_priority_issues)} high-priority preprocessing steps recommended."
            urgency = "Medium"
        else:
            summary_text = f"🚨 {len(high_priority_issues)} critical preprocessing steps needed before analysis."
            urgency = "High"

        return {
            'text': summary_text,
            'urgency': urgency,
            'total_issues': total_issues,
            'high_priority_count': len(high_priority_issues),
            'high_priority_areas': high_priority_issues
        }


def generate_preprocessing_script(suggestions: Dict[str, Any]) -> str:
    """Generate a complete preprocessing script based on suggestions."""
    script_lines = [
        "# Automated Data Preprocessing Script",
        "# Generated by Vizzy Preprocessing Engine",
        "",
        "import pandas as pd",
        "import numpy as np",
        "from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder",
        "",
        "# Load your data",
        "# df = pd.read_csv('your_data.csv')  # Replace with your data source",
        "",
    ]

    # Add preprocessing steps in priority order
    for category, data in suggestions.items():
        if isinstance(data, dict) and 'code_snippets' in data and data.get('priority', 0) > 0:
            script_lines.append(
                f"# {category.replace('_', ' ').title()} Processing")
            script_lines.extend(data['code_snippets'])
            script_lines.append("")

    script_lines.extend([
        "# Save processed data",
        "# df.to_csv('processed_data.csv', index=False)",
        "",
        "print('Preprocessing completed!')",
        "print(f'Final dataset shape: {df.shape}')"
    ])

    return "\n".join(script_lines)
