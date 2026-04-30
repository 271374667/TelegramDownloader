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
    limit: int = 8  # max number of concurrent tasks
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
    threads: int = 16  # max threads for transfer one item

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
    subfolder: str = ""  # subfolder under download directory (e.g., "相册")
    subfolder_enabled: bool = False  # whether to use subfolder

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
    skip_same: bool = True  # skip files with same name and size (default enabled)
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

            # Determine final download directory (with optional subfolder)
            final_directory = self.download.directory
            if self.download.subfolder_enabled and self.download.subfolder.strip():
                final_directory = os.path.join(self.download.directory, self.download.subfolder.strip())
            args.extend(["-d", final_directory])

            if self.download.skip_same:
                args.append("--skip-same")

            if self.download.takeout:
                args.append("--takeout")

            if self.download.group:
                args.append("--group")

            if self.download.restart:
                args.append("--restart")

            if self.download.rewrite_ext:
                args.append("--rewrite-ext")

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

        # Advanced settings
        if self.download.advanced_settings_enabled:
            if self.download.template != "{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}":
                args.extend(["--template", self.download.template])

        # Server settings
        if self.download.server_settings_enabled:
            if self.download.serve:
                args.append("--serve")

            if self.download.port != 8080:
                args.extend(["--port", str(self.download.port)])

        return args


# ---------------------------------------------------------------------------
# Export Configuration
# ---------------------------------------------------------------------------

@dataclass
class ExportConfig:
    """Configuration for tdl chat export parameters"""

    # Target chat (empty string = Saved Messages / Favourites)
    chat: str = ""

    # Output file path
    output: str = "tdl-export.json"

    # Source selection (topic / reply are mutually exclusive)
    topic_enabled: bool = False
    topic_id: int = 0

    reply_enabled: bool = False
    reply_post_id: int = 0

    # Range
    range_enabled: bool = False
    range_type: str = "time"   # "time" | "id" | "last"
    range_start: str = ""      # for time: Unix ts; for id: msg id; for last: N
    range_end: str = ""        # unused when range_type == "last"

    # Filter expression (expr-lang)
    filter_enabled: bool = False
    filter_expr: str = ""

    # Output options
    with_content: bool = False
    raw: bool = False
    all_messages: bool = False

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.topic_enabled and self.reply_enabled:
            errors.append("不能同时启用主题过滤和回复过滤")
        if self.topic_enabled and self.topic_id <= 0:
            errors.append("主题 ID 必须大于 0")
        if self.reply_enabled and self.reply_post_id <= 0:
            errors.append("回复帖子 ID 必须大于 0")
        if self.range_enabled and self.range_type == "last":
            try:
                n = int(self.range_start)
                if n < 1:
                    errors.append("最新消息数量必须大于 0")
            except (ValueError, TypeError):
                if self.range_start.strip():
                    errors.append("最新消息数量必须是整数")
        if self.raw and self.all_messages:
            errors.append("--raw 与 --all 不能同时使用")
        return errors

    def get_command_args(self, session: "SessionConfig") -> List[str]:
        """Build the full tdl chat export command argument list."""
        args: List[str] = ["bin\\tdl"]

        # ── Session-level flags ──────────────────────────────────────
        if session.basic_settings_enabled:
            if session.debug:
                args.append("--debug")
            if session.delay != "0s":
                args.extend(["--delay", session.delay])
            args.extend(["-l", str(session.limit)])
            args.extend(["-n", session.namespace])

        if session.network_settings_enabled:
            if session.ntp_server.strip():
                args.extend(["--ntp", session.ntp_server])
            args.extend(["--pool", str(session.pool)])
            if session.proxy.strip():
                args.extend(["--proxy", session.proxy])
            args.extend(["--reconnect-timeout", session.reconnect_timeout])

        if session.storage_settings_enabled:
            storage_cfg = f"type={session.storage_type},path={session.storage_path}"
            args.extend(["--storage", storage_cfg])

        if session.performance_settings_enabled:
            args.extend(["-t", str(session.threads)])

        # ── Sub-command ──────────────────────────────────────────────
        args.extend(["chat", "export"])

        if self.chat.strip():
            args.extend(["-c", self.chat.strip()])

        if self.output.strip() and self.output.strip() != "tdl-export.json":
            args.extend(["-o", self.output.strip()])

        # Source selection
        if self.topic_enabled and self.topic_id > 0:
            args.extend(["--topic", str(self.topic_id)])
        elif self.reply_enabled and self.reply_post_id > 0:
            args.extend(["--reply", str(self.reply_post_id)])

        # Range
        if self.range_enabled:
            args.extend(["-T", self.range_type])
            if self.range_type == "last":
                if self.range_start.strip():
                    args.extend(["-i", self.range_start.strip()])
            else:
                parts = [p for p in (self.range_start.strip(), self.range_end.strip()) if p]
                if parts:
                    args.extend(["-i", ",".join(parts)])

        # Filter
        if self.filter_enabled and self.filter_expr.strip():
            args.extend(["-f", self.filter_expr.strip()])

        # Options
        if self.with_content:
            args.append("--with-content")
        if self.raw:
            args.append("--raw")
        if self.all_messages:
            args.append("--all")

        return args