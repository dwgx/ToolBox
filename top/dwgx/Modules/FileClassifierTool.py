

import os
import sys
from collections import defaultdict
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTextEdit, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QStatusBar,
    QGroupBox, QGridLayout, QDialog, QMenu
)
from top.dwgx.Manager.ConfigManager import ConfigManager

class FileTreeDialog(QDialog):
    def __init__(self, file_dict):
        super().__init__()
        self.setWindowTitle("文件关系树")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["路径", "类型"])
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.create_right_click_menu)
        self.tree_widget.itemDoubleClicked.connect(self.open_item)
        self.populate_tree(file_dict)
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

    def populate_tree(self, file_dict):
        for folder, files in file_dict.items():
            folder_item = QTreeWidgetItem([folder, "文件夹"])
            self.tree_widget.addTopLevelItem(folder_item)
            for file in files:
                file_item = QTreeWidgetItem([file, "文件"])
                file_item.setData(0, Qt.ItemDataRole.UserRole, file)
                folder_item.addChild(file_item)
        self.tree_widget.expandAll()

    def create_right_click_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item and item.parent():
            menu = QMenu(self.tree_widget)
            open_action = menu.addAction(QIcon.fromTheme("document-open"), "打开")
            delete_action = menu.addAction(QIcon.fromTheme("list-remove"), "删除")
            open_action.triggered.connect(lambda: self.open_item(item, 0))
            delete_action.triggered.connect(lambda: self.delete_item(item, 0))
            menu.exec(self.tree_widget.mapToGlobal(position))

    def open_item(self, item, column):
        path = item.data(column, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def delete_item(self, item, column):
        path = item.data(column, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            os.remove(path)
            parent = item.parent()
            parent.removeChild(item)
            if parent.childCount() == 0:
                self.tree_widget.takeTopLevelItem(self.tree_widget.indexOfTopLevelItem(parent))

class FileClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件分类工具")
        self.setGeometry(100, 100, 1000, 700)
        self.file_dict = defaultdict(list)
        self.config_manager = ConfigManager()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)


        folder_group = QGroupBox("选择文件夹")
        folder_layout = QHBoxLayout()
        folder_group.setLayout(folder_layout)

        self.folder_path_label = QLabel("文件夹路径:")
        folder_layout.addWidget(self.folder_path_label)

        self.folder_path_entry = QLineEdit()
        folder_paths = self.config_manager.get('file_classifier', 'folder_path', '')
        self.folder_path_entry.setText(folder_paths)
        self.folder_path_entry.setPlaceholderText("请选择要分类的文件夹路径")
        folder_layout.addWidget(self.folder_path_entry)

        self.folder_path_button = QPushButton("选择文件夹")
        self.folder_path_button.setIcon(QIcon.fromTheme("document-open"))
        self.folder_path_button.setToolTip("点击选择要分类的文件夹")
        self.folder_path_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_path_button)

        main_layout.addWidget(folder_group)


        filter_group = QGroupBox("筛选设置")
        filter_layout = QGridLayout()
        filter_group.setLayout(filter_layout)

        self.filter_label = QLabel("筛选文件类型（用逗号分隔，例如：.py,.txt）：")
        filter_layout.addWidget(self.filter_label, 0, 0)

        self.filter_entry = QLineEdit()
        filter_types = self.config_manager.get('file_classifier', 'filter_types', '')
        self.filter_entry.setText(filter_types if isinstance(filter_types, str) else ','.join(filter_types))
        self.filter_entry.setPlaceholderText("例如：.py,.txt")
        filter_layout.addWidget(self.filter_entry, 0, 1)

        self.exclude_label = QLabel("排除文件类型（用逗号分隔，例如：.log,.tmp）：")
        filter_layout.addWidget(self.exclude_label, 1, 0)

        self.exclude_entry = QLineEdit()
        exclude_types = self.config_manager.get('file_classifier', 'exclude_types', '')
        self.exclude_entry.setText(exclude_types if isinstance(exclude_types, str) else ','.join(exclude_types))
        self.exclude_entry.setPlaceholderText("例如：.log,.tmp")
        filter_layout.addWidget(self.exclude_entry, 1, 1)

        main_layout.addWidget(filter_group)


        search_group = QGroupBox("搜索文件")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)

        self.search_label = QLabel("根据关键词搜索文件名:")
        search_layout.addWidget(self.search_label)

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("输入关键词，例如：report")
        search_layout.addWidget(self.search_entry)

        self.search_button = QPushButton("搜索")
        self.search_button.setIcon(QIcon.fromTheme("edit-find"))
        self.search_button.setToolTip("点击开始搜索")
        self.search_button.clicked.connect(self.search_files)
        search_layout.addWidget(self.search_button)

        main_layout.addWidget(search_group)


        action_group = QGroupBox("操作")
        action_layout = QHBoxLayout()
        action_group.setLayout(action_layout)

        self.scan_button = QPushButton("开始扫描")
        self.scan_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.scan_button.setToolTip("点击开始扫描文件")
        self.scan_button.clicked.connect(self.start_scan)
        action_layout.addWidget(self.scan_button)

        self.show_tree_button = QPushButton("显示文件树")
        self.show_tree_button.setIcon(QIcon.fromTheme("folder"))
        self.show_tree_button.setToolTip("点击显示扫描结果的文件关系树")
        self.show_tree_button.clicked.connect(self.show_file_tree)
        action_layout.addWidget(self.show_tree_button)

        main_layout.addWidget(action_group)


        result_group = QGroupBox("扫描结果")
        result_layout = QHBoxLayout()
        result_group.setLayout(result_layout)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont('Microsoft YaHei', 10))
        self.result_text.setPlaceholderText("扫描结果将在此显示")
        result_layout.addWidget(self.result_text)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["文件关系树"])
        self.tree_widget.itemDoubleClicked.connect(self.open_item)
        result_layout.addWidget(self.tree_widget)

        main_layout.addWidget(result_group)


        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if folder:
            self.folder_path_entry.setText(folder)
            self.config_manager.set("file_classifier", "folder_path", folder)

    def start_scan(self):
        folder_path = self.folder_path_entry.text().strip()
        filter_types = [ft.strip() for ft in self.filter_entry.text().strip().split(',')] if self.filter_entry.text().strip() else []
        exclude_types = [et.strip() for et in self.exclude_entry.text().strip().split(',')] if self.exclude_entry.text().strip() else []
        if not folder_path:
            QMessageBox.warning(self, "警告", "请先选择文件夹路径")
            return
        self.result_text.clear()
        self.tree_widget.clear()
        self.file_dict.clear()
        self.status_bar.showMessage("扫描中...")
        try:
            self.file_dict = ConfigManager.scan_files(folder_path, filter_types, exclude_types)
            result_text = ConfigManager.display_results(self.file_dict)
            self.result_text.setText(result_text)
            file_count = sum(len(files) for files in self.file_dict.values())
            self.status_bar.showMessage(f"扫描完成，共找到 {file_count} 个文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"扫描时发生错误: {str(e)}")
            self.status_bar.showMessage("扫描出错")

    def show_file_tree(self):
        if not self.file_dict:
            QMessageBox.warning(self, "警告", "请先进行文件扫描")
            return
        self.tree_widget.clear()
        for folder, files in self.file_dict.items():
            folder_item = QTreeWidgetItem([folder, "文件夹"])
            folder_item.setForeground(0, Qt.GlobalColor.darkMagenta)
            font = folder_item.font(0)
            font.setBold(True)
            folder_item.setFont(0, font)
            self.tree_widget.addTopLevelItem(folder_item)
            for file in files:
                file_item = QTreeWidgetItem([os.path.basename(file), "文件"])
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
        self.status_bar.showMessage(f"搜索 \"{keyword}\" 中...")
        try:
            filtered_dict = ConfigManager.search_files(self.file_dict, keyword)
            if filtered_dict:
                result_text = ConfigManager.display_results(filtered_dict)
                self.result_text.setText(result_text)
                file_count = sum(len(files) for files in filtered_dict.values())
                self.status_bar.showMessage(f"搜索完成，共找到 {file_count} 个文件")
                self.file_dict = filtered_dict
                self.show_file_tree()
            else:
                self.status_bar.showMessage(f"未找到与 \"{keyword}\" 相关的文件")
                QMessageBox.information(self, "搜索结果", f"未找到与 \"{keyword}\" 相关的文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索时发生错误: {str(e)}")
            self.status_bar.showMessage("搜索出错")

    def open_item(self, item, column):
        if item.parent() is not None:
            path = item.data(column, Qt.ItemDataRole.UserRole)
            if os.path.isfile(path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))

def main():
    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon.fromTheme("preferences-system"))
        main_win = FileClassifierApp()
        main_win.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"main错误: {str(e)}")

if __name__ == "__main__":
    main()
