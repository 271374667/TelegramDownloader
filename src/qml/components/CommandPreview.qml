import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../theme" as Theme
import "../controls"

/* Command preview bar — sits at the bottom of the main window. */
Rectangle {
    id: root
    color: Theme.Theme.surface
    border.width: 0

    // Top divider line
    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 1
        color: Theme.Theme.divider
    }

    implicitHeight: col.implicitHeight + 2 * Theme.Theme.spacingM

    Column {
        id: col
        anchors.fill: parent
        anchors.margins: Theme.Theme.spacingM
        spacing: Theme.Theme.spacingS

        // Preview label
        Text {
            text: "命令预览"
            font.pixelSize: Theme.Theme.fontSizeCaption
            font.family: Theme.Theme.fontFamily
            color: Theme.Theme.textSecondary
        }

        // Preview box
        Rectangle {
            width: parent.width
            height: Math.min(Math.max(previewText.implicitHeight + 16, 40), 120)
            color: Theme.Theme.inputBackground
            radius: Theme.Theme.radiusSmall
            border.width: 1
            border.color: Theme.Theme.cardBorder

            Behavior on height {
                NumberAnimation { duration: Theme.Theme.animNormal }
            }

            Flickable {
                id: previewFlickable
                anchors.fill: parent
                anchors.margins: 8
                contentWidth: previewText.implicitWidth
                contentHeight: previewText.implicitHeight
                clip: true
                flickableDirection: Flickable.AutoFlickIfNeeded

                TextEdit {
                    id: previewText
                    width: previewFlickable.width
                    text: appVM.commandPreview || "配置完成后将在此预览命令..."
                    font.pixelSize: 12
                    font.family: Theme.Theme.fontFamilyMono
                    color: appVM.commandPreview ? Theme.Theme.accent : Theme.Theme.textDisabled
                    readOnly: true
                    selectByMouse: true
                    wrapMode: Text.WrapAnywhere
                    selectionColor: Theme.Theme.accentDark

                    onTextChanged: {
                        // Brief flash effect to indicate the preview changed
                        flashAnim.restart()
                    }
                }
            }

            // Subtle flash overlay to indicate preview updated
            Rectangle {
                id: flashOverlay
                anchors.fill: parent
                radius: parent.radius
                color: Theme.Theme.accent
                opacity: 0

                SequentialAnimation {
                    id: flashAnim
                    NumberAnimation { target: flashOverlay; property: "opacity"; to: 0.08; duration: 80 }
                    NumberAnimation { target: flashOverlay; property: "opacity"; to: 0; duration: 300 }
                }
            }
        }

        // Action buttons
        RowLayout {
            width: parent.width
            spacing: Theme.Theme.spacingS

            // TDL status
            Text {
                text: {
                    switch (appVM.tdlStatus) {
                        case "ready": return "✓ TDL 就绪";
                        case "not_logged_in": return "⚠ 未登录";
                        case "no_tdl": return "✕ 未找到 tdl.exe";
                        default: return "";
                    }
                }
                font.pixelSize: Theme.Theme.fontSizeCaption
                font.family: Theme.Theme.fontFamily
                color: {
                    switch (appVM.tdlStatus) {
                        case "ready": return Theme.Theme.success;
                        case "not_logged_in": return Theme.Theme.warning;
                        default: return Theme.Theme.error;
                    }
                }
                Layout.fillWidth: true
            }

            FluentButton {
                text: "生成 BAT"
                variant: "standard"
                iconText: "📄"
                enabled: urlModel.count > 0
                onClicked: appVM.generateBatch()
            }

            FluentButton {
                text: "运行下载"
                variant: "accent"
                iconText: "▶"
                enabled: urlModel.count > 0
                onClicked: appVM.executeBatch()
            }
        }
    }
}
