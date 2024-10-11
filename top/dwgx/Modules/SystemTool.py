

import os
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPushButton, QTextEdit, QMessageBox,
    QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QApplication, QGroupBox,
    QGridLayout, QDialog, QMenu
)
import subprocess
import platform
import logging
import threading
import time
import re
import shutil

from Manager.ConfigManager import ConfigManager
from utils.loggerUtils import LogEmitter, setup_logger
from utils.IconImageUtils import icon_image_utils

DNS_INFO = {
    "8.8.8.8": ("Google DNS", "全球"),
    "8.8.4.4": ("Google DNS", "全球"),
    "1.1.1.1": ("Cloudflare DNS", "全球"),
    "1.0.0.1": ("Cloudflare DNS", "全球"),
    "9.9.9.9": ("Quad9 DNS", "全球"),
    "149.112.112.112": ("Quad9 DNS", "全球"),
    "208.67.222.222": ("OpenDNS", "全球"),
    "208.67.220.220": ("OpenDNS", "全球"),
    "8.26.56.26": ("Comodo Secure DNS", "全球"),
    "8.20.247.20": ("Comodo Secure DNS", "全球"),
    "4.2.2.2": ("Level3 DNS", "全球"),
    "4.2.2.1": ("Level3 DNS", "全球"),
    "208.67.222.123": ("OpenDNS Family Shield", "全球"),
    "208.67.220.123": ("OpenDNS Family Shield", "全球"),
    "114.114.114.114": ("中国电信 DNS", "中国"),
    "223.5.5.5": ("阿里云 DNS", "中国"),
    "223.6.6.6": ("阿里云 DNS", "中国"),
    "180.76.76.76": ("百度 DNS", "中国"),
    "119.29.29.29": ("DNSPod DNS", "中国"),
    "182.254.116.116": ("腾讯 DNS", "中国"),
    "119.28.28.28": ("腾讯 DNS", "中国"),
    "140.207.198.241": ("中国移动 DNS", "中国"),
    "210.140.92.20": ("NTT Communications", "日本"),
}

logger = setup_logger("SystemTool")


class SystemTool(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('专家系统维护工具')
        self.setGeometry(100, 100, 800, 600)
        main_layout = QVBoxLayout()


        tabs = QTabWidget()
        main_layout.addWidget(tabs)


        network_tab = QWidget()
        network_layout = QHBoxLayout()
        network_tab.setLayout(network_layout)

        self.repair_network_btn = QPushButton('修复网络问题', self)
        self.repair_network_btn.setIcon(QIcon.fromTheme("network-repair"))
        self.repair_network_btn.clicked.connect(self.confirm_and_execute(self.repair_network))
        network_layout.addWidget(self.repair_network_btn)

        self.reset_dns_btn = QPushButton('重置 DNS', self)
        self.reset_dns_btn.setIcon(QIcon.fromTheme("network-dns-reset"))
        self.reset_dns_btn.clicked.connect(self.confirm_and_execute(self.reset_dns))
        network_layout.addWidget(self.reset_dns_btn)

        self.release_renew_ip_btn = QPushButton('释放并刷新 IP 地址', self)
        self.release_renew_ip_btn.setIcon(QIcon.fromTheme("network-ip-refresh"))
        self.release_renew_ip_btn.clicked.connect(self.confirm_and_execute(self.release_and_renew_ip))
        network_layout.addWidget(self.release_renew_ip_btn)

        tabs.addTab(network_tab, "网络修复")


        system_tab = QWidget()
        system_layout = QHBoxLayout()
        system_tab.setLayout(system_layout)

        self.reset_proxy_btn = QPushButton('关闭所有代理', self)
        self.reset_proxy_btn.setIcon(QIcon.fromTheme("network-proxy"))
        self.reset_proxy_btn.clicked.connect(self.confirm_and_execute(self.reset_proxy))
        system_layout.addWidget(self.reset_proxy_btn)

        self.reset_winsock_btn = QPushButton('重置 Winsock', self)
        self.reset_winsock_btn.setIcon(QIcon.fromTheme("network-winsock-reset"))
        self.reset_winsock_btn.clicked.connect(self.confirm_and_execute(self.reset_winsock))
        system_layout.addWidget(self.reset_winsock_btn)

        self.check_hosts_btn = QPushButton('检测 HOSTS 文件', self)
        self.check_hosts_btn.setIcon(QIcon.fromTheme("document-check"))
        self.check_hosts_btn.clicked.connect(self.check_hosts_file)
        system_layout.addWidget(self.check_hosts_btn)

        tabs.addTab(system_tab, "系统修复")


        temp_cleanup_tab = QWidget()
        temp_cleanup_layout = QVBoxLayout()
        temp_cleanup_tab.setLayout(temp_cleanup_layout)

        self.cleanup_temp_btn = QPushButton('清理临时文件', self)
        self.cleanup_temp_btn.setIcon(QIcon.fromTheme("folder-cleanup"))
        self.cleanup_temp_btn.clicked.connect(self.confirm_and_execute(self.cleanup_temp_files))
        temp_cleanup_layout.addWidget(self.cleanup_temp_btn)

        tabs.addTab(temp_cleanup_tab, "临时文件清理")


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

        self.set_dns_btn = QPushButton('设置为当前 DNS', self)
        self.set_dns_btn.setIcon(QIcon.fromTheme("network-dns-set"))
        self.set_dns_btn.clicked.connect(self.set_selected_dns)
        dns_layout.addWidget(self.set_dns_btn)

        tabs.addTab(dns_tab, "DNS 管理")


        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont('Microsoft YaHei', 10))
        main_layout.addWidget(self.status_text)

        self.setLayout(main_layout)
        self.update_current_dns()

    def log(self, message):
        self.status_text.append(message)
        logger.info(message)

    def execute_command(self, command):
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            self.log(output.strip())
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"命令执行失败: {e.output.strip()}")
            return False
        except Exception as e:
            self.log(f"命令执行出现异常: {str(e)}")
            return False

    def confirm_and_execute(self, func):
        def wrapper():
            reply = QMessageBox.question(
                self,
                '确认操作',
                '你确定要执行此操作吗?\n注意：需要以管理员身份运行本程序。',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                func()
        return wrapper

    def repair_network(self):
        self.log("正在修复网络问题...")
        if self.execute_command("netsh int ip reset"):
            self.log("已成功重置 IP 协议栈。")
        else:
            self.log("重置 IP 协议栈失败。请以管理员身份运行本程序。")
        if self.execute_command("netsh winsock reset"):
            self.log("已成功重置 Winsock。")
        else:
            self.log("重置 Winsock 失败。请以管理员身份运行本程序。")
        self.log("网络修复操作已完成。")
        QMessageBox.information(self, "网络修复", "网络修复操作已完成。")

    def reset_dns(self):
        self.log("正在重置 DNS...")
        if self.execute_command("ipconfig /flushdns"):
            self.log("已成功刷新 DNS 缓存。")
        else:
            self.log("刷新 DNS 缓存失败。")
        self.log("DNS 重置操作已完成。")
        QMessageBox.information(self, "DNS 重置", "DNS 重置操作已完成。")

    def release_and_renew_ip(self):
        self.log("正在释放并刷新 IP 地址...")
        if self.execute_command("ipconfig /release") and self.execute_command("ipconfig /renew"):
            self.log("已成功释放并刷新 IP 地址。")
        else:
            self.log("释放或刷新 IP 地址失败。请以管理员身份运行本程序。")
        self.log("IP 地址释放并刷新操作已完成。")
        QMessageBox.information(self, "IP 地址刷新", "IP 地址释放并刷新操作完成。")

    def reset_proxy(self):
        self.log("正在关闭所有代理设置...")
        commands = [
            'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /f',
            'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /f',
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f',
            "netsh winhttp reset proxy"
        ]
        success = True
        for cmd in commands:
            if not self.execute_command(cmd):
                success = False
        if success:
            self.log("已成功关闭所有代理设置。")
            QMessageBox.information(self, "代理设置", "代理设置已重置。")
        else:
            self.log("关闭代理设置失败。请以管理员身份运行本程序。")
            QMessageBox.warning(self, "代理设置", "关闭代理设置失败。请以管理员身份运行本程序。")

    def reset_winsock(self):
        self.log("正在重置 Winsock...")
        if self.execute_command("netsh winsock reset"):
            self.log("已成功重置 Winsock。")
        else:
            self.log("重置 Winsock 失败。请以管理员身份运行本程序。")
        self.log("Winsock 重置操作已完成。")
        QMessageBox.information(self, "Winsock 重置", "Winsock 重置操作已完成。")

    def check_hosts_file(self):
        self.log("正在检测 HOSTS 文件...")
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            with open(hosts_path, 'r') as f:
                content = f.read()
                suspicious_entries = []
                for line in content.splitlines():
                    if line.strip() and not line.startswith('#'):
                        if 'localhost' not in line and '::1' not in line:
                            suspicious_entries.append(line)
                if suspicious_entries:
                    self.log("检测到可疑的 HOSTS 条目：")
                    for entry in suspicious_entries:
                        self.log(entry)
                    QMessageBox.warning(self, "HOSTS 文件检测", "检测到可疑的 HOSTS 条目，请检查日志。")
                else:
                    self.log("HOSTS 文件未发现异常。")
                    QMessageBox.information(self, "HOSTS 文件检测", "HOSTS 文件未发现异常。")
        except Exception as e:
            self.log(f"读取 HOSTS 文件失败: {str(e)}")
            QMessageBox.critical(self, "HOSTS 文件检测", f"读取 HOSTS 文件失败: {str(e)}")

    def cleanup_temp_files(self):
        self.log("正在清理临时文件...")
        temp_path = os.environ.get('TEMP', None)
        if temp_path and os.path.exists(temp_path):
            try:
                file_count = 0
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            file_count += 1
                        except Exception as e:
                            self.log(f"无法删除文件 {file_path}: {str(e)}")
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            shutil.rmtree(dir_path)
                            file_count += 1
                        except Exception as e:
                            self.log(f"无法删除文件夹 {dir_path}: {str(e)}")
                self.log(f"临时文件清理完成，删除了 {file_count} 个文件和文件夹。")
                QMessageBox.information(self, "清理完成", f"临时文件清理完成，删除了 {file_count} 个文件和文件夹。")
            except Exception as e:
                self.log(f"清理临时文件失败: {str(e)}")
                QMessageBox.critical(self, "清理失败", f"清理临时文件失败: {str(e)}")
        else:
            self.log("无法找到临时文件夹路径。")
            QMessageBox.warning(self, "清理失败", "无法找到临时文件夹路径。")

    def update_current_dns(self):
        try:
            if platform.system() == "Windows":
                command = "ipconfig /all"
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                dns_servers = re.findall(r"DNS Servers[ .]*?:\s*([^\n]+)", output)
                if dns_servers:
                    dns_list = dns_servers[0].split()
                    current_dns = dns_list[0]
                    current_secondary_dns = dns_list[1] if len(dns_list) > 1 else "未设置"
                else:
                    current_dns = "未设置"
                    current_secondary_dns = "未设置"
            else:
                with open('/etc/resolv.conf', 'r') as f:
                    dns_servers = [line.split()[1] for line in f if line.startswith('nameserver')]
                current_dns = dns_servers[0] if dns_servers else "未设置"
                current_secondary_dns = dns_servers[1] if len(dns_servers) > 1 else "未设置"
            self.current_dns_label.setText(f"当前 DNS: {current_dns}")
            self.current_secondary_dns_label.setText(f"当前次 DNS: {current_secondary_dns}")
            self.log(f"当前 DNS 设置: {current_dns}")
            self.log(f"当前次 DNS 设置: {current_secondary_dns}")
        except Exception as e:
            self.log(f"获取当前 DNS 设置失败: {str(e)}")

    def scan_fastest_dns(self):
        dns_list = self.config_manager.get("system_repair", "dns_servers", [])
        if not dns_list:
            QMessageBox.warning(self, "未配置 DNS", "请在配置文件中添加 DNS 服务器。")
            return
        self.log("正在扫描主 DNS 服务器速度...")
        fastest_dns = None
        fastest_time = float('inf')
        results = []

        def ping_dns(dns):
            try:
                start_time = time.time()
                if platform.system() == "Windows":
                    command = f"ping -n 1 -w 1000 {dns}"
                else:
                    command = f"ping -c 1 -W 1 {dns}"
                subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                end_time = time.time()
                return dns, end_time - start_time
            except subprocess.CalledProcessError:
                return dns, float('inf')

        threads = []
        results_lock = threading.Lock()
        for dns in dns_list:
            thread = threading.Thread(target=lambda d=dns: self.add_ping_result(ping_dns(d), results, results_lock))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        for dns, response_time in results:
            provider, region = DNS_INFO.get(dns, ("未知", "未知"))
            self.log(f"主 DNS: {dns} ({provider}, {region})，响应时间: {response_time:.2f} 秒")
            if response_time < fastest_time:
                fastest_time = response_time
                fastest_dns = dns
        if fastest_dns:
            self.log(f"最快的主 DNS 是: {fastest_dns} ({fastest_time:.2f} 秒)")
            self.dns_list.clear()
            for dns, response_time in sorted(results, key=lambda x: x[1]):
                provider, region = DNS_INFO.get(dns, ("未知", "未知"))
                self.dns_list.addItem(f"{dns} ({provider}, {region}) - {response_time:.2f} 秒")
        else:
            self.log("未能找到可用的主 DNS 服务器。")

    def add_ping_result(self, result, results, lock):
        with lock:
            results.append(result)

    def set_selected_dns(self):
        selected_items = self.dns_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择 DNS", "请选择一个 DNS 服务器来设置。")
            return
        selected_dns = selected_items[0].text().split(" ")[0]
        self.set_dns(selected_dns)

    def set_dns_via_double_click(self, item):
        selected_dns = item.text().split(" ")[0]
        self.log(f"双击设置 DNS: {selected_dns}")
        self.set_dns(selected_dns)

    def set_dns(self, selected_dns):
        secondary_dns = self.config_manager.get("system_repair", "secondary_dns", "114.114.114.114")
        fallback_secondary_dns = self.config_manager.get("system_repair", "fallback_secondary_dns", "8.8.8.8")
        try:
            if platform.system() == "Windows":
                interface_name = self.get_active_interface()
                if not interface_name:
                    self.log("未找到活动的网络接口。")
                    QMessageBox.critical(self, "设置 DNS 失败", "未找到活动的网络接口。")
                    return
                primary_command = f'netsh interface ip set dns name="{interface_name}" static {selected_dns} primary'
                if self.execute_command(primary_command):
                    self.log(f"已将主 DNS 设置为: {selected_dns}")
                else:
                    self.log(f"设置主 DNS 失败: {selected_dns}")
                    QMessageBox.critical(self, "设置 DNS 失败", f"设置主 DNS 失败: {selected_dns}")
                    return
                secondary_command = f'netsh interface ip add dns name="{interface_name}" addr={secondary_dns} index=2'
                if self.execute_command(secondary_command):
                    self.log(f"已将次 DNS 设置为: {secondary_dns}")
                else:
                    self.log(f"设置次 DNS 失败: {secondary_dns}，尝试设置备用次 DNS: {fallback_secondary_dns}")
                    fallback_command = f'netsh interface ip add dns name="{interface_name}" addr={fallback_secondary_dns} index=2'
                    if self.execute_command(fallback_command):
                        self.log(f"已将备用次 DNS 设置为: {fallback_secondary_dns}")
                        self.config_manager.set("system_repair", "secondary_dns", fallback_secondary_dns)
                    else:
                        self.log(f"设置备用次 DNS 失败: {fallback_secondary_dns}")
                        QMessageBox.critical(self, "设置 DNS 失败", f"设置备用次 DNS 失败: {fallback_secondary_dns}")
                        return
                QMessageBox.information(self, "设置 DNS", f"已将 DNS 设置为:\n主 DNS: {selected_dns}\n次 DNS: {secondary_dns}")
                self.update_current_dns()
            else:
                with open('/etc/resolv.conf', 'w') as f:
                    f.write(f"nameserver {selected_dns}\n")
                    f.write(f"nameserver {secondary_dns}\n")
                self.log(f"已将 DNS 设置为: {selected_dns} 和 次 DNS: {secondary_dns}")
                QMessageBox.information(self, "设置 DNS", f"已将 DNS 设置为: {selected_dns} 和 次 DNS: {secondary_dns}")
                self.update_current_dns()
        except Exception as e:
            self.log(f"设置 DNS 失败: {str(e)}")
            QMessageBox.critical(self, "设置 DNS 失败", f"设置 DNS 失败: {str(e)}")

    def get_active_interface(self):
        try:
            command = "netsh interface show interface"
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
            for line in output.splitlines():
                if "已连接" in line or "Connected" in line:
                    match = re.search(r"(已连接|Connected)\s+(专用|Dedicated)\s+([^\s]+)", line)
                    if match:
                        interface_name = match.group(3)
                        return interface_name
                    else:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            interface_name = parts[-1]
                            return interface_name
            return None
        except subprocess.CalledProcessError as e:
            self.log(f"获取活动网络接口失败: {e.output}")
            return None
        except Exception as e:
            self.log(f"获取活动网络接口出现异常: {str(e)}")
            return None

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
