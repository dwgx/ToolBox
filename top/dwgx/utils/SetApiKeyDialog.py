# utils/SetApiKeyDialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt


class SetApiKeyDialog(QDialog):
    def __init__(self, config_manager, logger, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logger
        self.setWindowTitle("设置API密钥")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.secret_id_input = QLineEdit()
        self.secret_id_input.setText(self.config_manager.get("translation", "SECRET_ID", ""))
        form_layout.addRow("SECRET_ID:", self.secret_id_input)

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.secret_key_input.setText(self.config_manager.get("translation", "SECRET_KEY", ""))
        form_layout.addRow("SECRET_KEY:", self.secret_key_input)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_api_keys)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_api_keys(self):
        secret_id = self.secret_id_input.text().strip()
        secret_key = self.secret_key_input.text().strip()

        if not secret_id or not secret_key:
            QMessageBox.warning(self, "警告", "SECRET_ID 和 SECRET_KEY 不能为空。")
            return

        self.config_manager.set("translation", "SECRET_ID", secret_id)
        self.config_manager.set("translation", "SECRET_KEY", secret_key)
        self.logger.info("API密钥已更新。")
        self.accept()
