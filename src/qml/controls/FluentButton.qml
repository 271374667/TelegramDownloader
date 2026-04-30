import QtQuick
import QtQuick.Controls.Basic
import "../theme" as Theme

Button {
    id: control

    property string variant: "standard"   // "accent" | "standard" | "subtle" | "danger" | "success"
    property string iconText: ""          // Unicode / emoji icon before text

    implicitWidth: Math.max(80, contentRow.implicitWidth + 28)
    implicitHeight: 34
    padding: 0
    topInset: 0; bottomInset: 0; leftInset: 0; rightInset: 0

    background: Rectangle {
        radius: Theme.Theme.radiusSmall
        border.width: variant === "subtle" || variant === "accent" ? 0 : 1
        border.color: "#12FFFFFF"
        color: bgColor

        property color bgColor: {
            if (!control.enabled) return Theme.Theme.btnStandard;
            switch (control.variant) {
                case "accent":
                    return control.pressed ? Theme.Theme.btnAccentPressed
                         : control.hovered ? Theme.Theme.btnAccentHover
                         : Theme.Theme.btnAccent;
                case "subtle":
                    return control.pressed ? Theme.Theme.btnSubtlePressed
                         : control.hovered ? Theme.Theme.btnSubtleHover
                         : Theme.Theme.btnSubtle;
                case "danger":
                    return control.pressed ? Theme.Theme.btnDangerPressed
                         : control.hovered ? Theme.Theme.btnDangerHover
                         : Theme.Theme.btnDanger;
                case "success":
                    return control.pressed ? Theme.Theme.btnSuccessPressed
                         : control.hovered ? Theme.Theme.btnSuccessHover
                         : Theme.Theme.btnSuccess;
                default:
                    return control.pressed ? Theme.Theme.btnStandardPressed
                         : control.hovered ? Theme.Theme.btnStandardHover
                         : Theme.Theme.btnStandard;
            }
        }

        Behavior on color { ColorAnimation { duration: Theme.Theme.animFast } }
    }

    contentItem: Item {
        implicitWidth: contentRow.implicitWidth
        implicitHeight: contentRow.implicitHeight

        Row {
            id: contentRow
            spacing: control.iconText ? 6 : 0
            anchors.centerIn: parent

            property color fgColor: {
                if (!control.enabled) return Theme.Theme.textDisabled;
                if (control.variant === "accent" || control.variant === "danger" || control.variant === "success")
                    return Theme.Theme.textOnAccent;
                return Theme.Theme.textPrimary;
            }

            Text {
                text: control.iconText
                visible: control.iconText !== ""
                font.pixelSize: Theme.Theme.fontSizeBody
                color: contentRow.fgColor
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: control.text
                font.pixelSize: Theme.Theme.fontSizeBody
                font.family: Theme.Theme.fontFamily
                color: contentRow.fgColor
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    HoverHandler { cursorShape: Qt.PointingHandCursor }
}
