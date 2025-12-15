#!/usr/bin/env python3
"""
Telegram Downloader GUI Launcher
Launches the application from the project root directory
"""

import sys
from pathlib import Path
from src.main import main

# Add the src directory to the Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))


if __name__ == "__main__":
    main()
