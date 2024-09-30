#top.dwgx.Manager.ModuleManager

import importlib
import inspect
import logging
import os

from PyQt6.QtWidgets import QWidget


class ModuleManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModuleManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, modules_folder=None):
        if not hasattr(self, 'initialized'):
            if modules_folder is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.modules_folder = os.path.join(current_dir, '..', 'Modules')
            else:
                self.modules_folder = modules_folder

            self.modules = []
            self.load_modules()
            self.initialized = True

    def load_modules(self):
        if not os.path.isdir(self.modules_folder):
            logging.error(f"指定的路径不存在: {self.modules_folder}")
            return

        module_files = [f for f in os.listdir(self.modules_folder) if f.endswith('.py') and f != '__init__.py']
        logging.info(f"发现模块: {module_files}")  # Log detected module files

        for module_file in module_files:
            module_name = module_file[:-3]
            module_path = f'top.dwgx.Modules.{module_name}'
            self.load_single_module(module_name, module_path)

    def load_single_module(self, module_name, module_path):
        try:
            module = importlib.import_module(module_path)
            # 遍历模块中的所有类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, QWidget) and obj.__module__ == module_path:
                    self.modules.append(obj)
                    logging.info(f"模块 {module_name} 中的类 {name} 加载成功.")
                    return  # 只加载第一个匹配的类
            logging.warning(f"模块 {module_name} 中没有找到 QWidget 的子类，已跳过.")
        except Exception as e:
            logging.error(f"加载模块 {module_name} 失败: {e}")

    def get_modules(self):
        return self.modules
