import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QColorDialog, QGridLayout, QMessageBox,
                             QListWidget, QListWidgetItem, QApplication, QComboBox, QFileDialog, QStyleFactory)
from Manager.ConfigManager import ConfigManager
from utils.IconImageUtils import icon_image_utils


class Setting(QWidget):
    def __init__(self, main_panel):
        super().__init__()
        self.setWindowTitle("设置")

        self.resize(800, 600)
        self.main_panel = main_panel
        self.config_manager = ConfigManager()

        main_layout = QVBoxLayout(self)


        ui_layout = QVBoxLayout()
        ui_label = QLabel("选择 UI 风格:")
        ui_layout.addWidget(ui_label)

        self.ui_style_combo_box = QComboBox()
        available_styles = QStyleFactory.keys()
        self.ui_style_combo_box.addItems(available_styles + ["自定义样式"])
        self.ui_style_combo_box.currentIndexChanged.connect(self.switch_ui_style)
        ui_layout.addWidget(self.ui_style_combo_box)
        main_layout.addLayout(ui_layout)

        self.custom_style_button = QPushButton("选择自定义样式文件")
        self.custom_style_button.clicked.connect(self.select_custom_style)
        main_layout.addWidget(self.custom_style_button)


        bg_layout = QVBoxLayout()
        bg_label = QLabel("选择背景图片:")
        bg_layout.addWidget(bg_label)

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

    def select_background_image(self, current, show_message=True):
        if current:
            image_path = current.data(Qt.ItemDataRole.UserRole)
            scaling_method = "保持比例"
            main_panel = self.main_panel
            if main_panel:
                icon_image_utils.update_background(main_panel, image_path, scaling_method)
                self.config_manager.set("ui_settings", "background_image", image_path)
                #if show_message:
                #   QMessageBox.information(self, "成功", f"背景图片已更改为: {os.path.basename(image_path)}")
                #不提示了
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
            main_panel = self.main_panel
            if main_panel and main_panel in icon_image_utils.background_config:
                del icon_image_utils.background_config[main_panel]
                main_panel.removeEventFilter(icon_image_utils)
                main_panel.setPalette(main_panel.style().standardPalette())
                main_panel.setAutoFillBackground(False)
            self.config_manager.set("ui_settings", "text_color", "#000000")
            QApplication.instance().setStyleSheet("")
            self.bg_list_widget.clearSelection()
            self.color_button.setStyleSheet("")

            QMessageBox.information(self, "成功", "已恢复默认设置。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"恢复默认设置失败: {e}")

    def load_settings(self):

        bg_image = self.config_manager.get("ui_settings", "background_image", "")
        if (bg_image) and (os.path.exists(bg_image)):
            for index in range(self.bg_list_widget.count()):
                item = self.bg_list_widget.item(index)
                if item.data(Qt.ItemDataRole.UserRole) == bg_image:
                    self.bg_list_widget.setCurrentItem(item)

                    self.select_background_image(item, show_message=False)
                    break


        text_color = self.config_manager.get("ui_settings", "text_color", "#000000")
        if text_color:
            app = QApplication.instance()
            app.setStyleSheet(f"QWidget {{ color: {text_color}; }}")


        ui_style = self.config_manager.get("ui_settings", "ui_style", "Fusion")
        self.ui_style_combo_box.setCurrentText(ui_style)
        self.switch_ui_style()

    def switch_ui_style(self):
        ui_style = self.ui_style_combo_box.currentText()
        if ui_style == "自定义样式":
            style_path = self.config_manager.get("ui_settings", "custom_style_path", "")
            if style_path and os.path.exists(style_path):
                with open(style_path, "r") as file:
                    custom_style = file.read()
                    QApplication.instance().setStyleSheet(custom_style)
        else:
            QApplication.setStyle(QStyleFactory.create(ui_style))
            self.config_manager.set("ui_settings", "ui_style", ui_style)

    def select_custom_style(self):
        file_dialog = QFileDialog()
        style_path, _ = file_dialog.getOpenFileName(self, "选择样式文件", "", "样式表文件 (*.qss);;所有文件 (*)")
        if style_path:
            self.config_manager.set("ui_settings", "custom_style_path", style_path)
            self.ui_style_combo_box.setCurrentText("自定义样式")
            self.switch_ui_style()
