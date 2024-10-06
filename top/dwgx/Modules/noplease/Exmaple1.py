# top/dwgx/Modules/Example1.py
import sys

from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGridLayout, QScrollArea, QLabel, QApplication
from PySide6.QtGui import QIcon
from top.dwgx.utils.IconImageUtils import icon_image_utils

class Example1(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example1 - Icons Showcase")
        self.resize(800, 600)

        main_layout = QVBoxLayout(self)

        # Scroll area to hold the grid of buttons
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        # Container widget inside the scroll area
        container = QWidget()
        scroll.setWidget(container)

        # Grid layout for buttons
        grid_layout = QGridLayout(container)
        container.setLayout(grid_layout)

        # 定义常见的图标名称列表
        icon_names = [
            "document-open", "document-save", "document-new", "document-print",
            "folder", "folder-open", "folder-new",
            "edit-copy", "edit-paste", "edit-delete", "edit-cut", "edit-undo", "edit-redo",
            "application-exit", "preferences-system", "system-run", "system-log-out", "system-shutdown",
            "media-playback-start", "media-playback-pause", "media-playback-stop",
            "media-skip-forward", "media-skip-backward",
            "audio-volume-high", "audio-volume-medium", "audio-volume-low", "audio-volume-muted",
            "utilities-terminal", "utilities-system-monitor",
            "help-about", "help-contents", "go-home", "go-up", "go-next", "go-previous"
        ]

        # 可以根据需要添加更多图标

        # 将按钮添加到网格布局中
        columns = 1
        row = 0
        col = 0
        for icon_name in icon_names:
            button = QPushButton(icon_name, self)
            button.setIcon(QIcon.fromTheme(icon_name))
            button.setIconSize(button.sizeHint())
            button.setToolTip(icon_name)
            button.clicked.connect(lambda checked, name=icon_name: self.icon_clicked(name))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        # 添加间距
        grid_layout.setRowStretch(row + 1, 1)

    def icon_clicked(self, icon_name):
        print(f"Icon clicked: {icon_name}")

def main():
    app = QApplication(sys.argv)
    example1 = Example1()
    example1.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()