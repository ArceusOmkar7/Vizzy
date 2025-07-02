# 📊 Vizzy

A **developer-friendly**, **Streamlit-powered** data visualization assistant that lets you drop in any CSV or Excel file and instantly get comprehensive data insights.

## 🎯 Features

- **📁 Easy File Upload**: Support for CSV and Excel files
- **📋 Data Overview**: Clean data preview, types, and basic statistics
- **🎯 Data Quality Scoring**: Comprehensive dataset health assessment with actionable insights
- **❓ Missing Values Analysis**: Interactive heatmaps and detailed null analysis
- **📊 Distribution Analysis**: Histograms and box plots for numeric data
- **🔗 Correlation Analysis**: Correlation heatmaps with strength insights
- **📂 Categorical Analysis**: Value counts and category distribution analysis
- **📈 Time Series Analysis**: Trend analysis, seasonality detection, and temporal patterns
- **🎨 Custom Color Palettes**: Choose from 12+ beautiful color schemes for all visualizations
- **🎨 Modern Interface**: Clean, tab-based UI focused on essential insights
- **📱 Responsive Design**: Works seamlessly on any screen size

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd "Vizzy"
   ```

2. **Install dependencies:**

   Using UV (recommended):

   ```bash
   uv sync
   ```

   Using pip:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   python run.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

> **Note:** The `run.py` script automatically handles dependency installation and sample data creation.

### Generate Sample Datasets (Optional)

Run

```bash
python create_sample_data.py
```

## 📖 Usage

1. **Upload your data**: Use the sidebar to upload a CSV or Excel file
2. **Customize appearance**: Expand the "🎨 Color Palette Settings" in the sidebar to choose your preferred color theme
3. **Explore with tabs**: Navigate through different analysis tabs:
   - **📋 Data Overview**: View data preview, types, and basic metrics
   - **❓ Missing Values**: Analyze null patterns with heatmaps and charts
   - **📊 Distributions**: Explore numeric data distributions
   - **🔗 Correlations**: Discover relationships between numeric variables
   - **📂 Categories**: Analyze categorical data and value frequencies
   - **📈 Time Series**: Analyze temporal patterns, trends, and seasonality
4. **Interactive analysis**: Each tab provides focused, relevant insights
5. **Export insights**: View summary tables and save analysis results

### Supported File Formats

- **.csv**: Comma-separated values (UTF-8 and Latin-1 encoding)
- **.xlsx/.xls**: Excel files (all modern versions)

## 🗂️ Project Structure

```
vizzy/
├── app.py                    # Main Streamlit application with tab interface
├── style.py                  # Global styling and themes
├── requirements.txt          # Python dependencies
├── pyproject.toml           # UV/pip project configuration
├── .streamlit/              # Streamlit configuration
│   └── config.toml
├── utils/                   # Pure Python utilities
│   ├── __init__.py
│   ├── data_checks.py       # Data quality analysis functions
│   ├── file_loader.py       # File loading and caching
│   └── quality_engine.py    # Comprehensive data quality scoring engine
├── visuals/                 # Visualization functions
│   ├── __init__.py
│   ├── nulls.py             # Missing values visualizations
│   ├── summary.py           # Data overview charts
│   ├── distributions.py     # Distribution analysis
│   ├── correlation.py       # Correlation analysis
│   ├── categories.py        # Categorical data analysis
│   ├── time_series.py       # Time series analysis and forecasting
│   └── quality_score.py     # Data quality visualization components
├── components/              # Tab-based UI components
│   ├── __init__.py
│   ├── data_overview.py     # Data overview tab
│   ├── missing_values.py    # Missing values analysis tab
│   ├── distributions.py     # Distribution analysis tab
│   ├── correlations.py      # Correlation analysis tab
│   ├── categorical.py       # Categorical analysis tab
│   ├── time_series.py       # Time series analysis tab
│   └── color_settings.py    # Color palette configuration
└── sample_data/             # Sample datasets for testing
    ├── sales_data.csv
    ├── student_performance.csv
    ├── messy_data.csv
    ├── high_cardinality_data.csv
    └── time_series_data.csv
```

## 🎨 Customization

### Themes

The app uses a consistent color scheme defined in `style.py`. You can customize:

- **Colors**: Modify the color palette in `get_color_palette()`
- **Chart styles**: Update `setup_plot_style()` for different themes
- **Streamlit theme**: Edit `.streamlit/config.toml`

### Adding New Tab Components

1. Create a new tab component in `components/` (e.g., `new_analysis.py`)
2. Add the visualization functions to the appropriate `visuals/*.py` module
3. Import and add the tab to `app.py` in the main tab interface
4. Follow the focused, single-purpose design pattern

## 📊 Analysis Types

### Data Overview Tab 📋

- **Data Quality Assessment**: Overall quality score with letter grade (A-F)
- **Quality Dimensions**: Breakdown across completeness, consistency, accuracy, uniqueness, and validity
- **Interactive Quality Gauge**: Visual quality score with color-coded status
- **Actionable Recommendations**: Specific suggestions for improving data quality
- **Column Quality Heatmap**: Visual overview of quality issues by column
- **Data Preview**: First N rows with customizable display count
- **Basic Metrics**: Rows, columns, memory usage, missing values count
- **Data Type Summary**: Visual breakdown of column types
- **Column Summary**: Detailed statistics for each column

### Missing Values Analysis Tab ❓

- **Missing Values Heatmap**: Visual pattern detection for null values
- **Missing Values Bar Chart**: Count and percentage of nulls per column
- **Null Pattern Analysis**: Insights about missing data distribution

### Distribution Analysis Tab 📊

- **Histograms**: Data distribution visualization for numeric columns
- **Box Plots**: Quartile analysis and outlier detection
- **Statistical Summary**: Key statistics (mean, std, quartiles) for each column

### Correlation Analysis Tab 🔗

- **Correlation Heatmap**: Clean matrix visualization with customizable methods
- **Strong Correlations Table**: Ranked relationships above threshold
- **Quick Insights**: Strongest correlation and average correlation metrics

### Categorical Analysis Tab 📂

- **Value Counts**: Top-K categories with frequency counts
- **Category Analysis**: Detailed breakdown per categorical column
- **Data Quality Insights**: Cardinality and balance analysis

### Time Series Analysis Tab 📈

- **Time Series Overview**: Interactive line plots with trend analysis
- **Temporal Patterns**: Analysis by month, day of week, hour, and year
- **Rolling Statistics**: Moving averages and rolling standard deviation
- **Seasonal Decomposition**: Advanced trend and seasonality breakdown (requires statsmodels)
- **DateTime Detection**: Automatic identification and conversion of date columns

## 🎯 Data Quality Scoring

Vizzy includes a comprehensive data quality assessment engine that automatically evaluates your dataset across multiple dimensions and provides actionable insights for improvement.

### Quality Dimensions

The scoring system evaluates your data across **5 key dimensions**:

1. **📋 Completeness (25% weight)**
   - Analyzes missing values across all columns
   - Provides weighted scoring based on missing data patterns
   - Identifies columns with critical missing data (>50%)

2. **🔧 Consistency (20% weight)**
   - Detects mixed data types within columns
   - Identifies formatting issues (whitespace, case inconsistencies)
   - Validates data type appropriateness

3. **🎯 Accuracy (25% weight)**
   - Statistical outlier detection using IQR method
   - Validates logical constraints (e.g., no negative ages)
   - Identifies suspicious patterns in categorical data

4. **🔍 Uniqueness (15% weight)**
   - Duplicate row detection and quantification
   - ID column validation for uniqueness
   - Low uniqueness pattern identification

5. **✅ Validity (15% weight)**
   - Format validation for emails, dates, and other structured data
   - Range validation for temporal data
   - Detection of numeric data stored as text

### Quality Scoring Output

- **Overall Score**: 0-100 with letter grades (A, B, C, D, F)
- **Visual Dashboard**: Interactive gauge with color-coded status
- **Dimension Breakdown**: Detailed scores for each quality aspect
- **Actionable Recommendations**: Specific steps to improve data quality
- **Column-Level Analysis**: Individual quality scores and issues per column
- **Exportable Reports**: Download detailed quality assessments as CSV

### Quality Grades

- **A (90-100)**: Excellent quality, ready for analysis
- **B (80-89)**: Good quality with minor issues
- **C (70-79)**: Fair quality, some cleaning recommended
- **D (60-69)**: Poor quality, substantial preprocessing needed
- **F (0-59)**: Very poor quality, major cleaning required

### Interactive Features

- **Quality Gauge**: Real-time visual scoring with color indicators
- **Heatmaps**: Column-level quality visualization (for datasets ≤20 columns)
- **Expandable Reports**: Detailed quality breakdowns and recommendations
- **Download Options**: Export quality reports for documentation

## ⚡ Performance & Simplicity

The new tab-based interface automatically handles performance optimization:

- **Automatic sampling** for large datasets (>10,000 rows)
- **Smart column limits** for categorical analysis (max 4 columns)
- **Optimized visualizations** with essential insights only
- **Streamlined workflow** reduces cognitive load and decision fatigue

## 🛠️ Development

### Running in Development Mode

```bash
python run.py
```

Or run Streamlit directly:

```bash
streamlit run app.py --logger.level=debug
```

### Adding Dependencies

Using UV:

```bash
uv add package_name
```

Using pip:

```bash
pip install package_name
# Then update requirements.txt
```

## 🔮 Future Enhancements

- [x] **Custom Color Palettes**: User-selectable themes for all visualizations ✅
- [x] **Time Series Analysis**: Comprehensive temporal analysis with trends and patterns ✅
- [x] **Data Quality Scoring**: Overall dataset health metrics ✅
- [ ] **PDF Export**: Generate downloadable reports
- [ ] **Data Preprocessing Suggestions**: Automated recommendations

## 🙋‍♀️ Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
