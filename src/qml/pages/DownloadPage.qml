import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Qt.labs.platform as Platform
import "../theme" as Theme
import "../controls"

Flickable {
    id: root
    contentHeight: mainCol.implicitHeight + Theme.Theme.spacingXL * 2
    clip: true
    boundsMovement: Flickable.StopAtBounds
    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

    Column {
        id: mainCol
        anchors.left: parent.left; anchors.right: parent.right
        anchors.margins: Theme.Theme.spacingXL
        anchors.topMargin: Theme.Theme.spacingXL
        y: Theme.Theme.spacingXL
        spacing: Theme.Theme.spacingL

        // ── URL Management Card ────────────────────────────────────
        FluentCard {
            title: "下载链接"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                // Input row
                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingS

                    FluentTextField {
                        id: urlInput
                        Layout.fillWidth: true
                        placeholderText: "https://t.me/channel/123"

                        Keys.onReturnPressed: addBtn.clicked()
                        Keys.onEnterPressed: addBtn.clicked()
                    }

                    FluentButton {
                        text: "添加"
                        variant: "accent"
                        onClicked: {
                            if (urlModel.addUrl(urlInput.text)) {
                                urlInput.text = "";
                            }
                        }
                    }
                }

                // URL List
                Rectangle {
                    width: parent.width
                    height: Math.min(Math.max(urlListView.contentHeight + 8, 60), 220)
                    color: Theme.Theme.inputBackground
                    radius: Theme.Theme.radiusSmall
                    border.width: 1
                    border.color: Theme.Theme.cardBorder

                    ListView {
                        id: urlListView
                        anchors.fill: parent
                        anchors.margins: 4
                        model: urlModel
                        clip: true
                        spacing: 2
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                        delegate: Rectangle {
                            width: urlListView.width
                            height: 30
                            radius: Theme.Theme.radiusSmall
                            color: delegateMa.containsMouse ? Theme.Theme.surfaceHover : "transparent"
                            property bool isSelected: urlListView.currentIndex === index

                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                spacing: 8

                                Text {
                                    width: parent.width - removeBtn.width - 16
                                    text: model.url
                                    font.pixelSize: Theme.Theme.fontSizeCaption
                                    font.family: Theme.Theme.fontFamily
                                    color: Theme.Theme.textPrimary
                                    elide: Text.ElideMiddle
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    id: removeBtn
                                    text: "✕"
                                    font.pixelSize: 11
                                    color: removeMa.containsMouse ? Theme.Theme.error : Theme.Theme.textDisabled
                                    anchors.verticalCenter: parent.verticalCenter
                                    MouseArea {
                                        id: removeMa; anchors.fill: parent; anchors.margins: -4
                                        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                        onClicked: urlModel.removeUrl(index)
                                    }
                                }
                            }

                            MouseArea {
                                id: delegateMa; anchors.fill: parent
                                hoverEnabled: true; z: -1
                                onClicked: urlListView.currentIndex = index
                            }
                        }

                        // Empty state
                        Text {
                            anchors.centerIn: parent
                            visible: urlListView.count === 0
                            text: "粘贴或添加 Telegram 链接"
                            font.pixelSize: Theme.Theme.fontSizeBody
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textDisabled
                        }
                    }
                }

                // Action row
                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingS

                    Text {
                        text: urlModel.statusText
                        font.pixelSize: Theme.Theme.fontSizeCaption
                        font.family: Theme.Theme.fontFamily
                        color: Theme.Theme.textSecondary
                        Layout.fillWidth: true
                    }

                    FluentButton {
                        text: "从剪贴板导入"
                        variant: "subtle"
                        iconText: "📋"
                        onClicked: appVM.importFromClipboard()
                    }

                    FluentButton {
                        text: "清空"
                        variant: "subtle"
                        iconText: "🗑"
                        enabled: urlModel.count > 0
                        onClicked: urlModel.clear()
                    }
                }

                // Clipboard monitoring toggle
                FluentSwitch {
                    text: "剪贴板自动检测"
                    checked: appVM.clipboardMonitoring
                    onCheckedChanged: appVM.clipboardMonitoring = checked
                }
            }
        }

        // ── Quick Settings Row ─────────────────────────────────────
        FluentCard {
            title: "下载目录"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingS

                    FluentTextField {
                        id: dirField
                        Layout.fillWidth: true
                        text: downloadVM.directory
                        placeholderText: "选择下载目录..."
                        onEditingFinished: downloadVM.directory = text
                    }

                    FluentButton {
                        text: "浏览"
                        onClicked: folderDialog.open()
                    }
                }

                FluentCheckBox {
                    id: subfolderCheck
                    text: "使用子文件夹"
                    checked: downloadVM.subfolderEnabled
                    onCheckedChanged: downloadVM.subfolderEnabled = checked
                }

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingS
                    visible: subfolderCheck.checked
                    opacity: visible ? 1.0 : 0.0
                    Behavior on opacity { NumberAnimation { duration: Theme.Theme.animNormal } }

                    FluentTextField {
                        Layout.fillWidth: true
                        text: downloadVM.subfolder
                        placeholderText: "子文件夹名称..."
                        onEditingFinished: downloadVM.subfolder = text
                    }
                }
            }
        }

        // ── Download Options ───────────────────────────────────────
        FluentExpander {
            title: "下载选项"
            subtitle: "续传、排序、去重等"
            width: parent.width
            expanded: true

            Flow {
                width: parent.width
                spacing: Theme.Theme.spacingM

                FluentCheckBox {
                    text: "续传上次下载"
                    checked: downloadVM.continueLast
                    onCheckedChanged: downloadVM.continueLast = checked
                }
                FluentCheckBox {
                    text: "从新到旧下载"
                    checked: downloadVM.desc
                    onCheckedChanged: downloadVM.desc = checked
                }
                FluentCheckBox {
                    text: "跳过同名文件"
                    checked: downloadVM.skipSame
                    onCheckedChanged: downloadVM.skipSame = checked
                }
                FluentCheckBox {
                    text: "自动检测群组消息"
                    checked: downloadVM.group
                    onCheckedChanged: downloadVM.group = checked
                }
                FluentCheckBox {
                    text: "重写文件扩展名"
                    checked: downloadVM.rewriteExt
                    onCheckedChanged: downloadVM.rewriteExt = checked
                }
                FluentCheckBox {
                    text: "使用 Takeout 会话"
                    checked: downloadVM.takeout
                    onCheckedChanged: downloadVM.takeout = checked
                }
                FluentCheckBox {
                    text: "重新开始下载"
                    checked: downloadVM.restart
                    onCheckedChanged: downloadVM.restart = checked
                }
            }
        }

        // ── File Filtering ─────────────────────────────────────────
        FluentExpander {
            title: "文件过滤"
            subtitle: "按扩展名包含或排除文件"
            width: parent.width
            toggleable: true
            toggled: downloadVM.filteringEnabled
            onToggleChanged: (v) => downloadVM.filteringEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                FluentTextField {
                    width: parent.width
                    label: "包含扩展名 (逗号分隔)"
                    text: downloadVM.includeExts
                    placeholderText: "jpg, png, mp4"
                    onEditingFinished: downloadVM.includeExts = text
                }

                FluentTextField {
                    width: parent.width
                    label: "排除扩展名 (逗号分隔)"
                    text: downloadVM.excludeExts
                    placeholderText: "exe, zip"
                    onEditingFinished: downloadVM.excludeExts = text
                }

                FluentTextField {
                    width: parent.width
                    label: "官方导出文件 (逗号分隔)"
                    text: downloadVM.officialFiles
                    placeholderText: "file1.json, file2.json"
                    onEditingFinished: downloadVM.officialFiles = text
                }
            }
        }

        // ── Advanced Settings ──────────────────────────────────────
        FluentExpander {
            title: "高级设置"
            subtitle: "模板与服务器模式"
            width: parent.width
            toggleable: true
            toggled: downloadVM.advancedEnabled
            onToggleChanged: (v) => downloadVM.advancedEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                FluentTextField {
                    width: parent.width
                    label: "文件名模板"
                    text: downloadVM.template
                    placeholderText: "{{ .DialogID }}_{{ .MessageID }}_{{ filenamify .FileName }}"
                    onEditingFinished: downloadVM.template = text
                }

                FluentSwitch {
                    text: "HTTP 服务器模式"
                    checked: downloadVM.serve
                    onCheckedChanged: downloadVM.serve = checked
                }

                FluentSpinBox {
                    label: "HTTP 端口"
                    value: downloadVM.port
                    from: 1; to: 65535
                    visible: downloadVM.serve
                    onValueModified: downloadVM.port = value
                }
            }
        }

        // Bottom spacing
        Item { width: 1; height: Theme.Theme.spacingXL }
    }

    // Folder dialog
    Platform.FolderDialog {
        id: folderDialog
        title: "选择下载目录"
        onAccepted: {
            var path = folder.toString();
            if (Qt.platform.os === "windows")
                path = path.replace(/^file:\/\/\//, "");
            else
                path = path.replace(/^file:\/\//, "");
            downloadVM.directory = path;
            dirField.text = path;
        }
    }
}
