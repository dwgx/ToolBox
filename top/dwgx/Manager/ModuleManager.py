import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QWidget, QMessageBox

logger = logging.getLogger("ModuleManager")

class ModuleManager:
    def __init__(self, modules_folder: str = None):
        # 初始化模块管理器
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        current_dir = Path(base_path).resolve().parent
        self.modules_folder = Path(modules_folder) if modules_folder else current_dir / 'Modules'
        self.modules = []
        self.load_modules()

    def load_modules(self):
        logger.info("=== 开始加载所有模块 ===")
        if not self.modules_folder.is_dir():
            logger.error(f"指定的模块路径不存在: {self.modules_folder}")
            QMessageBox.critical(None, "加载模块失败", f"指定的模块路径不存在: {self.modules_folder}")
            return

        module_files = [f for f in self.modules_folder.iterdir() if f.suffix == '.py' and f.name != '__init__.py']
        for module_file in module_files:
            module_name = module_file.stem
            module_path = f'top.dwgx.Modules.{module_name}'
            self.load_single_module(module_name, module_path)

    def load_single_module(self, module_name, module_path):
        try:
            logger.info(f"正在加载模块: {module_name}, 路径: {module_path}")
            module = importlib.import_module(module_path)
            logger.info(f"模块 {module_name} 导入成功")

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, QWidget) and obj.__module__ == module_path:
                    logger.info(f"找到 QWidget 子类: {name}")
                    is_special = module_name == "Setting"
                    self.modules.append((obj, is_special))
                    logger.info(f"  → 已加载模块类: {name} ({module_name})")
                    break
            else:
                logger.warning(f"未找到 QWidget 子类于模块 {module_name}，跳过加载")
        except ImportError as e:
            logger.error(f"模块 {module_name} 无法导入: {e}")
        except Exception as e:
            logger.error(f"加载模块 {module_name} 时发生错误: {e}", exc_info=True)

    def get_modules(self):
        sorted_modules = sorted(self.modules, key=lambda m: (m[1], m[0].__name__))
        return sorted_modules
