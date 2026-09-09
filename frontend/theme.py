"""Theme tokens for the settings window.

Canon visual language: modern Windows Settings — layer ground, white cards,
drawn state icons, one system accent. Dark and light both ship; the window
follows the Windows color scheme live.
"""

from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

LIGHT = {
    "layer": "#f3f3f3",
    "card": "#ffffff",
    "card_border": "#e5e5e5",
    "text": "#1b1b1b",
    "secondary": "#5d5d5d",
    "accent": "#0067c0",
    "accent_hover": "#1975c5",
    "accent_pressed": "#005ba1",
    "on_accent": "#ffffff",
    "field_bg": "#ffffff",
    "field_border": "#d0d0d0",
    "placeholder": "#767676",
    "hover_subtle": "rgba(0, 0, 0, 0.04)",
    "pressed_subtle": "rgba(0, 0, 0, 0.08)",
    "success": "#0f7b0f",
    "error": "#c42b1c",
    "icon_mark": "#ffffff",
}

DARK = {
    "layer": "#202020",
    "card": "#2b2b2b",
    "card_border": "#333333",
    "text": "#ffffff",
    "secondary": "#cfcfcf",
    "accent": "#4cc2ff",
    "accent_hover": "#68cbff",
    "accent_pressed": "#2e9fdc",
    "on_accent": "#000000",
    "field_bg": "#2d2d2d",
    "field_border": "#5a5a5a",
    "placeholder": "#9d9d9d",
    "hover_subtle": "rgba(255, 255, 255, 0.06)",
    "pressed_subtle": "rgba(255, 255, 255, 0.10)",
    "success": "#6cc75f",
    "error": "#ff99a4",
    "icon_mark": "#202020",
}

QSS = """
* {{
    font-family: 'Segoe UI Variable Text', 'Segoe UI', sans-serif;
    font-size: 14px;
    color: {text};
}}
QDialog {{
    background: {layer};
}}
QLabel#pageTitle {{
    font-size: 21px;
    font-weight: 600;
}}
QLabel#subtitle {{
    color: {secondary};
}}
QFrame#card {{
    background: {card};
    border: 1px solid {card_border};
    border-radius: 8px;
}}
QLabel#cardTitle {{
    font-size: 15px;
    font-weight: 600;
}}
QLabel#caption, QLabel#fieldLabel, QLabel#disclaimer {{
    color: {secondary};
    font-size: 12px;
}}
QLabel[state="ok"] {{
    color: {success};
    font-size: 13px;
}}
QLabel[state="bad"] {{
    color: {error};
    font-size: 13px;
}}
QLabel#savedLabel[state="ok"] {{
    color: {success};
}}
QLabel#savedLabel[state="bad"] {{
    color: {error};
}}
QLineEdit {{
    background: {field_bg};
    border: 1px solid {field_border};
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: {accent};
    selection-color: {on_accent};
}}
QLineEdit:hover {{
    border-color: {accent};
}}
QLineEdit:focus {{
    border: 1px solid {accent};
}}
QPushButton {{
    border-radius: 4px;
    padding: 6px 18px;
}}
QPushButton#accentButton {{
    background: {accent};
    color: {on_accent};
    border: 1px solid {accent};
    font-weight: 600;
}}
QPushButton#accentButton:hover {{
    background: {accent_hover};
    border-color: {accent_hover};
}}
QPushButton#accentButton:pressed {{
    background: {accent_pressed};
    border-color: {accent_pressed};
}}
QPushButton#accentButton:focus {{
    border: 1px solid {text};
}}
QPushButton#subtleButton {{
    background: transparent;
    color: {text};
    border: 1px solid {field_border};
}}
QPushButton#subtleButton:hover {{
    background: {hover_subtle};
}}
QPushButton#subtleButton:pressed {{
    background: {pressed_subtle};
}}
"""

_ICON_MARK_CHECK = "M6.2 10.4l2.5 2.5 5.1-5.6"
_ICON_MARK_CROSS = "M7.2 7.2l5.6 5.6M12.8 7.2l-5.6 5.6"


def state_pixmap(ok: bool, palette: dict) -> QPixmap:
    fill = palette["success"] if ok else palette["error"]
    mark = _ICON_MARK_CHECK if ok else _ICON_MARK_CROSS
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20'>"
        f"<circle cx='10' cy='10' r='9' fill='{fill}'/>"
        f"<path d='{mark}' stroke='{palette['icon_mark']}' stroke-width='1.8' "
        "fill='none' stroke-linecap='round' stroke-linejoin='round'/>"
        "</svg>"
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap
