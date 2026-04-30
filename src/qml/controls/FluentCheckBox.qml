import QtQuick
import QtQuick.Controls.Basic
import "../theme" as Theme

CheckBox {
    id: control
    implicitHeight: 28
    spacing: 8

    indicator: Rectangle {
        implicitWidth: 18; implicitHeight: 18
        x: 0
        anchors.verticalCenter: parent.verticalCenter
        radius: Theme.Theme.radiusSmall
        color: control.checked ? Theme.Theme.accentDark : "transparent"
        border.width: control.checked ? 0 : 1.5
        border.color: control.hovered ? "#50FFFFFF" : "#30FFFFFF"

        Behavior on color { ColorAnimation { duration: Theme.Theme.animFast } }

        Text {
            anchors.centerIn: parent
            text: "✓"
            font.pixelSize: 12
            font.bold: true
            color: "#FFFFFF"
            opacity: control.checked ? 1 : 0
            scale: control.checked ? 1 : 0.5
            Behavior on opacity { NumberAnimation { duration: Theme.Theme.animFast } }
            Behavior on scale { NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutBack } }
        }
    }

    contentItem: Text {
        text: control.text
        font.pixelSize: Theme.Theme.fontSizeBody
        font.family: Theme.Theme.fontFamily
        color: control.enabled ? Theme.Theme.textPrimary : Theme.Theme.textDisabled
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }

    HoverHandler { cursorShape: Qt.PointingHandCursor }
}
