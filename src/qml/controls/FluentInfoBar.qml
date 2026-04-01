import QtQuick
import "../theme" as Theme

Rectangle {
    id: root

    property string title: ""
    property string message: ""
    property string severity: "info"   // "info" | "success" | "warning" | "error"
    property bool showClose: true

    signal closed()

    visible: opacity > 0
    width: parent ? parent.width : 400
    height: 44
    radius: Theme.Theme.radiusSmall

    // Opaque background base so content below doesn't bleed through
    color: Theme.Theme.dark ? "#2D2D2D" : "#FAFAFA"

    border.width: 1
    border.color: {
        switch (severity) {
            case "success": return Theme.Theme.success;
            case "warning": return Theme.Theme.warning;
            case "error":   return Theme.Theme.error;
            default:        return Theme.Theme.info;
        }
    }

    // Tinted severity overlay
    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: {
            switch (root.severity) {
                case "success": return Qt.rgba(0.06, 0.48, 0.06, 0.15);
                case "warning": return Qt.rgba(0.62, 0.36, 0, 0.15);
                case "error":   return Qt.rgba(0.77, 0.17, 0.11, 0.15);
                default:        return Qt.rgba(0.38, 0.81, 1.0, 0.10);
            }
        }
    }

    // Drop shadow for elevation
    Rectangle {
        anchors.fill: parent
        anchors.margins: -1
        z: -1
        radius: parent.radius + 1
        color: "transparent"
        border.width: 1
        border.color: Theme.Theme.dark ? "#40000000" : "#20000000"
    }

    opacity: 0

    Behavior on opacity {
        NumberAnimation { duration: Theme.Theme.animNormal; easing.type: Easing.OutCubic }
    }

    Row {
        anchors.left: parent.left; anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        // Severity icon
        Text {
            font.pixelSize: 16
            text: {
                switch (root.severity) {
                    case "success": return "✓";
                    case "warning": return "⚠";
                    case "error":   return "✕";
                    default:        return "ℹ";
                }
            }
            color: root.border.color
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.title
            font.pixelSize: Theme.Theme.fontSizeBody
            font.family: Theme.Theme.fontFamily
            font.weight: Font.DemiBold
            color: Theme.Theme.textPrimary
            visible: root.title !== ""
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: root.message
            font.pixelSize: Theme.Theme.fontSizeBody
            font.family: Theme.Theme.fontFamily
            color: Theme.Theme.textSecondary
            anchors.verticalCenter: parent.verticalCenter
            elide: Text.ElideRight
            width: root.width - 120
        }
    }

    // Close button
    Text {
        anchors.right: parent.right; anchors.rightMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        text: "✕"
        font.pixelSize: 12
        color: closeMa.containsMouse ? Theme.Theme.textPrimary : Theme.Theme.textSecondary
        visible: root.showClose
        MouseArea {
            id: closeMa; anchors.fill: parent; anchors.margins: -6
            hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: root.hide()
        }
    }

    // Timer for auto-hide
    Timer {
        id: autoHide
        interval: 4000
        onTriggered: root.hide()
    }

    function show(title, message, severity) {
        root.title = title || "";
        root.message = message || "";
        root.severity = severity || "info";
        root.opacity = 1;
        autoHide.restart();
    }

    function hide() {
        root.opacity = 0;
        root.closed();
    }
}
