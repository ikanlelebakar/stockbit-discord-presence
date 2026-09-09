"""Settings window for Stockbit Discord Presence.

Canon visual language: modern Windows Settings — layer ground, white cards,
drawn state icons, one system accent. The RPC lifecycle stays with the hidden
script; this window never opens a second Discord IPC connection.
"""

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QColor, QPalette, QGuiApplication
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from frontend import startup as startup_manager
from frontend.config import DEFAULTS, load_config, save_config
from frontend.theme import DARK, LIGHT, QSS, state_pixmap
from system_probes import is_discord_running, is_stockbit_running

REFRESH_INTERVAL_MS = 5000
CONFIRM_HOLD_MS = 1600


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("stockbit discord presence")
        self.setFixedSize(600, 770)

        self._config = load_config()
        self._dark = (
            QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
        )

        self._build_layout()
        self._setup_saved_flash()
        self._apply_theme()
        self._restore_saved_values()

        self.setTabOrder(self.details_edit, self.state_edit)
        self.setTabOrder(self.state_edit, self.large_text_edit)
        self.setTabOrder(self.large_text_edit, self.startup_box)
        self.setTabOrder(self.startup_box, self.save_button)
        self.setTabOrder(self.save_button, self.cancel_button)

        QGuiApplication.styleHints().colorSchemeChanged.connect(
            self._on_scheme_changed
        )

        self._status_timer = QTimer(self)
        self._status_timer.setInterval(REFRESH_INTERVAL_MS)
        self._status_timer.timeout.connect(self._refresh_status)
        self._status_timer.start()
        self._refresh_status()

    # --- layout ------------------------------------------------------------

    def _build_layout(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 16)
        root.setSpacing(12)

        title = QLabel("stockbit discord presence")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Shows a Discord Rich Presence while Stockbit Desktop is running."
        )
        subtitle.setObjectName("subtitle")
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(8)

        root.addWidget(self._build_status_card())
        root.addWidget(self._build_text_card())
        root.addWidget(self._build_startup_card())

        footer = QHBoxLayout()
        self.saved_label = QLabel("")
        self.saved_label.setObjectName("savedLabel")
        footer.addWidget(self.saved_label)
        footer.addStretch(1)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("subtleButton")
        self.cancel_button.clicked.connect(self.reject)
        footer.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("accentButton")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._on_save)
        footer.addWidget(self.save_button)

        root.addSpacing(4)
        root.addLayout(footer)

        disclaimer = QLabel(
            "Not affiliated with Stockbit or Discord. For personal use."
        )
        disclaimer.setObjectName("disclaimer")
        root.addWidget(disclaimer)

    def _build_status_card(self):
        card, layout = self._make_card()

        layout.addWidget(QLabel("Status"), 0, Qt.AlignmentFlag.AlignLeft)
        caption = QLabel("Checked every 5 seconds while this window is open.")
        caption.setObjectName("caption")
        layout.addWidget(caption)

        self.stockbit_icon = QLabel()
        self.stockbit_state = QLabel()
        layout.addLayout(
            self._status_row("Stockbit Desktop", self.stockbit_icon, self.stockbit_state)
        )
        self.discord_icon = QLabel()
        self.discord_state = QLabel()
        layout.addLayout(
            self._status_row("Discord", self.discord_icon, self.discord_state)
        )
        return card

    def _status_row(self, name, icon_label, state_label):
        row = QHBoxLayout()
        row.setSpacing(10)
        icon_label.setFixedSize(20, 20)
        row.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)

        text_column = QVBoxLayout()
        text_column.setSpacing(1)
        name_label = QLabel(name)
        name_label.setObjectName("rowTitle")
        text_column.addWidget(name_label)
        text_column.addWidget(state_label)
        row.addLayout(text_column, 1)
        return row

    def _build_text_card(self):
        card, layout = self._make_card()

        layout.addWidget(QLabel("Presence text"), 0, Qt.AlignmentFlag.AlignLeft)
        caption = QLabel("Shown on your Discord profile while Stockbit is running.")
        caption.setObjectName("caption")
        layout.addWidget(caption)

        self.details_edit = self._add_field(layout, "Details", DEFAULTS["details"])
        self.state_edit = self._add_field(layout, "State", DEFAULTS["state"])
        self.large_text_edit = self._add_field(
            layout, "Large text", DEFAULTS["large_text"]
        )
        return card

    def _add_field(self, layout, label, placeholder):
        label_widget = QLabel(label)
        label_widget.setObjectName("fieldLabel")
        layout.addWidget(label_widget)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setMaxLength(128)
        layout.addWidget(edit)
        return edit

    def _build_startup_card(self):
        card, layout = self._make_card()

        row = QHBoxLayout()
        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        title = QLabel("Run on Startup")
        title.setObjectName("rowTitle")
        caption = QLabel("Start the presence script when you sign in to Windows.")
        caption.setObjectName("caption")
        text_column.addWidget(title)
        text_column.addWidget(caption)
        row.addLayout(text_column, 1)

        self.startup_box = QCheckBox()
        row.addWidget(self.startup_box, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(row)
        return card

    def _make_card(self):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        return card, layout

    # --- behavior ----------------------------------------------------------

    def _collect_config(self) -> dict:
        return {
            "state": self.state_edit.text().strip(),
            "details": self.details_edit.text().strip(),
            "large_text": self.large_text_edit.text().strip(),
            "run_on_startup": self.startup_box.isChecked(),
        }

    def _on_save(self):
        config = self._collect_config()
        try:
            save_config(config)
            self._sync_startup(config["run_on_startup"])
        except OSError:
            self._flash("Save failed — check file permissions", ok=False)
            return
        self._config = config
        self._flash("Saved", ok=True)

    def _sync_startup(self, wanted: bool):
        if wanted and not startup_manager.is_enabled():
            startup_manager.enable()
        elif not wanted and startup_manager.is_enabled():
            startup_manager.disable()

    def _restore_saved_values(self):
        self.state_edit.setText(self._config["state"])
        self.details_edit.setText(self._config["details"])
        self.large_text_edit.setText(self._config["large_text"])
        self.startup_box.setChecked(self._config["run_on_startup"])

    def reject(self):
        self._restore_saved_values()
        super().reject()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def _refresh_status(self):
        palette = DARK if self._dark else LIGHT

        stockbit_ok = is_stockbit_running()
        self._set_state(self.stockbit_icon, self.stockbit_state, stockbit_ok,
                        "Detected" if stockbit_ok else "Not detected", palette)

        discord_ok = is_discord_running()
        self._set_state(self.discord_icon, self.discord_state, discord_ok,
                        "Running" if discord_ok else "Not running", palette)

    def _set_state(self, icon_label, state_label, ok, text, palette):
        icon_label.setPixmap(state_pixmap(ok, palette))
        state_label.setProperty("state", "ok" if ok else "bad")
        state_label.setText(text)
        state_label.style().unpolish(state_label)
        state_label.style().polish(state_label)

    # --- theme -------------------------------------------------------------

    def _apply_theme(self):
        palette = DARK if self._dark else LIGHT
        self.setStyleSheet(QSS.format(**palette))
        self._apply_placeholder_color(palette)
        self._refresh_status()

    def _apply_placeholder_color(self, palette):
        color = QColor(palette["placeholder"])
        for edit in (self.state_edit, self.details_edit, self.large_text_edit):
            edit_palette = edit.palette()
            edit_palette.setColor(QPalette.ColorRole.PlaceholderText, color)
            edit.setPalette(edit_palette)

    def _on_scheme_changed(self, scheme):
        self._dark = scheme == Qt.ColorScheme.Dark
        self._apply_theme()

    # --- saved confirmation (the one authored motion) ----------------------

    def _setup_saved_flash(self):
        self._saved_effect = QGraphicsOpacityEffect(self.saved_label)
        self._saved_effect.setOpacity(0.0)
        self.saved_label.setGraphicsEffect(self._saved_effect)

        self._saved_in = QPropertyAnimation(self._saved_effect, b"opacity", self)
        self._saved_in.setDuration(200)
        self._saved_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._saved_in.setStartValue(0.0)
        self._saved_in.setEndValue(1.0)

        self._saved_out = QPropertyAnimation(self._saved_effect, b"opacity", self)
        self._saved_out.setDuration(400)
        self._saved_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._saved_out.setStartValue(1.0)
        self._saved_out.setEndValue(0.0)

    def _flash(self, text, ok):
        self._saved_in.stop()
        self._saved_out.stop()

        self.saved_label.setProperty("state", "ok" if ok else "bad")
        self.saved_label.setText(text)
        self.saved_label.style().unpolish(self.saved_label)
        self.saved_label.style().polish(self.saved_label)

        self._saved_effect.setOpacity(0.0)
        self._saved_in.start()
        QTimer.singleShot(200 + CONFIRM_HOLD_MS, self._begin_fade_out)

    def _begin_fade_out(self):
        if self._saved_effect.opacity() >= 1.0:
            self._saved_out.start()
