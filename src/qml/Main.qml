import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Qt.labs.platform as Platform
import "theme" as Theme
import "controls"
import "components"
import "pages"

ApplicationWindow {
    id: window
    visible: true
    width: 900
    height: 680
    minimumWidth: 680
    minimumHeight: 520
    title: "TDL - Telegram Downloader"
    color: Theme.Theme.background
    flags: Qt.FramelessWindowHint | Qt.Window

    // ── Load bundled fonts into QML engine ─────────────────────────
    FontLoader { source: "Fonts/SourceHanSansSC-Regular.otf" }
    FontLoader { source: "Fonts/SourceHanSansSC-Medium.otf" }
    FontLoader { source: "Fonts/SourceHanSansSC-Bold.otf" }

    font.family: Theme.Theme.fontFamily

    // ── System Tray ────────────────────────────────────────────────
    Platform.SystemTrayIcon {
        id: trayIcon
        visible: true
        tooltip: "TDL - Telegram Downloader"

        menu: Platform.Menu {
            Platform.MenuItem {
                text: "显示主界面"
                onTriggered: { window.show(); window.raise(); window.requestActivate(); }
            }
            Platform.MenuItem {
                text: "浮动面板"
                checkable: true
                checked: appVM.floatingPanelVisible
                onTriggered: appVM.floatingPanelVisible = checked
            }
            Platform.MenuItem {
                text: "剪贴板监控"
                checkable: true
                checked: appVM.clipboardMonitoring
                onTriggered: appVM.clipboardMonitoring = checked
            }
            Platform.MenuSeparator {}
            Platform.MenuItem {
                text: urlModel.statusText
                enabled: false
            }
            Platform.MenuSeparator {}
            Platform.MenuItem {
                text: "退出"
                onTriggered: Qt.quit()
            }
        }

        onActivated: (reason) => {
            if (reason === Platform.SystemTrayIcon.Trigger ||
                reason === Platform.SystemTrayIcon.DoubleClick) {
                window.show(); window.raise(); window.requestActivate();
            }
        }
    }

    // ── Keyboard shortcuts ─────────────────────────────────────────
    Shortcut {
        sequence: "Ctrl+Shift+F"
        onActivated: appVM.toggleFloatingPanel()
    }

    // ── Custom Title Bar ───────────────────────────────────────
    FluentTitleBar {
        id: titleBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: barHeight
        appName: "TDL - Telegram Downloader"
    }

    // ── Main Layout ────────────────────────────────────────────
    RowLayout {
        anchors.top: titleBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        spacing: 0

        // ── Navigation Sidebar ─────────────────────────────────────
        Rectangle {
            Layout.preferredWidth: 180
            Layout.fillHeight: true
            color: Theme.Theme.surface

            Column {
                anchors.fill: parent
                spacing: 0

                // App header
                Item {
                    width: parent.width
                    height: 56

                    Row {
                        anchors.centerIn: parent
                        spacing: 8
                        Text {
                            text: "TDL"
                            font.pixelSize: Theme.Theme.fontSizeTitle
                            font.weight: Font.Bold
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.accent
                        }
                        Text {
                            text: "下载器"
                            font.pixelSize: Theme.Theme.fontSizeSubtitle
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textSecondary
                            anchors.baseline: parent.children[0].baseline
                        }
                    }
                }

                Rectangle { width: parent.width; height: 1; color: Theme.Theme.divider }

                // Navigation items
                Repeater {
                    model: ListModel {
                        ListElement { label: "📥  下载"; pageIndex: 0 }
                        ListElement { label: "📤  消息导出"; pageIndex: 1 }
                        ListElement { label: "📦  队列下载"; pageIndex: 2 }
                        ListElement { label: "⚙  会话设置"; pageIndex: 3 }
                        ListElement { label: "📜  历史任务"; pageIndex: 4 }
                    }
                    delegate: Rectangle {
                        width: parent.width
                        height: 44
                        color: navArea.containsMouse
                            ? Theme.Theme.surfaceHover
                            : pageStack.currentIndex === model.pageIndex
                            ? "#0FFFFFFF"
                            : "transparent"
                        // No color animation — instant state change

                        // Left accent indicator
                        Rectangle {
                            width: 3; height: 20
                            radius: 2
                            anchors.left: parent.left; anchors.leftMargin: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: Theme.Theme.accent
                            visible: pageStack.currentIndex === model.pageIndex
                            opacity: visible ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: Theme.Theme.animNormal } }
                        }

                        Text {
                            text: model.label
                            anchors.left: parent.left; anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            font.pixelSize: Theme.Theme.fontSizeBody
                            font.family: Theme.Theme.fontFamily
                            color: pageStack.currentIndex === model.pageIndex
                                ? Theme.Theme.textPrimary
                                : Theme.Theme.textSecondary
                        }

                        // History failed-task badge
                        Rectangle {
                            visible: model.pageIndex === 4 && historyVM.failedCount > 0
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            width: Math.max(22, historyBadgeText.implicitWidth + 10)
                            height: 20
                            radius: 10
                            color: Theme.Theme.error

                            Text {
                                id: historyBadgeText
                                anchors.centerIn: parent
                                text: historyVM.failedCount
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: "#FFFFFF"
                            }
                        }

                        // URL count badge on download tab
                        Rectangle {
                            visible: model.pageIndex === 0 && urlModel.count > 0
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            width: Math.max(22, badgeText.implicitWidth + 10)
                            height: 20
                            radius: 10
                            color: Theme.Theme.accentDark

                            Text {
                                id: badgeText
                                anchors.centerIn: parent
                                text: urlModel.count
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: "#FFFFFF"
                            }
                        }

                        // Queue count badge
                        Rectangle {
                            visible: model.pageIndex === 2 && queueVM.queueCount > 0
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            width: Math.max(22, queueBadgeText.implicitWidth + 10)
                            height: 20
                            radius: 10
                            color: Theme.Theme.success

                            Text {
                                id: queueBadgeText
                                anchors.centerIn: parent
                                text: queueVM.queueCount
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: "#FFFFFF"
                            }
                        }

                        MouseArea {
                            id: navArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: pageStack.currentIndex = model.pageIndex
                        }
                    }
                }

                Item { Layout.fillHeight: true; height: 10 }
            }

            // Sidebar bottom info
            Column {
                anchors.bottom: parent.bottom
                anchors.bottomMargin: Theme.Theme.spacingM
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: Theme.Theme.spacingS
                anchors.rightMargin: Theme.Theme.spacingS
                spacing: 8

                // ── Divider ────────────────────────────────────────
                Rectangle {
                    width: parent.width - 16
                    height: 1
                    color: Theme.Theme.divider
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                // ── TDL Status ─────────────────────────────────────
                Text {
                    text: {
                        switch (appVM.tdlStatus) {
                            case "ready": return "● 已就绪";
                            case "not_logged_in": return "● 未登录";
                            default: return "● 未配置";
                        }
                    }
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: {
                        switch (appVM.tdlStatus) {
                            case "ready": return Theme.Theme.success;
                            case "not_logged_in": return Theme.Theme.warning;
                            default: return Theme.Theme.error;
                        }
                    }
                }

                FluentButton {
                    visible: appVM.tdlStatus === "not_logged_in"
                    text: "登录 Telegram"
                    variant: "subtle"
                    anchors.horizontalCenter: parent.horizontalCenter
                    onClicked: loginDialog.open()
                }
            }
        }

        // Sidebar separator
        Rectangle { Layout.preferredWidth: 1; Layout.fillHeight: true; color: Theme.Theme.divider }

        // ── Content Area ───────────────────────────────────────────
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Page title bar
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                color: "transparent"

                Text {
                    anchors.left: parent.left; anchors.leftMargin: Theme.Theme.spacingXL
                    anchors.verticalCenter: parent.verticalCenter
                    text: {
                        switch (pageStack.currentIndex) {
                            case 0: return "下载配置"
                            case 1: return "消息导出"
                            case 2: return "队列下载"
                            case 3: return "会话设置"
                            case 4: return "历史任务"
                            default: return ""
                        }
                    }
                    font.pixelSize: Theme.Theme.fontSizeTitle
                    font.family: Theme.Theme.fontFamily
                    font.weight: Font.DemiBold
                    color: Theme.Theme.textPrimary
                }

                // Floating panel toggle
                FluentButton {
                    anchors.right: parent.right; anchors.rightMargin: Theme.Theme.spacingXL
                    anchors.verticalCenter: parent.verticalCenter
                    text: appVM.floatingPanelVisible ? "隐藏浮窗" : "显示浮窗"
                    variant: "subtle"
                    onClicked: appVM.toggleFloatingPanel()
                }
            }

            Rectangle { Layout.fillWidth: true; height: 1; color: Theme.Theme.divider }

            // Page stack
            StackLayout {
                id: pageStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: 0

                DownloadPage {}
                ExportPage {}
                QueuePage {}
                SessionPage {}
                HistoryPage {}
            }
        }
    }

    // ── Floating Panel ─────────────────────────────────────────────
    FloatingPanel {
        id: floatingPanel
        urlCount: urlModel.count

        onClearRequested: urlModel.clear()
        onGenerateRequested: appVM.generateBatch()
        onExecuteRequested: appVM.executeBatch()
        onQueueRequested: floatingQueueDialog.open()
        onShowMainRequested: { window.show(); window.raise(); window.requestActivate(); }
        onCloseRequested: appVM.floatingPanelVisible = false
    }

    // ── Floating queue-name dialog ─────────────────────────────────
    Dialog {
        id: floatingQueueDialog
        parent: Overlay.overlay
        anchors.centerIn: parent
        modal: true
        width: 380
        height: floatingQueueDialogContent.implicitHeight + 72
        standardButtons: Dialog.NoButton

        background: Rectangle {
            color: Theme.Theme.surface
            radius: Theme.Theme.radiusMedium
            border.width: 1
            border.color: Theme.Theme.cardBorder
        }

        header: Item {
            height: 48
            Text {
                anchors.left: parent.left; anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: "导出到下载队列"
                font.pixelSize: Theme.Theme.fontSizeSubtitle
                font.family: Theme.Theme.fontFamily
                font.weight: Font.DemiBold
                color: Theme.Theme.textPrimary
            }
        }

        contentItem: Column {
            id: floatingQueueDialogContent
            spacing: Theme.Theme.spacingM
            topPadding: 16
            bottomPadding: 20
            leftPadding: 20
            rightPadding: 20

            Text {
                width: parent.width - 40
                text: "当前链接列表（" + urlModel.count + " 个）将保存为队列，不会立即下载。"
                font.pixelSize: Theme.Theme.fontSizeBody
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.textSecondary
                wrapMode: Text.Wrap
            }

            FluentTextField {
                id: fqInput
                width: parent.width - 40
                label: "队列名称"
                placeholderText: "例如：频道A第1批"
                Keys.onReturnPressed: fqOkBtn.clicked()
                Keys.onEnterPressed: fqOkBtn.clicked()
            }

            Text {
                id: fqError
                width: parent.width - 40
                text: ""
                font.pixelSize: Theme.Theme.fontSizeCaption
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.error
                wrapMode: Text.Wrap
                visible: text.length > 0
            }

            RowLayout {
                spacing: Theme.Theme.spacingS

                FluentButton {
                    id: fqOkBtn
                    text: "确定"
                    variant: "accent"
                    onClicked: {
                        var name = fqInput.text.trim()
                        if (!name) { fqError.text = "队列名称不能为空"; return }
                        if (queueVM.nameExists(name)) {
                            fqError.text = "队列「" + name + "」已存在，请换一个名称"; return
                        }
                        var err = appVM.exportToQueue(name)
                        if (err) { fqError.text = err } else { floatingQueueDialog.close() }
                    }
                }

                FluentButton {
                    text: "取消"
                    variant: "subtle"
                    onClicked: floatingQueueDialog.close()
                }
            }
        }

        onOpened: {
            fqInput.text = ""
            fqError.text = ""
            fqInput.forceActiveFocus()
        }
    }

    // ── InfoBar (notifications) ────────────────────────────────────
    FluentInfoBar {
        id: infoBar
        anchors.top: titleBar.bottom; anchors.topMargin: 8
        anchors.right: parent.right; anchors.rightMargin: 8
        anchors.left: parent.left; anchors.leftMargin: 190  // offset for sidebar
        z: 100
    }

    Connections {
        target: appVM
        function onNotificationRequested(title, message, severity) {
            infoBar.show(title, message, severity);
        }
        function onExportResultReady(files) {
            preDownloadDialog._fileList = files;
            preDownloadDialog._queryDone = true;
        }
        function onDownloadFinished(status, downloaded, expected, failedUrlsJson) {
            preDownloadDialog.close();
            downloadResultDialog.resultStatus  = status;
            downloadResultDialog.downloaded    = downloaded;
            downloadResultDialog.expected      = expected;
            downloadResultDialog.failedUrlsJson = failedUrlsJson;
            downloadResultDialog.open();
            historyVM.refresh();
        }
    }

    // ── Pre-download confirm dialog ────────────────────────────────
    Dialog {
        id: preDownloadDialog
        parent: Overlay.overlay
        anchors.centerIn: parent
        modal: true
        width: 500
        closePolicy: Dialog.NoAutoClose
        standardButtons: Dialog.NoButton

        property var  _fileList:  []
        property bool _queryDone: false

        background: Rectangle {
            color: Theme.Theme.surface
            radius: Theme.Theme.radiusMedium
            border.width: 1
            border.color: Theme.Theme.cardBorder
        }

        header: Item {
            height: 52
            Text {
                anchors.left: parent.left; anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: preDownloadDialog._queryDone ? "确认下载文件" : "正在查询文件信息..."
                font.pixelSize: Theme.Theme.fontSizeSubtitle
                font.weight: Font.DemiBold
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.textPrimary
            }
        }

        contentItem: Item {
            implicitHeight: _dlgCol.implicitHeight

            Column {
                id: _dlgCol
                anchors { left: parent.left; right: parent.right; top: parent.top }
                anchors.leftMargin: 20; anchors.rightMargin: 20
                spacing: Theme.Theme.spacingM
                topPadding: 8
                bottomPadding: 20

                // Spinner while querying
                Row {
                    visible: !preDownloadDialog._queryDone
                    spacing: Theme.Theme.spacingS

                    BusyIndicator {
                        running: !preDownloadDialog._queryDone
                        width: 28; height: 28
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "正在通过 tdl chat export 获取文件列表..."
                        font.pixelSize: Theme.Theme.fontSizeBody
                        font.family: Theme.Theme.fontFamily
                        color: Theme.Theme.textSecondary
                    }
                }

                // Summary when done
                Text {
                    visible: preDownloadDialog._queryDone
                    width: parent.width
                    text: preDownloadDialog._fileList.length > 0
                          ? "共检测到 " + preDownloadDialog._fileList.length + " 个待下载文件："
                          : "未能获取文件详情（链接可能不支持预查询），将直接开始下载。"
                    font.pixelSize: Theme.Theme.fontSizeBody
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textPrimary
                    wrapMode: Text.Wrap
                }

                // File list preview (scrollable, max height 220)
                Rectangle {
                    visible: preDownloadDialog._queryDone && preDownloadDialog._fileList.length > 0
                    width: parent.width
                    height: Math.min(220, fileListView.contentHeight + 12)
                    color: Theme.Theme.background
                    radius: 4
                    border.width: 1
                    border.color: Theme.Theme.divider

                    ListView {
                        id: fileListView
                        anchors.fill: parent
                        anchors.margins: 6
                        clip: true
                        model: preDownloadDialog._fileList
                        delegate: Text {
                            width: fileListView.width
                            text: (index + 1) + ".  " + (modelData.file || "(无文件名)")
                            font.pixelSize: Theme.Theme.fontSizeCaption
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textSecondary
                            elide: Text.ElideMiddle
                        }
                    }
                }

                // Buttons
                Row {
                    spacing: Theme.Theme.spacingS

                    FluentButton {
                        text: "开始下载"
                        variant: "accent"
                        enabled: preDownloadDialog._queryDone
                        onClicked: {
                            appVM.confirmDownload();
                            preDownloadDialog._queryDone = false;
                            preDownloadDialog._fileList  = [];
                        }
                    }

                    FluentButton {
                        text: "取消"
                        variant: "subtle"
                        onClicked: {
                            appVM.cancelDownload();
                            preDownloadDialog.close();
                            preDownloadDialog._queryDone = false;
                            preDownloadDialog._fileList  = [];
                        }
                    }
                }
            }
        }

        // Open automatically when download starts (triggered by isDownloading going true)
        Connections {
            target: appVM
            function onIsDownloadingChanged() {
                if (appVM.isDownloading && downloadVM.preDownloadCheck) {
                    preDownloadDialog._queryDone = false;
                    preDownloadDialog._fileList  = [];
                    preDownloadDialog.open();
                }
            }
        }
    }

    // ── Post-download result dialog ────────────────────────────────
    Dialog {
        id: downloadResultDialog
        parent: Overlay.overlay
        anchors.centerIn: parent
        modal: true
        width: 440
        closePolicy: Dialog.CloseOnEscape | Dialog.CloseOnPressOutside
        standardButtons: Dialog.NoButton

        property string resultStatus:   "completed"
        property int    downloaded:      0
        property int    expected:        0
        property string failedUrlsJson: "[]"

        background: Rectangle {
            color: Theme.Theme.surface
            radius: Theme.Theme.radiusMedium
            border.width: 1
            border.color: Theme.Theme.cardBorder
        }

        header: Item {
            height: 52
            Text {
                anchors.left: parent.left; anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: {
                    switch (downloadResultDialog.resultStatus) {
                        case "completed":  return "✅  下载完成"
                        case "partial":    return "⚠️  部分文件未下载"
                        case "failed":     return "❌  下载失败"
                        case "cancelled":  return "⛔  已取消"
                        default:           return "下载结果"
                    }
                }
                font.pixelSize: Theme.Theme.fontSizeSubtitle
                font.weight: Font.DemiBold
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.textPrimary
            }
        }

        contentItem: Column {
            spacing: Theme.Theme.spacingM
            topPadding: 8
            bottomPadding: 20
            leftPadding: 20
            rightPadding: 20

            Text {
                width: parent.width - 40
                text: {
                    var r = downloadResultDialog;
                    if (r.resultStatus === "completed") {
                        return "所有文件已成功下载" +
                               (r.expected > 0 ? "（共 " + r.expected + " 个）" : "") + "。";
                    } else if (r.resultStatus === "partial") {
                        return "已下载 " + r.downloaded + " 个文件，" +
                               (r.expected - r.downloaded) + " 个文件未能下载。\n" +
                               "是否重新下载缺失的文件？";
                    } else if (r.resultStatus === "failed") {
                        return "本次下载未检测到新文件，可能全部失败。\n是否重试？";
                    } else {
                        return "下载已取消。";
                    }
                }
                font.pixelSize: Theme.Theme.fontSizeBody
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.textPrimary
                wrapMode: Text.Wrap
            }

            RowLayout {
                width: parent.width - 40
                spacing: Theme.Theme.spacingS

                // Retry failed items button (partial / failed)
                FluentButton {
                    visible: downloadResultDialog.resultStatus === "partial" ||
                             downloadResultDialog.resultStatus === "failed"
                    text: "重新下载失败项"
                    variant: "accent"
                    onClicked: {
                        downloadResultDialog.close();
                        var urls = JSON.parse(downloadResultDialog.failedUrlsJson);
                        if (urls.length > 0) {
                            for (var i = 0; i < urls.length; i++) urlModel.addUrl(urls[i]);
                        }
                        appVM.executeBatch();
                    }
                }

                FluentButton {
                    visible: downloadResultDialog.resultStatus !== "cancelled"
                    text: downloadResultDialog.resultStatus === "completed" ? "确定" : "跳过"
                    variant: downloadResultDialog.resultStatus === "completed" ? "accent" : "subtle"
                    onClicked: downloadResultDialog.close()
                }

                FluentButton {
                    visible: downloadResultDialog.resultStatus === "cancelled"
                    text: "确定"
                    variant: "accent"
                    onClicked: downloadResultDialog.close()
                }
            }
        }
    }

    // ── Login Dialog ───────────────────────────────────────────────
    Dialog {
        id: loginDialog
        title: "Telegram 登录"
        anchors.centerIn: parent
        modal: true
        width: 420
        height: loginDialogContent.implicitHeight + 100

        background: Rectangle {
            color: Theme.Theme.surface
            radius: Theme.Theme.radiusMedium
            border.width: 0
        }

        header: Item {
            height: 48
            Text {
                anchors.left: parent.left; anchors.leftMargin: 20
                anchors.verticalCenter: parent.verticalCenter
                text: "Telegram 登录"
                font.pixelSize: Theme.Theme.fontSizeSubtitle
                font.family: Theme.Theme.fontFamily
                font.weight: Font.DemiBold
                color: Theme.Theme.textPrimary
            }
        }

        contentItem: Column {
            id: loginDialogContent
            spacing: Theme.Theme.spacingM
            padding: 20

            Text {
                text: "请选择 Telegram Desktop 安装目录\n（包含 tdata 文件夹的目录）"
                font.pixelSize: Theme.Theme.fontSizeBody
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.textSecondary
                width: parent.width - 40
                wrapMode: Text.Wrap
            }

            RowLayout {
                width: parent.width - 40
                spacing: Theme.Theme.spacingS

                FluentTextField {
                    id: telegramPathField
                    Layout.fillWidth: true
                    placeholderText: "C:\\Users\\xxx\\AppData\\Roaming\\Telegram Desktop"
                }

                FluentButton {
                    text: "浏览"
                    onClicked: telegramFolderDialog.open()
                }
            }

            Text {
                width: parent.width - 40
                text: "⚠ 登录前请确保 Telegram Desktop 已退出"
                font.pixelSize: Theme.Theme.fontSizeCaption
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.warning
                wrapMode: Text.Wrap
            }

            RowLayout {
                spacing: Theme.Theme.spacingS

                FluentButton {
                    text: "打开登录终端"
                    variant: "accent"
                    enabled: telegramPathField.text.length > 0
                    onClicked: appVM.login(telegramPathField.text)
                }

                FluentButton {
                    text: "验证登录"
                    variant: "standard"
                    onClicked: {
                        if (appVM.verifyLogin()) {
                            loginDialog.close();
                        }
                    }
                }

                FluentButton {
                    text: "取消"
                    variant: "subtle"
                    onClicked: loginDialog.close()
                }
            }
        }
    }

    Platform.FolderDialog {
        id: telegramFolderDialog
        title: "选择 Telegram Desktop 目录"
        onAccepted: {
            var path = folder.toString();
            if (Qt.platform.os === "windows")
                path = path.replace(/^file:\/\/\//, "");
            else
                path = path.replace(/^file:\/\//, "");
            telegramPathField.text = path;
        }
    }
}
