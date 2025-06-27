# 📊 Data Visualizer

A **developer-friendly**, **Streamlit-powered** data visualization assistant that lets you drop in any CSV or Excel file and instantly get comprehensive data insights.

## 🎯 Features

- **📁 Easy File Upload**: Support for CSV and Excel files
- **🔍 Missing Values Analysis**: Interactive heatmaps and bar charts
- **📊 Data Overview**: Data types, uniqueness, and memory usage analysis
- **📈 Distribution Analysis**: Histograms, box plots, and statistical summaries
- **🔗 Correlation Analysis**: Heatmaps, strength distribution, and network views
- **📂 Categorical Analysis**: Value counts, diversity metrics, and relationships
- **⚙️ Advanced Options**: Outlier detection, data sampling, and customization
- **📱 Responsive Design**: Clean, modern UI that works on any screen size

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
2. **Select visualizations**: Choose which analyses you want to see
3. **Explore insights**: Interact with the generated charts and tables
4. **Export results**: Download summary tables or save charts

### Supported File Formats

- **.csv**: Comma-separated values (UTF-8 and Latin-1 encoding)
- **.xlsx/.xls**: Excel files (all modern versions)

## 🗂️ Project Structure

```
data_visualizer/
├── app.py                    # Main Streamlit application
├── style.py                  # Global styling and themes
├── requirements.txt          # Python dependencies
├── pyproject.toml           # UV/pip project configuration
├── .streamlit/              # Streamlit configuration
│   └── config.toml
├── utils/                   # Pure Python utilities
│   ├── __init__.py
│   ├── data_checks.py       # Data quality analysis
│   └── file_loader.py       # File loading and caching
├── visuals/                 # Visualization functions
│   ├── __init__.py
│   ├── nulls.py             # Missing values visualizations
│   ├── summary.py           # Data overview charts
│   ├── distributions.py     # Distribution analysis
│   ├── correlation.py       # Correlation analysis
│   └── categories.py        # Categorical data analysis
└── components/              # Reusable UI components
    ├── __init__.py
    ├── sidebar.py           # Sidebar interface
    └── charts.py            # Chart rendering wrapper
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
