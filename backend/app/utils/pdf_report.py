"""
PDF Report Generator for Vizzy

Creates comprehensive, professional PDF reports with data analysis insights.
"""

import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import base64

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from .quality_engine import DataQualityEngine
from .preprocessing_suggestions import PreprocessingSuggestionEngine


class VizzyPDFReport:
    """
    Professional PDF report generator for Vizzy data analysis.

    Creates comprehensive reports including:
    - Executive Summary
    - Data Quality Assessment
    - Missing Values Analysis
    - Distribution Analysis
    - Correlation Analysis
    - Preprocessing Recommendations
    - Visualizations and Charts
    """

    def __init__(self, df: pd.DataFrame, filename: str = None, dataset_name: str = None):
        self.df = df.copy()
        self.filename = filename or f"vizzy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.dataset_name = dataset_name or "Uploaded Dataset"
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        # Generate analysis data
        self.quality_engine = DataQualityEngine(df)
        self.quality_results = self.quality_engine.calculate_overall_score()
        self.preprocessing_engine = PreprocessingSuggestionEngine(df)
        self.preprocessing_suggestions = self.preprocessing_engine.generate_all_suggestions()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""

        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=40,  # Increased spacing after title
                alignment=TA_CENTER
            ))

        # Section header style
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#3498db'),
                spaceBefore=35,  # Increased spacing before section
                spaceAfter=25,   # Increased spacing after section
                borderWidth=1,
                borderColor=colors.HexColor('#3498db'),
                borderPadding=8
            ))

        # Subsection header style
        if 'SubsectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SubsectionHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceBefore=25,  # Increased spacing before subsection
                spaceAfter=18    # Increased spacing after subsection
            ))

        # Executive summary style
        if 'ExecutiveSummary' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ExecutiveSummary',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=14,
                spaceBefore=15,  # Increased spacing
                spaceAfter=15,   # Increased spacing
                borderWidth=1,
                borderColor=colors.HexColor('#ecf0f1'),
                borderPadding=12,
                backColor=colors.HexColor('#f8f9fa')
            ))

        # Insight box style
        if 'InsightBox' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='InsightBox',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=12,
                spaceBefore=12,  # Increased spacing
                spaceAfter=12,   # Increased spacing
                borderWidth=1,
                borderColor=colors.HexColor('#3498db'),
                borderPadding=8,
                backColor=colors.HexColor('#ebf3fd')
            ))

        # Code style
        if 'VizzyCode' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='VizzyCode',
                parent=self.styles['Normal'],
                fontSize=9,
                fontName='Courier',
                leading=11,
                spaceBefore=10,  # Increased spacing
                spaceAfter=10,   # Increased spacing
                borderWidth=1,
                borderColor=colors.HexColor('#dee2e6'),
                borderPadding=8,
                backColor=colors.HexColor('#f8f9fa')
            ))

    def generate_report(self) -> bytes:
        """Generate the complete PDF report and return as bytes."""

        # Create document
        buffer = io.BytesIO()
        self.doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=110,  # Further increased top margin to prevent header overlap
            bottomMargin=90  # Further increased bottom margin to prevent footer overlap
        )

        # Build the story
        self._add_title_page()
        self._add_executive_summary()
        self._add_dataset_overview()
        self._add_data_quality_section()
        self._add_missing_values_section()
        self._add_distribution_analysis()
        self._add_correlation_analysis()
        self._add_preprocessing_recommendations()
        self._add_appendix()

        # Build the PDF
        self.doc.build(self.story, onFirstPage=self._add_header_footer,
                       onLaterPages=self._add_header_footer)

        buffer.seek(0)
        return buffer.getvalue()

    def _add_title_page(self):
        """Add the title page with report metadata."""

        # Report title
        self.story.append(Spacer(1, 1.5*inch))
        self.story.append(
            Paragraph("Vizzy Data Analysis Report (Beta)", self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.8*inch))

        # Dataset info
        dataset_info = f"""
        <b>Dataset:</b> {self.dataset_name}<br/>
        <b>Rows:</b> {len(self.df):,}<br/>
        <b>Columns:</b> {len(self.df.columns)}<br/>
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Quality Score:</b> {self.quality_results['overall_score']:.1f}/100 ({self.quality_results['grade']})
        """

        self.story.append(Paragraph(dataset_info, self.styles['Normal']))
        self.story.append(Spacer(1, 1.0*inch))

        # Quality overview
        quality_summary = self._get_quality_summary()
        self.story.append(
            Paragraph(quality_summary, self.styles['ExecutiveSummary']))

        self.story.append(PageBreak())

    def _add_executive_summary(self):
        """Add executive summary section."""

        self.story.append(Paragraph("Executive Summary",
                          self.styles['SectionHeader']))

        # Key insights
        insights = self._generate_key_insights()
        for insight in insights:
            self.story.append(Paragraph(f"- {insight}", self.styles['Normal']))
            self.story.append(Spacer(1, 8))

        # Increased spacing after executive summary
        self.story.append(Spacer(1, 35))

    def _add_dataset_overview(self):
        """Add dataset overview section."""

        self.story.append(Paragraph("Dataset Overview",
                          self.styles['SectionHeader']))

        # Basic statistics table
        basic_stats = [
            ['Metric', 'Value'],
            ['Total Rows', f"{len(self.df):,}"],
            ['Total Columns', f"{len(self.df.columns)}"],
            ['Memory Usage',
                f"{self.df.memory_usage(deep=True).sum() / 1024**2:.1f} MB"],
            ['Missing Values',
                f"{self.df.isnull().sum().sum():,} ({self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)) * 100:.1f}%)"],
            ['Duplicate Rows', f"{self.df.duplicated().sum():,}"],
        ]

        stats_table = Table(basic_stats, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),  # Increased bottom padding
            ('TOPPADDING', (0, 0), (-1, 0), 8),      # Added top padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Added padding to data rows
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            # Added padding to data rows
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6)
        ]))

        self.story.append(stats_table)
        self.story.append(Spacer(1, 35))  # Increased spacing after table

        # Data types breakdown
        self.story.append(Paragraph("Data Types Breakdown",
                          self.styles['SubsectionHeader']))

        dtype_counts = self.df.dtypes.value_counts()
        dtype_data = [['Data Type', 'Count']]
        for dtype, count in dtype_counts.items():
            dtype_data.append([str(dtype), str(count)])

        dtype_table = Table(dtype_data, colWidths=[2*inch, 1*inch])
        dtype_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Increased padding
            ('TOPPADDING', (0, 0), (-1, 0), 8),      # Added top padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Added padding to data rows
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            # Added padding to data rows
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6)
        ]))

        self.story.append(dtype_table)
        self.story.append(Spacer(1, 30))  # Increased spacing after section

    def _add_data_quality_section(self):
        """Add comprehensive data quality analysis."""

        self.story.append(
            Paragraph("Data Quality Assessment", self.styles['SectionHeader']))

        # Overall quality score
        quality_text = f"""
        <b>Overall Quality Score:</b> {self.quality_results['overall_score']:.1f}/100 (Grade: {self.quality_results['grade']})<br/>
        <b>Assessment:</b> {self._get_quality_interpretation(self.quality_results['overall_score'])}
        """
        self.story.append(Paragraph(quality_text, self.styles['Normal']))
        self.story.append(Spacer(1, 20))  # Increased spacing

        # Quality dimensions breakdown
        self.story.append(Paragraph("Quality Dimensions",
                          self.styles['SubsectionHeader']))

        dimensions_data = [['Dimension', 'Score', 'Weight', 'Status']]

        # Define weights (matching the quality engine)
        weights = {
            'completeness': 0.25,
            'consistency': 0.20,
            'accuracy': 0.25,
            'uniqueness': 0.15,
            'validity': 0.15
        }

        for dim, details in self.quality_results['dimensions'].items():
            score = details['score']
            weight = weights.get(dim, 0.0)
            status = self._get_dimension_status(score)
            dimensions_data.append([
                dim.replace('_', ' ').title(),
                f"{score:.1f}/100",
                f"{weight:.0%}",
                status
            ])

        dimensions_table = Table(dimensions_data, colWidths=[
                                 1.5*inch, 1*inch, 1*inch, 1.5*inch])
        dimensions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Increased padding
            ('TOPPADDING', (0, 0), (-1, 0), 8),      # Added top padding
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Added padding to data rows
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            # Added padding to data rows
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6)
        ]))

        self.story.append(dimensions_table)
        self.story.append(Spacer(1, 25))  # Increased spacing after table

        # Quality recommendations
        if self.quality_results.get('recommendations'):
            self.story.append(Paragraph(
                "Quality Improvement Recommendations", self.styles['SubsectionHeader']))
            for i, rec in enumerate(self.quality_results['recommendations'][:5], 1):
                self.story.append(
                    Paragraph(f"{i}. {rec}", self.styles['Normal']))
                self.story.append(Spacer(1, 8))

        self.story.append(Spacer(1, 30))  # Increased section spacing

    def _add_missing_values_section(self):
        """Add missing values analysis."""

        self.story.append(PageBreak())
        self.story.append(
            Paragraph("Missing Values Analysis", self.styles['SectionHeader']))

        missing_counts = self.df.isnull().sum()
        missing_cols = missing_counts[missing_counts > 0]

        if len(missing_cols) == 0:
            self.story.append(Paragraph(
                "[OK] No missing values detected in the dataset.", self.styles['InsightBox']))
        else:
            # Missing values summary
            total_missing = missing_counts.sum()
            missing_pct = (total_missing / (len(self.df)
                           * len(self.df.columns))) * 100

            summary_text = f"""
            <b>Missing Values Summary:</b><br/>
            - Total missing values: {total_missing:,}<br/>
            - Percentage of dataset: {missing_pct:.2f}%<br/>
            - Columns affected: {len(missing_cols)} out of {len(self.df.columns)}
            """
            self.story.append(
                Paragraph(summary_text, self.styles['InsightBox']))
            self.story.append(Spacer(1, 20))  # Increased spacing

            # Missing values table
            if len(missing_cols) <= 20:  # Only show table if manageable size
                self.story.append(
                    Paragraph("Missing Values by Column", self.styles['SubsectionHeader']))

                missing_data = [['Column', 'Missing Count', 'Missing %']]
                for col in missing_cols.index:
                    count = missing_cols[col]
                    pct = (count / len(self.df)) * 100
                    missing_data.append([col, f"{count:,}", f"{pct:.1f}%"])

                missing_table = Table(missing_data, colWidths=[
                                      2.5*inch, 1*inch, 1*inch])
                missing_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                self.story.append(missing_table)
                self.story.append(Spacer(1, 30))  # Added spacing after table

    def _add_distribution_analysis(self):
        """Add distribution analysis for numeric columns."""

        self.story.append(Spacer(1, 30))  # Increased spacing before section
        self.story.append(Paragraph("Distribution Analysis",
                          self.styles['SectionHeader']))

        numeric_cols = self.df.select_dtypes(
            include=[np.number]).columns.tolist()

        if not numeric_cols:
            self.story.append(Paragraph(
                "[INFO] No numeric columns found for distribution analysis.", self.styles['InsightBox']))
        else:
            # Numeric columns summary
            summary_text = f"Analysis of {len(numeric_cols)} numeric columns in the dataset."
            self.story.append(Paragraph(summary_text, self.styles['Normal']))
            self.story.append(Spacer(1, 20))  # Increased spacing

            # Statistical summary table
            if len(numeric_cols) <= 10:  # Limit to prevent overwhelming
                self.story.append(
                    Paragraph("Statistical Summary", self.styles['SubsectionHeader']))

                stats_data = [
                    ['Column', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']]
                for col in numeric_cols[:10]:  # Limit to first 10 columns
                    series = self.df[col].dropna()
                    if len(series) > 0:
                        stats_data.append([
                            col,
                            f"{series.mean():.2f}",
                            f"{series.median():.2f}",
                            f"{series.std():.2f}",
                            f"{series.min():.2f}",
                            f"{series.max():.2f}"
                        ])

                stats_table = Table(stats_data, colWidths=[
                                    1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                ]))

                self.story.append(stats_table)
                self.story.append(Spacer(1, 30))  # Added spacing after table

    def _add_correlation_analysis(self):
        """Add correlation analysis."""

        self.story.append(Spacer(1, 30))  # Increased spacing before section
        self.story.append(Paragraph("Correlation Analysis",
                          self.styles['SectionHeader']))

        numeric_cols = self.df.select_dtypes(
            include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            self.story.append(Paragraph(
                "[INFO] Need at least 2 numeric columns for correlation analysis.", self.styles['InsightBox']))
        else:
            # Calculate correlations
            corr_matrix = self.df[numeric_cols].corr()

            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) >= 0.5:  # Strong correlation threshold
                        strong_correlations.append((
                            corr_matrix.columns[i],
                            corr_matrix.columns[j],
                            corr_value
                        ))

            if strong_correlations:
                self.story.append(
                    Paragraph("Strong Correlations (|r| ≥ 0.5)", self.styles['SubsectionHeader']))

                corr_data = [
                    ['Variable 1', 'Variable 2', 'Correlation', 'Strength']]
                for var1, var2, corr in sorted(strong_correlations, key=lambda x: abs(x[2]), reverse=True):
                    strength = self._get_correlation_strength(abs(corr))
                    corr_data.append([var1, var2, f"{corr:.3f}", strength])

                corr_table = Table(corr_data, colWidths=[
                                   1.8*inch, 1.8*inch, 1*inch, 1*inch])
                corr_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                self.story.append(corr_table)
                self.story.append(Spacer(1, 30))  # Added spacing after table
            else:
                self.story.append(Paragraph(
                    "No strong correlations (|r| ≥ 0.5) found between numeric variables.", self.styles['InsightBox']))
                self.story.append(Spacer(1, 20))

    def _add_preprocessing_recommendations(self):
        """Add preprocessing recommendations section."""

        self.story.append(PageBreak())
        self.story.append(
            Paragraph("Preprocessing Recommendations", self.styles['SectionHeader']))

        # Summary
        summary = self.preprocessing_suggestions['summary']
        urgency_text = f"""
        <b>Preprocessing Assessment:</b> {summary['urgency']} Priority<br/>
        {summary['text']}<br/>
        <b>Total Issues Found:</b> {summary['total_issues']}<br/>
        <b>High Priority Areas:</b> {summary['high_priority_count']}
        """
        self.story.append(
            Paragraph(urgency_text, self.styles['ExecutiveSummary']))
        self.story.append(Spacer(1, 25))  # Increased spacing

        # Top priorities
        priorities = self.preprocessing_suggestions['priorities']
        if priorities:
            self.story.append(
                Paragraph("Priority Recommendations", self.styles['SubsectionHeader']))

            # Top 6 priorities
            for i, (category, priority) in enumerate(priorities[:6], 1):
                if priority > 0:
                    urgency = "[HIGH]" if priority > 70 else "[MEDIUM]" if priority > 40 else "[LOW]"
                    self.story.append(Paragraph(
                        f"{i}. <b>{category}</b> - Priority: {priority:.0f}/100 ({urgency})", self.styles['Normal']))
                    # Increased spacing between items
                    self.story.append(Spacer(1, 10))

        # Increased spacing before next section
        self.story.append(Spacer(1, 30))

        # Detailed recommendations for high-priority items
        self._add_detailed_preprocessing_recommendations()

    def _add_detailed_preprocessing_recommendations(self):
        """Add detailed preprocessing recommendations for each category."""

        high_priority_categories = [
            ('missing_values', 'Missing Values Handling'),
            ('outliers', 'Outlier Treatment'),
            ('encoding', 'Categorical Encoding'),
            ('scaling', 'Feature Scaling')
        ]

        for category_key, category_name in high_priority_categories:
            if category_key in self.preprocessing_suggestions:
                category_data = self.preprocessing_suggestions[category_key]
                # Only show significant priorities
                if category_data.get('priority', 0) > 30:
                    self.story.append(
                        Paragraph(category_name, self.styles['SubsectionHeader']))

                    # Add suggestions
                    suggestions = category_data.get('suggestions', [])
                    # Limit to top 3 suggestions
                    for suggestion in suggestions[:3]:
                        self.story.append(
                            Paragraph(f"- {suggestion}", self.styles['Normal']))
                        self.story.append(Spacer(1, 8))

                    # Add code snippet if available
                    code_snippets = category_data.get('code_snippets', [])
                    if code_snippets:
                        self.story.append(
                            Paragraph("<b>Example Code:</b>", self.styles['Normal']))
                        # Take the first code snippet and truncate if too long
                        code = code_snippets[0]
                        if len(code) > 300:
                            code = code[:300] + "..."
                        self.story.append(
                            Paragraph(code, self.styles['VizzyCode']))

                    # Increased spacing between sections
                    self.story.append(Spacer(1, 25))

    def _add_appendix(self):
        """Add appendix with additional information."""

        self.story.append(PageBreak())
        self.story.append(
            Paragraph("Appendix", self.styles['SectionHeader']))

        # Column details
        self.story.append(Paragraph("Column Details",
                          self.styles['SubsectionHeader']))

        col_data = [['Column Name', 'Data Type',
                     'Non-Null Count', 'Unique Values']]
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            unique_count = self.df[col].nunique()
            col_data.append([
                col,
                str(self.df[col].dtype),
                f"{non_null:,}",
                f"{unique_count:,}"
            ])

        col_table = Table(col_data, colWidths=[
                          2*inch, 1.2*inch, 1*inch, 1*inch])
        col_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))

        self.story.append(col_table)
        self.story.append(Spacer(1, 30))  # Increased spacing after table

        # Report metadata
        metadata_text = f"""
        <b>Report Generated by:</b> Vizzy Data Analysis Tool<br/>
        <b>Generation Time:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Version:</b> 1.0.0 (Beta)<br/>
        <b>Dataset Shape:</b> {self.df.shape[0]:,} rows × {self.df.shape[1]} columns<br/>
        <b>Status:</b> This PDF export feature is under development. Future versions will include visualizations and enhanced formatting.
        """
        self.story.append(Paragraph(metadata_text, self.styles['Normal']))

    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()

        # Header - positioned even higher to avoid overlap with increased top margin
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#3498db'))
        canvas.drawString(72, A4[1] - 50, "Vizzy Data Analysis Report")

        # Footer - positioned with more space from bottom
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawRightString(A4[0] - 72, 50, f"Page {doc.page}")
        canvas.drawString(
            72, 50, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        canvas.restoreState()

    # Helper methods
    def _get_quality_summary(self):
        """Generate quality summary text."""
        score = self.quality_results['overall_score']
        grade = self.quality_results['grade']

        if score >= 90:
            return f"<b>Excellent Data Quality (Grade {grade})</b><br/>Your dataset demonstrates exceptional quality with minimal preprocessing needs. The data is well-structured and ready for analysis."
        elif score >= 80:
            return f"<b>Good Data Quality (Grade {grade})</b><br/>Your dataset shows good quality with minor issues. Some light preprocessing may enhance analysis outcomes."
        elif score >= 70:
            return f"<b>Fair Data Quality (Grade {grade})</b><br/>Your dataset has acceptable quality but would benefit from preprocessing to address identified issues."
        elif score >= 60:
            return f"<b>Poor Data Quality (Grade {grade})</b><br/>Your dataset has significant quality issues that should be addressed before analysis."
        else:
            return f"<b>Very Poor Data Quality (Grade {grade})</b><br/>Your dataset requires substantial cleaning and preprocessing before reliable analysis can be performed."

    def _get_quality_interpretation(self, score):
        """Get interpretation of quality score."""
        if score >= 90:
            return "Excellent - Ready for analysis"
        elif score >= 80:
            return "Good - Minor preprocessing recommended"
        elif score >= 70:
            return "Fair - Moderate preprocessing needed"
        elif score >= 60:
            return "Poor - Significant preprocessing required"
        else:
            return "Very Poor - Major preprocessing essential"

    def _get_dimension_status(self, score):
        """Get status text for quality dimension."""
        if score >= 85:
            return "[EXCELLENT]"
        elif score >= 70:
            return "[GOOD]"
        elif score >= 50:
            return "[FAIR]"
        else:
            return "[POOR]"

    def _get_correlation_strength(self, abs_corr):
        """Get correlation strength description."""
        if abs_corr >= 0.8:
            return "Very Strong"
        elif abs_corr >= 0.6:
            return "Strong"
        elif abs_corr >= 0.4:
            return "Moderate"
        else:
            return "Weak"

    def _generate_key_insights(self):
        """Generate key insights for executive summary."""
        insights = []

        # Data quality insight
        score = self.quality_results['overall_score']
        grade = self.quality_results['grade']
        insights.append(
            f"Dataset quality score: {score:.1f}/100 (Grade {grade}) - {self._get_quality_interpretation(score)}")

        # Missing values insight
        total_missing = self.df.isnull().sum().sum()
        if total_missing > 0:
            missing_pct = (total_missing / (len(self.df)
                           * len(self.df.columns))) * 100
            insights.append(
                f"Missing values: {total_missing:,} cells ({missing_pct:.1f}% of dataset) require attention")
        else:
            insights.append(
                "No missing values detected - excellent data completeness")

        # Duplicates insight
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(self.df)) * 100
            insights.append(
                f"Duplicate rows: {duplicates:,} ({dup_pct:.1f}%) should be reviewed")

        # Preprocessing priority insight
        high_priority_areas = self.preprocessing_suggestions['summary']['high_priority_areas']
        if high_priority_areas:
            insights.append(
                f"High-priority preprocessing areas: {', '.join(high_priority_areas[:3])}")
        else:
            insights.append("No high-priority preprocessing issues identified")

        # Data structure insight
        numeric_cols = len(self.df.select_dtypes(include=[np.number]).columns)
        cat_cols = len(self.df.select_dtypes(
            include=['object', 'category']).columns)
        insights.append(
            f"Data composition: {numeric_cols} numeric and {cat_cols} categorical columns")

        return insights


def generate_pdf_report(df: pd.DataFrame, filename: str = None, dataset_name: str = None) -> bytes:
    """
    Generate a comprehensive PDF report for the given dataframe.

    Args:
        df (pd.DataFrame): The dataframe to analyze
        filename (str, optional): Custom filename for the report
        dataset_name (str, optional): Name of the dataset to display in the report

    Returns:
        bytes: PDF content as bytes
    """
    report_generator = VizzyPDFReport(df, filename, dataset_name)
    return report_generator.generate_report()
