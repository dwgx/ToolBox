# top/dwgx/Modules/Example2.py
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QProgressBar, QTextEdit, QLineEdit, QComboBox,
    QCheckBox, QRadioButton, QGroupBox, QSpinBox, QDateEdit, QApplication
)
from PySide6.QtCore import Qt

class Example2(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example2 - UI Controls Showcase")
        self.resize(800, 600)

        main_layout = QVBoxLayout(self)

        # 多行文本编辑器
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("这是一个多行文本编辑器。")
        main_layout.addWidget(text_edit)

        # 单行文本输入框
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("这是一个单行文本输入框。")
        main_layout.addWidget(line_edit)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_ok = QPushButton("确定")
        button_cancel = QPushButton("取消")
        button_layout.addWidget(button_ok)
        button_layout.addWidget(button_cancel)
        main_layout.addLayout(button_layout)

        # 滑块布局
        slider_layout = QHBoxLayout()
        slider_label = QLabel("滑块示例:")
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(slider)
        main_layout.addLayout(slider_layout)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setValue(70)
        main_layout.addWidget(progress_bar)

        # 下拉框
        combo_box = QComboBox()
        combo_box.addItems(["选项1", "选项2", "选项3"])
        main_layout.addWidget(combo_box)

        # 复选框布局
        checkbox_layout = QHBoxLayout()
        checkbox1 = QCheckBox("复选框1")
        checkbox2 = QCheckBox("复选框2")
        checkbox_layout.addWidget(checkbox1)
        checkbox_layout.addWidget(checkbox2)
        main_layout.addLayout(checkbox_layout)

        # 单选按钮组
        radio_group = QGroupBox("单选按钮组")
        radio_layout = QHBoxLayout()
        radio1 = QRadioButton("单选1")
        radio2 = QRadioButton("单选2")
        radio_layout.addWidget(radio1)
        radio_layout.addWidget(radio2)
        radio_group.setLayout(radio_layout)
        main_layout.addWidget(radio_group)

        # 标签
        label = QLabel("这是一个标签。")
        main_layout.addWidget(label)

        # 数字输入框
        spin_box = QSpinBox()
        spin_box.setRange(0, 100)
        spin_box.setValue(10)
        main_layout.addWidget(spin_box)

        # 日期选择器
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        main_layout.addWidget(date_edit)

        # 添加间距
        main_layout.addStretch()

        self.setLayout(main_layout)

def main():
    app = QApplication(sys.argv)
    example2 = Example2()
    example2.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()