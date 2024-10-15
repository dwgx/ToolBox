import os
import sys
import platform
import shutil
import threading

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPushButton, QTextEdit, QMessageBox,
    QHBoxLayout, QListWidget, QLabel, QApplication, QLineEdit
)
import logging

from Manager.ConfigManager import ConfigManager
from utils.loggerUtils import LogEmitter, setup_logger
from utils.SystemCore import (
    repair_network, reset_dns, release_and_renew_ip, reset_proxy, reset_winsock,
    check_hosts_file, get_current_dns, scan_fastest_dns,
    set_dns, DNS_INFO, is_admin
)

logger = setup_logger("SystemTool")

class DNSScanWorker(QThread):
    scan_completed = Signal(list, str)  # results, fastest_dns

    def __init__(self, dns_list):
        super().__init__()
        self.dns_list = dns_list

    def run(self):
        try:
            results, fastest_dns = scan_fastest_dns(self.dns_list)
            self.scan_completed.emit(results, fastest_dns)
        except Exception as e:
            logger.error(f"DNS 扫描线程出错: {str(e)}")
            self.scan_completed.emit([], "None")

class SetDNSWorker(QThread):
    set_completed = Signal(bool, str)  # success, message

    def __init__(self, primary_dns, secondary_dns, is_primary=True):
        super().__init__()
        self.primary_dns = primary_dns
        self.secondary_dns = secondary_dns
        self.is_primary = is_primary

    def run(self):
        try:
            success = set_dns(self.primary_dns, self.secondary_dns)
            if success:
                if self.is_primary:
                    message = f"已将主 DNS 设置为: {self.primary_dns}"
                else:
                    message = f"已将副 DNS 设置为: {self.secondary_dns}"
                self.set_completed.emit(True, message)
            else:
                if self.is_primary:
                    message = f"设置主 DNS 失败: {self.primary_dns}"
                else:
                    message = f"设置副 DNS 失败: {self.secondary_dns}"
                self.set_completed.emit(False, message)
        except Exception as e:
            if self.is_primary:
                message = f"设置主 DNS 出现异常: {str(e)}"
            else:
                message = f"设置副 DNS 出现异常: {str(e)}"
            self.set_completed.emit(False, message)

class CleanupWorker(QThread):
    cleanup_completed = Signal(int, list)  # deleted_count, failed_files

    def __init__(self, temp_path):
        super().__init__()
        self.temp_path = temp_path

    def run(self):
        deleted_count = 0
        failed_files = []
        if not os.path.exists(self.temp_path):
            logger.error(f"临时文件夹路径不存在: {self.temp_path}")
            self.cleanup_completed.emit(deleted_count, failed_files)
            return
        try:
            for root, dirs, files in os.walk(self.temp_path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"已删除文件: {file_path}")
                    except Exception as e:
                        logger.error(f"无法删除文件 {file_path}: {str(e)}")
                        failed_files.append(file_path)
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    try:
                        shutil.rmtree(dir_path)
                        deleted_count += 1
                        logger.info(f"已删除文件夹: {dir_path}")
                    except Exception as e:
                        logger.error(f"无法删除文件夹 {dir_path}: {str(e)}")
                        failed_files.append(dir_path)
            self.cleanup_completed.emit(deleted_count, failed_files)
        except Exception as e:
            logger.error(f"清理临时文件时出错: {str(e)}")
            self.cleanup_completed.emit(deleted_count, failed_files)

class SystemWorker(QThread):
    completed = Signal(bool, str)  # success, message

    def __init__(self, func, success_msg, failure_msg):
        super().__init__()
        self.func = func
        self.success_msg = success_msg
        self.failure_msg = failure_msg

    def run(self):
        try:
            result = self.func()
            if result:
                self.completed.emit(True, self.success_msg)
            else:
                self.completed.emit(False, self.failure_msg)
        except Exception as e:
            self.completed.emit(False, f"{self.failure_msg}: {str(e)}")

class SystemTool(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.init_ui()
        self.check_admin()

    def init_ui(self):
        self.setWindowTitle('专家系统维护工具')
        self.setGeometry(100, 100, 800, 600)
        main_layout = QVBoxLayout()

        # 日志发射器
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.handle_log)

        # 设置 logger 使用发射器
        global logger
        logger = setup_logger("SystemCore", log_emitter=self.log_emitter)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # 网络修复标签页
        network_tab = QWidget()
        network_layout = QHBoxLayout()
        network_tab.setLayout(network_layout)

        self.repair_network_btn = QPushButton('修复网络问题', self)
        self.repair_network_btn.setIcon(QIcon.fromTheme("network-repair"))
        self.repair_network_btn.clicked.connect(
            lambda: self.confirm_and_execute(repair_network, "网络修复操作已完成。", "网络修复操作失败。")
        )
        network_layout.addWidget(self.repair_network_btn)

        self.reset_dns_btn = QPushButton('重置 DNS', self)
        self.reset_dns_btn.setIcon(QIcon.fromTheme("network-dns-reset"))
        self.reset_dns_btn.clicked.connect(
            lambda: self.confirm_and_execute(reset_dns, "DNS 重置操作已完成。", "DNS 重置操作失败。")
        )
        network_layout.addWidget(self.reset_dns_btn)

        self.release_renew_ip_btn = QPushButton('释放并刷新 IP 地址', self)
        self.release_renew_ip_btn.setIcon(QIcon.fromTheme("network-ip-refresh"))
        self.release_renew_ip_btn.clicked.connect(
            lambda: self.confirm_and_execute(release_and_renew_ip, "IP 地址释放并刷新操作已完成。", "IP 地址释放并刷新操作失败。")
        )
        network_layout.addWidget(self.release_renew_ip_btn)

        tabs.addTab(network_tab, "网络修复")

        # 系统修复标签页
        system_tab = QWidget()
        system_layout = QHBoxLayout()
        system_tab.setLayout(system_layout)

        self.reset_proxy_btn = QPushButton('关闭所有代理', self)
        self.reset_proxy_btn.setIcon(QIcon.fromTheme("network-proxy"))
        self.reset_proxy_btn.clicked.connect(
            lambda: self.confirm_and_execute(reset_proxy, "代理设置已重置。", "关闭代理设置失败。")
        )
        system_layout.addWidget(self.reset_proxy_btn)

        self.reset_winsock_btn = QPushButton('重置 Winsock', self)
        self.reset_winsock_btn.setIcon(QIcon.fromTheme("network-winsock-reset"))
        self.reset_winsock_btn.clicked.connect(
            lambda: self.confirm_and_execute(reset_winsock, "Winsock 重置操作已完成。", "Winsock 重置操作失败。")
        )
        system_layout.addWidget(self.reset_winsock_btn)

        self.check_hosts_btn = QPushButton('检测 HOSTS 文件', self)
        self.check_hosts_btn.setIcon(QIcon.fromTheme("document-check"))
        self.check_hosts_btn.clicked.connect(self.check_hosts_file)
        system_layout.addWidget(self.check_hosts_btn)

        tabs.addTab(system_tab, "系统修复")

        # 临时文件清理标签页
        temp_cleanup_tab = QWidget()
        temp_cleanup_layout = QVBoxLayout()
        temp_cleanup_tab.setLayout(temp_cleanup_layout)

        self.cleanup_temp_btn = QPushButton('清理临时文件', self)
        self.cleanup_temp_btn.setIcon(QIcon.fromTheme("folder-cleanup"))
        self.cleanup_temp_btn.clicked.connect(self.start_cleanup)
        temp_cleanup_layout.addWidget(self.cleanup_temp_btn)

        tabs.addTab(temp_cleanup_tab, "临时文件清理")

        # DNS 管理标签页
        dns_tab = QWidget()
        dns_layout = QVBoxLayout()
        dns_tab.setLayout(dns_layout)

        self.current_dns_label = QLabel("当前 DNS: 未检测")
        dns_layout.addWidget(self.current_dns_label)

        self.current_secondary_dns_label = QLabel("当前次 DNS: 未检测")
        dns_layout.addWidget(self.current_secondary_dns_label)

        self.scan_dns_btn = QPushButton('扫描最快 DNS', self)
        self.scan_dns_btn.setIcon(QIcon.fromTheme("network-scan"))
        self.scan_dns_btn.clicked.connect(self.scan_fastest_dns)
        dns_layout.addWidget(self.scan_dns_btn)

        self.dns_list = QListWidget(self)
        self.dns_list.itemDoubleClicked.connect(self.set_dns_via_double_click)
        dns_layout.addWidget(self.dns_list)

        # 设置主 DNS
        primary_dns_layout = QHBoxLayout()
        self.primary_dns_input = QLineEdit()
        self.primary_dns_input.setPlaceholderText("主 DNS")
        primary_dns_layout.addWidget(QLabel("主 DNS:"))
        primary_dns_layout.addWidget(self.primary_dns_input)

        self.set_primary_dns_btn = QPushButton('设置主 DNS', self)
        self.set_primary_dns_btn.setIcon(QIcon.fromTheme("network-dns-set"))
        self.set_primary_dns_btn.clicked.connect(self.set_primary_dns)
        primary_dns_layout.addWidget(self.set_primary_dns_btn)

        dns_layout.addLayout(primary_dns_layout)

        # 设置副 DNS
        secondary_dns_layout = QHBoxLayout()
        self.secondary_dns_input = QLineEdit()
        self.secondary_dns_input.setPlaceholderText("副 DNS")
        secondary_dns_layout.addWidget(QLabel("副 DNS:"))
        secondary_dns_layout.addWidget(self.secondary_dns_input)

        self.set_secondary_dns_btn = QPushButton('设置副 DNS', self)
        self.set_secondary_dns_btn.setIcon(QIcon.fromTheme("network-dns-set"))
        self.set_secondary_dns_btn.clicked.connect(self.set_secondary_dns)
        secondary_dns_layout.addWidget(self.set_secondary_dns_btn)

        dns_layout.addLayout(secondary_dns_layout)

        tabs.addTab(dns_tab, "DNS 管理")

        # 状态日志
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont('Microsoft YaHei', 10))
        main_layout.addWidget(self.status_text)

        self.setLayout(main_layout)
        self.update_current_dns()

    def handle_log(self, level, message):
        self.status_text.append(f"{level}: {message}")
        # 自动滚动到底部
        self.status_text.verticalScrollBar().setValue(self.status_text.verticalScrollBar().maximum())

    def check_admin(self):
        if not is_admin():
            QMessageBox.critical(
                self,
                "权限不足",
                "请以管理员身份运行本程序。",
                QMessageBox.StandardButton.Ok
            )
            sys.exit(1)

    def confirm_and_execute(self, func, success_msg="操作已完成。", failure_msg="操作失败。"):
        reply = QMessageBox.question(
            self,
            '确认操作',
            '你确定要执行此操作吗?\n注意：需要以管理员身份运行本程序。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # 使用 SystemWorker 处理系统操作
            self.system_worker = SystemWorker(func, success_msg, failure_msg)
            self.system_worker.completed.connect(self.handle_system_operation)
            self.system_worker.start()

    def handle_system_operation(self, success, message):
        if success:
            self.log_emitter.log_signal.emit("INFO", message)
            QMessageBox.information(self, "操作完成", message)
        else:
            self.log_emitter.log_signal.emit("ERROR", message)
            QMessageBox.critical(self, "操作失败", message)

    def check_hosts_file(self):
        self.log_emitter.log_signal.emit("INFO", "正在检测 HOSTS 文件...")
        result = check_hosts_file()
        if result is None:
            self.log_emitter.log_signal.emit("ERROR", "读取 HOSTS 文件失败。")
            QMessageBox.critical(self, "HOSTS 文件检测", "读取 HOSTS 文件失败。")
        elif result:
            self.log_emitter.log_signal.emit("WARNING", "检测到可疑的 HOSTS 条目：")
            for entry in result:
                self.log_emitter.log_signal.emit("WARNING", entry)
            QMessageBox.warning(self, "HOSTS 文件检测", "检测到可疑的 HOSTS 条目，请检查日志。")
        else:
            self.log_emitter.log_signal.emit("INFO", "HOSTS 文件未发现异常。")
            QMessageBox.information(self, "HOSTS 文件检测", "HOSTS 文件未发现异常。")

    def update_current_dns(self):
        current_dns, current_secondary_dns = get_current_dns()
        if current_dns:
            self.current_dns_label.setText(f"当前 DNS: {current_dns}")
        else:
            self.current_dns_label.setText("当前 DNS: 未检测")
        if current_secondary_dns:
            self.current_secondary_dns_label.setText(f"当前次 DNS: {current_secondary_dns}")
        else:
            self.current_secondary_dns_label.setText("当前次 DNS: 未检测")

    def scan_fastest_dns(self):
        self.log_emitter.log_signal.emit("INFO", "正在扫描最快的 DNS 服务器...")
        dns_list = list(DNS_INFO.keys())
        if not dns_list:
            QMessageBox.warning(self, "未配置 DNS", "请在配置文件中添加 DNS 服务器。")
            return
        self.dns_list.clear()
        self.scan_dns_btn.setEnabled(False)
        self.dns_scan_worker = DNSScanWorker(dns_list)
        self.dns_scan_worker.scan_completed.connect(self.handle_scan_results)
        self.dns_scan_worker.start()

    def handle_scan_results(self, results, fastest_dns):
        self.dns_list.clear()
        for dns, response_time in sorted(results, key=lambda x: x[1]):
            provider, region = DNS_INFO.get(dns, ("未知", "未知"))
            time_display = f"{response_time:.2f} 秒" if response_time != float('inf') else "无响应"
            self.dns_list.addItem(f"{dns} ({provider}, {region}) - {time_display}")
        if fastest_dns and fastest_dns != "None":
            self.log_emitter.log_signal.emit("INFO", f"扫描完成。最快的 DNS 是: {fastest_dns}")
            QMessageBox.information(self, "DNS 扫描", f"扫描完成。最快的 DNS 是: {fastest_dns}")
        else:
            self.log_emitter.log_signal.emit("ERROR", "未能找到可用的 DNS 服务器。")
            QMessageBox.warning(self, "DNS 扫描", "未能找到可用的 DNS 服务器。")
        self.scan_dns_btn.setEnabled(True)
        self.log_emitter.log_signal.emit("INFO", "DNS 扫描完成。")
        self.update_current_dns()

    def set_primary_dns(self):
        primary_dns = self.primary_dns_input.text().strip()
        if not primary_dns:
            QMessageBox.warning(self, "未输入主 DNS", "请填写主 DNS 地址。")
            return
        secondary_dns = self.secondary_dns_input.text().strip() or self.config_manager.get("system_repair", "secondary_dns", "114.114.114.114")
        self.log_emitter.log_signal.emit("INFO", f"正在设置主 DNS: {primary_dns} 和副 DNS: {secondary_dns}")
        self.set_dns_worker = SetDNSWorker(primary_dns, secondary_dns, is_primary=True)
        self.set_dns_worker.set_completed.connect(self.handle_set_dns)
        self.set_dns_worker.start()

    def set_secondary_dns(self):
        secondary_dns = self.secondary_dns_input.text().strip()
        if not secondary_dns:
            QMessageBox.warning(self, "未输入副 DNS", "请填写副 DNS 地址。")
            return
        primary_dns = self.primary_dns_input.text().strip()
        if not primary_dns:
            QMessageBox.warning(self, "未输入主 DNS", "请先设置主 DNS。")
            return
        self.log_emitter.log_signal.emit("INFO", f"正在设置副 DNS: {secondary_dns}")
        self.set_dns_worker = SetDNSWorker(primary_dns, secondary_dns, is_primary=False)
        self.set_dns_worker.set_completed.connect(self.handle_set_dns)
        self.set_dns_worker.start()

    def handle_set_dns(self, success, message):
        if success:
            self.log_emitter.log_signal.emit("INFO", message)
            QMessageBox.information(self, "设置 DNS 成功", message)
        else:
            self.log_emitter.log_signal.emit("ERROR", message)
            QMessageBox.critical(self, "设置 DNS 失败", message)
        self.update_current_dns()

    def set_dns_via_double_click(self, item):
        selected_dns = item.text().split(" ")[0]
        if not self.primary_dns_input.text().strip():
            self.primary_dns_input.setText(selected_dns)
            self.log_emitter.log_signal.emit("INFO", f"双击选择主 DNS: {selected_dns}")
        elif not self.secondary_dns_input.text().strip():
            self.secondary_dns_input.setText(selected_dns)
            self.log_emitter.log_signal.emit("INFO", f"双击选择副 DNS: {selected_dns}")
        else:
            QMessageBox.warning(self, "DNS 已设置", "主 DNS 和副 DNS 均已设置。")

    def start_cleanup(self):
        reply = QMessageBox.question(
            self,
            '确认操作',
            '你确定要清理临时文件吗?\n注意：需要以管理员身份运行本程序。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_temp_btn.setEnabled(False)
            self.status_text.append("正在清理临时文件...")
            temp_path = os.environ.get('TEMP', None)
            if not temp_path:
                self.log_emitter.log_signal.emit("ERROR", "无法找到临时文件夹路径。")
                QMessageBox.critical(self, "清理失败", "无法找到临时文件夹路径。")
                self.cleanup_temp_btn.setEnabled(True)
                return
            self.cleanup_worker = CleanupWorker(temp_path)
            self.cleanup_worker.cleanup_completed.connect(self.handle_cleanup_result)
            self.cleanup_worker.start()

    def handle_cleanup_result(self, deleted_count, failed_files):
        self.cleanup_temp_btn.setEnabled(True)
        if deleted_count > 0:
            self.log_emitter.log_signal.emit("INFO", f"已成功清理 {deleted_count} 个文件和文件夹。")
            QMessageBox.information(self, "清理完成", f"已成功清理 {deleted_count} 个文件和文件夹。")
        else:
            self.log_emitter.log_signal.emit("INFO", "没有需要清理的文件。")
            QMessageBox.information(self, "清理完成", "没有需要清理的文件。")
        if failed_files:
            failed_message = "以下文件或文件夹无法删除（可能正在被使用）：\n" + "\n".join(failed_files)
            self.log_emitter.log_signal.emit("ERROR", failed_message)
            QMessageBox.warning(self, "清理部分失败", failed_message)
        else:
            self.log_emitter.log_signal.emit("INFO", "所有临时文件已成功清理。")
        self.status_text.append("INFO: 临时文件清理完成。")

def main():
    try:
        app = QApplication(sys.argv)
        system_tool = SystemTool()
        system_tool.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"main错误: {str(e)}")

if __name__ == "__main__":
    main()
