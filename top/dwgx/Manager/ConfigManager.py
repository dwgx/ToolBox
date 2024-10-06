import json
import os
from collections import defaultdict

ALLOWED_LANGUAGES = {
    "en": "英语",
    "zh": "中文",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "it": "意大利语",
    "pt": "葡萄牙语",
    "nl": "荷兰语",
    "ar": "阿拉伯语",
    "th": "泰语",
    "vi": "越南语",
    "id": "印尼语",
    "hi": "印地语",
    "fa": "波斯语",
}


class ConfigManager:
    def __init__(self, file_path='config.json'):
        self.file_path = file_path
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.file_path):
            default_config = {
                "translation": {
                    "SECRET_ID": "",
                    "SECRET_KEY": "",
                    "shortcut1": "",
                    "shortcut2": "",
                    "target_lang1": "en",
                    "target_lang2": "zh",
                    "copy_delay_ms": 100,
                    "languages": list(ALLOWED_LANGUAGES.keys())
                },
                "file_classifier": {
                    "folder_path": "",
                    "filter_types": "",
                    "exclude_types": ""
                },
                "ui_settings": {
                    "background_image": "",
                    "language": "zh",
                    "text_color": "#000000"  # 默认文本颜色为黑色
                }
            }
            self.save_config(default_config)
            return default_config
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_config(self, config=None):
        if config is None:
            config = self.config
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4, ensure_ascii=False)

    def get(self, section, option, default=None):
        return self.config.get(section, {}).get(option, default)

    def set(self, section, option, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = value
        self.save_config()

    @staticmethod
    def scan_files(folder_path, filter_types, exclude_types):
        file_dict = defaultdict(list)
        for root, _, files in os.walk(folder_path):
            for file in files:
                if filter_types and not any(file.lower().endswith(ft.lower()) for ft in filter_types):
                    continue
                if exclude_types and any(file.lower().endswith(et.lower()) for et in exclude_types):
                    continue
                file_dict[root].append(os.path.join(root, file))
        return file_dict

    @staticmethod
    def display_results(file_dict):
        result_text = ""
        for folder, files in file_dict.items():
            result_text += f"文件夹: {folder}\n"
            result_text += f"数量: {len(files)}\n"
            for file in files:
                result_text += f"  {file}\n"
        return result_text

    @staticmethod
    def search_files(file_dict, keyword):
        filtered_dict = defaultdict(list)
        for folder, files in file_dict.items():
            filtered_files = [file for file in files if keyword.lower() in os.path.basename(file).lower()]
            if filtered_files:
                filtered_dict[folder].extend(filtered_files)
        return filtered_dict
