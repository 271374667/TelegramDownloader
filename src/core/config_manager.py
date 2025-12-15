"""
Configuration data models for the Telegram Downloader GUI
Contains dataclasses for session and download configurations
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import os


@dataclass
class SessionConfig:
    """Configuration for tdl session parameters"""

    # Basic settings
    debug: bool = False
    delay: str = "0s"  # duration between each task, zero means no delay
    limit: int = 2  # max number of concurrent tasks
    namespace: str = "default"  # namespace for Telegram session

    # Network settings
    ntp_server: str = ""  # ntp server host, empty means use system time
    pool: int = 8  # specify the size of the DC pool
    proxy: str = "socks5://127.0.0.1:7897"  # proxy address
    reconnect_timeout: str = "5m0s"  # Telegram client reconnection timeout

    # Storage settings
    storage_type: str = "bolt"  # storage type: legacy, bolt, file
    storage_path: str = "~/.tdl/data"  # storage path

    # Performance settings
    threads: int = 4  # max threads for transfer one item

    # GroupBox enabled states
    basic_settings_enabled: bool = True
    network_settings_enabled: bool = True
    storage_settings_enabled: bool = False  # Default unchecked
    performance_settings_enabled: bool = True

    def validate(self) -> List[str]:
        """Validate session configuration and return list of errors"""
        errors = []

        if self.limit < 1:
            errors.append("Limit must be at least 1")

        if self.threads < 1:
            errors.append("Threads must be at least 1")

        if self.pool < 0:
            errors.append("Pool size cannot be negative")

        if not self.namespace.strip():
            errors.append("Namespace cannot be empty")

        # Validate proxy format if provided
        if self.proxy.strip():
            proxy_format = self.proxy.strip()
            valid_protocols = ["http://", "https://", "socks4://", "socks5://"]
            if not any(proxy_format.startswith(protocol) for protocol in valid_protocols):
                errors.append("Proxy must use format: protocol://[username:password@]host:port")

        # Validate delay format
        if self.delay.strip() and not self.delay.endswith(('s', 'm', 'h')):
            errors.append("Delay must end with 's' (seconds), 'm' (minutes), or 'h' (hours)")

        # Validate reconnect timeout format
        if not self.reconnect_timeout.endswith(('s', 'm', 'h')):
            errors.append("Reconnect timeout must end with 's', 'm', or 'h'")

        return errors


@dataclass
class DownloadConfig:
    """Configuration for tdl download parameters"""

    # URLs to download
    urls: List[str] = field(default_factory=list)

    # Basic settings
    continue_last: bool = False  # continue the last download directly
    desc: bool = False  # download files from newest to oldest
    directory: str = field(default_factory=lambda: os.path.join(os.getcwd(), "downloads"))  # download directory

    # File filtering
    exclude_extensions: List[str] = field(default_factory=list)  # exclude file extensions
    include_extensions: List[str] = field(default_factory=list)  # include file extensions

    # Special features
    official_files: List[str] = field(default_factory=list)  # official client exported files
    group: bool = False  # auto detect grouped message and download all of them

    # Server settings
    port: int = 8080  # http server port

    # Download behavior
    restart: bool = False  # restart the last download directly
    rewrite_ext: bool = False  # rewrite file extension according to file header MIME
    serve: bool = False  # serve as http server instead of downloading
    skip_same: bool = False  # skip files with same name and size
    takeout: bool = False  # use takeout sessions for lower flood wait limits

    # Template
    template: str = "{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}"  # download file name template

    # GroupBox enabled states
    basic_settings_enabled: bool = True
    file_filtering_enabled: bool = False  # Default unchecked
    advanced_settings_enabled: bool = False  # Default unchecked
    server_settings_enabled: bool = False  # Default unchecked

    def validate(self) -> List[str]:
        """Validate download configuration and return list of errors"""
        errors = []

        if not self.urls:
            errors.append("At least one URL must be provided")

        # Validate URLs
        for i, url in enumerate(self.urls):
            if not url.strip():
                errors.append(f"URL {i+1} is empty")
            elif not url.startswith("https://t.me/"):
                errors.append(f"URL {i+1} must be a valid Telegram URL (https://t.me/...)")

        # Validate directory
        if not self.directory.strip():
            errors.append("Download directory cannot be empty")

        # Validate extensions
        for ext in self.exclude_extensions + self.include_extensions:
            if ext.strip() and ext.startswith('.'):
                errors.append(f"Extension '{ext}' should not include the dot (use '{ext.lstrip('.')}' instead)")

        # Validate port
        if self.port < 1 or self.port > 65535:
            errors.append("Port must be between 1 and 65535")

        # Validate mutually exclusive options
        if self.continue_last and self.restart:
            errors.append("Cannot use both 'continue' and 'restart' options simultaneously")

        if self.serve and (self.continue_last or self.restart):
            errors.append("Server mode cannot be used with continue/restart options")

        if self.include_extensions and self.exclude_extensions:
            errors.append("Cannot use both include and exclude extensions simultaneously")

        return errors


@dataclass
class FullConfig:
    """Complete configuration combining session and download settings"""

    session: SessionConfig = field(default_factory=SessionConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)

    def validate(self) -> List[str]:
        """Validate the complete configuration"""
        errors = []
        errors.extend(self.session.validate())
        errors.extend(self.download.validate())
        return errors

    def get_command_args(self) -> List[str]:
        """Generate command line arguments for tdl"""
        args = ["bin\\tdl", "dl"]

        # Session arguments - only add if group is enabled
        if self.session.basic_settings_enabled:
            if self.session.debug:
                args.append("--debug")

            if self.session.delay != "0s":
                args.extend(["--delay", self.session.delay])

            args.extend(["-l", str(self.session.limit)])
            args.extend(["-n", self.session.namespace])

        if self.session.network_settings_enabled:
            if self.session.ntp_server.strip():
                args.extend(["--ntp", self.session.ntp_server])

            args.extend(["--pool", str(self.session.pool)])

            if self.session.proxy.strip():
                args.extend(["--proxy", self.session.proxy])

            args.extend(["--reconnect-timeout", self.session.reconnect_timeout])

        if self.session.storage_settings_enabled:
            # Storage configuration
            storage_config = f"type={self.session.storage_type},path={self.session.storage_path}"
            args.extend(["--storage", storage_config])

        if self.session.performance_settings_enabled:
            args.extend(["-t", str(self.session.threads)])

        # Download arguments - always add URLs (mandatory)
        for url in self.download.urls:
            if url.strip():
                args.extend(["-u", url.strip()])

        # Basic settings
        if self.download.basic_settings_enabled:
            if self.download.continue_last:
                args.append("--continue")

            if self.download.desc:
                args.append("--desc")

            args.extend(["-d", self.download.directory])

            if self.download.takeout:
                args.append("--takeout")

        # File filtering
        if self.download.file_filtering_enabled:
            for ext in self.download.exclude_extensions:
                if ext.strip():
                    args.extend(["-e", ext.strip()])

            for ext in self.download.include_extensions:
                if ext.strip():
                    args.extend(["-i", ext.strip()])

            for file_path in self.download.official_files:
                if file_path.strip():
                    args.extend(["-f", file_path.strip()])

            if self.download.group:
                args.append("--group")

            if self.download.skip_same:
                args.append("--skip-same")

        # Advanced settings
        if self.download.advanced_settings_enabled:
            if self.download.restart:
                args.append("--restart")

            if self.download.rewrite_ext:
                args.append("--rewrite-ext")

            if self.download.template != "{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}":
                args.extend(["--template", self.download.template])

        # Server settings
        if self.download.server_settings_enabled:
            if self.download.serve:
                args.append("--serve")

            if self.download.port != 8080:
                args.extend(["--port", str(self.download.port)])

        return args