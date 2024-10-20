# main.py

import logging
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QListWidget, QStackedWidget, QListWidgetItem
)

from Manager.ConfigManager import ConfigManager
from Manager.ModuleManager import ModuleManager
from Manager.ModuleManager import logger
from utils.IconImageUtils import icon_image_utils
from utils.loggerUtils import LogEmitter, setup_logger


class MainPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.setWindowTitle('ToolBox')
        self.resize(800, 600)
        self.center()

        window_icon = icon_image_utils.get_icon('java.exe.ico')
        self.setWindowIcon(window_icon)
        logger.info("设置窗口图标")

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
        logger.info("=== 开始加载所有模块 ===")
        try:
            modules = self.module_manager.get_modules()  # 获取模块
            for module_cls, is_special in modules:
                try:
                    module_name = module_cls.__name__
                    logger.info(f"正在加载模块: {module_name}")
                    # 实例化模块
                    if is_special and module_name == 'Setting':
                        module_instance = module_cls(main_panel=self)
                    else:
                        module_instance = module_cls()  # 实例化模块

                    # 将模块添加到界面
                    folder_icon = icon_image_utils.get_icon('folder-open.png')
                    list_item = QListWidgetItem(folder_icon, f"{module_name}")
                    self.navigation_list.addItem(list_item)
                    self.stack.addWidget(module_instance)

                    logger.info(f"模块加载成功: {module_name}")
                except Exception as e:
                    logger.error(f"加载模块 {module_name} 时发生错误: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"加载所有模块失败: {e}", exc_info=True)

    def switch_module(self, index):
        if index != -1:
            self.stack.setCurrentIndex(index)
            module_name = self.navigation_list.item(index).text()
            logger.info(f"→ 切换到模块: {module_name} (索引: {index})")

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )
        logger.info("窗口已居中")

    def apply_background_image(self):
        try:
            background_image_path = self.config_manager.get('ui_settings', 'background_image')
            logger.info(f"加载背景图片路径: {background_image_path}")

            pixmap = QPixmap(background_image_path)
            if not pixmap.isNull():
                palette = QPalette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
                logger.info(f"应用背景图片: {background_image_path}")
            else:
                logger.error(f"背景图片路径不存在或无效: {background_image_path}")

        except Exception as e:
            logger.error(f"应用背景图片失败: {e}", exc_info=True)

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
    # 配置全局日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("MainPanel")

    app = QApplication(sys.argv)

    # 设置全局日志记录（如果有 GUI 显示日志的需求）
    # 这里假设您有一个 LogEmitter 和 setup_logger 来处理日志显示
    log_emitter = LogEmitter()
    setup_logger("MainPanel", log_emitter)

    # 初始化并加载模块
    main_window = MainPanel()
    main_window.show()

    logger.info("主窗口已显示")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
