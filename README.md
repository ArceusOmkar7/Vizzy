# 📊 Vizzy

A **developer-friendly**, **Streamlit-powered** data visualization assistant that lets you drop in any CSV or Excel file and instantly get comprehensive data insights.

## 🎯 Features

- **📁 Easy File Upload**: Support for CSV and Excel files
- **📋 Data Overview**: Clean data preview, types, and basic statistics
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
│   └── file_loader.py       # File loading and caching
├── visuals/                 # Visualization functions
│   ├── __init__.py
│   ├── nulls.py             # Missing values visualizations
│   ├── summary.py           # Data overview charts
│   ├── distributions.py     # Distribution analysis
│   ├── correlation.py       # Correlation analysis
│   ├── categories.py        # Categorical data analysis
│   └── time_series.py       # Time series analysis and forecasting
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
- [ ] **PDF Export**: Generate downloadable reports
- [ ] **Machine Learning Insights**: Automated feature importance
- [ ] **Data Quality Scoring**: Overall dataset health metrics
- [ ] **Data Preprocessing Suggestions**: Automated recommendations

## 🙋‍♀️ Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
