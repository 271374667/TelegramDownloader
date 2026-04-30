pragma Singleton
import QtQuick

QtObject {
    // ══════════════════════════════════════════════════════════════
    //  WinUI 3 / Fluent 2  —  Dark theme only
    // ══════════════════════════════════════════════════════════════

    // ── Background / Layer / Surface ───────────────────────────────
    readonly property color background:       "#202020"
    readonly property color surface:          "#282828"
    readonly property color surfaceHover:     "#323232"
    readonly property color surfacePressed:   "#2E2E2E"
    readonly property color cardBackground:   "#2C2C2C"
    readonly property color cardBorder:       "#1AFFFFFF"

    // ── Control fill / stroke ──────────────────────────────────────
    readonly property color inputBackground:  "#2C2C2C"
    readonly property color inputBorder:      "#15FFFFFF"
    readonly property color inputBorderHover: "#20FFFFFF"
    readonly property color inputBorderFocus: "#60CDFF"

    // ── Accent ─────────────────────────────────────────────────────
    readonly property color accent:           "#60CDFF"
    readonly property color accentDark:       "#0078D4"
    readonly property color accentLight:      "#99ECFF"

    // ── Text ───────────────────────────────────────────────────────
    readonly property color textPrimary:      "#FFFFFF"
    readonly property color textSecondary:    "#C5C5C5"
    readonly property color textTertiary:     "#9A9A9A"
    readonly property color textDisabled:     "#A0A0A0"
    readonly property color textOnAccent:     "#FFFFFF"

    // ── Divider ────────────────────────────────────────────────────
    readonly property color divider:          "#15FFFFFF"

    // ── Status ─────────────────────────────────────────────────────
    readonly property color success:          "#6CCB5F"
    readonly property color warning:          "#FCE100"
    readonly property color error:            "#FF99A4"
    readonly property color info:             "#60CDFF"

    // ── Button variants ────────────────────────────────────────────
    //  AccentFill
    readonly property color btnAccent:          "#0078D4"
    readonly property color btnAccentHover:     "#0E84DE"
    readonly property color btnAccentPressed:   "#005EA6"
    //  StandardFill
    readonly property color btnStandard:        "#30FFFFFF"
    readonly property color btnStandardHover:   "#1AFFFFFF"
    readonly property color btnStandardPressed: "#12FFFFFF"
    //  SubtleFill
    readonly property color btnSubtle:          "transparent"
    readonly property color btnSubtleHover:     "#0FFFFFFF"
    readonly property color btnSubtlePressed:   "#0AFFFFFF"
    //  Danger
    readonly property color btnDanger:          "#C42B1C"
    readonly property color btnDangerHover:     "#D83B2B"
    readonly property color btnDangerPressed:   "#A41F13"
    //  Success
    readonly property color btnSuccess:         "#0F7B0F"
    readonly property color btnSuccessHover:    "#148A14"
    readonly property color btnSuccessPressed:  "#0B5E0B"

    // ── Typography ─────────────────────────────────────────────────
    readonly property string fontFamily: "Source Han Sans SC"
    readonly property string fontFamilyMono: "Consolas"
    readonly property int fontSizeCaption:  12
    readonly property int fontSizeBody:     14
    readonly property int fontSizeSubtitle: 16
    readonly property int fontSizeTitle:    20
    readonly property int fontSizeDisplay:  28

    // ── Spacing / Radius ───────────────────────────────────────────
    readonly property int radiusSmall:   4
    readonly property int radiusMedium:  8
    readonly property int radiusLarge:  12
    readonly property int spacingXS:     4
    readonly property int spacingS:      8
    readonly property int spacingM:     12
    readonly property int spacingL:     16
    readonly property int spacingXL:    24

    // ── Animation ──────────────────────────────────────────────────
    readonly property int animFast:     83
    readonly property int animNormal:  167
    readonly property int animSlow:    250
}
