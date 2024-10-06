import subprocess
import sys

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox, QMessageBox, QLabel, \
    QScrollArea, QGridLayout, QGroupBox


class LibUninstaller(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python 库卸载工具")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        self.info_label = QLabel("获取已安装的库", self)
        layout.addWidget(self.info_label)

        self.refresh_button = QPushButton("刷新库列表", self)
        self.refresh_button.clicked.connect(self.refresh_packages)
        layout.addWidget(self.refresh_button)

        self.select_all_button = QPushButton("全选", self)
        self.select_all_button.clicked.connect(self.select_all_packages)
        layout.addWidget(self.select_all_button)

        self.unselect_all_button = QPushButton("取消全选", self)
        self.unselect_all_button.clicked.connect(self.unselect_all_packages)
        layout.addWidget(self.unselect_all_button)

        self.uninstall_button = QPushButton("卸载选择的库", self)
        self.uninstall_button.clicked.connect(self.uninstall_selected_packages)
        layout.addWidget(self.uninstall_button)

        self.package_group_box = QGroupBox("已安装的库")
        self.package_layout = QGridLayout()
        self.package_group_box.setLayout(self.package_layout)

        scroll = QScrollArea()
        scroll.setWidget(self.package_group_box)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.package_checkboxes = []

        self.setLayout(layout)

        # 初次刷新库列表
        self.refresh_packages()

    def refresh_packages(self):
        self.package_checkboxes.clear()
        for i in reversed(range(self.package_layout.count())):
            widget = self.package_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        installed_packages = subprocess.check_output(['pip', 'freeze']).decode().split('\n')
        filtered_packages = [package.split('==')[0] for package in installed_packages if
                             package.strip() != '' and not package.startswith('pkg-resources')]

        for idx, package in enumerate(filtered_packages):
            checkbox = QCheckBox(package, self)
            self.package_checkboxes.append(checkbox)
            self.package_layout.addWidget(checkbox, idx // 2, idx % 2)

    def select_all_packages(self):
        for checkbox in self.package_checkboxes:
            checkbox.setChecked(True)

    def unselect_all_packages(self):
        for checkbox in self.package_checkboxes:
            checkbox.setChecked(False)

    def uninstall_selected_packages(self):
        selected_packages = [checkbox.text() for checkbox in self.package_checkboxes if checkbox.isChecked()]

        if not selected_packages:
            QMessageBox.information(self, "提示", "没有选择需要卸载的包。")
            return

        confirm = QMessageBox.question(self, "确认", f"你确定要卸载以下库吗？\n\n" + "\n".join(selected_packages))
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            uninstall_command = [sys.executable, '-m', 'pip', 'uninstall', '-y'] + selected_packages
            subprocess.check_call(uninstall_command)
            QMessageBox.information(self, "提示", f"已卸载 {len(selected_packages)} 个库。")
            self.refresh_packages()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "错误", f"卸载过程中出现错误: {e}")


def main():
    app = QApplication(sys.argv)
    package_uninstaller = LibUninstaller()
    package_uninstaller.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
