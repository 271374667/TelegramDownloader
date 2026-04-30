"""Download configuration ViewModel for QML binding."""

import os
from PySide6.QtCore import QObject, Signal, Slot, Property
from core.config_manager import DownloadConfig


class DownloadViewModel(QObject):
    """Exposes DownloadConfig fields as QML-bindable properties."""

    # ── Change signals ──────────────────────────────────────────────
    directoryChanged = Signal()
    subfolderChanged = Signal()
    subfolderEnabledChanged = Signal()
    continueLastChanged = Signal()
    restartChanged = Signal()
    descChanged = Signal()
    groupChanged = Signal()
    skipSameChanged = Signal()
    rewriteExtChanged = Signal()
    takeoutChanged = Signal()
    templateChanged = Signal()
    serveChanged = Signal()
    portChanged = Signal()
    includeExtsChanged = Signal()
    excludeExtsChanged = Signal()
    officialFilesChanged = Signal()
    basicEnabledChanged = Signal()
    filteringEnabledChanged = Signal()
    advancedEnabledChanged = Signal()
    serverEnabledChanged = Signal()
    preDownloadCheckChanged = Signal()

    configChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._directory = os.path.join(os.getcwd(), "downloads")
        self._subfolder = ""
        self._subfolderEnabled = False
        self._continueLast = False
        self._restart = False
        self._desc = False
        self._group = False
        self._skipSame = True
        self._rewriteExt = False
        self._takeout = False
        self._template = "{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}"
        self._serve = False
        self._port = 8080
        self._includeExts = ""
        self._excludeExts = ""
        self._officialFiles = ""
        self._basicEnabled = True
        self._filteringEnabled = False
        self._advancedEnabled = False
        self._serverEnabled = False
        self._preDownloadCheck = True

    def _set(self, attr, value, signal):
        if getattr(self, attr) != value:
            setattr(self, attr, value)
            signal.emit()
            self.configChanged.emit()

    def get_config(self) -> DownloadConfig:
        include = [e.strip() for e in self._includeExts.split(",") if e.strip()] if self._includeExts else []
        exclude = [e.strip() for e in self._excludeExts.split(",") if e.strip()] if self._excludeExts else []
        official = [f.strip() for f in self._officialFiles.split(",") if f.strip()] if self._officialFiles else []

        return DownloadConfig(
            urls=[],  # filled by AppViewModel
            continue_last=self._continueLast,
            desc=self._desc,
            directory=self._directory,
            subfolder=self._subfolder,
            subfolder_enabled=self._subfolderEnabled,
            exclude_extensions=exclude,
            include_extensions=include,
            official_files=official,
            group=self._group,
            port=self._port,
            restart=self._restart,
            rewrite_ext=self._rewriteExt,
            serve=self._serve,
            skip_same=self._skipSame,
            takeout=self._takeout,
            template=self._template,
            basic_settings_enabled=self._basicEnabled,
            file_filtering_enabled=self._filteringEnabled,
            advanced_settings_enabled=self._advancedEnabled,
            server_settings_enabled=self._serverEnabled,
        )

    @Slot(str)
    def setDirectory(self, path: str):
        self._set_directory(path)

    @Slot(str)
    def setSubfolder(self, path: str):
        self._set_subfolder(path)

    # ── Properties ──────────────────────────────────────────────────

    def _get_directory(self): return self._directory
    def _set_directory(self, v): self._set("_directory", v, self.directoryChanged)
    directory = Property(str, _get_directory, _set_directory, notify=directoryChanged)

    def _get_subfolder(self): return self._subfolder
    def _set_subfolder(self, v): self._set("_subfolder", v, self.subfolderChanged)
    subfolder = Property(str, _get_subfolder, _set_subfolder, notify=subfolderChanged)

    def _get_subfolderEnabled(self): return self._subfolderEnabled
    def _set_subfolderEnabled(self, v): self._set("_subfolderEnabled", v, self.subfolderEnabledChanged)
    subfolderEnabled = Property(bool, _get_subfolderEnabled, _set_subfolderEnabled, notify=subfolderEnabledChanged)

    def _get_continueLast(self): return self._continueLast
    def _set_continueLast(self, v): self._set("_continueLast", v, self.continueLastChanged)
    continueLast = Property(bool, _get_continueLast, _set_continueLast, notify=continueLastChanged)

    def _get_restart(self): return self._restart
    def _set_restart(self, v): self._set("_restart", v, self.restartChanged)
    restart = Property(bool, _get_restart, _set_restart, notify=restartChanged)

    def _get_desc(self): return self._desc
    def _set_desc(self, v): self._set("_desc", v, self.descChanged)
    desc = Property(bool, _get_desc, _set_desc, notify=descChanged)

    def _get_group(self): return self._group
    def _set_group(self, v): self._set("_group", v, self.groupChanged)
    group = Property(bool, _get_group, _set_group, notify=groupChanged)

    def _get_skipSame(self): return self._skipSame
    def _set_skipSame(self, v): self._set("_skipSame", v, self.skipSameChanged)
    skipSame = Property(bool, _get_skipSame, _set_skipSame, notify=skipSameChanged)

    def _get_rewriteExt(self): return self._rewriteExt
    def _set_rewriteExt(self, v): self._set("_rewriteExt", v, self.rewriteExtChanged)
    rewriteExt = Property(bool, _get_rewriteExt, _set_rewriteExt, notify=rewriteExtChanged)

    def _get_takeout(self): return self._takeout
    def _set_takeout(self, v): self._set("_takeout", v, self.takeoutChanged)
    takeout = Property(bool, _get_takeout, _set_takeout, notify=takeoutChanged)

    def _get_template(self): return self._template
    def _set_template(self, v): self._set("_template", v, self.templateChanged)
    template = Property(str, _get_template, _set_template, notify=templateChanged)

    def _get_serve(self): return self._serve
    def _set_serve(self, v): self._set("_serve", v, self.serveChanged)
    serve = Property(bool, _get_serve, _set_serve, notify=serveChanged)

    def _get_port(self): return self._port
    def _set_port(self, v): self._set("_port", int(v), self.portChanged)
    port = Property(int, _get_port, _set_port, notify=portChanged)

    def _get_includeExts(self): return self._includeExts
    def _set_includeExts(self, v): self._set("_includeExts", v, self.includeExtsChanged)
    includeExts = Property(str, _get_includeExts, _set_includeExts, notify=includeExtsChanged)

    def _get_excludeExts(self): return self._excludeExts
    def _set_excludeExts(self, v): self._set("_excludeExts", v, self.excludeExtsChanged)
    excludeExts = Property(str, _get_excludeExts, _set_excludeExts, notify=excludeExtsChanged)

    def _get_officialFiles(self): return self._officialFiles
    def _set_officialFiles(self, v): self._set("_officialFiles", v, self.officialFilesChanged)
    officialFiles = Property(str, _get_officialFiles, _set_officialFiles, notify=officialFilesChanged)

    def _get_basicEnabled(self): return self._basicEnabled
    def _set_basicEnabled(self, v): self._set("_basicEnabled", v, self.basicEnabledChanged)
    basicEnabled = Property(bool, _get_basicEnabled, _set_basicEnabled, notify=basicEnabledChanged)

    def _get_filteringEnabled(self): return self._filteringEnabled
    def _set_filteringEnabled(self, v): self._set("_filteringEnabled", v, self.filteringEnabledChanged)
    filteringEnabled = Property(bool, _get_filteringEnabled, _set_filteringEnabled, notify=filteringEnabledChanged)

    def _get_advancedEnabled(self): return self._advancedEnabled
    def _set_advancedEnabled(self, v): self._set("_advancedEnabled", v, self.advancedEnabledChanged)
    advancedEnabled = Property(bool, _get_advancedEnabled, _set_advancedEnabled, notify=advancedEnabledChanged)

    def _get_serverEnabled(self): return self._serverEnabled
    def _set_serverEnabled(self, v): self._set("_serverEnabled", v, self.serverEnabledChanged)
    serverEnabled = Property(bool, _get_serverEnabled, _set_serverEnabled, notify=serverEnabledChanged)

    def _get_preDownloadCheck(self): return self._preDownloadCheck
    def _set_preDownloadCheck(self, v): self._set("_preDownloadCheck", v, self.preDownloadCheckChanged)
    preDownloadCheck = Property(bool, _get_preDownloadCheck, _set_preDownloadCheck, notify=preDownloadCheckChanged)
