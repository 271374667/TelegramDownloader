#!/usr/bin/env python3
"""
Test script to verify default checkbox states
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config_manager import SessionConfig, DownloadConfig, FullConfig
from core.batch_generator import BatchGenerator


def test_default_states():
    """Test that default GroupBox states are correct"""

    print("Testing Default GroupBox States")
    print("=" * 60)

    # Create default configurations
    session = SessionConfig()
    download = DownloadConfig(urls=["https://t.me/test/1"])

    # Print default states
    print("\nSession Configuration GroupBox States:")
    print("-" * 40)
    print(f"Basic Settings:          {'[ENABLED]' if session.basic_settings_enabled else '[DISABLED]'} (should be [ENABLED])")
    print(f"Network Settings:        {'[ENABLED]' if session.network_settings_enabled else '[DISABLED]'} (should be [ENABLED])")
    print(f"Storage Settings:        {'[ENABLED]' if session.storage_settings_enabled else '[DISABLED]'} (should be [DISABLED])")
    print(f"Performance Settings:    {'[ENABLED]' if session.performance_settings_enabled else '[DISABLED]'} (should be [ENABLED])")

    print("\nDownload Configuration GroupBox States:")
    print("-" * 40)
    print(f"Basic Settings:          {'[ENABLED]' if download.basic_settings_enabled else '[DISABLED]'} (should be [ENABLED])")
    print(f"File Filtering:           {'[ENABLED]' if download.file_filtering_enabled else '[DISABLED]'} (should be [DISABLED])")
    print(f"Advanced Settings:       {'[ENABLED]' if download.advanced_settings_enabled else '[DISABLED]'} (should be [DISABLED])")
    print(f"Server Settings:          {'[ENABLED]' if download.server_settings_enabled else '[DISABLED]'} (should be [DISABLED])")

    # Generate command with defaults
    config = FullConfig(session=session, download=download)
    generator = BatchGenerator()
    command = generator.get_preview_command(config)

    print("\nDefault Generated Command:")
    print("-" * 40)
    print(command)

    print("\nCommand Analysis:")
    print("-" * 40)
    print(f"Contains --storage:    {'--storage' in command} (should be False)")
    print(f"Contains -i/-e:        {'-i mp4' in command or '-e jpg' in command} (should be False)")
    print(f"Contains --template:   {'--template' in command} (should be False)")
    print(f"Contains --serve:      {'--serve' in command} (should be False)")
    print(f"Contains --port:       {'--port' in command} (should be False)")
    print(f"Contains URLs:        {'-u https://t.me/test/1' in command} (should be True)")

    # Expected minimal command with defaults
    expected_parts = [
        "bin\\tdl dl",
        "-u https://t.me/test/1",
        "-l 2",  # From Basic Settings
        "-n default",  # From Basic Settings
        "-t 4",  # From Performance Settings
        "-d",  # Download directory from Basic Settings
        "--pool 8",  # From Network Settings
        "--proxy socks5://127.0.0.1:7897",  # From Network Settings
        "--reconnect-timeout 5m0s"  # From Network Settings
    ]

    print("\nExpected Command Parts (should be present):")
    print("-" * 40)
    for part in expected_parts:
        present = part in command
        status = "[OK]" if present else "[MISSING]"
        print(f"{status} {part}")

    print("\n" + "=" * 60)
    print("Test completed!")

    # Check if defaults are correct
    defaults_correct = (
        session.basic_settings_enabled and
        session.network_settings_enabled and
        not session.storage_settings_enabled and
        session.performance_settings_enabled and
        download.basic_settings_enabled and
        not download.file_filtering_enabled and
        not download.advanced_settings_enabled and
        not download.server_settings_enabled
    )

    if defaults_correct:
        print("\n[SUCCESS] All default states are CORRECT!")
    else:
        print("\n[ERROR] Some default states are INCORRECT!")

    return defaults_correct


if __name__ == "__main__":
    success = test_default_states()
    sys.exit(0 if success else 1)