#!/usr/bin/env python3
"""
Build script for Telegram Downloader GUI
Supports both PyInstaller and Nuitka for creating standalone executables
Optimized for minimal package size by excluding unused PySide6 modules
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


# Configuration
APP_NAME = "TDL-GUI"
APP_VERSION = "1.0.0"
ENTRY_POINT = "run.py"
ICON_PATH = None  # Set to icon path if available, e.g., "assets/icon.ico"

# Directories
PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_DIR = PROJECT_ROOT

# ============================================================
# PySide6 Module Optimization
# ============================================================

# Modules actually used by this project (QtWidgets, QtCore, QtGui only)
PYSIDE6_REQUIRED_MODULES = [
    "PySide6.QtWidgets",
    "PySide6.QtCore",
    "PySide6.QtGui",
]

# Large modules to exclude (saves ~200-500MB)
PYSIDE6_EXCLUDE_MODULES = [
    # WebEngine - extremely large (~150MB+)
    "PySide6.QtWebEngine",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtWebChannel",
    "PySide6.QtWebSockets",

    # 3D modules (~50MB+)
    "PySide6.Qt3DCore",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DExtras",
    "PySide6.Qt3DAnimation",

    # Multimedia (~30MB+)
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",

    # Quick/QML (~40MB+)
    "PySide6.QtQuick",
    "PySide6.QtQuickWidgets",
    "PySide6.QtQuickControls2",
    "PySide6.QtQml",
    "PySide6.QtQmlModels",
    "PySide6.QtQmlCore",

    # Data visualization (~20MB+)
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtGraphs",

    # PDF (~15MB+)
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",

    # OpenGL
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",

    # Other unused modules
    "PySide6.QtDesigner",
    "PySide6.QtHelp",
    "PySide6.QtSql",
    "PySide6.QtTest",
    "PySide6.QtXml",
    "PySide6.QtSvg",
    "PySide6.QtSvgWidgets",
    "PySide6.QtNetwork",
    "PySide6.QtNetworkAuth",
    "PySide6.QtPositioning",
    "PySide6.QtLocation",
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtRemoteObjects",
    "PySide6.QtScxml",
    "PySide6.QtSensors",
    "PySide6.QtSerialPort",
    "PySide6.QtSerialBus",
    "PySide6.QtStateMachine",
    "PySide6.QtTextToSpeech",
    "PySide6.QtDBus",
    "PySide6.QtAxContainer",
    "PySide6.QtUiTools",
    "PySide6.QtConcurrent",
    "PySide6.QtSpatialAudio",
    "PySide6.QtHttpServer",
    "PySide6.QtShaderTools",
    "PySide6.QtAsyncio",
    "PySide6.QtGraphsWidgets",
]

# Qt plugins to exclude
QT_PLUGINS_EXCLUDE = [
    "imageformats/qgif",
    "imageformats/qicns",
    "imageformats/qjpeg",
    "imageformats/qpdf",
    "imageformats/qsvg",
    "imageformats/qtga",
    "imageformats/qtiff",
    "imageformats/qwbmp",
    "imageformats/qwebp",
    "multimedia",
    "mediaservice",
    "playlistformats",
    "position",
    "geoservices",
    "texttospeech",
    "virtualkeyboard",
    "canbus",
    "scenegraph",
    "qmltooling",
    "designer",
    "sqldrivers",
    "webview",
]


def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")

    dirs_to_clean = [DIST_DIR, BUILD_DIR]
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_path}")

    # Remove .spec file (PyInstaller)
    spec_file = SPEC_DIR / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"  Removed: {spec_file}")

    # Remove Nuitka build artifacts
    nuitka_build = PROJECT_ROOT / f"{ENTRY_POINT.replace('.py', '')}.build"
    if nuitka_build.exists():
        shutil.rmtree(nuitka_build)
        print(f"  Removed: {nuitka_build}")

    nuitka_dist = PROJECT_ROOT / f"{ENTRY_POINT.replace('.py', '')}.dist"
    if nuitka_dist.exists():
        shutil.rmtree(nuitka_dist)
        print(f"  Removed: {nuitka_dist}")


# ============================================================
# PyInstaller Build (Optimized)
# ============================================================

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("ERROR: PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        return False


def check_upx():
    """Check if UPX is available for compression"""
    try:
        result = subprocess.run(["upx", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("UPX available for compression")
            return True
    except (FileNotFoundError, OSError):
        pass
    print("UPX not found - skipping compression (optional)")
    return False


def build_with_pyinstaller(use_upx: bool = True):
    """Build the executable using PyInstaller with size optimization"""
    print(f"\nBuilding {APP_NAME} with PyInstaller (optimized)...")

    if not check_pyinstaller():
        return False

    upx_available = check_upx() if use_upx else False

    # Change to project root directory
    os.chdir(PROJECT_ROOT)

    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onedir",            # Directory distribution (faster startup, easier debugging)
        "--windowed",          # No console window (GUI app)
        "--noconfirm",         # Replace output directory without confirmation
        "--clean",             # Clean cache before building

        # Optimize size
        "--strip",             # Strip debug symbols (Linux/Mac)
        "--noupx",             # Disable UPX (causes issues without proper installation)

        # Log level
        "--log-level", "WARN",
    ]

    # Add source path
    cmd.extend(["--add-data", f"src{os.pathsep}src"])

    # Hidden imports - only what's actually needed
    for module in PYSIDE6_REQUIRED_MODULES:
        cmd.extend(["--hidden-import", module])

    # Additional hidden imports for winotify
    cmd.extend([
        "--hidden-import", "winotify",
        "--hidden-import", "winotify._registry",
    ])

    # shiboken6 is required by PySide6 at runtime
    cmd.extend([
        "--hidden-import", "shiboken6",
        "--hidden-import", "shiboken6.Shiboken",
    ])

    # Python standard library modules that may be needed
    cmd.extend([
        "--hidden-import", "platform",
        "--hidden-import", "subprocess",
        "--hidden-import", "json",
        "--hidden-import", "logging",
        "--hidden-import", "pathlib",
        "--hidden-import", "typing",
        "--hidden-import", "dataclasses",
        "--hidden-import", "enum",
        "--hidden-import", "re",
        "--hidden-import", "os",
        "--hidden-import", "sys",
        "--hidden-import", "shutil",
        "--hidden-import", "tempfile",
        "--hidden-import", "datetime",
        "--hidden-import", "uuid",
        "--hidden-import", "threading",
        "--hidden-import", "queue",
        "--hidden-import", "winsound",  # Windows sound module
        "--hidden-import", "ctypes",
        "--hidden-import", "winreg",    # Windows registry
    ])

    # Exclude all unused PySide6 modules (CRITICAL for size reduction)
    for module in PYSIDE6_EXCLUDE_MODULES:
        cmd.extend(["--exclude-module", module])

    # Exclude other large unused packages (be conservative to avoid runtime errors)
    extra_excludes = [
        # Data science libraries (large, definitely not needed)
        "matplotlib", "numpy", "pandas", "scipy", "PIL", "cv2",
        "torch", "tensorflow", "keras", "sklearn",
        # Development tools
        "IPython", "notebook", "jupyter",
        "pytest",
        # Other GUI frameworks
        "tkinter", "turtle",
        # Network protocols not used
        "xmlrpc", "ftplib", "imaplib", "smtplib",
        # Database (not used)
        "sqlite3", "dbm",
        # Unix-specific
        "curses", "readline",
    ]
    for module in extra_excludes:
        cmd.extend(["--exclude-module", module])

    # Add icon if available
    if ICON_PATH:
        icon_full_path = PROJECT_ROOT / ICON_PATH
        if icon_full_path.exists():
            cmd.extend(["--icon", str(icon_full_path)])
            print(f"Using icon: {icon_full_path}")

    # Add entry point
    cmd.append(ENTRY_POINT)

    print(f"\nRunning: {' '.join(cmd[:10])}... (truncated)")
    print(f"Excluding {len(PYSIDE6_EXCLUDE_MODULES)} unused PySide6 modules")

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    return result.returncode == 0


# ============================================================
# Nuitka Build (Optimized)
# ============================================================

def check_nuitka():
    """Check if Nuitka is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"Nuitka version: {version}")
            return True
        else:
            raise ImportError()
    except (ImportError, FileNotFoundError):
        print("ERROR: Nuitka is not installed.")
        print("Install it with: pip install nuitka")
        return False


def build_with_nuitka(standalone: bool = True, onefile: bool = True):
    """
    Build the executable using Nuitka with size optimization

    Args:
        standalone: Create a standalone distribution (default: True)
        onefile: Create a single executable file (default: True)
    """
    print(f"\nBuilding {APP_NAME} with Nuitka (optimized)...")

    if not check_nuitka():
        return False

    # Change to project root directory
    os.chdir(PROJECT_ROOT)

    # Build Nuitka command
    cmd = [
        sys.executable, "-m", "nuitka",
        f"--output-filename={APP_NAME}.exe",
        "--windows-console-mode=disable",  # No console window (GUI app)
        "--remove-output",                  # Remove build directory after compilation

        # Include source package
        "--include-package=src",
        "--include-package-data=src",

        # PySide6 plugin with optimization
        "--enable-plugin=pyside6",

        # Include winotify
        "--include-module=winotify",

        # Windows specific
        "--windows-company-name=TDL",
        "--windows-product-name=Telegram Downloader GUI",
        f"--windows-file-version={APP_VERSION}.0",
        f"--windows-product-version={APP_VERSION}.0",
        "--windows-file-description=Telegram Downloader GUI Application",

        # Optimization flags
        "--lto=yes",                        # Link Time Optimization
        "--jobs=4",                         # Parallel compilation
    ]

    # Exclude unused PySide6 modules using nofollow patterns (CRITICAL for size reduction)
    qt_nofollow_patterns = [
        "PySide6.QtWebEngine*",
        "PySide6.Qt3D*",
        "PySide6.QtMultimedia*",
        "PySide6.QtQuick*",
        "PySide6.QtQml*",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtPdf*",
        "PySide6.QtOpenGL*",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
        "PySide6.QtSql",
        "PySide6.QtTest",
        "PySide6.QtNetwork*",
        "PySide6.QtSvg*",
        "PySide6.QtBluetooth",
        "PySide6.QtNfc",
        "PySide6.QtPositioning",
        "PySide6.QtLocation",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort",
        "PySide6.QtSerialBus",
        "PySide6.QtRemoteObjects",
        "PySide6.QtScxml",
        "PySide6.QtStateMachine",
        "PySide6.QtTextToSpeech",
        "PySide6.QtDBus",
        "PySide6.QtHttpServer",
    ]

    for pattern in qt_nofollow_patterns:
        cmd.append(f"--nofollow-import-to={pattern}")

    # Exclude other unused packages
    other_excludes = [
        "matplotlib", "numpy", "pandas", "scipy",
        "PIL", "cv2", "torch", "tensorflow",
        "pytest", "unittest", "IPython", "notebook",
        "tkinter", "turtle", "sqlite3",
    ]
    for module in other_excludes:
        cmd.append(f"--nofollow-import-to={module}")

    # Standalone mode
    if standalone:
        cmd.append("--standalone")

    # Onefile mode
    if onefile:
        cmd.append("--onefile")
        cmd.append(f"--onefile-tempdir-spec=%TEMP%/{APP_NAME}")
        # Compression for onefile (requires zstandard)
        try:
            import zstandard
            cmd.append("--onefile-compression=zstd")
            print("Using zstd compression for onefile")
        except ImportError:
            print("zstandard not available, using default compression")

    # Output directory
    cmd.append(f"--output-dir={DIST_DIR}")

    # Add icon if available
    if ICON_PATH:
        icon_full_path = PROJECT_ROOT / ICON_PATH
        if icon_full_path.exists():
            cmd.append(f"--windows-icon-from-ico={icon_full_path}")
            print(f"Using icon: {icon_full_path}")

    # Add entry point
    cmd.append(ENTRY_POINT)

    print(f"\nRunning Nuitka with {len(cmd)} arguments...")
    print(f"Excluding {len(qt_nofollow_patterns)} unused PySide6 module patterns")
    print("Note: Nuitka compilation may take several minutes...\n")

    # Run Nuitka
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    return result.returncode == 0


def build_with_nuitka_standalone():
    """Build standalone (folder) distribution with Nuitka"""
    return build_with_nuitka(standalone=True, onefile=False)


def build_with_nuitka_onefile():
    """Build single-file executable with Nuitka"""
    return build_with_nuitka(standalone=True, onefile=True)


# ============================================================
# Post-build Operations
# ============================================================

def copy_dependencies():
    """Copy additional dependencies to dist folder"""
    print("\nCopying additional files...")

    # For --onedir mode, output is in dist/APP_NAME/
    dist_app_dir = DIST_DIR / APP_NAME

    # PyInstaller places dependencies in _internal folder
    internal_dir = dist_app_dir / "_internal"
    if not internal_dir.exists():
        internal_dir.mkdir(parents=True, exist_ok=True)

    # Copy bin folder (contains tdl.exe) to _internal
    bin_src = PROJECT_ROOT / "bin"
    bin_dst = internal_dir / "bin"
    if bin_src.exists():
        if bin_dst.exists():
            shutil.rmtree(bin_dst)
        shutil.copytree(bin_src, bin_dst)
        print(f"  Copied: bin/ -> {bin_dst}")
    else:
        print("  Warning: bin/ folder not found, creating empty folder")
        bin_dst.mkdir(parents=True, exist_ok=True)

    # Copy downloads folder structure (empty) to _internal
    downloads_dst = internal_dir / "downloads"
    downloads_dst.mkdir(parents=True, exist_ok=True)
    print(f"  Created: {downloads_dst}")

    # Create a simple README for the distribution
    readme_content = f"""# {APP_NAME} v{APP_VERSION}

Telegram Downloader GUI - A graphical interface for tdl

## Usage
1. Place tdl.exe in the '_internal/bin' folder
2. Run {APP_NAME}.exe
3. Configure your session and download settings
4. Add Telegram URLs and generate/run batch files

## Features
- Session configuration for Telegram API
- Download configuration with multiple options
- Clipboard monitoring for automatic URL detection
- Floating quick action panel
- System tray integration

## Requirements
- Windows 10/11
- tdl.exe in the _internal/bin folder

## Keyboard Shortcuts
- Ctrl+Shift+F: Toggle floating panel
"""

    readme_path = dist_app_dir / "README.txt"
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"  Created: {readme_path}")


def print_success(builder: str):
    """Print success message"""
    print("\n" + "=" * 50)
    print(f"  BUILD SUCCESSFUL! ({builder})")
    print("=" * 50)

    # For --onedir mode, exe is in dist/APP_NAME/
    dist_app_dir = DIST_DIR / APP_NAME
    exe_path = dist_app_dir / f"{APP_NAME}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\nExecutable: {exe_path}")
        print(f"Size: {size_mb:.2f} MB")

        # Calculate total folder size
        total_size = sum(f.stat().st_size for f in dist_app_dir.rglob('*') if f.is_file())
        total_mb = total_size / (1024 * 1024)
        print(f"Total folder size: {total_mb:.2f} MB")

        # Size comparison guidance
        if size_mb < 50:
            print("✅ Excellent! Package size is well optimized")
        elif size_mb < 100:
            print("✅ Good package size")
        elif size_mb < 150:
            print("⚠️ Package size is moderate, consider further optimization")
        else:
            print("⚠️ Package size is large, check if all exclusions are working")

    dist_app_dir = DIST_DIR / APP_NAME  # Define again for print statements
    internal_dir = dist_app_dir / "_internal"
    print(f"\nTo run the application:")
    print(f"  1. Ensure tdl.exe is in {internal_dir / 'bin'}")
    print(f"  2. Run {dist_app_dir / f'{APP_NAME}.exe'}")


def print_size_tips():
    """Print tips for further size reduction"""
    print("\n" + "-" * 50)
    print("TIPS FOR FURTHER SIZE REDUCTION:")
    print("-" * 50)
    print("""
1. Install UPX for compression:
   - Download from https://upx.github.io/
   - Add to PATH or place in project root

2. For Nuitka, install zstandard:
   pip install zstandard

3. Use --nuitka for potentially smaller builds
   (Nuitka often produces smaller executables than PyInstaller)

4. If using PyInstaller, try creating a .spec file
   for fine-grained control over bundled files
""")


# ============================================================
# Main Entry Points
# ============================================================

def build_pyinstaller():
    """Complete build process using PyInstaller"""
    print("=" * 50)
    print(f"  {APP_NAME} Build Script (PyInstaller - Optimized)")
    print("=" * 50)

    clean_build()

    if not build_with_pyinstaller():
        print("\nERROR: Build failed!")
        return False

    copy_dependencies()
    print_success("PyInstaller")
    print_size_tips()
    return True


def build_nuitka(onefile: bool = True):
    """Complete build process using Nuitka"""
    mode = "onefile" if onefile else "standalone"
    print("=" * 50)
    print(f"  {APP_NAME} Build Script (Nuitka - {mode} - Optimized)")
    print("=" * 50)

    clean_build()

    if onefile:
        success = build_with_nuitka_onefile()
    else:
        success = build_with_nuitka_standalone()

    if not success:
        print("\nERROR: Build failed!")
        return False

    copy_dependencies()
    print_success(f"Nuitka {mode}")
    print_size_tips()
    return True


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description=f"Build {APP_NAME} executable (optimized for minimal size)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Default: PyInstaller build
  python build.py --pyinstaller      # PyInstaller build
  python build.py --nuitka           # Nuitka onefile build (recommended)
  python build.py --nuitka-folder    # Nuitka standalone folder build
  python build.py --clean            # Clean build artifacts only

Size Optimization Notes:
  - This script excludes ~50 unused PySide6 modules
  - Expected size reduction: 200-500MB compared to unoptimized build
  - Nuitka typically produces smaller executables than PyInstaller
  - Install UPX for additional compression with PyInstaller
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--pyinstaller", "-p",
        action="store_true",
        help="Build using PyInstaller (default)"
    )
    group.add_argument(
        "--nuitka", "-n",
        action="store_true",
        help="Build using Nuitka (onefile mode) - often produces smaller builds"
    )
    group.add_argument(
        "--nuitka-folder", "-nf",
        action="store_true",
        help="Build using Nuitka (standalone folder mode)"
    )
    group.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Clean build artifacts only"
    )

    args = parser.parse_args()

    if args.clean:
        clean_build()
        print("\nClean completed!")
        return

    if args.nuitka:
        success = build_nuitka(onefile=True)
    elif args.nuitka_folder:
        success = build_nuitka(onefile=False)
    else:
        # Default to PyInstaller
        success = build_pyinstaller()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # main()
    # build_nuitka(onefile=False)
    build_pyinstaller()
