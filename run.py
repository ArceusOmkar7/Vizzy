"""
Quick run script for the Vizzy app.

This script handles dependency installation and runs the Streamlit app.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import pandas
        import matplotlib
        import seaborn
        import numpy
        return True
    except ImportError:
        return False


def install_dependencies():
    """Install dependencies using UV or pip."""
    print("📦 Installing dependencies...")

    # Check if UV is available
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("Using UV package manager...")
        subprocess.run(["uv", "sync"], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("UV not found, using pip...")
        subprocess.run([sys.executable, "-m", "pip", "install",
                       "-r", "requirements.txt"], check=True)

    print("✅ Dependencies installed successfully!")


def create_sample_data():
    """Create sample data if it doesn't exist."""
    data_dir = Path("sample_data")
    if not data_dir.exists() or not any(data_dir.glob("*.csv")):
        print("📊 Creating sample datasets...")
        subprocess.run([sys.executable, "create_sample_data.py"])


def main():
    """Main function to run the Vizzy app."""
    print("🚀 Starting Vizzy...")

    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found. Please run this script from the project root directory.")
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        try:
            install_dependencies()
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            print("Please install dependencies manually:")
            print("  UV: uv sync")
            print("  Pip: pip install -r requirements.txt")
            sys.exit(1)

    # Create sample data
    create_sample_data()

    # Run the Streamlit app
    print("\n🎉 Launching Vizzy...")
    print("📱 The app will open in your default browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("\n" + "="*50 + "\n")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Vizzy!")
    except Exception as e:
        print(f"\n❌ Error running the app: {e}")
        print("Try running manually: streamlit run app.py")


if __name__ == "__main__":
    main()
