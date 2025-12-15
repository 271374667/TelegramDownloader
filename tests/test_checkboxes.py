#!/usr/bin/env python3
"""
Test script to verify GroupBox checkbox functionality
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config_manager import SessionConfig, DownloadConfig, FullConfig
from core.batch_generator import BatchGenerator


def test_checkbox_functionality():
    """Test that checkbox states control command generation"""

    print("Testing GroupBox Checkbox Functionality")
    print("=" * 60)

    # Test 1: All checkboxes enabled
    print("\n1. Testing with ALL GroupBoxes ENABLED:")
    print("-" * 40)

    session = SessionConfig(
        debug=True,
        delay="2s",
        limit=4,
        namespace="test",
        ntp_server="pool.ntp.org",
        pool=8,
        proxy="socks5://127.0.0.1:7897",
        reconnect_timeout="5m0s",
        storage_type="bolt",
        storage_path="~/.tdl/data",
        threads=8,
        # All enabled
        basic_settings_enabled=True,
        network_settings_enabled=True,
        storage_settings_enabled=True,
        performance_settings_enabled=True
    )

    download = DownloadConfig(
        urls=["https://t.me/test/1"],
        directory=os.path.join(os.getcwd(), "downloads"),
        include_extensions=["mp4"],
        skip_same=True,
        takeout=True,
        serve=True,
        port=9090,
        # All enabled
        basic_settings_enabled=True,
        file_filtering_enabled=True,
        advanced_settings_enabled=True,
        server_settings_enabled=True
    )

    config = FullConfig(session=session, download=download)
    generator = BatchGenerator()
    command = generator.get_preview_command(config)
    print(f"Command generated with all enabled:")
    print(f"Length: {len(command)} characters")
    print(f"Contains --debug: {'--debug' in command}")
    print(f"Contains --ntp: {'--ntp' in command}")
    print(f"Contains --serve: {'--serve' in command}")

    # Test 2: Some checkboxes disabled
    print("\n2. Testing with SOME GroupBoxes DISABLED:")
    print("-" * 40)

    session.basic_settings_enabled = False
    session.network_settings_enabled = False
    download.file_filtering_enabled = False
    download.server_settings_enabled = False

    command = generator.get_preview_command(config)
    print(f"Command generated with some disabled:")
    print(f"Length: {len(command)} characters")
    print(f"Contains --debug: {'--debug' in command}")
    print(f"Contains --ntp: {'--ntp' in command}")
    print(f"Contains --serve: {'--serve' in command}")
    print(f"Contains -i mp4: {'-i mp4' in command}")

    # Test 3: Only essential settings enabled
    print("\n3. Testing with ONLY ESSENTIAL GroupBoxes ENABLED:")
    print("-" * 40)

    session.basic_settings_enabled = False
    session.network_settings_enabled = False
    session.storage_settings_enabled = False
    session.performance_settings_enabled = False

    download.basic_settings_enabled = False
    download.file_filtering_enabled = False
    download.advanced_settings_enabled = False
    download.server_settings_enabled = False

    command = generator.get_preview_command(config)
    print(f"Command generated with only essentials:")
    print(f"Length: {len(command)} characters")
    print(f"Command: {command}")

    # Test 4: Batch file generation
    print("\n4. Testing BATCH FILE GENERATION:")
    print("-" * 40)

    # Re-enable some settings for a realistic test
    session.basic_settings_enabled = True
    session.storage_settings_enabled = True
    download.basic_settings_enabled = True

    success, message = generator.generate_batch(config)
    if success:
        print(f"[SUCCESS] {message}")
        print(f"Batch file location: {generator.get_batch_file_path()}")

        # Check first few lines of generated batch
        batch_path = generator.get_batch_file_path()
        if Path(batch_path).exists():
            with open(batch_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print("\nGenerated command in batch file:")
            for line in lines:
                if "tdl" in line and "dl" in line:
                    print(f"  {line.strip()}")
                    break
    else:
        print(f"[FAIL] {message}")

    # Test 5: Verify URL is always included (mandatory)
    print("\n5. Testing that URLs are ALWAYS INCLUDED:")
    print("-" * 40)

    # Disable all download settings
    download.basic_settings_enabled = False
    download.file_filtering_enabled = False
    download.advanced_settings_enabled = False
    download.server_settings_enabled = False

    command = generator.get_preview_command(config)
    has_url = "-u https://t.me/test/1" in command
    print(f"URL always included: {has_url}")
    print(f"Command still has URL: {has_url}")

    print("\n" + "=" * 60)
    print("Test completed!")

    return True


if __name__ == "__main__":
    test_checkbox_functionality()