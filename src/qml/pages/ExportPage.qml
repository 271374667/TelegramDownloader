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
        y: Theme.Theme.spacingXL
        spacing: Theme.Theme.spacingL

        // ── Target Chat Card ───────────────────────────────────────
        FluentCard {
            title: "导出目标"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                FluentTextField {
                    label: "聊天 ID / 用户名"
                    text: exportVM.chat
                    placeholderText: "留空 = 收藏夹 (Saved Messages)"
                    width: parent.width
                    helperText: "例如: @channel、-100123456789、https://t.me/group"
                    onEditingFinished: exportVM.chat = text
                }

                // ── Source: Topic / Reply ──────────────────────────
                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingL

                    FluentSwitch {
                        id: topicSwitch
                        text: "从主题导出"
                        checked: exportVM.topicEnabled
                        onCheckedChanged: {
                            exportVM.topicEnabled = checked
                            if (checked) exportVM.replyEnabled = false
                        }
                    }

                    FluentSpinBox {
                        label: "主题 ID"
                        value: exportVM.topicId
                        from: 1; to: 2147483647
                        enabled: exportVM.topicEnabled
                        Layout.preferredWidth: 160
                        onValueModified: exportVM.topicId = value
                    }
                }

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingL

                    FluentSwitch {
                        text: "从回复导出"
                        checked: exportVM.replyEnabled
                        onCheckedChanged: {
                            exportVM.replyEnabled = checked
                            if (checked) exportVM.topicEnabled = false
                        }
                    }

                    FluentSpinBox {
                        label: "帖子 ID"
                        value: exportVM.replyPostId
                        from: 1; to: 2147483647
                        enabled: exportVM.replyEnabled
                        Layout.preferredWidth: 160
                        onValueModified: exportVM.replyPostId = value
                    }
                }
            }
        }

        // ── Output Path Card ────────────────────────────────────────
        FluentCard {
            title: "输出文件"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingS

                    FluentTextField {
                        label: "输出路径"
                        text: exportVM.output
                        placeholderText: "tdl-export.json"
                        Layout.fillWidth: true
                        helperText: "默认保存到当前目录 tdl-export.json"
                        onEditingFinished: exportVM.output = text
                    }

                    FluentButton {
                        text: "浏览"
                        variant: "subtle"
                        Layout.alignment: Qt.AlignBottom
                        onClicked: saveFileDialog.open()
                    }
                }

                Platform.FileDialog {
                    id: saveFileDialog
                    title: "选择输出文件"
                    fileMode: Platform.FileDialog.SaveFile
                    nameFilters: ["JSON 文件 (*.json)", "所有文件 (*)"]
                    defaultSuffix: "json"
                    onAccepted: exportVM.output = file.toString().replace("file:///", "")
                }
            }
        }

        // ── Range Settings ──────────────────────────────────────────
        FluentExpander {
            id: rangeExpander
            title: "消息范围"
            subtitle: "按时间戳、消息 ID 或最新 N 条筛选"
            width: parent.width
            expanded: false
            toggleable: true
            toggled: exportVM.rangeEnabled
            onToggleChanged: (v) => exportVM.rangeEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                FluentComboBox {
                    label: "范围类型"
                    width: parent.width
                    model: ["时间范围 (time)", "ID 范围 (id)", "最新 N 条 (last)"]
                    currentIndex: {
                        switch (exportVM.rangeType) {
                            case "time": return 0
                            case "id":   return 1
                            case "last": return 2
                            default:     return 0
                        }
                    }
                    onActivated: (idx) => {
                        const types = ["time", "id", "last"]
                        exportVM.rangeType = types[idx]
                    }
                }

                // Dynamic input row based on range type
                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingL
                    visible: exportVM.rangeType !== "last"

                    FluentTextField {
                        label: exportVM.rangeType === "time" ? "开始时间戳 (Unix)" : "起始消息 ID"
                        text: exportVM.rangeStart
                        placeholderText: exportVM.rangeType === "time" ? "1665700000" : "100"
                        Layout.preferredWidth: 180
                        helperText: exportVM.rangeType === "time" ? "Unix 时间戳（秒）" : "消息 ID"
                        onEditingFinished: exportVM.rangeStart = text
                    }

                    FluentTextField {
                        label: exportVM.rangeType === "time" ? "结束时间戳 (Unix)" : "结束消息 ID"
                        text: exportVM.rangeEnd
                        placeholderText: exportVM.rangeType === "time" ? "1665761624" : "500"
                        Layout.preferredWidth: 180
                        helperText: exportVM.rangeType === "time" ? "Unix 时间戳（秒）" : "消息 ID"
                        onEditingFinished: exportVM.rangeEnd = text
                    }
                }

                FluentTextField {
                    label: "最新消息数量"
                    text: exportVM.rangeStart
                    placeholderText: "100"
                    visible: exportVM.rangeType === "last"
                    width: parent.width
                    helperText: "导出最新的 N 条媒体消息"
                    onEditingFinished: exportVM.rangeStart = text
                }
            }
        }

        // ── Filter Expression ───────────────────────────────────────
        FluentExpander {
            title: "过滤表达式"
            subtitle: "使用 expr-lang 对消息字段进行过滤"
            width: parent.width
            expanded: false
            toggleable: true
            toggled: exportVM.filterEnabled
            onToggleChanged: (v) => exportVM.filterEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                // Filter input (multi-line friendly)
                Column {
                    width: parent.width
                    spacing: Theme.Theme.spacingXS

                    Text {
                        text: "过滤条件"
                        font.pixelSize: Theme.Theme.fontSizeCaption
                        font.family: Theme.Theme.fontFamily
                        color: Theme.Theme.textSecondary
                    }

                    Rectangle {
                        width: parent.width
                        height: 72
                        radius: Theme.Theme.radiusSmall
                        color: Theme.Theme.inputBackground
                        border.width: 1
                        border.color: filterField.activeFocus
                            ? Theme.Theme.inputBorderFocus
                            : Theme.Theme.inputBorder

                        Behavior on border.color { ColorAnimation { duration: Theme.Theme.animFast } }

                        Rectangle {
                            anchors.bottom: parent.bottom
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: filterField.activeFocus ? parent.width - 2 : 0
                            height: 2; radius: 1
                            color: Theme.Theme.accent
                            Behavior on width { NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutCubic } }
                        }

                        TextEdit {
                            id: filterField
                            anchors.fill: parent
                            anchors.margins: 8
                            text: exportVM.filterExpr
                            font.pixelSize: Theme.Theme.fontSizeBody
                            font.family: "Consolas, " + Theme.Theme.fontFamily
                            color: Theme.Theme.textPrimary
                            wrapMode: TextEdit.Wrap
                            onTextChanged: exportVM.filterExpr = text
                        }

                        // Sync TextEdit when ViewModel changes from outside (chip/reset)
                        Connections {
                            target: exportVM
                            function onFilterExprChanged() {
                                if (filterField.text !== exportVM.filterExpr)
                                    filterField.text = exportVM.filterExpr
                            }
                        }

                        // Placeholder
                        Text {
                            anchors.fill: parent
                            anchors.margins: 8
                            visible: filterField.text === ""
                            text: 'Views > 200 && Media.Name endsWith ".zip" && Media.Size > 5*1024*1024'
                            font.pixelSize: Theme.Theme.fontSizeBody
                            font.family: "Consolas, " + Theme.Theme.fontFamily
                            color: Theme.Theme.textDisabled
                            wrapMode: Text.Wrap
                        }
                    }
                }

                // Helper chips
                Column {
                    width: parent.width
                    spacing: 4

                    Text {
                        text: "常用字段参考（点击插入）："
                        font.pixelSize: Theme.Theme.fontSizeCaption
                        font.family: Theme.Theme.fontFamily
                        color: Theme.Theme.textSecondary
                    }

                    Flow {
                        width: parent.width
                        spacing: 6

                        Repeater {
                            model: [
                                "Views > 0",
                                "Media.Size > 1024*1024",
                                'Media.Name endsWith ".mp4"',
                                'Media.Name endsWith ".zip"',
                                "Date > date(\"2024-01-01\")",
                                "ForwardsCount > 0",
                                "!Media.Photo"
                            ]

                            delegate: Rectangle {
                                height: 26
                                width: chipText.implicitWidth + 16
                                radius: 13
                                color: chipMa.containsMouse
                                    ? Theme.Theme.accentDark
                                    : "#2AFFFFFF"
                                border.width: 1
                                border.color: Theme.Theme.divider

                                Text {
                                    id: chipText
                                    anchors.centerIn: parent
                                    text: modelData
                                    font.pixelSize: 11
                                    font.family: "Consolas, " + Theme.Theme.fontFamily
                                    color: chipMa.containsMouse
                                        ? "#FFFFFF"
                                        : Theme.Theme.textPrimary
                                }

                                MouseArea {
                                    id: chipMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        const cur = exportVM.filterExpr
                                        exportVM.filterExpr = cur
                                            ? (cur + " && " + modelData)
                                            : modelData
                                    }
                                }
                            }
                        }
                    }
                }

                // Expr-lang tip
                Rectangle {
                    width: parent.width
                    height: tipText.implicitHeight + 16
                    radius: Theme.Theme.radiusSmall
                    color: "#1A3A6A"
                    border.width: 1
                    border.color: "#2060B0"

                    Text {
                        id: tipText
                        anchors { fill: parent; margins: 8 }
                        text: "💡 过滤表达式使用 expr-lang 语法。支持：&&、||、!、>、<、==、contains、startsWith、endsWith、matches 等运算符。"
                        font.pixelSize: Theme.Theme.fontSizeCaption
                        font.family: Theme.Theme.fontFamily
                        color: "#90C8FF"
                        wrapMode: Text.Wrap
                    }
                }
            }
        }

        // ── Export Options ──────────────────────────────────────────
        FluentCard {
            title: "导出选项"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                FluentSwitch {
                    text: "包含消息内容 (--with-content)"
                    checked: exportVM.withContent
                    onCheckedChanged: exportVM.withContent = checked
                }

                FluentSwitch {
                    text: "包含非媒体消息 (--all)"
                    checked: exportVM.allMessages
                    onCheckedChanged: {
                        exportVM.allMessages = checked
                        if (checked) exportVM.raw = false
                    }
                }

                FluentSwitch {
                    text: "导出原始 MTProto 结构 (--raw，用于调试)"
                    checked: exportVM.raw
                    onCheckedChanged: {
                        exportVM.raw = checked
                        if (checked) exportVM.allMessages = false
                    }
                }
            }
        }

        // ── Command Preview ─────────────────────────────────────────
        FluentCard {
            title: "命令预览"
            width: parent.width

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                Rectangle {
                    width: parent.width
                    height: Math.max(previewText.implicitHeight + 16, 48)
                    radius: Theme.Theme.radiusSmall
                    color: "#0D0D0D"
                    border.width: 1
                    border.color: Theme.Theme.divider
                    clip: true

                    Text {
                        id: previewText
                        anchors { fill: parent; margins: 8 }
                        text: appVM.exportCommandPreview || "（配置后预览命令）"
                        font.pixelSize: 12
                        font.family: "Consolas, " + Theme.Theme.fontFamily
                        color: appVM.exportCommandPreview
                            ? Theme.Theme.textPrimary
                            : Theme.Theme.textDisabled
                        wrapMode: Text.Wrap
                    }
                }

                // Action buttons
                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingM

                    FluentButton {
                        text: "生成 BAT"
                        variant: "accent"
                        onClicked: appVM.generateExportBatch()
                    }

                    FluentButton {
                        text: "▶  运行导出"
                        variant: "accent"
                        enabled: appVM.tdlStatus === "ready"
                        onClicked: appVM.executeExportBatch()
                    }

                    Item { Layout.fillWidth: true }

                    FluentButton {
                        text: "重置"
                        variant: "subtle"
                        onClicked: exportVM.resetDefaults()
                    }
                }
            }
        }
    }
}
