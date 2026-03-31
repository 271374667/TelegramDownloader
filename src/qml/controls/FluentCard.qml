import QtQuick
import "../theme" as Theme

Rectangle {
    id: root

    property string title: ""
    default property alias content: contentCol.data

    color: Theme.Theme.cardBackground
    border.width: 1
    border.color: Theme.Theme.cardBorder
    radius: Theme.Theme.radiusMedium

    // Fluent 2: subtle top-highlight for layered depth
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        radius: parent.radius
        color: Theme.Theme.dark ? "#08FFFFFF" : "#15FFFFFF"
    }

    implicitWidth: 400
    implicitHeight: innerCol.implicitHeight + 2 * Theme.Theme.spacingL

    Column {
        id: innerCol
        anchors.fill: parent
        anchors.margins: Theme.Theme.spacingL
        spacing: Theme.Theme.spacingM

        Text {
            text: root.title
            visible: root.title !== ""
            font.pixelSize: Theme.Theme.fontSizeSubtitle
            font.family: Theme.Theme.fontFamily
            font.weight: Font.DemiBold
            color: Theme.Theme.textPrimary
        }

        Column {
            id: contentCol
            width: parent.width
            spacing: Theme.Theme.spacingS
        }
    }
}

