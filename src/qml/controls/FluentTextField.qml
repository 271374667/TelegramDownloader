import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../theme" as Theme

Column {
    id: root

    property alias text: field.text
    property alias placeholderText: field.placeholderText
    property alias readOnly: field.readOnly
    property string label: ""
    property string helperText: ""
    property bool hasError: false
    property alias echoMode: field.echoMode

    signal editingFinished()

    spacing: Theme.Theme.spacingXS
    width: 260

    // Label
    Text {
        text: root.label
        visible: root.label !== ""
        font.pixelSize: Theme.Theme.fontSizeCaption
        font.family: Theme.Theme.fontFamily
        color: Theme.Theme.textSecondary
    }

    // Input container
    Rectangle {
        id: container
        width: parent.width
        height: 34
        radius: Theme.Theme.radiusSmall
        color: Theme.Theme.inputBackground
        border.width: 1
        border.color: root.hasError ? Theme.Theme.error
                    : field.activeFocus ? Theme.Theme.inputBorderFocus
                    : hoverHandler.hovered ? Theme.Theme.inputBorderHover
                    : Theme.Theme.inputBorder

        Behavior on border.color { ColorAnimation { duration: Theme.Theme.animFast } }


        // Bottom accent line
        Rectangle {
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: field.activeFocus ? parent.width - 2 : 0
            height: 2
            radius: 1
            color: root.hasError ? Theme.Theme.error : Theme.Theme.accent
            Behavior on width { NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutCubic } }
        }

        TextField {
            id: field
            anchors.fill: parent
            anchors.margins: 1
            verticalAlignment: Text.AlignVCenter
            leftPadding: 10
            rightPadding: 10
            font.pixelSize: Theme.Theme.fontSizeBody
            font.family: Theme.Theme.fontFamily
            color: enabled ? Theme.Theme.textPrimary : Theme.Theme.textDisabled
            placeholderTextColor: Theme.Theme.textDisabled
            selectionColor: Theme.Theme.accentDark
            selectedTextColor: "#FFFFFF"
            background: null
            onEditingFinished: root.editingFinished()
        }

        HoverHandler { id: hoverHandler }
    }

    // Helper text
    Text {
        text: root.helperText
        visible: root.helperText !== ""
        font.pixelSize: 11
        font.family: Theme.Theme.fontFamily
        color: root.hasError ? Theme.Theme.error : Theme.Theme.textDisabled
    }
}
