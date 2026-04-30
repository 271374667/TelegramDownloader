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
                    }
                    delegate: Rectangle {
                        width: parent.width
                        height: 44
                        color: navArea.containsMouse
                            ? Theme.Theme.surfaceHover
                            : pageStack.currentIndex === model.pageIndex
                            ? (Theme.Theme.dark ? "#0FFFFFFF" : "#0F000000")
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

                // ── Theme toggle ───────────────────────────────────
                Rectangle {
                    width: parent.width
                    height: 36
                    radius: Theme.Theme.radiusSmall
                    color: themeToggleMa.containsMouse ? Theme.Theme.surfaceHover : "transparent"

                    Row {
                        anchors.centerIn: parent
                        spacing: 8

                        Text {
                            text: Theme.Theme.dark ? "🌙" : "☀️"
                            font.pixelSize: 16
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: Theme.Theme.dark ? "深色模式" : "浅色模式"
                            font.pixelSize: Theme.Theme.fontSizeBody
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textPrimary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    MouseArea {
                        id: themeToggleMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: Theme.Theme.dark = !Theme.Theme.dark
                    }
                }

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
            width: floatingQueueDialog.width
            spacing: Theme.Theme.spacingM
            topPadding: 4
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

            Row {
                spacing: 8

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
