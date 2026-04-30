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

        // ── Queue Folder ───────────────────────────────────────────
        FluentCard {
            title: "队列文件夹"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingS

                    FluentTextField {
                        id: queueDirField
                        Layout.fillWidth: true
                        text: queueVM.queueDir
                        placeholderText: "队列文件夹路径…"
                        onEditingFinished: queueVM.queueDir = text
                    }

                    FluentButton {
                        text: "浏览"
                        Layout.alignment: Qt.AlignBottom
                        onClicked: queueFolderDialog.open()
                    }

                    FluentButton {
                        text: "刷新"
                        variant: "subtle"
                        Layout.alignment: Qt.AlignBottom
                        onClicked: queueVM.refreshQueues()
                    }
                }
            }
        }

        // ── Queue List ─────────────────────────────────────────────
        FluentCard {
            title: "当前队列"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                // Header row
                Rectangle {
                    width: parent.width
                    height: 28
                    color: Qt.rgba(1,1,1,0.04)
                    radius: Theme.Theme.radiusSmall

                    visible: queueVM.queueCount > 0

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 44

                        Text {
                            width: parent.width * 0.45
                            text: "队列名称"
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            width: parent.width * 0.2
                            text: "链接数"
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            width: parent.width * 0.35
                            text: "创建时间"
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }

                // Queue list view
                Rectangle {
                    width: parent.width
                    height: queueVM.queueCount > 0
                        ? Math.min(Math.max(queueListView.contentHeight + 8, 40), 280)
                        : 56
                    color: Theme.Theme.inputBackground
                    radius: Theme.Theme.radiusSmall
                    border.width: 1
                    border.color: Theme.Theme.cardBorder

                    ListView {
                        id: queueListView
                        anchors.fill: parent
                        anchors.margins: 4
                        model: queueVM.queueList
                        clip: true
                        spacing: 2
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                        delegate: Rectangle {
                            width: queueListView.width
                            height: 34
                            radius: Theme.Theme.radiusSmall
                            color: rowMa.containsMouse
                                ? Theme.Theme.surfaceHover
                                : "transparent"

                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 8
                                spacing: 0

                                Text {
                                    width: parent.width * 0.45 - 8
                                    text: modelData.name
                                    font.pixelSize: Theme.Theme.fontSizeBody
                                    font.family: Theme.Theme.fontFamily
                                    color: Theme.Theme.textPrimary
                                    elide: Text.ElideRight
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                Text {
                                    width: parent.width * 0.2
                                    text: modelData.urlCount + " 个"
                                    font.pixelSize: Theme.Theme.fontSizeCaption
                                    font.family: Theme.Theme.fontFamily
                                    color: Theme.Theme.textSecondary
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                Text {
                                    width: parent.width * 0.28
                                    text: modelData.createdAt.substring(0, 16).replace("T", " ")
                                    font.pixelSize: Theme.Theme.fontSizeCaption
                                    font.family: Theme.Theme.fontFamily
                                    color: Theme.Theme.textDisabled
                                    elide: Text.ElideRight
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                Text {
                                    text: "✕"
                                    font.pixelSize: 11
                                    color: delMa.containsMouse
                                        ? Theme.Theme.error
                                        : Theme.Theme.textDisabled
                                    anchors.verticalCenter: parent.verticalCenter
                                    MouseArea {
                                        id: delMa
                                        anchors.fill: parent
                                        anchors.margins: -4
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: queueVM.deleteQueue(modelData.name)
                                    }
                                }
                            }

                            MouseArea {
                                id: rowMa
                                anchors.fill: parent
                                hoverEnabled: true
                                z: -1
                            }
                        }

                        // Empty state
                        Text {
                            anchors.centerIn: parent
                            visible: queueListView.count === 0
                            text: "暂无队列 — 在下载页点击「导出到队列」添加"
                            font.pixelSize: Theme.Theme.fontSizeBody
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textDisabled
                        }
                    }
                }

                // Hint about subfolder naming
                Text {
                    width: parent.width
                    visible: queueVM.queueCount > 0
                    text: "下载时每个队列将创建独立子文件夹：队列名称 + UUID 短码"
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textSecondary
                    wrapMode: Text.Wrap
                }
            }
        }

        // ── Output Directory ───────────────────────────────────────
        FluentCard {
            title: "下载输出目录"
            width: parent.width

            RowLayout {
                width: parent.width
                spacing: Theme.Theme.spacingS

                FluentTextField {
                    id: outputDirField
                    Layout.fillWidth: true
                    text: queueVM.outputDir
                    placeholderText: "输出目录…"
                    onEditingFinished: queueVM.outputDir = text
                }

                FluentButton {
                    text: "浏览"
                    Layout.alignment: Qt.AlignBottom
                    onClicked: outputFolderDialog.open()
                }
            }
        }

        // ── Action Buttons ─────────────────────────────────────────
        FluentCard {
            title: "执行下载"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                Text {
                    width: parent.width
                    visible: queueVM.queueCount === 0
                    text: "队列为空，请先在下载页将链接导出到队列。"
                    font.pixelSize: Theme.Theme.fontSizeBody
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textSecondary
                    wrapMode: Text.Wrap
                }

                Row {
                    spacing: 8

                    FluentButton {
                        text: "▶  运行队列下载"
                        variant: "accent"
                        enabled: queueVM.queueCount > 0
                        onClicked: appVM.executeQueueBatch()
                    }

                    FluentButton {
                        text: "生成 BAT"
                        enabled: queueVM.queueCount > 0
                        onClicked: appVM.generateQueueBatch()
                    }
                }

                Text {
                    width: parent.width
                    text: "已跳过设置：--continue 和 --skip-same 始终启用，避免重复下载已有文件。"
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textDisabled
                    wrapMode: Text.Wrap
                }
            }
        }

        Item { width: 1; height: Theme.Theme.spacingXL }
    }

    // ── Folder dialogs ─────────────────────────────────────────────
    Platform.FolderDialog {
        id: queueFolderDialog
        title: "选择队列文件夹"
        onAccepted: {
            var path = folder.toString()
            if (Qt.platform.os === "windows")
                path = path.replace(/^file:\/\/\//, "")
            else
                path = path.replace(/^file:\/\//, "")
            queueVM.queueDir = path
            queueDirField.text = path
        }
    }

    Platform.FolderDialog {
        id: outputFolderDialog
        title: "选择输出目录"
        onAccepted: {
            var path = folder.toString()
            if (Qt.platform.os === "windows")
                path = path.replace(/^file:\/\/\//, "")
            else
                path = path.replace(/^file:\/\//, "")
            queueVM.outputDir = path
            outputDirField.text = path
        }
    }
}
