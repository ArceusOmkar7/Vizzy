# 📊 Vizzy

A **developer-friendly**, **Streamlit-powered** data visualization assistant that lets you drop in any CSV or Excel file and instantly get comprehensive data insights.

## 🎯 Features

- **📁 Easy File Upload**: Support for CSV and Excel files
- **📋 Data Overview**: Clean data preview, types, and basic statistics
- **🎯 Data Quality Scoring**: Comprehensive dataset health assessment with actionable insights
- **🛠️ Data Preprocessing Suggestions**: Intelligent recommendations with ready-to-use code snippets
- **❓ Missing Values Analysis**: Interactive heatmaps and detailed null analysis
- **📊 Distribution Analysis**: Histograms and box plots for numeric data
- **🔗 Correlation Analysis**: Correlation heatmaps with strength insights
- **📂 Categorical Analysis**: Value counts and category distribution analysis
- **📈 Time Series Analysis**: Trend analysis, seasonality detection, and temporal patterns
- **🤖 AI-Powered Insights**: LLM-generated human-readable insights and recommendations
- **🎨 Custom Color Palettes**: Choose from 12+ beautiful color schemes for all visualizations
- **🎨 Modern Interface**: Clean, tab-based UI focused on essential insights
- **📱 Responsive Design**: Works seamlessly on any screen size
- **📄 PDF Export (Beta)**: Generate basic analysis reports - currently under development

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- Google Gemini API key (free, for AI-powered insights)

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

### Getting Gemini API Key (for AI Insights)

To use the AI-powered insights feature:

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and enter it in the 🤖 AI Insights tab

**Note:** The API key is free and only stored for your current session.

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
   - **🛠️ Preprocessing**: Get intelligent recommendations for data cleaning and preparation
   - **🤖 AI Insights**: Generate human-readable insights using Google's Gemini AI
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
│   ├── quality_engine.py    # Comprehensive data quality scoring engine
│   ├── preprocessing_suggestions.py # Intelligent preprocessing recommendations engine
│   └── insights_generator.py # LLM-powered insights generation
├── visuals/                 # Visualization functions
│   ├── __init__.py
│   ├── nulls.py             # Missing values visualizations
│   ├── summary.py           # Data overview charts
│   ├── distributions.py     # Distribution analysis
│   ├── correlation.py       # Correlation analysis
│   ├── categories.py        # Categorical data analysis
│   ├── time_series.py       # Time series analysis and forecasting
│   ├── quality_score.py     # Data quality visualization components
│   └── preprocessing.py     # Preprocessing suggestions visualizations
├── components/              # Tab-based UI components
│   ├── __init__.py
│   ├── data_overview.py     # Data overview tab
│   ├── missing_values.py    # Missing values analysis tab
│   ├── distributions.py     # Distribution analysis tab
│   ├── correlations.py      # Correlation analysis tab
│   ├── categorical.py       # Categorical analysis tab
│   ├── time_series.py       # Time series analysis tab
│   ├── preprocessing.py     # Data preprocessing suggestions tab
│   ├── insights.py          # AI-powered insights tab
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

### Data Preprocessing Tab 🛠️

- **Intelligent Analysis**: 8 preprocessing categories with priority scoring
- **Missing Values Strategy**: Column-specific recommendations with code snippets
- **Outlier Treatment**: Statistical detection and treatment suggestions
- **Feature Scaling**: Automatic scale analysis and scaler recommendations
- **Categorical Encoding**: Smart encoding strategy selection based on cardinality
- **Data Type Optimization**: Memory usage analysis and optimization suggestions
- **Feature Engineering**: DateTime extraction, transformation, and binning recommendations
- **Code Generation**: Ready-to-use Python scripts for all preprocessing steps
- **Priority Dashboard**: Visual urgency assessment and category breakdown
- **Export Options**: Download complete preprocessing scripts and reports

### AI-Powered Insights Tab 🤖

- **LLM Integration**: Powered by Google's Gemini AI for intelligent data analysis
- **Human-Readable Insights**: Plain English summaries of key data patterns and findings
- **Automated Analysis**: AI analyzes data quality, distributions, correlations, and business implications
- **Actionable Recommendations**: Specific suggestions for data improvement and next steps
- **Context-Aware**: Insights adapt based on your dataset's characteristics and patterns
- **Export Options**: Download insights as text files for documentation and sharing
- **API Key Management**: Secure, session-based API key storage (not saved permanently)
- **Regeneration**: Refresh insights to get new perspectives on your data

#### How AI Insights Work:

1. **Data Analysis**: The system extracts comprehensive statistics from your dataset
2. **Pattern Recognition**: AI identifies trends, correlations, quality issues, and anomalies
3. **Business Context**: Insights are generated with practical, business-relevant interpretations
4. **Quality Focus**: Emphasis on data quality issues and improvement recommendations
5. **Actionable Output**: Clear, numbered insights that guide your next analytical steps

#### Sample Insights:

- "Sales data shows a 23% increase in Q4, with December being the strongest month"
- "Customer age distribution is right-skewed with 15% missing values requiring attention"
- "Strong correlation (0.82) between marketing spend and revenue suggests effective campaigns"
- "High cardinality in product categories (847 unique values) may benefit from grouping"

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

## 🛠️ Data Preprocessing Suggestions

Vizzy's intelligent preprocessing engine analyzes your dataset and provides actionable recommendations for data cleaning and preparation, complete with ready-to-use code snippets.

### Preprocessing Categories

The system evaluates your data across **8 key preprocessing areas**:

1. **🔧 Missing Values Handling**

   - Strategy recommendations based on missing percentage and data type
   - Column-specific approaches (median, mode, forward fill, interpolation)
   - Advanced imputation suggestions for complex cases

2. **📊 Outlier Treatment**

   - Statistical outlier detection using IQR method
   - Treatment strategies: removal, capping, transformation
   - Column-specific outlier analysis and recommendations

3. **📏 Feature Scaling**

   - Automatic detection of scale differences between columns
   - StandardScaler vs MinMaxScaler recommendations
   - Scaling necessity assessment based on data characteristics

4. **🏷️ Categorical Encoding**

   - Smart encoding strategy selection based on cardinality
   - One-hot, label, frequency, and target encoding recommendations
   - High cardinality handling with grouping strategies

5. **💾 Data Type Optimization**

   - Memory usage analysis and optimization suggestions
   - Automatic downcasting recommendations for numeric types
   - String to categorical conversion for memory efficiency

6. **🔨 Feature Engineering**

   - DateTime feature extraction (year, month, weekday, etc.)
   - Skewed data transformation suggestions
   - Polynomial features for small datasets
   - Binning recommendations for high-cardinality features

7. **🔍 Duplicate Handling**

   - Duplicate detection and removal strategies
   - Impact assessment and removal recommendations

8. **✅ Data Validation**
   - Format validation and standardization suggestions
   - Impossible value detection (negative ages, invalid percentages)
   - Text cleaning recommendations (whitespace, case consistency)

### Preprocessing Output

- **Priority Scoring**: 0-100 priority scores for each preprocessing category
- **Urgency Assessment**: Low/Medium/High urgency classification
- **Interactive Visualizations**: Priority charts, category breakdowns, and analysis charts
- **Ready-to-Use Code**: Python code snippets for each recommendation
- **Complete Script Generation**: Download a comprehensive preprocessing script
- **Category-Specific Analysis**: Detailed charts for missing values, outliers, encoding strategies
- **Quick Actions**: One-click data type display, missing values analysis, duplicate removal

### Smart Recommendations

- **Context-Aware**: Suggestions adapt based on data characteristics and size
- **Prioritized**: Focus on high-impact preprocessing steps first
- **Code-Ready**: Every suggestion includes executable Python code
- **Export Options**: Download preprocessing scripts and suggestion reports
- **Visual Feedback**: Interactive charts show preprocessing impact and priorities

### Interactive Features

- **Priority Dashboard**: Visual urgency gauge and category breakdown
- **Tabbed Interface**: Organized suggestions by preprocessing category
- **Code Snippets**: Copy-ready Python code for each recommendation
- **Progress Tracking**: Clear priority scoring to guide preprocessing workflow
- **Export Options**: Generate complete preprocessing scripts for implementation

## 📄 PDF Report Generation

Vizzy includes a comprehensive PDF report generator that creates professional, detailed analysis reports with a single click.

### Report Contents

The generated PDF reports include:

1. **Executive Summary**: Key findings and recommendations at a glance
2. **Dataset Overview**: Basic statistics, data types, and structure analysis
3. **Data Quality Assessment**: Comprehensive quality scoring across 5 dimensions
4. **Missing Values Analysis**: Detailed missing data patterns and recommendations
5. **Distribution Analysis**: Statistical summaries for numeric columns
6. **Correlation Analysis**: Strong relationships and correlation matrix insights
7. **Preprocessing Recommendations**: Prioritized suggestions with code snippets
8. **Appendix**: Complete column details and metadata

### Report Features

- **Professional Layout**: Clean, branded design with proper formatting
- **Executive Summary**: High-level insights for stakeholders
- **Visual Elements**: Tables, charts, and color-coded quality indicators
- **Actionable Recommendations**: Specific steps with ready-to-use code
- **Comprehensive Coverage**: All analysis areas in a single document
- **Automated Generation**: One-click export from the sidebar
- **Timestamped Reports**: Automatic filename with generation timestamp

### Export Options

- **One-Click Generation**: Simple button in the sidebar to generate reports
- **Instant Download**: PDF downloads immediately after generation
- **Custom Naming**: Automatic timestamped filenames for organization
- **Progress Indication**: Real-time feedback during report generation
- **Error Handling**: Graceful error messages if generation fails

### Use Cases

- **Stakeholder Reports**: Professional summaries for non-technical audiences
- **Documentation**: Analysis documentation for project records
- **Quality Audits**: Comprehensive data quality assessments
- **Preprocessing Guides**: Step-by-step data cleaning instructions
- **Archive Records**: Snapshot of analysis at specific points in time

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
- [x] **Data Preprocessing Suggestions**: Automated recommendations ✅
- [x] **AI-Powered Insights**: LLM-generated insights using Google's Gemini API ✅
- [x] **PDF Export (Beta)**: Basic report generation implemented - needs charts and enhanced formatting 🚧

### Recently Added Features

**🤖 AI-Powered Insights (New!)**

- Powered by Google's Gemini AI for intelligent data analysis
- Human-readable insights in plain English
- Automatic analysis of data quality, patterns, and business implications
- Free API key required (get yours at [Google AI Studio](https://aistudio.google.com/app/apikey))
- Session-based secure API key storage
- Export insights for documentation

## 🙋‍♀️ Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
