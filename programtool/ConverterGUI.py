import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget,
    QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit
)


class ConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 to PySide6 Converter")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()

    def init_ui(self):
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()

        # 项目路径输入
        path_layout = QHBoxLayout()
        self.path_label = QLabel("项目路径：")
        self.path_input = QLineEdit()
        self.path_button = QPushButton("选择路径")
        self.path_button.clicked.connect(self.choose_directory)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_button)

        # 日志显示文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # 转换按钮
        self.convert_button = QPushButton("转换 PyQt6 导入为 PySide6")
        self.convert_button.clicked.connect(self.convert_imports)

        # 将部件添加到主布局
        main_layout.addLayout(path_layout)
        main_layout.addWidget(self.log_text)
        main_layout.addWidget(self.convert_button)

        # 设置主布局
        central_widget.setLayout(main_layout)

    def choose_directory(self):
        # 打开文件夹选择对话框
        directory = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if directory:
            self.path_input.setText(directory)

    def convert_imports(self):
        # 获取项目目录
        project_dir = self.path_input.text()
        if not os.path.exists(project_dir):
            QMessageBox.critical(self, "错误", "请指定有效的项目路径。")
            return

        # 遍历指定目录并替换导入
        for subdir, _, files in os.walk(project_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(subdir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # 替换 PyQt6 导入为 PySide6
                        updated_content = content
                        replacements = {
                            "from PySide6.QtCore": "from PySide6.QtCore",
                            "from PySide6.QtGui": "from PySide6.QtGui",
                            "from PySide6.QtWidgets": "from PySide6.QtWidgets",
                            "import PySide6.QtCore": "import PySide6.QtCore",
                            "import PySide6.QtGui": "import PySide6.QtGui",
                            "import PySide6.QtWidgets": "import PySide6.QtWidgets"
                        }

                        # 进行替换
                        for old, new in replacements.items():
                            updated_content = updated_content.replace(old, new)

                        # 保存文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)

                        self.log_text.append(f"Processed: {file_path}")

                    except Exception as e:
                        self.log_text.append(f"Failed: {file_path} with error {str(e)}")

        QMessageBox.information(self, "完成", "所有导入替换完成！")


def main():
    app = QApplication(sys.argv)
    window = ConverterGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
