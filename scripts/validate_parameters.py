#!/usr/bin/env python3
"""
Comprehensive validation test to ensure all command-line parameters from req.md are properly handled
"""

import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_manager import SessionConfig, DownloadConfig, FullConfig


def test_all_parameters():
    """Test that all parameters from req.md are properly handled"""

    print("Validating All TDL Parameters from req.md")
    print("=" * 60)

    # Test Session Parameters (from req.md lines 8-18)
    print("\n1. Testing SESSION PARAMETERS:")
    print("-" * 30)

    session = SessionConfig(
        debug=True,  # --debug
        delay="5s",  # --delay duration
        limit=3,  # -l, --limit int
        namespace="test_session",  # -n, --ns string
        ntp_server="pool.ntp.org",  # --ntp string
        pool=16,  # --pool int
        proxy="https://localhost:8081",  # --proxy string
        reconnect_timeout="10m0s",  # --reconnect-timeout duration
        storage_type="file",  # --storage stringToString
        storage_path="/custom/path",
        threads=8  # -t, --threads int
    )

    print("   [SET] debug: True")
    print("   [SET] delay: 5s")
    print("   [SET] limit: 3")
    print("   [SET] namespace: test_session")
    print("   [SET] ntp_server: pool.ntp.org")
    print("   [SET] pool: 16")
    print("   [SET] proxy: https://localhost:8081")
    print("   [SET] reconnect_timeout: 10m0s")
    print("   [SET] storage_type: file")
    print("   [SET] storage_path: /custom/path")
    print("   [SET] threads: 8")

    # Test Download Parameters (from req.md lines 38-54)
    print("\n2. Testing DOWNLOAD PARAMETERS:")
    print("-" * 30)

    download = DownloadConfig(
        urls=[
            "https://t.me/test/1",
            "https://t.me/test/2",
            "https://t.me/test/3"
        ],  # -u, --url strings (multiple)
        continue_last=True,  # --continue
        desc=True,  # --desc
        directory="my_downloads",  # -d, --dir string
        exclude_extensions=["png", "gif", "bmp"],  # -e, --exclude strings
        official_files=["file1.txt", "file2.json"],  # -f, --file strings
        group=True,  # --group
        include_extensions=["mp4", "avi", "mkv"],  # -i, --include strings
        port=9090,  # --port int
        restart=False,  # --restart
        rewrite_ext=True,  # --rewrite-ext
        serve=False,  # --serve
        skip_same=True,  # --skip-same
        takeout=True,  # --takeout
        template="custom_{{ .MessageID }}_{{ .FileName }}"  # --template string
    )

    print("   [SET] urls: 3 URLs")
    print("   [SET] continue_last: True")
    print("   [SET] desc: True")
    print("   [SET] directory: my_downloads")
    print("   [SET] exclude_extensions: png, gif, bmp")
    print("   [SET] official_files: 2 files")
    print("   [SET] group: True")
    print("   [SET] include_extensions: mp4, avi, mkv")
    print("   [SET] port: 9090")
    print("   [SET] restart: False")
    print("   [SET] rewrite_ext: True")
    print("   [SET] serve: False")
    print("   [SET] skip_same: True")
    print("   [SET] takeout: True")
    print("   [SET] template: custom")

    # Create full configuration
    config = FullConfig(session=session, download=download)

    # Validate
    print("\n3. VALIDATION RESULTS:")
    print("-" * 30)
    errors = config.validate()
    if errors:
        print("   [FAIL] Validation errors found:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("   [PASS] All validations passed")

    # Generate command
    print("\n4. GENERATED COMMAND:")
    print("-" * 30)
    args = config.get_command_args()
    command = ' '.join(args)

    print(f"   Command length: {len(command)} characters")
    print(f"   Total arguments: {len(args)}")

    # Check for all required parameters
    expected_params = {
        '--debug': 'debug flag',
        '--delay': 'delay parameter',
        '-l': 'limit parameter',
        '-n': 'namespace parameter',
        '--ntp': 'ntp parameter',
        '--pool': 'pool parameter',
        '--proxy': 'proxy parameter',
        '--reconnect-timeout': 'reconnect timeout',
        '--storage': 'storage configuration',
        '-t': 'threads parameter',
        '-u': 'url parameter',
        '--continue': 'continue flag',
        '--desc': 'desc flag',
        '-d': 'directory parameter',
        '-e': 'exclude parameter',
        '-f': 'file parameter',
        '--group': 'group flag',
        '-i': 'include parameter',
        '--port': 'port parameter',
        '--rewrite-ext': 'rewrite extension flag',
        '--skip-same': 'skip same flag',
        '--takeout': 'takeout flag',
        '--template': 'template parameter'
    }

    print("\n5. PARAMETER COVERAGE CHECK:")
    print("-" * 30)
    all_found = True
    for param, description in expected_params.items():
        found = param in command
        status = "[PASS]" if found else "[FAIL]"
        print(f"   {status} {param:20} - {description}")
        if not found:
            all_found = False

    # Summary
    print("\n" + "=" * 60)
    if all_found:
        print("[SUCCESS] All parameters from req.md are properly handled!")
    else:
        print("[WARNING] Some parameters may be missing")

    print("\nGenerated command:")
    print(command)

    return all_found and not errors


if __name__ == "__main__":
    success = test_all_parameters()
    sys.exit(0 if success else 1)