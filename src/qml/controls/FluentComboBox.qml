import QtQuick
import QtQuick.Controls.Basic
import "../theme" as Theme

Column {
    id: root

    property string label: ""
    property alias model: combo.model
    property alias currentIndex: combo.currentIndex
    property alias currentText: combo.currentText

    signal activated(int index)

    spacing: Theme.Theme.spacingXS
    width: 200

    Text {
        text: root.label
        visible: root.label !== ""
        font.pixelSize: Theme.Theme.fontSizeCaption
        font.family: Theme.Theme.fontFamily
        color: Theme.Theme.textSecondary
    }

    ComboBox {
        id: combo
        width: parent.width
        height: 34
        onActivated: (index) => root.activated(index)

        background: Rectangle {
            radius: Theme.Theme.radiusSmall
            color: combo.pressed ? Theme.Theme.surfacePressed
                 : combo.hovered ? Theme.Theme.surfaceHover
                 : Theme.Theme.inputBackground
            border.width: 1
            border.color: combo.activeFocus ? Theme.Theme.inputBorderFocus : Theme.Theme.inputBorder

        }

        contentItem: Text {
            leftPadding: 10
            rightPadding: combo.indicator.width + 8
            text: combo.displayText
            font.pixelSize: Theme.Theme.fontSizeBody
            font.family: Theme.Theme.fontFamily
            color: Theme.Theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        indicator: Text {
            x: combo.width - width - 8
            anchors.verticalCenter: parent.verticalCenter
            text: "▾"
            font.pixelSize: 12
            color: Theme.Theme.textSecondary
        }

        popup: Popup {
            y: combo.height + 4
            width: combo.width
            implicitHeight: contentItem.implicitHeight + 8
            padding: 4

            background: Rectangle {
                radius: Theme.Theme.radiusMedium
                color: Theme.Theme.surface
                border.width: 1
                border.color: Theme.Theme.cardBorder
                layer.enabled: true
                layer.effect: null
            }

            contentItem: ListView {
                clip: true
                implicitHeight: contentHeight
                model: combo.popup.visible ? combo.delegateModel : null
                currentIndex: combo.highlightedIndex
                ScrollIndicator.vertical: ScrollIndicator {}
            }
        }

        delegate: ItemDelegate {
            width: combo.width - 8
            height: 32
            highlighted: combo.highlightedIndex === index

            background: Rectangle {
                radius: Theme.Theme.radiusSmall
                color: parent.highlighted ? Theme.Theme.surfaceHover
                     : parent.hovered ? Theme.Theme.surfaceHover
                     : "transparent"
            }

            contentItem: Text {
                text: modelData
                font.pixelSize: Theme.Theme.fontSizeBody
                font.family: Theme.Theme.fontFamily
                color: Theme.Theme.textPrimary
                verticalAlignment: Text.AlignVCenter
                leftPadding: 8
            }
        }
    }
}
