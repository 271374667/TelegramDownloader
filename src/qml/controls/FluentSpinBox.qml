import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../theme" as Theme

Column {
    id: root

    property string label: ""
    property alias value: spin.value
    property alias from: spin.from
    property alias to: spin.to
    property alias stepSize: spin.stepSize

    signal valueModified()

    spacing: Theme.Theme.spacingXS
    width: 160

    Text {
        text: root.label
        visible: root.label !== ""
        font.pixelSize: Theme.Theme.fontSizeCaption
        font.family: Theme.Theme.fontFamily
        color: Theme.Theme.textSecondary
    }

    SpinBox {
        id: spin
        width: parent.width
        height: 34
        from: 1; to: 999; stepSize: 1
        editable: true
        onValueModified: root.valueModified()

        background: Rectangle {
            radius: Theme.Theme.radiusSmall
            color: Theme.Theme.inputBackground
            border.width: 1
            border.color: spin.activeFocus ? Theme.Theme.inputBorderFocus : Theme.Theme.inputBorder

        }

        contentItem: TextInput {
            text: spin.textFromValue(spin.value, spin.locale)
            font.pixelSize: Theme.Theme.fontSizeBody
            font.family: Theme.Theme.fontFamily
            color: Theme.Theme.textPrimary
            selectionColor: Theme.Theme.accentDark
            selectedTextColor: "#FFFFFF"
            horizontalAlignment: Qt.AlignHCenter
            verticalAlignment: Qt.AlignVCenter
            readOnly: !spin.editable
            validator: spin.validator
            inputMethodHints: Qt.ImhFormattedNumbersOnly
        }

        up.indicator: Rectangle {
            x: parent.width - width
            height: parent.height
            width: 28
            radius: Theme.Theme.radiusSmall
            color: spin.up.pressed ? Theme.Theme.surfacePressed
                 : spin.up.hovered ? Theme.Theme.surfaceHover
                 : "transparent"
            Text {
                anchors.centerIn: parent
                text: "+"
                font.pixelSize: 16
                color: Theme.Theme.textPrimary
            }
        }

        down.indicator: Rectangle {
            x: 0
            height: parent.height
            width: 28
            radius: Theme.Theme.radiusSmall
            color: spin.down.pressed ? Theme.Theme.surfacePressed
                 : spin.down.hovered ? Theme.Theme.surfaceHover
                 : "transparent"
            Text {
                anchors.centerIn: parent
                text: "−"
                font.pixelSize: 16
                color: Theme.Theme.textPrimary
            }
        }
    }
}
