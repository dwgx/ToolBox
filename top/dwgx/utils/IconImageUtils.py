#top.dwgx.util.sIconImageUtils

import os
from PyQt6.QtGui import QIcon, QImage, QPalette, QBrush
from PyQt6.QtCore import Qt, QObject, QEvent
import logging

class IconImageUtils(QObject):
    def __init__(self):
        super().__init__()
        self.icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'resource', 'Icon', 'ico'
        )
        self.bg_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'resource', 'Icon', 'bg'
        )
        self.background_config = {}
        logging.basicConfig(level=logging.INFO)

    def get_icon(self, icon_name: str) -> QIcon:
        icon_name = os.path.splitext(icon_name)[0]
        #尝试加载PNG
        icon_full_path_png = os.path.join(self.icon_path, icon_name + ".png")
        icon_full_path_ico = os.path.join(self.icon_path, icon_name + ".ico")
        if os.path.exists(icon_full_path_png):
            logging.info(f"加载图标: {icon_full_path_png}")
            return QIcon(icon_full_path_png)
        elif os.path.exists(icon_full_path_ico):
            logging.info(f"加载图标: {icon_full_path_ico}")
            return QIcon(icon_full_path_ico)
        else:
            logging.warning(f"图标文件不存在: {icon_full_path_png} 或 {icon_full_path_ico}, 使用系统默认图标.")
            return QIcon.fromTheme(icon_name)

    def get_background_icons(self):
        icons = []
        if not os.path.isdir(self.bg_path):
            logging.warning(f"背景图标目录不存在: {self.bg_path}")
            return icons
        for file in os.listdir(self.bg_path):
            if file.lower().endswith('.png'):
                file_path = os.path.join(self.bg_path, file)
                icons.append(QIcon(file_path))
        return icons

    def get_background_images(self):
        images = []
        if not os.path.isdir(self.bg_path):
            logging.warning(f"背景图标目录不存在: {self.bg_path}")
            return images
        for file in os.listdir(self.bg_path):
            if file.lower().endswith('.png'):
                file_path = os.path.join(self.bg_path, file)
                images.append(file_path)
        return images

    def update_background(self, widget, image_path, scaling_method):
        self.background_config[widget] = (image_path, scaling_method)
        widget.installEventFilter(self)
        self._apply_background(widget, image_path, scaling_method)

    def _apply_background(self, widget, image_path, scaling_method):
        palette = QPalette()
        image = QImage(image_path)
        if not image.isNull():
            if scaling_method == "保持比例":
                scaled_image = image.scaled(
                    widget.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            elif scaling_method == "拉伸":
                scaled_image = image.scaled(
                    widget.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            elif scaling_method == "裁剪":
                scaled_image = image.copy(
                    0, 0,
                    min(image.width(), widget.width()),
                    min(image.height(), widget.height())
                )
            else:
                #默认保持比例
                scaled_image = image.scaled(
                    widget.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_image))
            widget.setPalette(palette)
            widget.setAutoFillBackground(True)
        else:
            print(f"无效的图片路径或文件: {image_path}")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize and obj in self.background_config:
            image_path, scaling_method = self.background_config[obj]
            self._apply_background(obj, image_path, scaling_method)
        return super().eventFilter(obj, event)


icon_image_utils = IconImageUtils()
