import QtQuick
import QtQuick.Controls.Basic
import "../theme" as Theme

Switch {
    id: control

    implicitHeight: 28
    implicitWidth: textItem.implicitWidth + indicator.width + spacing + 4
    spacing: 10

    indicator: Rectangle {
        implicitWidth: 40; implicitHeight: 20
        anchors.verticalCenter: parent.verticalCenter
        radius: height / 2
        color: control.checked ? Theme.Theme.accentDark : "#4D4D4D"
        border.width: control.checked ? 0 : 1
        border.color: "#30FFFFFF"

        Behavior on color { ColorAnimation { duration: Theme.Theme.animFast } }

        Rectangle {
            id: thumb
            width: 14; height: 14
            radius: width / 2
            anchors.verticalCenter: parent.verticalCenter
            x: control.checked ? parent.width - width - 3 : 3
            color: control.checked ? "#FFFFFF" : "#B0B0B0"

            Behavior on x { NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutCubic } }
        }
    }

    contentItem: Text {
        id: textItem
        text: control.text
        font.pixelSize: Theme.Theme.fontSizeBody
        font.family: Theme.Theme.fontFamily
        color: control.enabled ? Theme.Theme.textPrimary : Theme.Theme.textDisabled
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }

    HoverHandler { cursorShape: Qt.PointingHandCursor }
}
