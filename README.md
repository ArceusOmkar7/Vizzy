# 📊 Data Visualizer

A **developer-friendly**, **Streamlit-powered** data visualization assistant that lets you drop in any CSV or Excel file and instantly get comprehensive data insights.

## 🎯 Features

- **📁 Easy File Upload**: Support for CSV and Excel files
- **� Data Overview**: Clean data preview, types, and basic statistics
- **❓ Missing Values Analysis**: Interactive heatmaps and detailed null analysis
- **� Distribution Analysis**: Histograms and box plots for numeric data
- **🔗 Correlation Analysis**: Correlation heatmaps with strength insights
- **📂 Categorical Analysis**: Value counts and category distribution analysis
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
   cd "Data Visualizer"
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
   streamlit run app.py
   ```

4. **Open your browser** and navigate to `http://localhost:8501`

## 📖 Usage

1. **Upload your data**: Use the sidebar to upload a CSV or Excel file
2. **Explore with tabs**: Navigate through different analysis tabs:
   - **📋 Data Overview**: View data preview, types, and basic metrics
   - **❓ Missing Values**: Analyze null patterns with heatmaps and charts
   - **📊 Distributions**: Explore numeric data distributions
   - **🔗 Correlations**: Discover relationships between numeric variables
   - **📂 Categories**: Analyze categorical data and value frequencies
3. **Interactive analysis**: Each tab provides focused, relevant insights
4. **Export insights**: View summary tables and save analysis results

### Supported File Formats

- **.csv**: Comma-separated values (UTF-8 and Latin-1 encoding)
- **.xlsx/.xls**: Excel files (all modern versions)

## 🗂️ Project Structure

```
data_visualizer/
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
│   └── categories.py        # Categorical data analysis
├── components/              # Tab-based UI components
│   ├── __init__.py
│   ├── data_overview.py     # Data overview tab
│   ├── missing_values.py    # Missing values analysis tab
│   ├── distributions.py     # Distribution analysis tab
│   ├── correlations.py      # Correlation analysis tab
│   └── categorical.py       # Categorical analysis tab
└── sample_data/             # Sample datasets for testing
    ├── sales_data.csv
    ├── student_performance.csv
    ├── messy_data.csv
    └── high_cardinality_data.csv
```

## 🎨 Customization

### Themes

The app uses a consistent color scheme defined in `style.py`. You can customize:

- **Colors**: Modify the color palette in `get_color_palette()`
- **Chart styles**: Update `setup_plot_style()` for different themes
- **Streamlit theme**: Edit `.streamlit/config.toml`

### Adding New Visualizations

1. Create your visualization function in the appropriate `visuals/*.py` module
2. Add the option to `components/sidebar.py`
3. Wire it up in `components/charts.py`

## 📊 Visualization Types

### Missing Values Analysis
- **Bar Chart**: Shows count of missing values per column
- **Heatmap**: Reveals patterns in missing data
- **Correlation**: Analyzes relationships between missing value patterns

### Distribution Analysis
- **Histograms**: Shows data distribution with KDE overlay
- **Box Plots**: Reveals outliers and quartiles
- **Q-Q Plots**: Tests for normality

### Correlation Analysis
- **Heatmap**: Classic correlation matrix
- **Strength Distribution**: Histogram of correlation values
- **Top Correlations**: Ranked list of strongest relationships
- **Network View**: Graph-based correlation visualization

### Categorical Analysis
- **Value Counts**: Bar charts for category frequencies
- **Pie Charts**: Proportion visualization
- **Diversity Metrics**: Shannon entropy, Gini impurity, Simpson index
- **Relationship Analysis**: Cross-tabulation heatmaps

## ⚡ Performance Tips

- **Enable sampling** for datasets with >10,000 rows
- **Limit categorical analysis** to columns with reasonable cardinality
- **Use correlation thresholds** to focus on meaningful relationships
- **Check memory usage** for very wide datasets

## 🛠️ Development

### Running in Development Mode

```bash
streamlit run app.py --logger.level=debug
```

### Code Style

- **Functions**: `snake_case`
- **Classes**: `CamelCase` (if any)
- **Constants**: `UPPER_CASE`
- **Docstrings**: Required for all functions
- **Type hints**: Encouraged for function parameters

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

- [ ] **PDF Export**: Generate downloadable reports
- [ ] **Advanced Outlier Detection**: IQR and Z-score methods with visualization
- [ ] **Time Series Analysis**: For datetime columns
- [ ] **Machine Learning Insights**: Automated feature importance
- [ ] **Data Quality Scoring**: Overall dataset health metrics
- [ ] **Custom Color Palettes**: User-selectable themes
- [ ] **Data Preprocessing Suggestions**: Automated recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check the `/docs` folder (coming soon)

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web app framework
- **Seaborn/Matplotlib**: For beautiful statistical visualizations
- **Pandas**: For powerful data manipulation capabilities
- **The Python Community**: For the incredible ecosystem

---

**Made with ❤️ for data scientists, analysts, and developers who love clean, insightful visualizations.**
