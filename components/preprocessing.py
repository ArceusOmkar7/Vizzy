"""
Data Preprocessing Suggestions Tab Component

Provides intelligent preprocessing recommendations with actionable insights.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from utils.preprocessing_suggestions import PreprocessingSuggestionEngine, generate_preprocessing_script
from visuals.preprocessing import (
    create_priority_chart, create_summary_gauge, create_category_breakdown_chart,
    create_missing_values_strategy_chart, create_outlier_analysis_chart,
    create_encoding_strategy_pie, create_memory_optimization_chart,
    create_suggestions_table, format_code_snippet, create_recommendations_summary
)


def render_preprocessing_tab(df):
    """
    Render the data preprocessing suggestions tab.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("🛠️ Data Preprocessing Suggestions")

    st.markdown("""
    Get intelligent, actionable recommendations for cleaning and preparing your data for analysis.
    Our engine analyzes your dataset and provides specific suggestions with ready-to-use code snippets.
    """)

    # Generate preprocessing suggestions
    with st.spinner("Analyzing data and generating preprocessing suggestions..."):
        suggestion_engine = PreprocessingSuggestionEngine(df)
        suggestions = suggestion_engine.generate_all_suggestions()

    # Get color palette
    palette_name = getattr(st.session_state, 'color_palette', 'Default (Husl)')

    # Summary Section
    st.subheader("📊 Preprocessing Overview")

    col1, col2 = st.columns([1, 2])

    with col1:
        # Urgency gauge
        summary_gauge = create_summary_gauge(
            suggestions['summary'], palette_name)
        st.plotly_chart(summary_gauge, use_container_width=True)

    with col2:
        # Summary text and priorities
        summary_text = create_recommendations_summary(suggestions)
        st.markdown(summary_text)

    # Priority Chart
    st.subheader("🎯 Priority Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        priority_chart = create_priority_chart(
            suggestions['priorities'], palette_name)
        st.plotly_chart(priority_chart, use_container_width=True)

    with col2:
        category_chart = create_category_breakdown_chart(
            suggestions, palette_name)
        st.plotly_chart(category_chart, use_container_width=True)

    # Detailed Suggestions by Category
    st.subheader("📋 Detailed Recommendations")

    # Create tabs for each category with issues
    categories_with_issues = []
    for category, data in suggestions.items():
        if (isinstance(data, dict) and
            'suggestions' in data and
            data.get('priority', 0) > 0 and
                category not in ['priorities', 'summary']):
            categories_with_issues.append(category)

    if categories_with_issues:
        # Sort by priority
        categories_with_issues.sort(
            key=lambda x: suggestions[x].get('priority', 0), reverse=True)

        tab_names = [cat.replace('_', ' ').title()
                     for cat in categories_with_issues]
        tabs = st.tabs(tab_names)

        for i, category in enumerate(categories_with_issues):
            with tabs[i]:
                render_category_suggestions(
                    category, suggestions[category], palette_name)
    else:
        st.success(
            "🎉 **Excellent!** Your data requires minimal preprocessing. You're ready to analyze!")
        st.info("💡 **Tip**: While your data is in great shape, consider the optional optimizations below for enhanced performance.")

    # Complete Preprocessing Script
    st.subheader("📜 Complete Preprocessing Script")

    with st.expander("Generate Complete Preprocessing Script", expanded=False):
        st.markdown("""
        **Download a complete Python script** with all recommended preprocessing steps.
        This script includes all the suggestions above in a single, executable file.
        """)

        preprocessing_script = generate_preprocessing_script(suggestions)

        st.code(preprocessing_script, language='python')

        # Download button
        st.download_button(
            label="📥 Download Preprocessing Script",
            data=preprocessing_script,
            file_name=f"preprocessing_script_{df.shape[0]}x{df.shape[1]}.py",
            mime="text/x-python"
        )

    # Quick Actions
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧹 Remove Duplicates", help="Remove duplicate rows from the dataset", key="remove_duplicates_btn"):
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                st.success(f"Would remove {duplicate_count} duplicate rows")
                st.code("df = df.drop_duplicates(keep='first')")
            else:
                st.info("No duplicate rows found")

    with col2:
        if st.button("📝 Show Data Types", help="Display current data types and optimization suggestions", key="show_dtypes_btn"):
            st.write("**Current Data Types:**")
            dtype_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes,
                'Memory (KB)': [df[col].memory_usage(deep=True) / 1024 for col in df.columns]
            })
            st.dataframe(dtype_df, use_container_width=True)

    with col3:
        if st.button("🔍 Missing Values", help="Show detailed missing values analysis", key="show_missing_btn"):
            missing_df = pd.DataFrame({
                'Column': df.columns,
                'Missing Count': df.isnull().sum(),
                'Missing %': (df.isnull().sum() / len(df)) * 100
            })
            missing_df = missing_df[missing_df['Missing Count'] > 0]
            if not missing_df.empty:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.info("No missing values found")

    # Export Options
    st.subheader("📤 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        # Export suggestions as CSV
        suggestions_df = create_suggestions_table(suggestions)
        if not suggestions_df.empty:
            suggestions_csv = suggestions_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Suggestions Report",
                data=suggestions_csv,
                file_name=f"preprocessing_suggestions_{df.shape[0]}x{df.shape[1]}.csv",
                mime="text/csv"
            )

    with col2:
        # Export data quality + preprocessing combined report
        if st.button("📋 Generate Combined Report", help="Create comprehensive data quality + preprocessing report", key="generate_report_btn"):
            st.info(
                "Combined report feature coming soon! For now, use individual reports from each tab.")


def render_category_suggestions(category: str, data: Dict[str, Any], palette_name: str):
    """Render suggestions for a specific category."""
    category_name = category.replace('_', ' ').title()
    priority = data.get('priority', 0)
    suggestions = data.get('suggestions', [])

    # Priority indicator
    if priority >= 70:
        st.error(f"🚨 **Critical Priority** (Score: {priority:.0f})")
    elif priority >= 50:
        st.warning(f"⚠️ **High Priority** (Score: {priority:.0f})")
    elif priority >= 30:
        st.info(f"📝 **Medium Priority** (Score: {priority:.0f})")
    else:
        st.success(f"💡 **Low Priority** (Score: {priority:.0f})")

    # Display suggestions
    st.markdown("### 📋 Recommendations")
    for suggestion in suggestions:
        if suggestion.startswith('✅'):
            st.success(suggestion)
        elif suggestion.startswith('⚠️') or suggestion.startswith('🚨'):
            st.warning(suggestion)
        elif suggestion.startswith('ℹ️'):
            st.info(suggestion)
        else:
            st.markdown(f"• {suggestion}")

    # Category-specific visualizations
    if category == 'missing_values' and 'column_strategies' in data:
        strategies = data['column_strategies']
        if strategies:
            st.markdown("### 📊 Missing Values Analysis")
            missing_chart = create_missing_values_strategy_chart(
                strategies, palette_name)
            st.plotly_chart(missing_chart, use_container_width=True)

            # Detailed strategies table
            with st.expander("📋 Detailed Missing Value Strategies", expanded=False):
                strategy_data = []
                for col, strategy_info in strategies.items():
                    strategy_data.append({
                        'Column': col,
                        'Missing %': f"{strategy_info['missing_percentage']:.1f}%",
                        'Strategy': strategy_info['strategy']
                    })
                strategy_df = pd.DataFrame(strategy_data)
                st.dataframe(strategy_df, use_container_width=True)

    elif category == 'outliers' and 'column_strategies' in data:
        strategies = data['column_strategies']
        if strategies:
            st.markdown("### 📊 Outlier Analysis")
            outlier_chart = create_outlier_analysis_chart(
                strategies, palette_name)
            st.plotly_chart(outlier_chart, use_container_width=True)

    elif category == 'encoding' and 'column_strategies' in data:
        strategies = data['column_strategies']
        if strategies:
            st.markdown("### 📊 Encoding Strategies")
            encoding_chart = create_encoding_strategy_pie(
                strategies, palette_name)
            st.plotly_chart(encoding_chart, use_container_width=True)

    elif category == 'data_types' and 'memory_savings' in data:
        if data['memory_savings'] > 0:
            st.markdown("### 💾 Memory Optimization")
            memory_chart = create_memory_optimization_chart(data, palette_name)
            st.plotly_chart(memory_chart, use_container_width=True)

    # Code snippets
    if 'code_snippets' in data and data['code_snippets']:
        st.markdown("### 💻 Code Snippets")

        for i, code in enumerate(data['code_snippets']):
            if code.strip():
                formatted_code = format_code_snippet(code)
                st.code(formatted_code, language='python')

                # Copy button simulation
                st.caption(
                    f"💡 Copy the code above to implement this preprocessing step")

    # Column-specific details
    if 'column_strategies' in data and data['column_strategies']:
        with st.expander("🔍 Column-Specific Details", expanded=False):
            for col, details in data['column_strategies'].items():
                st.markdown(f"**{col}:**")
                for key, value in details.items():
                    if key != 'code':
                        st.markdown(
                            f"  • {key.replace('_', ' ').title()}: {value}")
                st.markdown("---")
