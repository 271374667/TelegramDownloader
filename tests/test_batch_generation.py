#!/usr/bin/env python3
"""
Test script to verify batch file generation functionality
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config_manager import SessionConfig, DownloadConfig, FullConfig
from core.batch_generator import BatchGenerator


def test_batch_generation():
    """Test the batch file generation with sample configuration"""

    print("Testing TDL Batch File Generation...")
    print("=" * 50)

    # Create sample session configuration
    session = SessionConfig(
        debug=True,
        delay="2s",
        limit=4,
        namespace="test",
        pool=8,
        proxy="socks5://127.0.0.1:7897",
        threads=8
    )

    # Create sample download configuration
    download = DownloadConfig(
        urls=[
            "https://t.me/tdl/1",
            "https://t.me/tdl/2"
        ],
        directory="test_downloads",
        include_extensions=["mp4", "jpg"],
        skip_same=True,
        takeout=True
    )

    # Create full configuration
    config = FullConfig(session=session, download=download)

    # Create batch generator
    generator = BatchGenerator()

    # Test 1: Validate configuration
    print("\n1. Testing configuration validation...")
    errors = config.validate()
    if errors:
        print(f"[FAIL] Validation errors found:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("[PASS] Configuration validation passed")

    # Test 2: Check for tdl.exe
    print("\n2. Checking for tdl.exe...")
    exists, message = generator.validate_tdl_executable()
    if exists:
        print(f"[PASS] {message}")
    else:
        print(f"[FAIL] {message}")

    # Test 3: Generate command preview
    print("\n3. Testing command preview...")
    preview = generator.get_preview_command(config)
    print(f"Generated command preview:")
    print(f"   {preview}")

    # Test 4: Generate batch file
    print("\n4. Testing batch file generation...")
    success, message = generator.generate_batch(config)
    if success:
        print(f"[PASS] {message}")
        print(f"   Batch file location: {generator.get_batch_file_path()}")

        # Show first few lines of generated batch file
        batch_path = generator.get_batch_file_path()
        if Path(batch_path).exists():
            with open(batch_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
            print("\n   First 10 lines of generated batch file:")
            for i, line in enumerate(lines, 1):
                print(f"   {i:2d}: {line.rstrip()}")
    else:
        print(f"[FAIL] {message}")

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_batch_generation()