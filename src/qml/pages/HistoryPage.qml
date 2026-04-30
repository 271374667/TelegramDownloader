import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../theme" as Theme
import "../controls"

Item {
    id: root

    ScrollView {
        anchors.fill: parent
        anchors.margins: Theme.Theme.spacingXL
        contentWidth: availableWidth
        clip: true

        Column {
            width: parent.width
            spacing: Theme.Theme.spacingM

            // ── Header ─────────────────────────────────────────────
            RowLayout {
                width: parent.width
                spacing: Theme.Theme.spacingS

                Text {
                    text: "最近任务历史"
                    font.pixelSize: Theme.Theme.fontSizeBody
                    font.weight: Font.Medium
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textPrimary
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "最多显示"
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textSecondary
                    Layout.alignment: Qt.AlignVCenter
                }

                FluentSpinBox {
                    from: 5
                    to: 100
                    value: historyVM.maxHistory
                    onValueModified: historyVM.maxHistory = value
                }

                Text {
                    text: "条"
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textSecondary
                    Layout.alignment: Qt.AlignVCenter
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.Theme.divider
            }

            // ── Empty state ────────────────────────────────────────
            Item {
                visible: historyVM.count === 0
                width: parent.width
                height: 160

                Column {
                    anchors.centerIn: parent
                    spacing: Theme.Theme.spacingS

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "📋"
                        font.pixelSize: 36
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "暂无历史任务"
                        font.pixelSize: Theme.Theme.fontSizeBody
                        font.family: Theme.Theme.fontFamily
                        color: Theme.Theme.textSecondary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "使用「执行下载」后任务记录将显示在此处"
                        font.pixelSize: Theme.Theme.fontSizeCaption
                        font.family: Theme.Theme.fontFamily
                        color: Theme.Theme.textSecondary
                    }
                }
            }

            // ── Task list ──────────────────────────────────────────
            Repeater {
                model: historyVM.historyModel

                delegate: Rectangle {
                    id: taskCard
                    width: parent.width
                    height: cardContent.implicitHeight + 28
                    radius: Theme.Theme.radiusMedium
                    color: Theme.Theme.cardBackground
                    border.width: 1
                    border.color: {
                        if (model.taskStatus === "partial") return "#80FF9800"
                        if (model.taskStatus === "failed")  return "#80F44336"
                        return Theme.Theme.cardBorder
                    }

                    Column {
                        id: cardContent
                        anchors {
                            left: parent.left;  leftMargin:  16
                            right: parent.right; rightMargin: 16
                            verticalCenter: parent.verticalCenter
                        }
                        spacing: 8

                        // ── Row 1: title + status badge + time ──────
                        RowLayout {
                            width: parent.width
                            spacing: Theme.Theme.spacingS

                            // Status icon
                            Text {
                                text: {
                                    switch (model.taskStatus) {
                                        case "completed": return "✅"
                                        case "partial":   return "⚠️"
                                        case "failed":    return "❌"
                                        default:          return "⏳"
                                    }
                                }
                                font.pixelSize: 14
                            }

                            Text {
                                text: model.taskTitle
                                font.pixelSize: Theme.Theme.fontSizeBody
                                font.weight: Font.Medium
                                font.family: Theme.Theme.fontFamily
                                color: Theme.Theme.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }

                            // Status badge
                            Rectangle {
                                radius: 4
                                width:  statusBadgeText.implicitWidth + 12
                                height: 20
                                color: {
                                    switch (model.taskStatus) {
                                        case "completed": return "#334CAF50"
                                        case "partial":   return "#33FF9800"
                                        case "failed":    return "#33F44336"
                                        default:          return "#330078D4"
                                    }
                                }

                                Text {
                                    id: statusBadgeText
                                    anchors.centerIn: parent
                                    text: model.taskStatusLabel
                                    font.pixelSize: Theme.Theme.fontSizeCaption
                                    font.family: Theme.Theme.fontFamily
                                    color: {
                                        switch (model.taskStatus) {
                                            case "completed": return "#4CAF50"
                                            case "partial":   return "#FF9800"
                                            case "failed":    return "#F44336"
                                            default:          return Theme.Theme.accent
                                        }
                                    }
                                }
                            }

                            Text {
                                text: model.taskTime
                                font.pixelSize: Theme.Theme.fontSizeCaption
                                font.family: Theme.Theme.fontFamily
                                color: Theme.Theme.textSecondary
                            }
                        }

                        // ── Row 2: summary info ─────────────────────
                        Text {
                            text: model.taskSummary + "  ·  " + model.urlCount + " 条链接"
                            font.pixelSize: Theme.Theme.fontSizeCaption
                            font.family: Theme.Theme.fontFamily
                            color: Theme.Theme.textSecondary
                        }

                        // ── Row 3: action buttons ───────────────────
                        RowLayout {
                            width: parent.width
                            spacing: Theme.Theme.spacingS

                            FluentButton {
                                visible: model.hasFailures
                                text: "重新下载失败项"
                                variant: "accent"
                                onClicked: historyVM.retryFailedItems(model.taskId)
                            }

                            FluentButton {
                                text: "重新开始任务"
                                variant: "subtle"
                                onClicked: historyVM.restartTask(model.taskId)
                            }

                            Item { Layout.fillWidth: true }

                            FluentButton {
                                text: "删除"
                                variant: "subtle"
                                onClicked: historyVM.deleteTask(model.taskId)
                            }
                        }
                    }
                }
            }

            // Bottom padding
            Item { width: 1; height: Theme.Theme.spacingXL }
        }
    }
}
