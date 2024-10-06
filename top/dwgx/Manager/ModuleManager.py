

import logging
import os
from pathlib import Path
import importlib
import inspect
from PySide6.QtWidgets import QWidget, QMessageBox
from Manager.ConfigManager import ConfigManager
from utils.loggerutils import setup_logger

logger = setup_logger("ModuleManager")


class ModuleManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, modules_folder: str = None):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        current_dir = Path(__file__).resolve().parent
        self.modules_folder = Path(modules_folder) if modules_folder else current_dir.parent / 'Modules'
        self.modules = []
        self.load_modules()

    def load_modules(self):
        if not os.path.isdir(self.modules_folder):
            logger.error(f"指定的模块路径不存在: {self.modules_folder}")
            QMessageBox.critical(None, "加载模块失败", f"指定的模块路径不存在: {self.modules_folder}")
            return
        module_files = [f for f in os.listdir(self.modules_folder) if f.endswith('.py') and f != '__init__.py']
        for module_file in module_files:
            module_name = module_file[:-3]
            module_path = f'top.dwgx.Modules.{module_name}'
            self.load_single_module(module_name, module_path)

    def load_single_module(self, module_name, module_path):
        try:
            module = importlib.import_module(module_path)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, QWidget) and obj.__module__ == module_path:
                    if module_name == "Setting":
                        self.modules.append((obj, True))
                    else:
                        self.modules.append((obj, False))
                    logger.info(f"  → 已加载模块类: {name} ({module_name})")
                    return
            logger.warning(f"  ✗ 未找到 QWidget 子类于模块 {module_name}，跳过加载")
        except Exception as e:
            logger.error(f"  ✗ 加载模块 {module_name} 失败: {e}")

    def get_modules(self):
        sorted_modules = sorted(self.modules, key=lambda m: (m[1], m[0].__name__))
        return sorted_modules