# Telegram Downloader GUI - TDL GUI

A PySide6-based graphical user interface for the [TDL (Telegram Downloader)](https://github.com/iyear/tdl) tool.

## Features

- 🖥️ **Intuitive GUI**: User-friendly interface for configuring TDL parameters
- 🔧 **Session Configuration**: Complete control over TDL session settings
- 📥 **Download Management**: Easy URL management with validation
- ⚙️ **Advanced Options**: Full access to all TDL parameters
- 🚀 **Batch Generation**: Generates ready-to-use .bat files for downloading

## Installation

### Prerequisites

1. Make sure you have [Python 3.8+](https://www.python.org/) installed
2. Download [tdl.exe](https://github.com/iyear/tdl/releases) and place it in the same directory as the GUI application

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure `tdl.exe` is in the application directory

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### 1. Session Configuration

Configure your Telegram session settings:

- **Basic Settings**: Debug mode, delay between tasks, concurrent tasks limit, session namespace
- **Network Settings**: NTP server, DC pool size, proxy settings, reconnect timeout
- **Storage Settings**: Storage type and path for session data
- **Performance Settings**: Thread count for transfers

### 2. Download Configuration

Set up your download parameters:

- **URL Management**: Add, edit, and remove Telegram message URLs
- **Basic Settings**: Download directory, continue/restart options, ordering preferences
- **File Filtering**: Include/exclude specific file extensions
- **Advanced Options**: Custom file naming templates, server mode
- **Server Settings**: HTTP server port for server mode

### 3. Generate Batch File

1. Configure all desired parameters
2. Click "👁️ Update Preview" to see the command that will be generated
3. Click "🚀 Generate Batch File" to create `telegram_downloader.bat`
4. Run the generated batch file to start downloading

## URL Format

Supported Telegram message URL formats:
- `https://t.me/channel/123`
- `https://t.me/c/123/456`

## Batch File

The generated `telegram_downloader.bat` file contains:
- Proper UTF-8 encoding setup
- Command echo for transparency
- The actual TDL command with all parameters
- Completion messages

## Requirements

- **Python**: 3.8 or higher
- **PySide6**: 6.5.0 or higher
- **TDL**: tdl.exe executable in the same directory

## Directory Structure

```
TDL/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── tdl.exe                # TDL executable (you need to download this)
├── telegram_downloader.bat # Generated batch file (created by GUI)
├── core/                  # Core functionality
│   ├── config_manager.py  # Configuration data models
│   └── batch_generator.py # Batch file generation
└── ui/                    # User interface components
    ├── main_window.py     # Main application window
    ├── session_tab.py     # Session configuration tab
    ├── download_tab.py    # Download configuration tab
    └── widgets/
        └── url_list.py    # Custom URL list widget
```

## Examples

### Basic Download
1. Add URL: `https://t.me/somechannel/123`
2. Set download directory: `downloads`
3. Click "Generate Batch File"
4. Run the generated batch file

### Advanced Download with Proxy
1. **Session Tab**:
   - Set proxy: `socks5://127.0.0.1:7897`
   - Increase threads: `8`
   - Set pool size: `4`

2. **Download Tab**:
   - Add multiple URLs
   - Set include extensions: `mp4,mp3,jpg`
   - Enable "Takeout session" for lower flood limits

3. Generate and run batch file

## Troubleshooting

### tdl.exe Not Found
- Ensure `tdl.exe` is in the same directory as the GUI application
- Download the latest version from the [TDL releases](https://github.com/iyear/tdl/releases)

### Import Errors
- Install required dependencies: `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

### Configuration Validation Errors
- Check that all required fields are filled
- Verify URL format is correct
- Ensure numeric values are within valid ranges

## License

This GUI application is provided as-is for use with TDL. Please refer to the [TDL license](https://github.com/iyear/tdl/blob/main/LICENSE) for the underlying tool.