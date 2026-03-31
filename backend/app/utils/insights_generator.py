"""
LLM-powered insights generator for Vizzy
Uses Google's Gemini API to generate human-readable insights from data.
Streamlit dependencies have been removed for FastAPI compatibility.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd

from .data_checks import analyze_null_values, analyze_data_types
from .quality_engine import DataQualityEngine

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def load_api_key_from_env():
    """Load API key from .env file if available."""
    if not DOTENV_AVAILABLE:
        return None
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        return os.getenv("GEMINI_API_KEY")
    return None


def extract_data_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract comprehensive data insights for LLM processing.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        dict: Structured insights about the dataset
    """
    insights = {}

    original_shape = df.shape
    if len(df) > 10000:
        sample_df = df.sample(n=10000, random_state=42)
    else:
        sample_df = df.copy()

    insights['basic_info'] = {
        'shape': original_shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 ** 2,
    }

    null_analysis = analyze_null_values(df)
    insights['missing_values'] = {
        'total_missing': int(null_analysis['total_nulls']),
        'missing_percentage': (null_analysis['total_nulls'] / (len(df) * len(df.columns))) * 100,
        'columns_with_missing': null_analysis['columns_with_nulls'],
        'mostly_null_columns': null_analysis['mostly_null_columns'],
    }

    try:
        quality_engine = DataQualityEngine(sample_df)
        quality_results = quality_engine.calculate_overall_score()
        insights['quality'] = {
            'overall_score': quality_results['overall_score'],
            'grade': quality_results['grade'],
            'dimensions': quality_results['dimensions'],
        }
    except Exception:
        insights['quality'] = {'overall_score': 'N/A', 'grade': 'N/A'}

    numeric_cols = sample_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        numeric_stats = sample_df[numeric_cols].describe()
        insights['numeric_analysis'] = {
            'columns': numeric_cols.tolist(),
            'stats': numeric_stats.to_dict(),
            'correlations': sample_df[numeric_cols].corr().to_dict() if len(numeric_cols) > 1 else {},
        }
    else:
        insights['numeric_analysis'] = {'columns': [], 'stats': {}, 'correlations': {}}

    categorical_cols = sample_df.select_dtypes(include=['object', 'category']).columns
    cat_insights = {}
    for col in categorical_cols[:5]:
        value_counts = sample_df[col].value_counts()
        cat_insights[col] = {
            'unique_count': sample_df[col].nunique(),
            'top_values': value_counts.head(5).to_dict(),
            'cardinality': 'high' if sample_df[col].nunique() > 50 else 'low',
        }
    insights['categorical_analysis'] = cat_insights

    datetime_cols = sample_df.select_dtypes(include=['datetime64']).columns
    if len(datetime_cols) > 0:
        time_insights = {}
        for col in datetime_cols[:2]:
            time_insights[col] = {
                'date_range': f"{sample_df[col].min()} to {sample_df[col].max()}",
                'time_span_days': (sample_df[col].max() - sample_df[col].min()).days,
            }
        insights['time_series'] = time_insights
    else:
        insights['time_series'] = {}

    duplicate_count = df.duplicated().sum()
    insights['duplicates'] = {
        'count': int(duplicate_count),
        'percentage': (duplicate_count / len(df)) * 100,
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

    if insights['numeric_analysis']['columns']:
        prompt += "\nNumeric Columns Analysis:\n"
        for col in insights['numeric_analysis']['columns'][:5]:
            if col in insights['numeric_analysis']['stats']:
                stats = insights['numeric_analysis']['stats'][col]
                prompt += (
                    f"- {col}: mean={stats.get('mean', 'N/A'):.2f}, "
                    f"std={stats.get('std', 'N/A'):.2f}, "
                    f"min={stats.get('min', 'N/A')}, max={stats.get('max', 'N/A')}\n"
                )

    if insights['categorical_analysis']:
        prompt += "\nCategorical Columns Analysis:\n"
        for col, data in insights['categorical_analysis'].items():
            top_val = list(data['top_values'].keys())[0] if data['top_values'] else 'N/A'
            prompt += f"- {col}: {data['unique_count']} unique values, top value: {top_val}\n"

    if insights['numeric_analysis']['correlations']:
        prompt += "\nKey Correlations:\n"
        correlations = insights['numeric_analysis']['correlations']
        for col1 in list(correlations.keys())[:3]:
            for col2, corr_val in correlations[col1].items():
                if col1 != col2 and abs(corr_val) > 0.5:
                    prompt += f"- {col1} and {col2}: correlation = {corr_val:.2f}\n"

    if insights['time_series']:
        prompt += "\nTime Series Information:\n"
        for col, data in insights['time_series'].items():
            prompt += f"- {col}: spans {data['time_span_days']} days from {data['date_range']}\n"

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
        return None

    try:
        insights = extract_data_insights(df)
        prompt = create_insights_prompt(df, insights)

        model = genai.GenerativeModel('gemini-2.5-flash')
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        response = model.generate_content(prompt, generation_config=generation_config)

        if not response or not hasattr(response, 'text'):
            return None

        response_text = response.text
        if not response_text or len(response_text.strip()) < 50:
            return None

        bullet_points = []
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*')):
                clean_line = line.lstrip('•-* ').strip()
                if clean_line and len(clean_line) > 15:
                    clean_line = clean_line.replace('**', '').replace('__', '').replace('***', '')
                    if clean_line.endswith(('.', '!', '?')) or len(clean_line) > 40:
                        bullet_points.append(clean_line)
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                clean_line = line[2:].strip()
                if clean_line and len(clean_line) > 15:
                    clean_line = clean_line.replace('**', '').replace('__', '').replace('***', '')
                    if clean_line.endswith(('.', '!', '?')) or len(clean_line) > 40:
                        bullet_points.append(clean_line)

        if not bullet_points:
            paragraphs = response_text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if len(para) > 20 and not para.startswith(('Dataset', 'Analysis', 'Summary')):
                    para = para.replace('**', '').replace('__', '').replace('***', '')
                    bullet_points.append(para)

            if not bullet_points:
                sentences = response_text.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20:
                        sentence = sentence.replace('**', '').replace('__', '').replace('***', '')
                        bullet_points.append(sentence)
                bullet_points = bullet_points[:8]

        if not bullet_points:
            return None

        complete_insights = [
            insight.strip()
            for insight in bullet_points
            if len(insight.strip()) > 20 and not insight.strip().endswith(('...', '..'))
        ]

        if len(complete_insights) < 3:
            return complete_insights if complete_insights else None

        return complete_insights[:8]

    except Exception:
        return None


async def generate_llm_insights_stream(df: pd.DataFrame):
    """
    Async generator that yields Gemini response chunks as SSE-ready strings.
    Falls back gracefully if GEMINI_API_KEY is not set.
    """
    from ..core.config import settings

    if not GEMINI_AVAILABLE:
        yield 'data: {"chunk": "Gemini package not installed. Run: pip install google-generativeai"}\n\n'
        return

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        yield 'data: {"chunk": "No GEMINI_API_KEY configured. Set it in your .env file."}\n\n'
        return

    try:
        genai.configure(api_key=api_key)
        insights = extract_data_insights(df)
        prompt = create_insights_prompt(df, insights)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        response = model.generate_content(prompt, generation_config=generation_config, stream=True)
        for chunk in response:
            if chunk.text:
                yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
