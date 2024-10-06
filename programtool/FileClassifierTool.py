import configparser
import os
from collections import defaultdict

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem
)

CONFIG_FILE = 'config.cfg'


def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config['settings'] = {
            'folder_path': '',
            'filter_types': '',
            'exclude_types': ''
        }
        with open(CONFIG_FILE, 'w') as config_file:
            config.write(config_file)
    return config


def save_config(folder_path, filter_types, exclude_types):
    config = configparser.ConfigParser()
    config['settings'] = {
        'folder_path': folder_path,
        'filter_types': ','.join(filter_types),
        'exclude_types': ','.join(exclude_types)
    }
    with open(CONFIG_FILE, 'w') as config_file:
        config.write(config_file)


def scan_files(folder_path, filter_types, exclude_types):
    file_dict = defaultdict(list)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if filter_types and not any(file.lower().endswith(ft) for ft in filter_types):
                continue
            if exclude_types and any(file.lower().endswith(et) for et in exclude_types):
                continue
            file_dict[root].append(os.path.join(root, file))

    return file_dict


def display_results(file_dict):
    result_text = ""
    for folder, files in file_dict.items():
        result_text += f'文件夹: {folder}\n'
        result_text += f'数量: {len(files)}\n'
        for file in files:
            result_text += f'  - {file}\n'
        result_text += '\n'
    return result_text


def search_files(file_dict, keyword):
    keyword_lower = keyword.lower()
    return {
        folder: [file for file in files if keyword_lower in os.path.basename(file).lower()]
        for folder, files in file_dict.items() if any(keyword_lower in os.path.basename(file).lower() for file in files)
    }


class FileClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件分类工具")
        self.setGeometry(100, 100, 1000, 600)

        self.file_dict = {}
        self.config = load_config()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        folder_layout = QHBoxLayout()
        self.folder_path_label = QLabel("文件夹路径:")
        folder_layout.addWidget(self.folder_path_label)

        self.folder_path_entry = QLineEdit()
        folder_layout.addWidget(self.folder_path_entry)
        self.folder_path_entry.setText(self.config['settings'].get('folder_path', ''))

        self.folder_path_button = QPushButton("选择文件夹")
        self.folder_path_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_path_button)
        main_layout.addLayout(folder_layout)

        filter_layout = QHBoxLayout()

        self.filter_label = QLabel("筛选文件类型（用逗号分隔，例如：.py,.txt）：")
        filter_layout.addWidget(self.filter_label)

        self.filter_entry = QLineEdit()
        filter_layout.addWidget(self.filter_entry)
        self.filter_entry.setText(self.config['settings'].get('filter_types', ''))
        main_layout.addLayout(filter_layout)

        exclude_layout = QHBoxLayout()

        self.exclude_label = QLabel("排除文件类型（用逗号分隔，例如：.log,.tmp）：")
        exclude_layout.addWidget(self.exclude_label)

        self.exclude_entry = QLineEdit()
        exclude_layout.addWidget(self.exclude_entry)
        self.exclude_entry.setText(self.config['settings'].get('exclude_types', ''))
        main_layout.addLayout(exclude_layout)

        search_layout = QHBoxLayout()

        self.search_label = QLabel("根据关键词搜索文件名:")
        search_layout.addWidget(self.search_label)

        self.search_entry = QLineEdit()
        search_layout.addWidget(self.search_entry)

        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_files)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        button_layout = QHBoxLayout()

        self.scan_button = QPushButton("开始扫描")
        self.scan_button.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_button)

        self.show_graph_button = QPushButton("显示关系图")
        self.show_graph_button.clicked.connect(self.show_graph)
        button_layout.addWidget(self.show_graph_button)

        main_layout.addLayout(button_layout)

        result_and_tree_layout = QHBoxLayout()

        self.result_text = QTextEdit()
        result_and_tree_layout.addWidget(self.result_text)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["文件关系树"])
        self.tree_widget.itemDoubleClicked.connect(self.open_item)
        result_and_tree_layout.addWidget(self.tree_widget)

        main_layout.addLayout(result_and_tree_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_path_entry.setText(folder)

    def start_scan(self):
        folder_path = self.folder_path_entry.text().strip()
        filter_types = self.filter_entry.text().strip().split(',') if self.filter_entry.text().strip() else []
        exclude_types = self.exclude_entry.text().strip().split(',') if self.exclude_entry.text().strip() else []

        if not folder_path:
            QMessageBox.warning(self, "警告", "请先选择文件夹路径")
            return

        self.result_text.clear()

        save_config(folder_path, filter_types, exclude_types)

        self.file_dict = scan_files(folder_path, filter_types, exclude_types)
        result_text = display_results(self.file_dict)
        self.result_text.insertPlainText(result_text)

    def show_graph(self):
        self.tree_widget.clear()

        for folder, files in self.file_dict.items():
            folder_item = QTreeWidgetItem([folder])
            folder_item.setForeground(0, Qt.GlobalColor.blue)
            font = folder_item.font(0)
            font.setBold(True)
            folder_item.setFont(0, font)
            self.tree_widget.addTopLevelItem(folder_item)

            for file in files:
                file_item = QTreeWidgetItem([os.path.basename(file)])
                file_item.setData(0, Qt.ItemDataRole.UserRole, file)
                folder_item.addChild(file_item)

        self.tree_widget.expandAll()

    def search_files(self):
        keyword = self.search_entry.text().strip()
        if not keyword:
            QMessageBox.warning(self, "警告", "请先输入搜索关键词")
            return

        if not self.file_dict:
            QMessageBox.warning(self, "警告", "请先进行文件扫描")
            return

        filtered_dict = search_files(self.file_dict, keyword)
        result_text = display_results(filtered_dict)
        self.result_text.clear()
        self.result_text.insertPlainText(result_text)

        self.file_dict = filtered_dict
        self.show_graph()

    def open_item(self, item, column):
        if item.parent() is not None:
            path = item.data(column, Qt.ItemDataRole.UserRole)
            if os.path.isfile(path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))


def main():
    app = QApplication([])
    window = FileClassifierApp()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
