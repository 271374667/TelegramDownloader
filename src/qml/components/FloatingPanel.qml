import QtQuick
import QtQuick.Controls.Basic
import "../theme" as Theme
import "../controls"

/*  Compact floating panel — always-on-top, draggable, frameless.
    Acts as a quick-action overlay.                                  */
Item {
    id: root

    signal clearRequested()
    signal generateRequested()
    signal executeRequested()
    signal showMainRequested()
    signal closeRequested()

    property int urlCount: 0
    property int previousUrlCount: 0
    property int recentIncrease: 0
    property bool initialized: false
    property real flashOpacity: 0.0
    property real glowOpacity: 0.0
    property real countPulseScale: 1.0

    function withAlpha(color, alpha) {
        return Qt.rgba(color.r, color.g, color.b, alpha);
    }

    function triggerNewUrlCue(diff) {
        root.recentIncrease = diff;
        recentBadgeTimer.restart();
        cueAnim.restart();
    }

    onUrlCountChanged: {
        if (!initialized)
            return;

        var diff = urlCount - previousUrlCount;
        if (diff > 0)
            triggerNewUrlCue(diff);

        previousUrlCount = urlCount;
    }

    Component.onCompleted: {
        previousUrlCount = urlCount;
        initialized = true;
    }

    Timer {
        id: recentBadgeTimer
        interval: 2200
        onTriggered: root.recentIncrease = 0
    }

    SequentialAnimation {
        id: cueAnim

        ParallelAnimation {
            NumberAnimation {
                target: root
                property: "flashOpacity"
                from: 0.0
                to: 0.18
                duration: 100
                easing.type: Easing.OutCubic
            }
            NumberAnimation {
                target: root
                property: "glowOpacity"
                from: 0.0
                to: 1.0
                duration: 100
                easing.type: Easing.OutCubic
            }
            NumberAnimation {
                target: root
                property: "countPulseScale"
                from: 1.0
                to: 1.18
                duration: 120
                easing.type: Easing.OutBack
            }
        }

        ParallelAnimation {
            NumberAnimation {
                target: root
                property: "flashOpacity"
                to: 0.0
                duration: 300
                easing.type: Easing.OutCubic
            }
            NumberAnimation {
                target: root
                property: "countPulseScale"
                to: 1.0
                duration: 260
                easing.type: Easing.OutBack
            }
            NumberAnimation {
                target: root
                property: "glowOpacity"
                to: 0.0
                duration: 650
                easing.type: Easing.OutCubic
            }
        }
    }

    // The actual floating window
    Window {
        id: panelWindow
        flags: Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool
        color: "transparent"
        width: panelContent.implicitWidth
        height: 44
        visible: appVM.floatingPanelVisible

        // Position at top-right of screen
        Component.onCompleted: {
            x = Screen.width - width - 20;
            y = 40;
        }

        Rectangle {
            anchors.fill: parent
            radius: Theme.Theme.radiusLarge + 1
            color: "transparent"
            border.width: 1
            border.color: root.withAlpha(Theme.Theme.accentLight, 0.95)
            opacity: root.glowOpacity
        }

        Rectangle {
            id: panelContent
            anchors.fill: parent
            radius: Theme.Theme.radiusLarge
            color: Theme.Theme.dark ? "#E6202020" : "#E6F3F3F3"
            border.width: 1
            border.color: root.recentIncrease > 0 ? Theme.Theme.accentLight : Theme.Theme.cardBorder
            implicitWidth: panelRow.implicitWidth + 20
            implicitHeight: 44

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: root.withAlpha(Theme.Theme.accent, root.flashOpacity)
            }

            // Drag handling
            MouseArea {
                id: dragArea
                anchors.fill: parent
                onPressed: (mouse) => {
                    if (mouse.button === Qt.LeftButton)
                        panelWindow.startSystemMove()
                }
                onDoubleClicked: root.showMainRequested()
                z: -1
            }

            Row {
                id: panelRow
                anchors.centerIn: parent
                spacing: 6

                // Title
                Text {
                    text: "TDL"
                    font.pixelSize: 14
                    font.weight: Font.Bold
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.accent
                    anchors.verticalCenter: parent.verticalCenter
                }

                // Separator
                Rectangle {
                    width: 1; height: 20
                    color: Theme.Theme.divider
                    anchors.verticalCenter: parent.verticalCenter
                }

                // URL count
                Item {
                    width: countText.implicitWidth
                    height: 20
                    scale: root.countPulseScale
                    transformOrigin: Item.Center
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        id: countText
                        anchors.centerIn: parent
                        text: root.urlCount + " 链接"
                        font.pixelSize: 12
                        font.family: Theme.Theme.fontFamily
                        color: root.recentIncrease > 0
                            ? Theme.Theme.accentLight
                            : (root.urlCount > 0 ? Theme.Theme.textPrimary : Theme.Theme.textDisabled)
                    }
                }

                Rectangle { width: 1; height: 20; color: Theme.Theme.divider; anchors.verticalCenter: parent.verticalCenter }

                // Clear button
                PanelButton {
                    text: "清空"
                    bgColor: Theme.Theme.btnDanger
                    enabled: root.urlCount > 0
                    onClicked: root.clearRequested()
                }

                // Generate button
                PanelButton {
                    text: "BAT"
                    bgColor: Theme.Theme.btnSuccess
                    enabled: root.urlCount > 0
                    onClicked: root.generateRequested()
                }

                // Run button
                PanelButton {
                    text: "运行"
                    bgColor: Theme.Theme.accentDark
                    enabled: root.urlCount > 0
                    onClicked: root.executeRequested()
                }

                // Show main
                PanelButton {
                    text: "主界面"
                    bgColor: "#6A1B9A"
                    onClicked: root.showMainRequested()
                }

                // Close
                PanelButton {
                    text: "✕"
                    bgColor: Theme.Theme.btnDanger
                    onClicked: root.closeRequested()
                }
            }
        }
    }

    // Mini button component
    component PanelButton: Rectangle {
        property string text: ""
        property color bgColor: Theme.Theme.btnStandard
        property bool enabled: true

        signal clicked()

        width: Math.max(36, btnText.implicitWidth + 16)
        height: 26
        radius: Theme.Theme.radiusSmall
        color: !enabled ? (Theme.Theme.dark ? "#333333" : "#E0E0E0")
             : ma.pressed ? Qt.darker(bgColor, 1.3)
             : ma.containsMouse ? Qt.lighter(bgColor, 1.15)
             : bgColor
        opacity: enabled ? 1.0 : 0.5

        Behavior on color { ColorAnimation { duration: 60 } }

        Text {
            id: btnText
            anchors.centerIn: parent
            text: parent.text
            font.pixelSize: 11
            font.family: Theme.Theme.fontFamily
            font.weight: Font.DemiBold
            color: parent.enabled ? "#FFFFFF" : Theme.Theme.textDisabled
        }

        MouseArea {
            id: ma
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            enabled: parent.enabled
            onClicked: parent.clicked()
        }
    }
}
