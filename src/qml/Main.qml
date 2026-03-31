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

    // ── Main Layout ────────────────────────────────────────────────
    RowLayout {
        anchors.fill: parent
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
                        ListElement { label: "⚙  会话设置"; pageIndex: 1 }
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
                    text: pageStack.currentIndex === 0 ? "下载配置" : "会话设置"
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
                SessionPage {}
            }

            // Bottom bar: Command Preview
            CommandPreview {
                Layout.fillWidth: true
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
        onShowMainRequested: { window.show(); window.raise(); window.requestActivate(); }
        onCloseRequested: appVM.floatingPanelVisible = false
    }

    // ── InfoBar (notifications) ────────────────────────────────────
    FluentInfoBar {
        id: infoBar
        anchors.top: parent.top; anchors.topMargin: 8
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
