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
            id: panelContent
            anchors.fill: parent
            radius: Theme.Theme.radiusLarge
            color: Theme.Theme.dark ? "#E6202020" : "#E6F3F3F3"
            border.width: 1
            border.color: Theme.Theme.cardBorder
            implicitWidth: panelRow.implicitWidth + 20
            implicitHeight: 44

            // Drag handling
            MouseArea {
                id: dragArea
                anchors.fill: parent
                property point startPos
                onPressed: (mouse) => startPos = Qt.point(mouse.x, mouse.y)
                onPositionChanged: (mouse) => {
                    if (pressed) {
                        panelWindow.x += mouse.x - startPos.x;
                        panelWindow.y += mouse.y - startPos.y;
                    }
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
                Text {
                    text: root.urlCount + " 链接"
                    font.pixelSize: 12
                    font.family: Theme.Theme.fontFamily
                    color: root.urlCount > 0 ? Theme.Theme.textPrimary : Theme.Theme.textDisabled
                    anchors.verticalCenter: parent.verticalCenter
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
            color: Theme.Theme.textOnAccent
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
