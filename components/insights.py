"""
LLM Insights Tab Component

Provides AI-powered insights generation using Google's Gemini API.
"""

import streamlit as st
import pandas as pd
from utils.insights_generator import (
    configure_gemini_api,
    generate_llm_insights,
    display_insights
)


def render_insights_tab(df: pd.DataFrame):
    """
    Render the LLM insights tab with AI-powered data analysis.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("🤖 AI-Powered Insights")

    # Introduction
    st.markdown("""
    Get intelligent, human-readable insights about your dataset powered by Google's Gemini AI. 
    The AI analyzes your data's patterns, quality, and relationships to provide actionable insights.
    """)

    # API Configuration Section
    st.subheader("🔑 API Configuration")

    with st.expander("ℹ️ How to get your Gemini API Key", expanded=False):
        st.markdown("""
        1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy the API key and paste it below
        
        **Note:** The API key is stored only for this session and is not saved permanently.
        """)

    # Configure API
    api_configured = configure_gemini_api()

    if not api_configured:
        st.warning("⚠️ Please enter your Gemini API key to generate insights.")
        st.stop()

    st.success("✅ API configured successfully!")

    # Generate Insights Section
    st.subheader("🔍 Generate Insights")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        **Dataset Overview:**
        - 📊 {len(df):,} rows × {len(df.columns)} columns
        - 💾 {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB
        - ❓ {df.isnull().sum().sum():,} missing values
        """)

    with col2:
        generate_button = st.button(
            "🚀 Generate AI Insights",
            type="primary",
            use_container_width=True,
            help="Analyze your dataset and generate intelligent insights"
        )

    # Generate and display insights
    if generate_button:
        with st.spinner("🤖 AI is analyzing your dataset... This may take 10-30 seconds."):
            insights = generate_llm_insights(df)

            if insights:
                # Store insights in session state for persistence
                st.session_state.generated_insights = insights
                st.success("✅ Insights generated successfully!")
                if len(insights) < 5:
                    st.info(
                        "💡 Got fewer insights than expected? Try regenerating for more complete results.")
            else:
                st.error("❌ Failed to generate insights. Please try again.")
                st.info("💡 **Troubleshooting tips:**\n- Check your API key is valid\n- Ensure stable internet connection\n- Try clicking 'Regenerate Insights' if partially successful")

    # Display stored insights if available
    if hasattr(st.session_state, 'generated_insights') and st.session_state.generated_insights:
        st.markdown("---")
        display_insights(st.session_state.generated_insights)

        # Additional options
        st.markdown("---")
        st.subheader("📋 Next Steps")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Regenerate Insights", use_container_width=True):
                with st.spinner("🤖 Regenerating insights..."):
                    new_insights = generate_llm_insights(df)
                    if new_insights:
                        st.session_state.generated_insights = new_insights
                        st.rerun()

        with col2:
            if st.button("🧹 Clear Insights", use_container_width=True):
                if hasattr(st.session_state, 'generated_insights'):
                    del st.session_state.generated_insights
                st.rerun()

        with col3:
            st.markdown("💡 Use other tabs for detailed analysis")

    # Tips section
    elif api_configured:
        st.markdown("---")
        st.subheader("💡 What you'll get:")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Data Quality Insights:**
            - Missing data patterns
            - Data quality assessment
            - Potential data issues
            """)

        with col2:
            st.markdown("""
            **Statistical Insights:**
            - Key trends and patterns
            - Variable relationships
            - Business implications
            """)

        st.info("👆 Click 'Generate AI Insights' to get started!")

        # Show sample insights
        st.markdown("---")
        st.subheader("📋 Sample Insights")
        st.markdown("""
        Here are examples of the types of insights you might receive:
        
        **🔍 Data Quality Insights:**
        - "Dataset has 15% missing values in the 'age' column, which may impact age-related analysis"
        - "Found 23 duplicate rows (2.3% of data) that should be investigated before analysis"
        
        **📊 Statistical Insights:**  
        - "Sales show a strong seasonal pattern with 40% higher revenue in Q4"
        - "Strong correlation (0.78) between marketing spend and revenue indicates effective campaigns"
        
        **💡 Business Recommendations:**
        - "Customer categories are highly imbalanced - consider grouping smaller segments"
        - "Revenue data is right-skewed, suggesting a few high-value customers drive most sales"
        """)

        st.info("🤖 Generate insights using your own data above!")
