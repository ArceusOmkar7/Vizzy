#!/usr/bin/env python3
"""
Setup and Installation Guide for Vizzy

This script provides step-by-step guidance for setting up the Vizzy app.
"""

import subprocess
import sys
import os
from pathlib import Path
import platform


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("📊 VIZZY - SETUP & INSTALLATION GUIDE")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required!")
        print(
            f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again.")
        return False
    else:
        print(
            f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
        return True


def check_package_manager():
    """Check which package manager is available."""
    print("\n📦 Checking package managers...")

    # Check for UV
    try:
        result = subprocess.run(["uv", "--version"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ UV package manager found - Recommended!")
            return "uv"
    except FileNotFoundError:
        pass

    # Check for pip
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pip package manager found")
            return "pip"
    except FileNotFoundError:
        pass

    print("❌ No compatible package manager found!")
    return None


def install_uv():
    """Install UV package manager."""
    print("\n🚀 Installing UV package manager...")
    system = platform.system().lower()

    if system == "windows":
        print("Run this command in PowerShell:")
        print("   powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
    else:
        print("Run this command in your terminal:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")

    print("\nAfter installation, restart your terminal and run this script again.")


def install_dependencies(package_manager):
    """Install project dependencies."""
    print(f"\n📚 Installing dependencies using {package_manager}...")

    try:
        if package_manager == "uv":
            subprocess.run(["uv", "sync"], check=True)
        else:  # pip
            subprocess.run([sys.executable, "-m", "pip", "install",
                           "-r", "requirements.txt"], check=True)

        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_sample_data():
    """Create sample datasets."""
    print("\n📊 Creating sample datasets...")

    try:
        subprocess.run([sys.executable, "create_sample_data.py"], check=True)
        print("✅ Sample data created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating sample data: {e}")
        return False


def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE! HERE'S HOW TO USE THE APP:")
    print("=" * 60)
    print()
    print("1. 🚀 START THE APP:")
    print("   • Method 1 (Simple): python run.py")
    print("   • Method 2 (Manual): streamlit run app.py")
    print()
    print("2. 📁 UPLOAD YOUR DATA:")
    print("   • Supported formats: CSV, Excel (.xlsx, .xls)")
    print("   • Use the sample data in 'sample_data/' folder to test")
    print()
    print("3. 🎯 SELECT VISUALIZATIONS:")
    print("   • Use the sidebar to choose which charts to generate")
    print("   • Start with basic options, then explore advanced features")
    print()
    print("4. 📊 EXPLORE YOUR DATA:")
    print("   • View missing values patterns")
    print("   • Analyze distributions and correlations")
    print("   • Examine categorical data insights")
    print()
    print("💡 SAMPLE DATASETS AVAILABLE:")
    print("   • sales_data.csv - E-commerce sales data")
    print("   • student_performance.csv - Academic scores")
    print("   • messy_data.csv - Data with missing values")
    print("   • high_cardinality_data.csv - Transaction data")
    print()
    print("🔗 ACCESS: http://localhost:8501")
    print("⏹️  STOP: Press Ctrl+C in the terminal")
    print()
    print("=" * 60)


def main():
    """Main setup function."""
    print_header()

    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found!")
        print("   Please run this script from the Vizzy project directory.")
        return

    # Check Python version
    if not check_python_version():
        return

    # Check package manager
    package_manager = check_package_manager()
    if not package_manager:
        print("\n💡 Recommendation: Install UV for better dependency management")
        install_uv()
        return

    # Install dependencies
    if package_manager == "uv":
        print("\n📋 Using UV for dependency management (recommended)")
    else:
        print("\n📋 Using pip for dependency management")
        print("   💡 Consider installing UV for faster dependency resolution")

    if not install_dependencies(package_manager):
        print("\n🔧 TROUBLESHOOTING:")
        print("   • Check your internet connection")
        print("   • Try running the installation command manually:")
        if package_manager == "uv":
            print("     uv sync")
        else:
            print("     pip install -r requirements.txt")
        return

    # Create sample data
    if not create_sample_data():
        print("   Sample data creation failed, but you can still use your own data")

    # Print usage instructions
    print_usage_instructions()


if __name__ == "__main__":
    main()
