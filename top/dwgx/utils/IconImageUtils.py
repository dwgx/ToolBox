# top/dwgx/utils/IconImageUtils.py

import os
from PySide6.QtGui import QIcon, QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QObject, QEvent
import logging

import top.resource.Icons.resources_rc


class IconImageUtils(QObject):
    def __init__(self):
        super().__init__()
        self.background_config = {}
        logging.basicConfig(level=logging.DEBUG)  # 设置为 DEBUG 级别以捕获更多日志

    def get_icon(self, icon_name: str) -> QIcon:
        icon_name = os.path.splitext(icon_name)[0]

        icon_path_png = f":/icons/ico/{icon_name}.png"
        icon_path_ico = f":/icons/ico/{icon_name}.ico"

        # 检查并加载图标资源
        if QIcon(icon_path_png) and not QIcon(icon_path_png).isNull():
            logging.info(f"加载图标: {icon_path_png}")
            return QIcon(icon_path_png)
        elif QIcon(icon_path_ico) and not QIcon(icon_path_ico).isNull():
            logging.info(f"加载图标: {icon_path_ico}")
            return QIcon(icon_path_ico)
        else:
            logging.warning(f"图标文件不存在: {icon_path_png} 或 {icon_path_ico}, 使用系统默认图标.")
            return QIcon.fromTheme(icon_name)

    def get_background_images(self):
        images = []
        bg_files = [
            "bg1.png",
            "bg2.png",
            "DXLBG.png",
            "DXLBG2.png",
            "DXLBG3.png",
            "javaduke.png"
        ]
        for file in bg_files:
            image_path = f":/icons/bg/{file}"
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                images.append(image_path)
                logging.info(f"加载背景图片: {image_path}")
            else:
                logging.warning(f"背景图片文件不存在或无效: {image_path}")
        return images

    def update_background(self, widget, image_path, scaling_method):
        self.background_config[widget] = (image_path, scaling_method)
        widget.installEventFilter(self)
        self._apply_background(widget, image_path, scaling_method)

    def _apply_background(self, widget, image_path, scaling_method):
        palette = QPalette()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            if scaling_method == "保持比例":
                scaled_pixmap = pixmap.scaled(
                    widget.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
            elif scaling_method == "拉伸":
                scaled_pixmap = pixmap.scaled(
                    widget.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            elif scaling_method == "裁剪":
                scaled_pixmap = pixmap.copy(
                    0, 0,
                    min(pixmap.width(), widget.width()),
                    min(pixmap.height(), widget.height())
                )
            else:
                scaled_pixmap = pixmap.scaled(
                    widget.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )

            palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
            widget.setPalette(palette)
            widget.setAutoFillBackground(True)
            logging.info(f"应用背景图片: {image_path} 到控件: {widget}")
        else:
            logging.warning(f"无效的图片路径或文件: {image_path}")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize and obj in self.background_config:
            image_path, scaling_method = self.background_config[obj]
            self._apply_background(obj, image_path, scaling_method)
            logging.info(f"窗口大小调整，重新应用背景图片: {image_path}")
        return super().eventFilter(obj, event)


# 在此处添加 icon_image_utils 实例
icon_image_utils = IconImageUtils()
