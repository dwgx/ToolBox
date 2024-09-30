#top.dwgx.Client #累死我了 妈的敲得

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QSplitter, QListWidget,
    QStackedWidget, QListWidgetItem
)
from top.dwgx.Manager.ModuleManager import ModuleManager
from top.dwgx.utils.IconImageUtils import icon_image_utils


class MainPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Client Main Panel')
        self.resize(800, 600)
        self.center()

        window_icon = icon_image_utils.get_icon('java.exe.ico')
        self.setWindowIcon(window_icon)

        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.navigation_list = QListWidget()
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

    def load_modules(self):
        try:
            modules = self.module_manager.get_modules()
            for module_cls in modules:
                module_instance = module_cls()
                module_name = module_cls.__name__

                icon = QIcon.fromTheme("folder-open")

                # 创建带图标的列表项
                list_item = QListWidgetItem(icon, f"模块 {module_name}")
                self.navigation_list.addItem(list_item)

                self.stack.addWidget(module_instance)
        except Exception as e:
            print(f"加载模块失败: {e}")

    def switch_module(self, index):
        self.stack.setCurrentIndex(index)

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )


def main():
    app = QApplication(sys.argv)

    app_icon = icon_image_utils.get_icon('java.exe.ico')
    app.setWindowIcon(app_icon)

    main_window = MainPanel()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
