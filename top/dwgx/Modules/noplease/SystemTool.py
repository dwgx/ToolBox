import os
import sys
import shutil
import logging
import subprocess

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTextEdit, QMessageBox, QListWidget, QLabel, QLineEdit
)

# 确保正确导入您的模块
# from Manager.ConfigManager import ConfigManager
# from utils.loggerUtils import LogEmitter, setup_logger
# from utils.SystemCore import (
#     repair_network, check_hosts_file, get_current_dns, scan_fastest_dns,
#     set_dns, DNS_INFO, is_admin
# )

# 为了演示，这里将相关函数和变量直接定义在此代码中
# 实际使用时，请从您的模块中正确导入

# 模拟 utils.SystemCore 的内容
DNS_INFO = {
    "8.8.8.8": ("Google DNS", "全球"),
    "114.114.114.114": ("114DNS", "中国"),
    # ... 其他 DNS 服务器
}

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

def repair_network():
    commands = [
        'netsh int ip reset',
        'netsh winsock reset',
        'ipconfig /release',
        'ipconfig /renew',
        'ipconfig /flushdns'
    ]
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"命令执行失败: {cmd}\n{result.stderr}")
            return False
    return True

def check_hosts_file():
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 简单的检测，可以根据需要增强
        if "malicious" in content:
            return ["检测到可疑的 HOSTS 条目"]
        else:
            return []
    except Exception as e:
        logging.error(f"读取 HOSTS 文件失败: {str(e)}")
        return None

def get_current_dns():
    # 简单模拟，实际应解析系统的 DNS 设置
    return "8.8.8.8", "8.8.4.4"

def scan_fastest_dns(dns_list):
    # 模拟扫描，返回固定结果
    results = [(dns, 0.1 * i) for i, dns in enumerate(dns_list)]
    fastest_dns = dns_list[0] if dns_list else None
    return results, fastest_dns

def set_dns(primary_dns, secondary_dns):
    # 模拟设置 DNS，实际应调用系统命令
    return True

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class SystemWorker(QThread):
    completed = Signal(bool, str)

    def __init__(self, func, success_msg, failure_msg):
        super().__init__()
        self.func = func
        self.success_msg = success_msg
        self.failure_msg = failure_msg

    def run(self):
        try:
            result = self.func()
            self.completed.emit(result, self.success_msg if result else self.failure_msg)
        except Exception as e:
            self.completed.emit(False, f"{self.failure_msg}: {str(e)}")

class SystemTool(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.check_admin()

    def init_ui(self):
        self.setWindowTitle('系统维护工具')
        self.resize(800, 600)

        main_layout = QVBoxLayout(self)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # 网络修复标签页
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)

        self.repair_network_btn = QPushButton('一键修复网络')
        self.repair_network_btn.setIcon(QIcon.fromTheme("network-repair"))
        self.repair_network_btn.clicked.connect(
            lambda: self.confirm_and_execute(repair_network, "网络修复完成。", "网络修复失败。")
        )
        network_layout.addWidget(self.repair_network_btn)

        self.check_hosts_btn = QPushButton('检测 HOSTS 文件')
        self.check_hosts_btn.setIcon(QIcon.fromTheme("document-check"))
        self.check_hosts_btn.clicked.connect(self.check_hosts_file)
        network_layout.addWidget(self.check_hosts_btn)

        tabs.addTab(network_tab, "网络修复")

        # 临时文件清理标签页
        temp_cleanup_tab = QWidget()
        temp_cleanup_layout = QVBoxLayout(temp_cleanup_tab)
        self.cleanup_temp_btn = QPushButton('清理临时文件')
        self.cleanup_temp_btn.setIcon(QIcon.fromTheme("folder-cleanup"))
        self.cleanup_temp_btn.clicked.connect(self.start_cleanup)
        temp_cleanup_layout.addWidget(self.cleanup_temp_btn)
        tabs.addTab(temp_cleanup_tab, "临时文件清理")

        # DNS 管理标签页
        dns_tab = QWidget()
        dns_layout = QVBoxLayout(dns_tab)

        self.current_dns_label = QLabel("当前 DNS: 未检测")
        dns_layout.addWidget(self.current_dns_label)

        self.scan_dns_btn = QPushButton('扫描最快 DNS')
        self.scan_dns_btn.setIcon(QIcon.fromTheme("network-scan"))
        self.scan_dns_btn.clicked.connect(self.scan_fastest_dns)
        dns_layout.addWidget(self.scan_dns_btn)

        self.dns_list = QListWidget()
        self.dns_list.itemDoubleClicked.connect(self.set_dns_via_double_click)
        dns_layout.addWidget(self.dns_list)

        # 设置 DNS
        dns_input_layout = QHBoxLayout()
        self.primary_dns_input = QLineEdit()
        self.primary_dns_input.setPlaceholderText("主 DNS")
        dns_input_layout.addWidget(QLabel("主 DNS:"))
        dns_input_layout.addWidget(self.primary_dns_input)

        self.secondary_dns_input = QLineEdit()
        self.secondary_dns_input.setPlaceholderText("副 DNS")
        dns_input_layout.addWidget(QLabel("副 DNS:"))
        dns_input_layout.addWidget(self.secondary_dns_input)

        dns_layout.addLayout(dns_input_layout)

        self.set_dns_btn = QPushButton('设置 DNS')
        self.set_dns_btn.clicked.connect(self.set_dns)
        dns_layout.addWidget(self.set_dns_btn)

        tabs.addTab(dns_tab, "DNS 管理")

        # 日志显示
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont('Microsoft YaHei', 10))
        main_layout.addWidget(self.status_text)

        self.update_current_dns()

    def handle_log(self, level, message):
        self.status_text.append(f"{level}: {message}")
        self.status_text.verticalScrollBar().setValue(self.status_text.verticalScrollBar().maximum())

    def check_admin(self):
        if not is_admin():
            QMessageBox.critical(self, "权限不足", "请以管理员身份运行本程序。")
            sys.exit(1)

    def confirm_and_execute(self, func, success_msg="操作已完成。", failure_msg="操作失败。"):
        reply = QMessageBox.question(self, '确认操作', '你确定要执行此操作吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.system_worker = SystemWorker(func, success_msg, failure_msg)
            self.system_worker.completed.connect(self.handle_system_operation)
            self.system_worker.start()

    def handle_system_operation(self, success, message):
        if success:
            logging.info(message)
            QMessageBox.information(self, "操作完成", message)
        else:
            logging.error(message)
            QMessageBox.critical(self, "操作失败", message)

    def check_hosts_file(self):
        logging.info("正在检测 HOSTS 文件...")
        result = check_hosts_file()
        if result is None:
            logging.error("读取 HOSTS 文件失败。")
            QMessageBox.critical(self, "HOSTS 文件检测", "读取 HOSTS 文件失败。")
        elif result:
            logging.warning("检测到可疑的 HOSTS 条目：")
            for entry in result:
                logging.warning(entry)
            QMessageBox.warning(self, "HOSTS 文件检测", "检测到可疑的 HOSTS 条目，请检查日志。")
        else:
            logging.info("HOSTS 文件未发现异常。")
            QMessageBox.information(self, "HOSTS 文件检测", "HOSTS 文件未发现异常。")

    def update_current_dns(self):
        current_dns, current_secondary_dns = get_current_dns()
        self.current_dns_label.setText(f"当前 DNS: {current_dns or '未检测'}")

    def scan_fastest_dns(self):
        logging.info("正在扫描最快的 DNS 服务器...")
        dns_list = list(DNS_INFO.keys())
        if not dns_list:
            QMessageBox.warning(self, "未配置 DNS", "请在配置文件中添加 DNS 服务器。")
            return

        self.dns_list.clear()
        self.scan_dns_btn.setEnabled(False)
        self.dns_scan_thread = QThread()
        self.dns_scan_thread.run = self.perform_dns_scan
        self.dns_scan_thread.finished.connect(self.dns_scan_thread.deleteLater)
        self.dns_scan_thread.start()

    def perform_dns_scan(self):
        results, fastest_dns = scan_fastest_dns(list(DNS_INFO.keys()))
        for dns, response_time in sorted(results, key=lambda x: x[1]):
            provider, region = DNS_INFO.get(dns, ("未知", "未知"))
            time_display = f"{response_time:.2f} 秒"
            self.dns_list.addItem(f"{dns} ({provider}, {region}) - {time_display}")
        message = f"扫描完成。最快的 DNS 是: {fastest_dns}" if fastest_dns else "未能找到可用的 DNS 服务器。"
        logging.info(message)
        self.scan_dns_btn.setEnabled(True)
        self.update_current_dns()

    def set_dns_via_double_click(self, item):
        selected_dns = item.text().split(" ")[0]
        self.primary_dns_input.setText(selected_dns)
        logging.info(f"选择的 DNS: {selected_dns}")

    def set_dns(self):
        primary_dns = self.primary_dns_input.text().strip()
        secondary_dns = self.secondary_dns_input.text().strip()
        if not primary_dns:
            QMessageBox.warning(self, "未输入主 DNS", "请填写主 DNS 地址。")
            return
        success = set_dns(primary_dns, secondary_dns)
        if success:
            logging.info(f"DNS 设置成功: 主 DNS - {primary_dns}, 副 DNS - {secondary_dns}")
            QMessageBox.information(self, "设置 DNS 成功", f"已设置主 DNS: {primary_dns}, 副 DNS: {secondary_dns}")
        else:
            logging.error("设置 DNS 失败")
            QMessageBox.critical(self, "设置 DNS 失败", "无法设置 DNS。")
        self.update_current_dns()

    def start_cleanup(self):
        reply = QMessageBox.question(self, '确认操作', '你确定要清理临时文件吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cleanup_temp_btn.setEnabled(False)
            self.cleanup_thread = QThread()
            self.cleanup_thread.run = self.perform_cleanup
            self.cleanup_thread.finished.connect(self.cleanup_thread.deleteLater)
            self.cleanup_thread.start()

    def perform_cleanup(self):
        temp_path = os.environ.get('TEMP', None)
        if not temp_path:
            logging.error("无法找到临时文件夹路径。")
            QMessageBox.critical(self, "清理失败", "无法找到临时文件夹路径。")
            self.cleanup_temp_btn.setEnabled(True)
            return
        deleted_count = 0
        for root, dirs, files in os.walk(temp_path):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception:
                    pass
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                    deleted_count += 1
                except Exception:
                    pass
        logging.info(f"已清理 {deleted_count} 个文件和文件夹。")
        QMessageBox.information(self, "清理完成", f"已清理 {deleted_count} 个文件和文件夹。")
        self.cleanup_temp_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    system_tool = SystemTool()
    system_tool.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
