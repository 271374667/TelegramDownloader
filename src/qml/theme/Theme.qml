pragma Singleton
import QtQuick

QtObject {
    // ══════════════════════════════════════════════════════════════
    //  WinUI 3 / Fluent 2  —  Dark & Light theme support
    // ══════════════════════════════════════════════════════════════

    property bool dark: true   // toggle to switch themes

    // ── Background / Layer / Surface ───────────────────────────────
    property color background:       dark ? "#202020"   : "#F3F3F3"
    property color surface:          dark ? "#282828"   : "#FAFAFA"
    property color surfaceHover:     dark ? "#323232"   : "#E8E8E8"
    property color surfacePressed:   dark ? "#2E2E2E"   : "#E0E0E0"
    property color cardBackground:   dark ? "#2C2C2C"   : "#FFFFFF"
    property color cardBorder:       dark ? "#1AFFFFFF" : "#0F000000"

    // ── Control fill / stroke ──────────────────────────────────────
    property color inputBackground:  dark ? "#2C2C2C"   : "#FFFFFF"
    property color inputBorder:      dark ? "#15FFFFFF"  : "#0F000000"
    property color inputBorderHover: dark ? "#20FFFFFF"  : "#18000000"
    property color inputBorderFocus: "#60CDFF"

    // ── Accent ─────────────────────────────────────────────────────
    property color accent:           dark ? "#60CDFF"   : "#005FB8"
    property color accentDark:       "#0078D4"
    property color accentLight:      dark ? "#99ECFF"   : "#0067C0"

    // ── Text ───────────────────────────────────────────────────────
    property color textPrimary:      dark ? "#FFFFFF"   : "#1A1A1A"
    property color textSecondary:    dark ? "#C5C5C5"   : "#616161"
    property color textTertiary:     dark ? "#9A9A9A"   : "#8A8A8A"
    property color textDisabled:     dark ? "#A0A0A0"   : "#888888"
    property color textOnAccent:     "#FFFFFF"

    // ── Divider ────────────────────────────────────────────────────
    property color divider:          dark ? "#15FFFFFF"  : "#0F000000"

    // ── Status ─────────────────────────────────────────────────────
    property color success:          dark ? "#6CCB5F"   : "#0F7B0F"
    property color warning:          dark ? "#FCE100"   : "#9D5D00"
    property color error:            dark ? "#FF99A4"   : "#C42B1C"
    property color info:             dark ? "#60CDFF"   : "#005FB8"

    // ── Button variants ────────────────────────────────────────────
    //  AccentFill
    property color btnAccent:          "#0078D4"
    property color btnAccentHover:     "#0E84DE"
    property color btnAccentPressed:   "#005EA6"
    //  StandardFill
    property color btnStandard:        dark ? "#30FFFFFF" : "#0A000000"
    property color btnStandardHover:   dark ? "#1AFFFFFF" : "#12000000"
    property color btnStandardPressed: dark ? "#12FFFFFF" : "#08000000"
    //  SubtleFill
    property color btnSubtle:          "transparent"
    property color btnSubtleHover:     dark ? "#0FFFFFFF" : "#08000000"
    property color btnSubtlePressed:   dark ? "#0AFFFFFF" : "#05000000"
    //  Danger
    property color btnDanger:          "#C42B1C"
    property color btnDangerHover:     "#D83B2B"
    property color btnDangerPressed:   "#A41F13"
    //  Success
    property color btnSuccess:         "#0F7B0F"
    property color btnSuccessHover:    "#148A14"
    property color btnSuccessPressed:  "#0B5E0B"

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
