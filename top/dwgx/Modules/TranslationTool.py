# top.dwgx.Modules.TranslationTool

import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from threading import Timer
import keyboard
import pyperclip
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QComboBox, QSlider, QMessageBox
)
from PyQt6.QtGui import QIcon

from top.dwgx.Manager.ConfigManager import ConfigManager, ALLOWED_LANGUAGES
from top.dwgx.utils.Translationcore import perform_translation
from top.dwgx.utils.loggerutils import LogEmitter, setup_logger
from top.dwgx.utils.SetApiKeyDialog import SetApiKeyDialog


class TranslationTool(QWidget):
    def __init__(self):
        super().__init__()
        self.current_hotkeys = {"shortcut1": None, "shortcut2": None}
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.config_manager = ConfigManager()
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)
        self.logger = setup_logger("TranslationTool", self.log_emitter)

        # 初始化 UI
        self.text_edit = None
        self.translate_button1 = None
        self.translate_button2 = None
        self.log_edit = None
        self.shortcut_input1 = None
        self.set_shortcut_button1 = None
        self.target_lang_combo1 = None
        self.shortcut_input2 = None
        self.set_shortcut_button2 = None
        self.target_lang_combo2 = None
        self.delay_label = None
        self.delay_slider = None
        self.current_delay_label = None

        self.init_ui()
        self.load_config()
        self.start_listening_thread()

    def append_log(self, level, message):
        color = {
            "ERROR": Qt.GlobalColor.red,
            "WARNING": Qt.GlobalColor.yellow,
            "INFO": Qt.GlobalColor.green
        }.get(level, Qt.GlobalColor.white)

        self.log_edit.setTextColor(color)
        self.log_edit.append(message)

    def init_ui(self):
        self.setWindowTitle('Translation Tool')
        self.setWindowIcon(QIcon.fromTheme("applications-education-language"))
        self.resize(800, 800)

        main_layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        main_layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        self.translate_button1 = QPushButton("翻译1", self)
        self.translate_button1.setIcon(QIcon.fromTheme("media-playback-start"))
        self.translate_button1.clicked.connect(self.translate_text1)
        button_layout.addWidget(self.translate_button1)

        self.translate_button2 = QPushButton("翻译2", self)
        self.translate_button2.setIcon(QIcon.fromTheme("media-playback-start"))
        self.translate_button2.clicked.connect(self.translate_text2)
        button_layout.addWidget(self.translate_button2)

        main_layout.addLayout(button_layout)

        self.log_edit = QTextEdit(self)
        self.log_edit.setReadOnly(True)
        self.log_edit.setStyleSheet("background-color: black; color: white;")
        main_layout.addWidget(self.log_edit)

        shortcut_layout = QGridLayout()
        self.shortcut_input1 = QLineEdit(self)
        self.shortcut_input1.setPlaceholderText("输入快捷键1 (例如: ctrl+alt+t)")
        self.set_shortcut_button1 = QPushButton("设置快捷键1", self)
        self.set_shortcut_button1.setIcon(QIcon.fromTheme("document-save"))
        self.set_shortcut_button1.clicked.connect(self.set_shortcut1)
        self.target_lang_combo1 = QComboBox(self)
        shortcut_layout.addWidget(QLabel("快捷键1:", self), 0, 0)
        shortcut_layout.addWidget(self.shortcut_input1, 0, 1)
        shortcut_layout.addWidget(self.set_shortcut_button1, 0, 2)
        shortcut_layout.addWidget(QLabel("目标语言1:", self), 1, 0)
        shortcut_layout.addWidget(self.target_lang_combo1, 1, 1)

        self.shortcut_input2 = QLineEdit(self)
        self.shortcut_input2.setPlaceholderText("输入快捷键2 (例如: ctrl+alt+y)")
        self.set_shortcut_button2 = QPushButton("设置快捷键2", self)
        self.set_shortcut_button2.setIcon(QIcon.fromTheme("document-save"))
        self.set_shortcut_button2.clicked.connect(self.set_shortcut2)
        self.target_lang_combo2 = QComboBox(self)
        shortcut_layout.addWidget(QLabel("快捷键2:", self), 2, 0)
        shortcut_layout.addWidget(self.shortcut_input2, 2, 1)
        shortcut_layout.addWidget(self.set_shortcut_button2, 2, 2)
        shortcut_layout.addWidget(QLabel("目标语言2:", self), 3, 0)
        shortcut_layout.addWidget(self.target_lang_combo2, 3, 1)

        main_layout.addLayout(shortcut_layout)

        self.target_lang_combo1.currentIndexChanged.connect(self.on_target_lang1_changed)
        self.target_lang_combo2.currentIndexChanged.connect(self.on_target_lang2_changed)

        delay_layout = QHBoxLayout()
        self.delay_label = QLabel("延迟 (毫秒):", self)
        self.delay_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.delay_slider.setMinimum(0)
        self.delay_slider.setMaximum(1000)
        self.delay_slider.setValue(self.config_manager.get("translation", "copy_delay_ms", 100))
        self.delay_slider.setTickInterval(100)
        self.delay_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.delay_slider.valueChanged.connect(self.update_delay_label)
        self.current_delay_label = QLabel(f"{self.delay_slider.value()} ms", self)

        delay_layout.addWidget(self.delay_label)
        delay_layout.addWidget(self.delay_slider)
        delay_layout.addWidget(self.current_delay_label)
        main_layout.addLayout(delay_layout)

        self.setLayout(main_layout)

        settings_button = QPushButton("设置 API 密钥", self)
        settings_button.setIcon(QIcon.fromTheme("document-print"))
        settings_button.clicked.connect(self.open_settings_dialog)
        main_layout.addWidget(settings_button)

    def set_shortcut1(self):
        try:
            shortcut = self.shortcut_input1.text().strip()
            if shortcut:
                if self.current_hotkeys["shortcut1"]:
                    keyboard.remove_hotkey(self.current_hotkeys["shortcut1"])
                self.current_hotkeys["shortcut1"] = shortcut
                self.config_manager.set("translation", "shortcut1", shortcut)
                keyboard.add_hotkey(shortcut, self.translate_from_shortcut1)
                self.logger.info(f"快捷键1已设置为: {shortcut}")
            else:
                self.logger.warning("快捷键1不能为空")
        except Exception as e:
            self.logger.error(f"set_shortcut1错误: {str(e)}")

    def set_shortcut2(self):
        try:
            shortcut = self.shortcut_input2.text().strip()
            if shortcut:
                if self.current_hotkeys["shortcut2"]:
                    keyboard.remove_hotkey(self.current_hotkeys["shortcut2"])
                self.current_hotkeys["shortcut2"] = shortcut
                self.config_manager.set("translation", "shortcut2", shortcut)
                keyboard.add_hotkey(shortcut, self.translate_from_shortcut2)
                self.logger.info(f"快捷键2已设置为: {shortcut}")
            else:
                self.logger.warning("快捷键2不能为空")
        except Exception as e:
            self.logger.error(f"set_shortcut2错误: {str(e)}")

    def on_target_lang1_changed(self):
        index = self.target_lang_combo1.currentIndex()
        target_lang = self.target_lang_combo1.itemData(index)
        current_target_lang1 = self.config_manager.get("translation", "target_lang1")
        if target_lang and target_lang != current_target_lang1:
            self.config_manager.set("translation", "target_lang1", target_lang)
            self.logger.info(f"目标语言1已更改为: {target_lang}")

    def on_target_lang2_changed(self):
        index = self.target_lang_combo2.currentIndex()
        target_lang = self.target_lang_combo2.itemData(index)
        current_target_lang2 = self.config_manager.get("translation", "target_lang2")
        if target_lang and target_lang != current_target_lang2:
            self.config_manager.set("translation", "target_lang2", target_lang)
            self.logger.info(f"目标语言2已更改为: {target_lang}")

    def translate_text1(self):
        try:
            target_lang = self.target_lang_combo1.currentData()
            self.translate_text(target_lang)
        except Exception as e:
            self.logger.error(f"translate_text1错误: {str(e)}")

    def translate_text2(self):
        try:
            target_lang = self.target_lang_combo2.currentData()
            self.translate_text(target_lang)
        except Exception as e:
            self.logger.error(f"translate_text2错误: {str(e)}")

    def translate_text(self, target_lang):
        try:
            if not target_lang:
                self.logger.warning("翻译错误: 未选择目标语言")
                return
            text = self.text_edit.toPlainText().strip()
            if not text:
                self.logger.warning("翻译错误: 文本不能为空")
                return
            self.logger.info(f"正在翻译文本: {text}")
            self.executor.submit(self.translate_task, text, target_lang)
        except Exception as e:
            self.logger.error(f"translate_text错误: {str(e)}")

    def translate_from_shortcut1(self):
        try:
            target_lang = self.config_manager.get("translation", "target_lang1", "en")
            self.translate_from_shortcut(target_lang, "shortcut1")
        except Exception as e:
            self.logger.error(f"translate_from_shortcut1错误: {str(e)}")

    def translate_from_shortcut2(self):
        try:
            target_lang = self.config_manager.get("translation", "target_lang2", "zh")
            self.translate_from_shortcut(target_lang, "shortcut2")
        except Exception as e:
            self.logger.error(f"translate_from_shortcut2错误: {str(e)}")

    def translate_from_shortcut(self, target_lang, shortcut):
        def is_clipboard_ready():
            text = pyperclip.paste().strip()
            return bool(text)

        try:
            delay_ms = self.config_manager.get("translation", "copy_delay_ms", 100)
            delay = delay_ms / 1000.0

            if is_clipboard_ready() and keyboard.is_pressed("ctrl"):
                keyboard.press_and_release('ctrl+a')
                Timer(delay, lambda: keyboard.press_and_release('ctrl+c')).start()
                Timer(delay + 0.1, lambda: self.handle_translation(target_lang, shortcut)).start()
            else:
                self.logger.warning("未能识别到剪贴板内容或未处于按键组合状态。")
        except Exception as e:
            self.logger.error(f"{shortcut}翻译错误: {str(e)}")

    def handle_translation(self, target_lang, shortcut):
        text = pyperclip.paste().strip()
        if not text:
            self.logger.warning(f"{shortcut}翻译错误: 文本不能为空")
            return
        self.logger.info(f"正在翻译剪贴板内容: {text}")
        self.executor.submit(self.translate_task, text, target_lang)

    def translate_task(self, text, target_lang):
        try:
            translation = perform_translation(text, target_lang, self.config_manager, self.logger)
            if "翻译错误" not in translation:
                Timer(0, lambda: self.update_clipboard_and_paste(translation)).start()
            else:
                self.logger.error("翻译任务失败，未更新剪贴板。")
        except Exception as e:
            self.logger.error(f"翻译任务错误: {str(e)}")

    def update_clipboard_and_paste(self, translation):
        pyperclip.copy(translation)
        if pyperclip.paste() == translation:
            try:
                keyboard.press_and_release('ctrl+v')
                self.logger.info("翻译结果已粘贴到剪贴板。")
            except Exception as e:
                self.logger.error(f"update_clipboard_and_paste错误: {str(e)}")
        else:
            self.logger.error(f"更新剪贴板内容失败，期望：{translation}")

    def update_delay_label(self, value):
        self.current_delay_label.setText(f"{value} ms")
        self.config_manager.set("translation", "copy_delay_ms", value)
        self.logger.info(f"复制延迟已设置为: {value} ms")

    def open_settings_dialog(self):
        settings_dialog = SetApiKeyDialog(self.config_manager, self.logger, self)
        if settings_dialog.exec():
            self.on_settings_saved()

    def on_settings_saved(self):
        QMessageBox.information(self, "设置保存", "API 密钥设置已更新。")

    def load_config(self):
        self.current_hotkeys["shortcut1"] = self.config_manager.get("translation", "shortcut1", "")
        self.current_hotkeys["shortcut2"] = self.config_manager.get("translation", "shortcut2", "")
        self.shortcut_input1.setText(self.current_hotkeys["shortcut1"])
        self.shortcut_input2.setText(self.current_hotkeys["shortcut2"])

        target_lang1 = self.config_manager.get("translation", "target_lang1", "en")
        target_lang2 = self.config_manager.get("translation", "target_lang2", "zh")

        self.target_lang_combo1.clear()
        self.target_lang_combo2.clear()
        for lang_code, lang_name in ALLOWED_LANGUAGES.items():
            self.target_lang_combo1.addItem(lang_name, lang_code)
            self.target_lang_combo2.addItem(lang_name, lang_code)

        self.set_combobox_current_index(self.target_lang_combo1, target_lang1)
        self.set_combobox_current_index(self.target_lang_combo2, target_lang2)

        self.register_shortcut("shortcut1", self.translate_from_shortcut1)
        self.register_shortcut("shortcut2", self.translate_from_shortcut2)

    def register_shortcut(self, shortcut_key, action):
        if self.current_hotkeys[shortcut_key]:
            try:
                keyboard.add_hotkey(self.current_hotkeys[shortcut_key], action)
                self.logger.info(f"已注册{shortcut_key}: {self.current_hotkeys[shortcut_key]}")
            except Exception as e:
                self.logger.error(f"注册{shortcut_key}失败: {str(e)}")

    def set_combobox_current_index(self, combobox, lang_code):
        for index in range(combobox.count()):
            if combobox.itemData(index) == lang_code:
                combobox.setCurrentIndex(index)
                return
        self.logger.warning(f"配置文件中指定的语言代码 '{lang_code}' 未在当前支持的语言中找到。")

    @staticmethod
    def listen_for_hotkeys():
        keyboard.wait()

    def start_listening_thread(self):
        listening_thread = threading.Thread(target=self.listen_for_hotkeys, daemon=True)
        listening_thread.start()


def main():
    try:
        app = QApplication(sys.argv)
        translation_tool = TranslationTool()
        translation_tool.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"main错误: {str(e)}")

if __name__ == "__main__":
    main()
