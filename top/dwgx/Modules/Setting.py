# top.dwgx.Modules.Setting

import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QColorDialog, QGridLayout, QMessageBox, QListWidget, QListWidgetItem,
    QApplication
)
from top.dwgx.Manager.ConfigManager import ConfigManager
from top.dwgx.utils.IconImageUtils import icon_image_utils

class Setting(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设置")
        self.resize(800, 600)

        self.config_manager = ConfigManager()

        main_layout = QVBoxLayout(self)

        # 背景图片选择
        bg_layout = QVBoxLayout()
        bg_label = QLabel("选择背景图片:")
        bg_layout.addWidget(bg_label)

        # List widget to display background images
        self.bg_list_widget = QListWidget()
        self.bg_list_widget.setIconSize(QSize(64, 64))
        self.bg_list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.bg_list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.bg_list_widget.setSpacing(10)
        self.bg_list_widget.setMovement(QListWidget.Movement.Static)
        self.bg_list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.populate_background_images()

        bg_layout.addWidget(self.bg_list_widget)
        main_layout.addLayout(bg_layout)

        self.bg_list_widget.currentItemChanged.connect(self.select_background_image)

        palette_layout = QGridLayout()
        palette_label = QLabel("选择文本颜色:")
        palette_layout.addWidget(palette_label, 0, 0)

        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.select_text_color)
        palette_layout.addWidget(self.color_button, 0, 1)

        main_layout.addLayout(palette_layout)

        self.apply_button = QPushButton("应用设置")
        self.apply_button.clicked.connect(self.apply_settings)
        main_layout.addWidget(self.apply_button)

        self.reset_button = QPushButton("恢复默认设置")
        self.reset_button.clicked.connect(self.reset_settings)
        main_layout.addWidget(self.reset_button)

        self.setLayout(main_layout)

        self.load_settings()

    def populate_background_images(self):
        images = icon_image_utils.get_background_images()
        for image_path in images:
            icon = QIcon(image_path)
            item = QListWidgetItem(icon, os.path.basename(image_path))
            item.setData(Qt.ItemDataRole.UserRole, image_path)
            self.bg_list_widget.addItem(item)

    def select_background_image(self, current):
        if current:
            image_path = current.data(Qt.ItemDataRole.UserRole)
            scaling_method = "保持比例"  #
            main_panel = self.get_main_panel()
            if main_panel:
                icon_image_utils.update_background(main_panel, image_path, scaling_method)
                self.config_manager.set("ui_settings", "background_image", image_path)
                QMessageBox.information(self, "成功", f"背景图片已更改为: {os.path.basename(image_path)}")
            else:
                QMessageBox.critical(self, "错误", "无法找到主窗口实例。")

    def select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            app = QApplication.instance()
            app.setStyleSheet(f"QWidget {{ color: {color.name()}; }}")
            self.config_manager.set("ui_settings", "text_color", color.name())
            QMessageBox.information(self, "成功", f"文本颜色已更改为: {color.name()}")

    def apply_settings(self):
        QMessageBox.information(self, "信息", "设置已应用。")

    def reset_settings(self):
        try:
            self.config_manager.set("ui_settings", "background_image", "")
            main_panel = self.get_main_panel()
            if main_panel:
                if main_panel in icon_image_utils.background_config:
                    del icon_image_utils.background_config[main_panel]
                    main_panel.removeEventFilter(icon_image_utils)
                main_panel.setPalette(main_panel.style().standardPalette())
                main_panel.setAutoFillBackground(False)
            self.config_manager.set("ui_settings", "text_color", "#000000")  # 默认黑色
            QApplication.instance().setStyleSheet("")

            self.bg_list_widget.clearSelection()
            self.color_button.setStyleSheet("")

            QMessageBox.information(self, "成功", "已恢复默认设置。")
            print("已恢复默认设置.")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"恢复默认设置失败: {e}")
            print(f"恢复默认设置失败: {e}")

    def get_main_panel(self):
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'navigation_list'):
                return parent
            parent = parent.parent()
        return None

    def load_settings(self):
        bg_image = self.config_manager.get("ui_settings", "background_image", "")
        if bg_image and os.path.exists(bg_image):
            for index in range(self.bg_list_widget.count()):
                item = self.bg_list_widget.item(index)
                if item.data(Qt.ItemDataRole.UserRole) == bg_image:
                    self.bg_list_widget.setCurrentItem(item)
                    break

        text_color = self.config_manager.get("ui_settings", "text_color", "#000000")
        if text_color:
            app = QApplication.instance()
            app.setStyleSheet(f"QWidget {{ color: {text_color}; }}")
            self.color_button.setStyleSheet(f"background-color: {text_color};")
