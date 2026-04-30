pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls.FluentWinUI3
import QtQuick.Layouts
import QtQuick.Window
import "../theme" as Theme

Item {
    id: root

    property var window: Window.window
    property url logoSource
    property string appName: ""
    property url minimizeIconSource
    property url maximizeIconSource
    property url restoreIconSource
    property url closeIconSource
    property int barHeight: 40
    property int resizeMargin: 5
    property int resizeCornerSize: 10

    readonly property bool isMaximized: root.window && root.window.visibility === Window.Maximized
    readonly property bool hasLogo: hasIcon(root.logoSource)
    readonly property bool canResize: root.window
        && root.window.visibility !== Window.Maximized
        && root.window.visibility !== Window.FullScreen
    readonly property color barColor: "#252525"
    readonly property color separatorColor: "#3a3a3a"
    readonly property color textColor: "#f5f5f5"
    readonly property color secondaryTextColor: "#d7d7d7"
    readonly property color logoBadgeColor: "#313131"
    readonly property color hoverColor: "#353535"
    readonly property color pressedColor: "#454545"
    readonly property color closeHoverColor: "#c42b1c"
    readonly property color closePressedColor: "#a52619"
    readonly property string minimizeGlyph: "\uE921"
    readonly property string maximizeGlyph: "\uE922"
    readonly property string restoreGlyph: "\uE923"
    readonly property string closeGlyph: "\uE8BB"

    function hasIcon(iconSource) {
        return iconSource && iconSource.toString() !== ""
    }

    function toggleMaximized() {
        if (!root.window) {
            return
        }

        if (root.window.visibility === Window.Maximized) {
            root.window.showNormal()
        } else {
            root.window.showMaximized()
        }
    }

    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: root.barHeight
        color: root.barColor
    }

    Rectangle {
        anchors.top: parent.top
        anchors.topMargin: root.barHeight - 1
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: root.separatorColor
    }

    RowLayout {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: root.barHeight
        spacing: 0

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 10

                Rectangle {
                    visible: root.hasLogo
                    Layout.alignment: Qt.AlignVCenter
                    Layout.preferredWidth: 26
                    Layout.preferredHeight: 26
                    radius: 7
                    color: root.logoBadgeColor

                    Image {
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        source: root.logoSource
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        antialiasing: true
                    }
                }

                Label {
                    Layout.alignment: Qt.AlignVCenter
                    text: root.appName
                    color: root.textColor
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                }

                Item {
                    Layout.fillWidth: true
                }
            }

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton

                onPositionChanged: function(mouse) {
                    if ((mouse.buttons & Qt.LeftButton) && root.window) {
                        root.window.startSystemMove()
                    }
                }

                onDoubleClicked: function(mouse) {
                    if (mouse.button === Qt.LeftButton) {
                        root.toggleMaximized()
                    }
                }
            }
        }

        RowLayout {
            Layout.preferredWidth: implicitWidth
            Layout.fillHeight: true
            spacing: 0

            WindowControlButton {
                glyph: root.minimizeGlyph
                onClicked: {
                    if (root.window) {
                        root.window.showMinimized()
                    }
                }
            }

            WindowControlButton {
                glyph: root.isMaximized ? root.restoreGlyph : root.maximizeGlyph
                onClicked: root.toggleMaximized()
            }

            WindowControlButton {
                glyph: root.closeGlyph
                isCloseButton: true
                onClicked: {
                    if (root.window) {
                        root.window.close()
                    }
                }
            }
        }
    }

    component WindowControlButton: Button {
        id: controlButton

        property string glyph
        property bool isCloseButton: false
        readonly property color iconColor: controlButton.isCloseButton && (controlButton.hovered || controlButton.down)
            ? "#ffffff"
            : root.secondaryTextColor

        Layout.preferredWidth: 46
        Layout.preferredHeight: root.barHeight
        Layout.fillHeight: true
        visible: controlButton.glyph !== ""
        padding: 0
        hoverEnabled: true
        flat: true

        contentItem: Text {
            text: controlButton.glyph
            color: controlButton.iconColor
            font.family: "Segoe MDL2 Assets"
            font.pixelSize: 10
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            renderType: Text.NativeRendering
        }

        background: Rectangle {
            color: {
                if (controlButton.down) {
                    return controlButton.isCloseButton ? root.closePressedColor : root.pressedColor
                }

                if (controlButton.hovered) {
                    return controlButton.isCloseButton ? root.closeHoverColor : root.hoverColor
                }

                return "transparent"
            }
        }
    }

    component ResizeHandle: MouseArea {
        required property int resizeEdges

        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        enabled: root.canResize

        onPressed: function(mouse) {
            if (mouse.button === Qt.LeftButton && root.window) {
                root.window.startSystemResize(resizeEdges)
            }
        }
    }

    ResizeHandle {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: root.resizeMargin
        resizeEdges: Qt.LeftEdge
        cursorShape: Qt.SizeHorCursor
    }

    ResizeHandle {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: root.resizeMargin
        resizeEdges: Qt.RightEdge
        cursorShape: Qt.SizeHorCursor
    }

    ResizeHandle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: root.resizeMargin
        resizeEdges: Qt.TopEdge
        cursorShape: Qt.SizeVerCursor
    }

    ResizeHandle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: root.resizeMargin
        resizeEdges: Qt.BottomEdge
        cursorShape: Qt.SizeVerCursor
    }

    ResizeHandle {
        anchors.top: parent.top
        anchors.left: parent.left
        width: root.resizeCornerSize
        height: root.resizeCornerSize
        resizeEdges: Qt.TopEdge | Qt.LeftEdge
        cursorShape: Qt.SizeFDiagCursor
    }

    ResizeHandle {
        anchors.top: parent.top
        anchors.right: parent.right
        width: root.resizeCornerSize
        height: root.resizeCornerSize
        resizeEdges: Qt.TopEdge | Qt.RightEdge
        cursorShape: Qt.SizeBDiagCursor
    }

    ResizeHandle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: root.resizeCornerSize
        height: root.resizeCornerSize
        resizeEdges: Qt.BottomEdge | Qt.LeftEdge
        cursorShape: Qt.SizeBDiagCursor
    }

    ResizeHandle {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: root.resizeCornerSize
        height: root.resizeCornerSize
        resizeEdges: Qt.BottomEdge | Qt.RightEdge
        cursorShape: Qt.SizeFDiagCursor
    }
}
