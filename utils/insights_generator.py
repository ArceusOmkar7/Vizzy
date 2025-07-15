"""
LLM-powered insights generator for Vizzy
Uses Google's Gemini API to generate human-readable insights from data
"""

# Show setup options
from utils.quality_engine import DataQualityEngine
from utils.data_checks import analyze_null_values, analyze_data_types
from pathlib import Path
import os
import json
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import streamlit as st

setup_option = st.radio(
    "Choose your preferred setup method:",
    ["📝 Enter manually", "📁 Use .env file"],
    help="Manual entry is temporary, .env file persists across sessions",
    key="api_setup_method_radio"
)


# Try to import required packages
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.error(
        "Google Generative AI package not installed. Please run: pip install google-generativeai")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_api_key_from_env():
    """Load API key from .env file if available."""
    if not DOTENV_AVAILABLE:
        return None

    # Load .env file
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv("GEMINI_API_KEY")
    return None


def save_api_key_to_file(api_key: str):
    """Save API key to a local file for persistence."""
    try:
        key_file = Path(".streamlit") / "api_key.txt"
        key_file.parent.mkdir(exist_ok=True)
        key_file.write_text(api_key)
        return True
    except Exception:
        return False


def load_api_key_from_file():
    """Load API key from local file."""
    try:
        key_file = Path(".streamlit") / "api_key.txt"
        if key_file.exists():
            return key_file.read_text().strip()
    except Exception:
        pass
    return None


def should_save_api_key():
    """Check if API key should be saved based on environment variable."""
    if DOTENV_AVAILABLE:
        load_dotenv(Path(".env"), override=False)
        return os.getenv("SAVE_API_KEY", "false").lower() == "true"
    return False


def configure_gemini_api():
    """Configure the Gemini API with user's API key from various sources."""
    if not GEMINI_AVAILABLE:
        st.error(
            "❌ Google Generative AI package is not available. Please install it first.")
        return False

    # Initialize session state
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = None

    # Try to load API key from various sources if not already in session
    if not st.session_state.gemini_api_key:
        # 1. Try loading from .env file
        env_key = load_api_key_from_env()
        if env_key:
            st.session_state.gemini_api_key = env_key
            st.info("✅ API key loaded from .env file")
        else:
            # 2. Try loading from saved file
            saved_key = load_api_key_from_file()
            if saved_key:
                st.session_state.gemini_api_key = saved_key
                st.info("✅ API key loaded from saved settings")

    # Display current status
    if st.session_state.gemini_api_key:
        masked_key = st.session_state.gemini_api_key[:8] + "..." + st.session_state.gemini_api_key[-4:] if len(
            st.session_state.gemini_api_key) > 12 else "***"
        st.success(f"🔑 API key configured: {masked_key}")

        # Option to clear/change key
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Change Key", help="Clear current API key and enter a new one", key="change_api_key_btn"):
                st.session_state.gemini_api_key = None
                # Use session state flag instead of rerun to avoid tab switching
                st.session_state.api_key_changed = True

    # Get API key from user if not available
    if not st.session_state.gemini_api_key:
        st.markdown("### 🔑 API Key Setup")

        # Show setup options
        setup_option = st.radio(
            "Choose your preferred setup method:",
            ["� Enter manually", "📁 Use .env file"],
            help="Manual entry is temporary, .env file persists across sessions"
        )

        if setup_option == "📁 Use .env file":
            st.info("""
            **Setup Instructions: **
            1. Copy `.env.example` to `.env` in your project folder
            2. Edit `.env` and add your API key: `GEMINI_API_KEY = your_actual_key_here`
            3. Refresh this page

            **Benefits: ** API key persists across sessions, more secure than manual entry
            """)

            if st.button("🔄 Check for .env file", type="secondary", key="check_env_btn"):
                env_key = load_api_key_from_env()
                if env_key:
                    st.session_state.gemini_api_key = env_key
                    st.session_state.env_key_loaded = True
                else:
                    st.warning(
                        "No API key found in .env file. Please check your setup.")

        else:  # Manual entry
            api_key = st.text_input(
                "🔑 Enter your Gemini API Key",
                type="password",
                placeholder="Enter your API key here...",
                help="Get your free API key from https://aistudio.google.com/app/apikey",
                key="manual_api_key_input"
            )

            # Option to save the key
            save_key = st.checkbox(
                "💾 Remember this API key for future sessions",
                help="Saves API key locally (not recommended for shared computers)",
                key="save_api_key_checkbox"
            )

            if api_key:
                st.session_state.gemini_api_key = api_key

                # Save if requested
                if save_key:
                    if save_api_key_to_file(api_key):
                        st.success("✅ API key saved for future sessions")
                    else:
                        st.warning(
                            "⚠️ Could not save API key, but it will work for this session")

                # Set a flag instead of rerun to avoid tab switching
                st.session_state.api_key_entered = True

    # Configure the API if we have a key
    if st.session_state.gemini_api_key:
        try:
            genai.configure(api_key=st.session_state.gemini_api_key)
            return True
        except Exception as e:
            st.error(f"❌ Error configuring API: {str(e)}")
            return False

    return False


def extract_data_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract comprehensive data insights for LLM processing.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        dict: Structured insights about the dataset
    """
    insights = {}

    # For very large datasets, work with a sample for analysis but keep original stats
    original_shape = df.shape
    if len(df) > 10000:
        # Use a representative sample for detailed analysis
        sample_df = df.sample(n=10000, random_state=42)
        st.info(
            f"📊 Using sample of 10,000 rows from {len(df):,} total rows for detailed analysis.")
    else:
        sample_df = df.copy()

    # Basic dataset info (use original)
    insights['basic_info'] = {
        'shape': original_shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }

    # Missing values analysis (use original)
    null_analysis = analyze_null_values(df)
    insights['missing_values'] = {
        'total_missing': int(null_analysis['total_nulls']),
        'missing_percentage': (null_analysis['total_nulls'] / (len(df) * len(df.columns))) * 100,
        'columns_with_missing': null_analysis['columns_with_nulls'],
        'mostly_null_columns': null_analysis['mostly_null_columns']
    }

    # Data quality scores (use sample for performance)
    try:
        quality_engine = DataQualityEngine(sample_df)
        quality_results = quality_engine.calculate_overall_score()
        insights['quality'] = {
            'overall_score': quality_results['overall_score'],
            'grade': quality_results['grade'],
            'dimensions': quality_results['dimensions']
        }
    except Exception:
        insights['quality'] = {'overall_score': 'N/A', 'grade': 'N/A'}

    # Numeric columns analysis (use sample)
    numeric_cols = sample_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        numeric_stats = sample_df[numeric_cols].describe()
        insights['numeric_analysis'] = {
            'columns': numeric_cols.tolist(),
            'stats': numeric_stats.to_dict(),
            'correlations': sample_df[numeric_cols].corr().to_dict() if len(numeric_cols) > 1 else {}
        }
    else:
        insights['numeric_analysis'] = {
            'columns': [], 'stats': {}, 'correlations': {}}

    # Categorical columns analysis (use sample)
    categorical_cols = sample_df.select_dtypes(
        include=['object', 'category']).columns
    cat_insights = {}
    for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
        value_counts = sample_df[col].value_counts()
        cat_insights[col] = {
            'unique_count': sample_df[col].nunique(),
            'top_values': value_counts.head(5).to_dict(),
            'cardinality': 'high' if sample_df[col].nunique() > 50 else 'low'
        }
    insights['categorical_analysis'] = cat_insights

    # Time series detection (use sample)
    datetime_cols = sample_df.select_dtypes(include=['datetime64']).columns
    if len(datetime_cols) > 0:
        time_insights = {}
        for col in datetime_cols[:2]:  # Limit to first 2 datetime columns
            time_insights[col] = {
                'date_range': f"{sample_df[col].min()} to {sample_df[col].max()}",
                'time_span_days': (sample_df[col].max() - sample_df[col].min()).days
            }
        insights['time_series'] = time_insights
    else:
        insights['time_series'] = {}

    # Duplicate analysis (use original for accuracy)
    duplicate_count = df.duplicated().sum()
    insights['duplicates'] = {
        'count': int(duplicate_count),
        'percentage': (duplicate_count / len(df)) * 100
    }

    return insights


def create_insights_prompt(df: pd.DataFrame, insights: Dict[str, Any]) -> str:
    """
    Create a structured prompt for the LLM to generate insights.

    Args:
        df (pd.DataFrame): Input dataframe
        insights (dict): Extracted data insights

    Returns:
        str: Formatted prompt for LLM
    """
    prompt = f"""
You are a data analyst AI assistant. Analyze the following dataset information and provide 5-8 clear, actionable insights in bullet point format. Focus on the most important findings that would be valuable for business decisions or data understanding.

Dataset Overview:
- Shape: {insights['basic_info']['shape'][0]} rows × {insights['basic_info']['shape'][1]} columns
- Memory usage: {insights['basic_info']['memory_usage_mb']:.1f} MB
- Data Quality Score: {insights['quality']['overall_score']}/100 (Grade: {insights['quality']['grade']})

Missing Values:
- Total missing values: {insights['missing_values']['total_missing']} ({insights['missing_values']['missing_percentage']:.1f}%)
- Columns with missing data: {insights['missing_values']['columns_with_missing']}

"""

    # Add numeric analysis if available
    if insights['numeric_analysis']['columns']:
        prompt += f"\nNumeric Columns Analysis:\n"
        for col in insights['numeric_analysis']['columns'][:5]:
            if col in insights['numeric_analysis']['stats']:
                stats = insights['numeric_analysis']['stats'][col]
                prompt += f"- {col}: mean={stats.get('mean', 'N/A'):.2f}, std={stats.get('std', 'N/A'):.2f}, min={stats.get('min', 'N/A')}, max={stats.get('max', 'N/A')}\n"

    # Add categorical analysis if available
    if insights['categorical_analysis']:
        prompt += f"\nCategorical Columns Analysis:\n"
        for col, data in insights['categorical_analysis'].items():
            prompt += f"- {col}: {data['unique_count']} unique values, top value: {list(data['top_values'].keys())[0] if data['top_values'] else 'N/A'}\n"

    # Add correlation insights if available
    if insights['numeric_analysis']['correlations']:
        prompt += f"\nKey Correlations:\n"
        correlations = insights['numeric_analysis']['correlations']
        for col1 in list(correlations.keys())[:3]:
            for col2, corr_val in correlations[col1].items():
                if col1 != col2 and abs(corr_val) > 0.5:
                    prompt += f"- {col1} and {col2}: correlation = {corr_val:.2f}\n"

    # Add time series info if available
    if insights['time_series']:
        prompt += f"\nTime Series Information:\n"
        for col, data in insights['time_series'].items():
            prompt += f"- {col}: spans {data['time_span_days']} days from {data['date_range']}\n"

    # Add duplicate info
    if insights['duplicates']['count'] > 0:
        prompt += f"\nDuplicate Rows: {insights['duplicates']['count']} ({insights['duplicates']['percentage']:.1f}%)\n"

    prompt += """
Generate exactly 6-8 clear, actionable insights as complete bullet points. Each insight should be a full, complete sentence.

Format your response in markdown with proper formatting:

## Key Data Insights

• **Data Quality**: [Insight about completeness, missing values, duplicates]
• **Statistical Patterns**: [Insight about distributions, outliers, ranges]  
• **Correlations**: [Insight about relationships between variables]
• **Business Implications**: [Insight about actionable findings]
• **Trends & Patterns**: [Insight about temporal or categorical patterns]
• **Data Recommendations**: [Insight about data improvement opportunities]

Example format:
• **Data Quality**: Dataset quality is **excellent** with only 2% missing values across all columns.
• **Revenue Patterns**: Revenue shows **strong seasonal patterns** with Q4 being **40% higher** than average quarters.
• **Geographic Distribution**: Customer segments are **well-balanced** across all geographic regions.

Requirements:
- Use **bold** text for key terms and numbers
- Each insight must be a complete sentence ending with proper punctuation
- Focus on the most important and actionable findings
- Use simple, clear business language
- Provide specific numbers and percentages when relevant
- Ensure each insight adds unique value

Generate complete, well-formed markdown insights only. Use proper markdown formatting with bold text for emphasis."""

    return prompt


def generate_llm_insights(df: pd.DataFrame) -> Optional[List[str]]:
    """
    Generate LLM-powered insights from the dataset.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        Optional[List[str]]: List of insight bullet points or None if failed
    """
    if not GEMINI_AVAILABLE:
        st.error("❌ Google Generative AI package is not available.")
        return None

    try:
        # Extract insights from data
        insights = extract_data_insights(df)

        # Create prompt
        prompt = create_insights_prompt(df, insights)

        # Generate insights using Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Add generation config for more consistent output
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,  # Increased for longer responses
        }

        response = model.generate_content(
            prompt, generation_config=generation_config)

        # Check if we got a valid response
        if not response or not hasattr(response, 'text'):
            st.error(
                "❌ Failed to get response from AI. Please check your API key and try again.")
            return None

        # Parse response into bullet points
        response_text = response.text

        # Check if response was truncated
        if not response_text or len(response_text.strip()) < 50:
            st.warning(
                "⚠️ Received incomplete response from AI. Try regenerating insights.")
            return None

        # Debug: Show raw response if needed (remove this in production)
        # st.text_area("Debug - Raw AI Response:", response_text, height=200)

        # Extract bullet points
        bullet_points = []
        lines = response_text.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Remove bullet point character and clean up
                clean_line = line.lstrip('•-* ').strip()
                if clean_line and len(clean_line) > 15:  # Ensure meaningful content
                    # Clean up any remaining markdown formatting issues
                    clean_line = clean_line.replace(
                        '**', '').replace('__', '').replace('***', '')
                    # Check if the line seems complete (ends with punctuation or is reasonably long)
                    if clean_line.endswith(('.', '!', '?')) or len(clean_line) > 40:
                        bullet_points.append(clean_line)
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                # Handle numbered bullet points
                clean_line = line[2:].strip()  # Remove number and dot
                if clean_line and len(clean_line) > 15:
                    # Clean up any remaining markdown formatting issues
                    clean_line = clean_line.replace(
                        '**', '').replace('__', '').replace('***', '')
                    # Check if the line seems complete
                    if clean_line.endswith(('.', '!', '?')) or len(clean_line) > 40:
                        bullet_points.append(clean_line)

        # If no bullet points found, try to split by periods or other delimiters
        if not bullet_points:
            # Try splitting by double newlines first (paragraph breaks)
            paragraphs = response_text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if len(para) > 20 and not para.startswith(('Dataset', 'Analysis', 'Summary')):
                    # Clean up markdown formatting
                    para = para.replace(
                        '**', '').replace('__', '').replace('***', '')
                    bullet_points.append(para)

            # If still no good content, split by sentences
            if not bullet_points:
                sentences = response_text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20:
                        # Clean up markdown formatting
                        sentence = sentence.replace(
                            '**', '').replace('__', '').replace('***', '')
                        bullet_points.append(sentence)
                bullet_points = bullet_points[:8]

        # Validate that we have meaningful insights
        if not bullet_points:
            st.warning(
                "⚠️ Could not extract meaningful insights from AI response. Please try regenerating.")
            return None

        # Filter out any remaining incomplete insights
        complete_insights = []
        for insight in bullet_points:
            # Remove insights that are too short or seem incomplete
            if len(insight.strip()) > 20 and not insight.strip().endswith(('...', '..')):
                complete_insights.append(insight.strip())

        if len(complete_insights) < 3:
            st.warning(
                "⚠️ Generated insights seem incomplete. Try regenerating for better results.")
            return complete_insights if complete_insights else None

        return complete_insights[:8]  # Limit to 8 insights

    except Exception as e:
        st.error(f"Error generating insights: {str(e)}")
        return None


def display_insights(insights: List[str]):
    """
    Display the generated insights in a nice format with markdown support.

    Args:
        insights (List[str]): List of insight strings
    """
    st.markdown("### 🔍 Key Insights")

    # Convert markdown formatting to HTML for proper display
    def convert_markdown_to_html(text):
        """Convert basic markdown to HTML"""
        import re
        # Convert **text** to <strong>text</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Convert *text* to <em>text</em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        return text

    # Convert insights to HTML format
    html_insights = []
    for i, insight in enumerate(insights, 1):
        clean_insight = insight.strip()
        # Remove surrounding quotes if present
        if clean_insight.startswith('"') and clean_insight.endswith('"'):
            clean_insight = clean_insight[1:-1]
        if clean_insight.startswith("'") and clean_insight.endswith("'"):
            clean_insight = clean_insight[1:-1]
        # Remove any remaining bullet points
        clean_insight = clean_insight.lstrip('•-* ').strip()
        # Ensure starts with capital letter
        if clean_insight and not clean_insight[0].isupper():
            clean_insight = clean_insight[0].upper() + clean_insight[1:]

        # Convert to HTML and add numbering
        html_insight = convert_markdown_to_html(clean_insight)
        html_insights.append(f"<strong>{i}.</strong> {html_insight}")

    # Create the complete HTML container with insights
    insights_html = f"""
    <div style="
        padding: 24px; 
        margin: 16px 0; 
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f2f6 100%);
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border-left: 6px solid #1f77b4;
    ">
        <div style="
            font-size: 16px;
            line-height: 1.7;
            color: #2c3e50;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        ">
            {'<br><br>'.join(html_insights)}
        </div>
    </div>
    """

    st.markdown(insights_html, unsafe_allow_html=True)

    # Add export option
    clean_insights_for_export = []
    for i, insight in enumerate(insights, 1):
        clean_text = insight.strip()
        # Remove surrounding quotes
        if clean_text.startswith('"') and clean_text.endswith('"'):
            clean_text = clean_text[1:-1]
        if clean_text.startswith("'") and clean_text.endswith("'"):
            clean_text = clean_text[1:-1]
        clean_text = clean_text.lstrip('•-* ').strip()
        clean_insights_for_export.append(f"{i}. {clean_text}")

    insights_text = "\n".join(clean_insights_for_export)

    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            "💡 **Tip:** These insights are generated based on your data patterns and quality metrics.")
    with col2:
        st.download_button(
            label="📥 Download Insights",
            data=insights_text,
            file_name="data_insights.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_insights_btn"
        )
