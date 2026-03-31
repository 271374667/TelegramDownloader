"""Session configuration ViewModel for QML binding."""

from PySide6.QtCore import QObject, Signal, Slot, Property
from core.config_manager import SessionConfig


class SessionViewModel(QObject):
    """Exposes SessionConfig fields as QML-bindable properties."""

    # ── Change signals ──────────────────────────────────────────────
    debugChanged = Signal()
    delayChanged = Signal()
    limitChanged = Signal()
    namespaceChanged = Signal()
    ntpServerChanged = Signal()
    poolChanged = Signal()
    proxyChanged = Signal()
    reconnectTimeoutChanged = Signal()
    storageTypeChanged = Signal()
    storagePathChanged = Signal()
    threadsChanged = Signal()
    basicEnabledChanged = Signal()
    networkEnabledChanged = Signal()
    storageEnabledChanged = Signal()
    performanceEnabledChanged = Signal()

    # Generic "something changed" signal for preview debounce
    configChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._debug = False
        self._delay = "0s"
        self._limit = 8
        self._namespace = "default"
        self._ntpServer = ""
        self._pool = 8
        self._proxy = "socks5://127.0.0.1:7897"
        self._reconnectTimeout = "5m0s"
        self._storageType = "bolt"
        self._storagePath = "~/.tdl/data"
        self._threads = 16
        self._basicEnabled = True
        self._networkEnabled = True
        self._storageEnabled = False
        self._performanceEnabled = True

    # ── Helpers ──────────────────────────────────────────────────────

    def _set(self, attr, value, signal):
        if getattr(self, attr) != value:
            setattr(self, attr, value)
            signal.emit()
            self.configChanged.emit()

    def get_config(self) -> SessionConfig:
        return SessionConfig(
            debug=self._debug,
            delay=self._delay,
            limit=self._limit,
            namespace=self._namespace,
            ntp_server=self._ntpServer,
            pool=self._pool,
            proxy=self._proxy,
            reconnect_timeout=self._reconnectTimeout,
            storage_type=self._storageType,
            storage_path=self._storagePath,
            threads=self._threads,
            basic_settings_enabled=self._basicEnabled,
            network_settings_enabled=self._networkEnabled,
            storage_settings_enabled=self._storageEnabled,
            performance_settings_enabled=self._performanceEnabled,
        )

    @Slot()
    def loadDefaults(self):
        cfg = SessionConfig()
        self.load_config(cfg)

    def load_config(self, c: SessionConfig):
        self._set("_debug", c.debug, self.debugChanged)
        self._set("_delay", c.delay, self.delayChanged)
        self._set("_limit", c.limit, self.limitChanged)
        self._set("_namespace", c.namespace, self.namespaceChanged)
        self._set("_ntpServer", c.ntp_server, self.ntpServerChanged)
        self._set("_pool", c.pool, self.poolChanged)
        self._set("_proxy", c.proxy, self.proxyChanged)
        self._set("_reconnectTimeout", c.reconnect_timeout, self.reconnectTimeoutChanged)
        self._set("_storageType", c.storage_type, self.storageTypeChanged)
        self._set("_storagePath", c.storage_path, self.storagePathChanged)
        self._set("_threads", c.threads, self.threadsChanged)
        self._set("_basicEnabled", c.basic_settings_enabled, self.basicEnabledChanged)
        self._set("_networkEnabled", c.network_settings_enabled, self.networkEnabledChanged)
        self._set("_storageEnabled", c.storage_settings_enabled, self.storageEnabledChanged)
        self._set("_performanceEnabled", c.performance_settings_enabled, self.performanceEnabledChanged)

    # ── Properties (type, getter, setter, notify) ───────────────────

    # --- debug ---
    def _get_debug(self): return self._debug
    def _set_debug(self, v): self._set("_debug", v, self.debugChanged)
    debug = Property(bool, _get_debug, _set_debug, notify=debugChanged)

    # --- delay ---
    def _get_delay(self): return self._delay
    def _set_delay(self, v): self._set("_delay", v, self.delayChanged)
    delay = Property(str, _get_delay, _set_delay, notify=delayChanged)

    # --- limit ---
    def _get_limit(self): return self._limit
    def _set_limit(self, v): self._set("_limit", int(v), self.limitChanged)
    limit = Property(int, _get_limit, _set_limit, notify=limitChanged)

    # --- namespace ---
    def _get_namespace(self): return self._namespace
    def _set_namespace(self, v): self._set("_namespace", v, self.namespaceChanged)
    namespace = Property(str, _get_namespace, _set_namespace, notify=namespaceChanged)

    # --- ntpServer ---
    def _get_ntpServer(self): return self._ntpServer
    def _set_ntpServer(self, v): self._set("_ntpServer", v, self.ntpServerChanged)
    ntpServer = Property(str, _get_ntpServer, _set_ntpServer, notify=ntpServerChanged)

    # --- pool ---
    def _get_pool(self): return self._pool
    def _set_pool(self, v): self._set("_pool", int(v), self.poolChanged)
    pool = Property(int, _get_pool, _set_pool, notify=poolChanged)

    # --- proxy ---
    def _get_proxy(self): return self._proxy
    def _set_proxy(self, v): self._set("_proxy", v, self.proxyChanged)
    proxy = Property(str, _get_proxy, _set_proxy, notify=proxyChanged)

    # --- reconnectTimeout ---
    def _get_reconnectTimeout(self): return self._reconnectTimeout
    def _set_reconnectTimeout(self, v): self._set("_reconnectTimeout", v, self.reconnectTimeoutChanged)
    reconnectTimeout = Property(str, _get_reconnectTimeout, _set_reconnectTimeout, notify=reconnectTimeoutChanged)

    # --- storageType ---
    def _get_storageType(self): return self._storageType
    def _set_storageType(self, v): self._set("_storageType", v, self.storageTypeChanged)
    storageType = Property(str, _get_storageType, _set_storageType, notify=storageTypeChanged)

    # --- storagePath ---
    def _get_storagePath(self): return self._storagePath
    def _set_storagePath(self, v): self._set("_storagePath", v, self.storagePathChanged)
    storagePath = Property(str, _get_storagePath, _set_storagePath, notify=storagePathChanged)

    # --- threads ---
    def _get_threads(self): return self._threads
    def _set_threads(self, v): self._set("_threads", int(v), self.threadsChanged)
    threads = Property(int, _get_threads, _set_threads, notify=threadsChanged)

    # --- basicEnabled ---
    def _get_basicEnabled(self): return self._basicEnabled
    def _set_basicEnabled(self, v): self._set("_basicEnabled", v, self.basicEnabledChanged)
    basicEnabled = Property(bool, _get_basicEnabled, _set_basicEnabled, notify=basicEnabledChanged)

    # --- networkEnabled ---
    def _get_networkEnabled(self): return self._networkEnabled
    def _set_networkEnabled(self, v): self._set("_networkEnabled", v, self.networkEnabledChanged)
    networkEnabled = Property(bool, _get_networkEnabled, _set_networkEnabled, notify=networkEnabledChanged)

    # --- storageEnabled ---
    def _get_storageEnabled(self): return self._storageEnabled
    def _set_storageEnabled(self, v): self._set("_storageEnabled", v, self.storageEnabledChanged)
    storageEnabled = Property(bool, _get_storageEnabled, _set_storageEnabled, notify=storageEnabledChanged)

    # --- performanceEnabled ---
    def _get_performanceEnabled(self): return self._performanceEnabled
    def _set_performanceEnabled(self, v): self._set("_performanceEnabled", v, self.performanceEnabledChanged)
    performanceEnabled = Property(bool, _get_performanceEnabled, _set_performanceEnabled, notify=performanceEnabledChanged)

    # ── Proxy presets slot ──────────────────────────────────────────

    @Slot(int)
    def applyProxyPreset(self, index: int):
        """Apply a proxy preset by index.
        0 = Custom, 1 = SOCKS5:7897, 2 = SOCKS5:1080,
        3 = HTTP:8080, 4 = HTTPS:8080"""
        presets = {
            1: "socks5://127.0.0.1:7897",
            2: "socks5://127.0.0.1:1080",
            3: "http://127.0.0.1:8080",
            4: "https://127.0.0.1:8080",
        }
        if index in presets:
            self._set_proxy(presets[index])
