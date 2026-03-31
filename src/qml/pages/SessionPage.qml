import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
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

        // ── Basic Settings ─────────────────────────────────────────
        FluentExpander {
            title: "基本设置"
            subtitle: "调试、延迟、并发数、命名空间"
            width: parent.width
            expanded: true
            toggleable: true
            toggled: sessionVM.basicEnabled
            onToggleChanged: (v) => sessionVM.basicEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                FluentSwitch {
                    text: "调试模式"
                    checked: sessionVM.debug
                    onCheckedChanged: sessionVM.debug = checked
                }

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingL

                    FluentTextField {
                        label: "任务延迟"
                        text: sessionVM.delay
                        placeholderText: "0s"
                        Layout.preferredWidth: 140
                        helperText: "例如: 0s, 5s, 1m"
                        onEditingFinished: sessionVM.delay = text
                    }

                    FluentSpinBox {
                        label: "并发上限"
                        value: sessionVM.limit
                        from: 1; to: 128
                        Layout.preferredWidth: 140
                        onValueModified: sessionVM.limit = value
                    }
                }

                FluentTextField {
                    label: "命名空间"
                    text: sessionVM.namespace
                    placeholderText: "default"
                    width: parent.width
                    onEditingFinished: sessionVM.namespace = text
                }
            }
        }

        // ── Network Settings ───────────────────────────────────────
        FluentExpander {
            title: "网络设置"
            subtitle: "代理、NTP、连接池、重连超时"
            width: parent.width
            expanded: true
            toggleable: true
            toggled: sessionVM.networkEnabled
            onToggleChanged: (v) => sessionVM.networkEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                Column {
                    width: parent.width
                    spacing: Theme.Theme.spacingS

                    FluentComboBox {
                        label: "代理预设"
                        width: parent.width
                        model: [
                            "自定义代理",
                            "SOCKS5 (127.0.0.1:7897)",
                            "SOCKS5 (127.0.0.1:1080)",
                            "HTTP (127.0.0.1:8080)",
                            "HTTPS (127.0.0.1:8080)"
                        ]
                        onActivated: (index) => {
                            sessionVM.applyProxyPreset(index);
                            if (index > 0)
                                proxyField.text = sessionVM.proxy;
                        }
                    }

                    FluentTextField {
                        id: proxyField
                        label: "代理地址"
                        text: sessionVM.proxy
                        placeholderText: "socks5://127.0.0.1:7897"
                        width: parent.width
                        onEditingFinished: sessionVM.proxy = text
                    }
                }

                RowLayout {
                    width: parent.width
                    spacing: Theme.Theme.spacingL

                    FluentTextField {
                        label: "NTP 服务器"
                        text: sessionVM.ntpServer
                        placeholderText: "留空使用系统时间"
                        Layout.fillWidth: true
                        onEditingFinished: sessionVM.ntpServer = text
                    }

                    FluentSpinBox {
                        label: "连接池大小"
                        value: sessionVM.pool
                        from: 1; to: 64
                        Layout.preferredWidth: 140
                        onValueModified: sessionVM.pool = value
                    }
                }

                FluentTextField {
                    label: "重连超时"
                    text: sessionVM.reconnectTimeout
                    placeholderText: "5m0s"
                    width: parent.width
                    helperText: "例如: 30s, 5m0s, 1h"
                    onEditingFinished: sessionVM.reconnectTimeout = text
                }
            }
        }

        // ── Storage Settings ───────────────────────────────────────
        FluentExpander {
            title: "存储设置"
            subtitle: "存储类型和路径"
            width: parent.width
            toggleable: true
            toggled: sessionVM.storageEnabled
            onToggleChanged: (v) => sessionVM.storageEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingM

                FluentComboBox {
                    label: "存储类型"
                    width: parent.width
                    model: ["bolt", "legacy", "file"]
                    currentIndex: {
                        var types = ["bolt", "legacy", "file"];
                        var idx = types.indexOf(sessionVM.storageType);
                        return idx >= 0 ? idx : 0;
                    }
                    onActivated: (index) => {
                        var types = ["bolt", "legacy", "file"];
                        sessionVM.storageType = types[index];
                    }
                }

                FluentTextField {
                    label: "存储路径"
                    text: sessionVM.storagePath
                    placeholderText: "~/.tdl/data"
                    width: parent.width
                    onEditingFinished: sessionVM.storagePath = text
                }
            }
        }

        // ── Performance Settings ───────────────────────────────────
        FluentExpander {
            title: "性能设置"
            subtitle: "传输线程数"
            width: parent.width
            expanded: true
            toggleable: true
            toggled: sessionVM.performanceEnabled
            onToggleChanged: (v) => sessionVM.performanceEnabled = v

            Column {
                width: parent.width
                spacing: Theme.Theme.spacingS

                FluentSpinBox {
                    label: "线程数"
                    value: sessionVM.threads
                    from: 1; to: 128
                    onValueModified: sessionVM.threads = value
                }

                Text {
                    text: "每个下载项使用的最大线程数，建议值 8-32"
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textDisabled
                }
            }
        }

        // Bottom spacing
        Item { width: 1; height: Theme.Theme.spacingXL }
    }
}
