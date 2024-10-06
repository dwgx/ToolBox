import os
import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit, QCheckBox,
    QHBoxLayout
)


class QRCGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QRC 文件生成器")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        # 主部件和布局
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # 文件夹选择
        path_layout = QHBoxLayout()
        self.path_label = QLabel("资源文件夹路径：", self)
        path_layout.addWidget(self.path_label)

        self.path_input = QLineEdit(self)
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)

        self.path_button = QPushButton("选择文件夹", self)
        self.path_button.clicked.connect(self.choose_directory)
        path_layout.addWidget(self.path_button)

        main_layout.addLayout(path_layout)

        # 智能排除复选框
        self.exclude_checkbox = QCheckBox("智能排除常见文件（如 __pycache__, .pyc 等）", self)
        self.exclude_checkbox.setChecked(True)
        main_layout.addWidget(self.exclude_checkbox)

        # 预览
        self.preview_text = QTextEdit(self)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("QRC 预览将显示在这里...")
        main_layout.addWidget(self.preview_text)

        # 生成和打包按钮
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("生成 QRC 文件", self)
        self.generate_button.clicked.connect(self.generate_qrc)
        button_layout.addWidget(self.generate_button)

        self.pack_button = QPushButton("一键打包成 resources_rc.py", self)
        self.pack_button.clicked.connect(self.pack_resources_rc)
        button_layout.addWidget(self.pack_button)

        main_layout.addLayout(button_layout)

    def choose_directory(self):
        # 弹出文件夹选择框
        resource_dir = QFileDialog.getExistingDirectory(self, "选择资源文件夹", "")
        if resource_dir:
            self.path_input.setText(resource_dir)
            self.preview_qrc()

    def preview_qrc(self):
        # 获取路径
        resource_dir = self.path_input.text()
        if not resource_dir:
            return

        # 生成预览
        qrc_preview = self.create_qrc_preview(resource_dir)
        self.preview_text.setPlainText(qrc_preview)

    def create_qrc_preview(self, resource_dir):
        # 获取资源文件夹中的文件
        qrc_preview = '<RCC>\n    <qresource prefix="/icons">\n'
        for root, dirs, files in os.walk(resource_dir):
            for file in files:
                if self.exclude_checkbox.isChecked() and self.smart_exclude(file):
                    continue
                relative_path = os.path.relpath(os.path.join(root, file), resource_dir).replace("\\", "/")
                qrc_preview += f'        <file>{relative_path}</file>\n'
        qrc_preview += '    </qresource>\n</RCC>'
        return qrc_preview

    def smart_exclude(self, file_name):
        # 智能排除规则
        excluded_extensions = {'.py', '.pyc', '.pyo', '.exe', '.dll'}
        excluded_files = {'__pycache__', 'thumbs.db', 'desktop.ini'}
        extension = os.path.splitext(file_name)[1].lower()
        base_name = os.path.basename(file_name).lower()
        return extension in excluded_extensions or base_name in excluded_files

    def generate_qrc(self):
        resource_dir = self.path_input.text()
        if not resource_dir:
            QMessageBox.warning(self, "警告", "请选择一个资源文件夹。")
            return

        qrc_file = os.path.join(resource_dir, 'resources.qrc')
        try:
            # 生成 QRC 文件
            qrc_content = self.create_qrc_preview(resource_dir)
            with open(qrc_file, 'w', encoding='utf-8') as f:
                f.write(qrc_content)
            QMessageBox.information(self, "生成成功", f"{qrc_file} 已成功生成！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成 QRC 文件时发生错误：{e}")

    def pack_resources_rc(self):
        resource_dir = self.path_input.text()
        if not resource_dir:
            QMessageBox.warning(self, "警告", "请选择一个资源文件夹。")
            return

        qrc_file = os.path.join(resource_dir, 'resources.qrc')
        output_py = os.path.join(resource_dir, 'resources_rc.py')

        # 检查 qrc 文件是否存在
        if not os.path.exists(qrc_file):
            QMessageBox.warning(self, "警告", "QRC 文件不存在，请先生成 QRC 文件。")
            return

        try:
            # 尝试运行 pyside6-rcc 或 pyrcc6 进行打包
            cmd = f'pyside6-rcc "{qrc_file}" -o "{output_py}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # 如果 pyside6-rcc 失败，尝试 pyrcc6
            if result.returncode != 0:
                cmd = f'pyrcc6 "{qrc_file}" -o "{output_py}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # 检查打包结果
            if result.returncode == 0:
                QMessageBox.information(self, "打包成功", f"资源文件已打包为 {output_py}")
            else:
                raise Exception(result.stderr)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打包资源文件时发生错误：{e}")


def main():
    app = QApplication(sys.argv)
    window = QRCGenerator()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
