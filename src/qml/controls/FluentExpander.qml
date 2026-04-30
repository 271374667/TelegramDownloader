import QtQuick
import QtQuick.Controls.Basic
import "../theme" as Theme

Rectangle {
    id: root

    property string title: ""
    property string subtitle: ""
    property bool expanded: false
    property bool toggleable: false
    property bool toggled: true
    default property alias content: contentContainer.data

    signal toggleChanged(bool value)

    color: Theme.Theme.cardBackground
    border.width: 1
    border.color: Theme.Theme.cardBorder
    radius: Theme.Theme.radiusMedium
    clip: true

    // Fluent 2: subtle top-highlight for layered depth
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        radius: parent.radius
        color: "#08FFFFFF"
        z: 1
    }

    implicitWidth: 400
    implicitHeight: header.height + (root.expanded ? contentWrapper.implicitHeight : 0)

    Behavior on implicitHeight {
        NumberAnimation { duration: Theme.Theme.animSlow; easing.type: Easing.OutQuad }
    }

    // ── Header ─────────────────────────────────────────────────────
    Rectangle {
        id: header
        width: parent.width
        height: 48
        color: headerMa.containsMouse ? Theme.Theme.surfaceHover : "transparent"
        radius: Theme.Theme.radiusMedium

        MouseArea {
            id: headerMa
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.expanded = !root.expanded
        }

        Row {
            anchors.left: parent.left
            anchors.leftMargin: Theme.Theme.spacingL
            anchors.verticalCenter: parent.verticalCenter
            spacing: Theme.Theme.spacingM

            // Toggle switch (optional)
            Switch {
                id: toggleSwitch
                visible: root.toggleable
                checked: root.toggled
                anchors.verticalCenter: parent.verticalCenter
                width: 40; height: 20

                indicator: Rectangle {
                    implicitWidth: 40; implicitHeight: 20
                    radius: 10
                    color: toggleSwitch.checked ? Theme.Theme.accentDark : "#4D4D4D"
                    border.width: toggleSwitch.checked ? 0 : 1
                    border.color: "#30FFFFFF"
                    Behavior on color { ColorAnimation { duration: Theme.Theme.animFast } }

                    Rectangle {
                        width: 14; height: 14; radius: 7
                        anchors.verticalCenter: parent.verticalCenter
                        x: toggleSwitch.checked ? parent.width - width - 3 : 3
                        color: toggleSwitch.checked ? "#FFFFFF" : "#B0B0B0"
                        Behavior on x { NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutCubic } }
                    }
                }

                onCheckedChanged: {
                    root.toggled = checked
                    root.toggleChanged(checked)
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2

                Text {
                    text: root.title
                    font.pixelSize: Theme.Theme.fontSizeBody
                    font.family: Theme.Theme.fontFamily
                    font.weight: Font.DemiBold
                    color: Theme.Theme.textPrimary
                }

                Text {
                    text: root.subtitle
                    visible: root.subtitle !== ""
                    font.pixelSize: Theme.Theme.fontSizeCaption
                    font.family: Theme.Theme.fontFamily
                    color: Theme.Theme.textSecondary
                }
            }
        }

        // Chevron
        Text {
            anchors.right: parent.right
            anchors.rightMargin: Theme.Theme.spacingL
            anchors.verticalCenter: parent.verticalCenter
            text: "›"
            font.pixelSize: 18
            color: Theme.Theme.textSecondary
            rotation: root.expanded ? 90 : 0
            Behavior on rotation { NumberAnimation { duration: Theme.Theme.animNormal } }
        }
    }

    // ── Content ────────────────────────────────────────────────────
    Item {
        id: contentWrapper
        anchors.top: header.bottom
        width: parent.width
        implicitHeight: contentContainer.implicitHeight + Theme.Theme.spacingL
        opacity: root.expanded ? 1 : 0
        visible: opacity > 0

        Behavior on opacity {
            NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutCubic }
        }

        // Separator
        Rectangle {
            width: parent.width - 2 * Theme.Theme.spacingL
            height: 1
            anchors.horizontalCenter: parent.horizontalCenter
            color: Theme.Theme.divider
        }

        Column {
            id: contentContainer
            anchors.top: parent.top
            anchors.topMargin: Theme.Theme.spacingM + 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: Theme.Theme.spacingL
            anchors.rightMargin: Theme.Theme.spacingL
            spacing: Theme.Theme.spacingS
        }
    }
}
