import logging
import os
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPalette, QBrush
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QSplitter, QListWidget, QStackedWidget, QListWidgetItem, QMessageBox
)
from Manager.ModuleManager import logger, ModuleManager
from utils.IconImageUtils import icon_image_utils
from utils.loggerutils import LogEmitter, setup_logger
from Manager.ConfigManager import ConfigManager
import top.resource.Icons.resources_rc

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(base_path)

class MainPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.setWindowTitle('ToolBox')
        self.resize(800, 600)
        self.center()

        window_icon = icon_image_utils.get_icon('java.exe.ico')
        self.setWindowIcon(window_icon)
        logging.info("设置窗口图标")

        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.navigation_list = CustomListWidget(self)
        self.navigation_list.setMinimumWidth(180)
        self.navigation_list.setStyleSheet("QListWidget::item { height: 40px; }")
        self.navigation_list.currentRowChanged.connect(self.switch_module)

        splitter.addWidget(self.navigation_list)

        self.stack = QStackedWidget()
        splitter.addWidget(self.stack)

        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

        self.module_manager = ModuleManager()
        self.load_modules()

        self.apply_background_image()

    def load_modules(self):
        logger.info("=== 开始加载模块 ===")
        try:
            modules = self.module_manager.get_modules()
            for module_cls, is_special in modules:
                try:
                    module_name = module_cls.__name__

                    if is_special and module_name == 'Setting':
                        module_instance = module_cls(main_panel=self)
                    else:
                        module_instance = module_cls()

                        folder_icon = icon_image_utils.get_icon('folder-open.png')
                    logger.info(f"为模块 '{module_name}' 加载图标: {folder_icon}")

                    list_item = QListWidgetItem(folder_icon, f"{module_name}")
                    self.navigation_list.addItem(list_item)
                    self.stack.addWidget(module_instance)

                    logger.info(f"已加载模块: {module_name}")
                except Exception as e:
                    logger.error(f"加载单个模块失败: {module_name}, 错误信息: {e}")

        except Exception as e:
            logger.error(f"加载模块失败: {e}")

    def switch_module(self, index):
        if index != -1:
            self.stack.setCurrentIndex(index)
            module_name = self.navigation_list.item(index).text()
            logging.info(f"→ 切换到模块: {module_name} (索引: {index})")

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )
        logging.info("窗口已居中")

    def apply_background_image(self):

        try:
            background_image_path = self.config_manager.get('ui_settings', 'background_image')
            logging.info(f"加载背景图片路径: {background_image_path}")


            pixmap = QPixmap(background_image_path)
            if not pixmap.isNull():
                palette = QPalette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
                logging.info(f"应用背景图片: {background_image_path}")
            else:
                logging.error(f"背景图片路径不存在或无效: {background_image_path}")

        except Exception as e:
            logging.error(f"应用背景图片失败: {e}")

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        else:
            self.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
        super().mouseReleaseEvent(event)

def main():
    app = QApplication(sys.argv)
    log_emitter = LogEmitter()
    logger = setup_logger("MainPanel", log_emitter)
    main_window = MainPanel()
    main_window.show()
    logger.info("主窗口已显示")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()