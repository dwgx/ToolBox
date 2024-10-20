import logging
import os
import re
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QCheckBox, QProgressBar,
    QFileDialog, QComboBox, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from bs4 import BeautifulSoup
from newspaper import Article
import yt_dlp

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("YuShengJunApp")


class YuShengJunApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YuShengJun 爬虫工具")
        self.resize(900, 700)

        main_layout = QVBoxLayout(self)

        # URL 输入布局
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入要爬取的URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        # 选择内容布局
        options_layout = QHBoxLayout()
        self.text_checkbox = QCheckBox("文本")
        self.text_checkbox.setChecked(True)
        self.images_checkbox = QCheckBox("图像")
        self.videos_checkbox = QCheckBox("视频")
        self.audio_checkbox = QCheckBox("音频")
        options_layout.addWidget(QLabel("选择要爬取的内容:"))
        options_layout.addWidget(self.text_checkbox)
        options_layout.addWidget(self.images_checkbox)
        options_layout.addWidget(self.videos_checkbox)
        options_layout.addWidget(self.audio_checkbox)

        # 文本获取方式布局
        display_layout = QHBoxLayout()
        self.text_mode_radio = QCheckBox("提取纯文本")
        self.text_mode_radio.setChecked(True)
        display_layout.addWidget(QLabel("选择文本获取方式:"))
        display_layout.addWidget(self.text_mode_radio)

        # 下载路径布局
        path_layout = QHBoxLayout()
        self.path_label = QLabel("下载路径:")
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_display)
        path_layout.addWidget(self.browse_button)

        # 画质选择布局
        format_layout = QHBoxLayout()
        self.format_button = QPushButton("获取可用画质")
        self.format_button.clicked.connect(self.fetch_formats)
        self.format_combo = QComboBox()
        format_layout.addWidget(self.format_button)
        format_layout.addWidget(QLabel("选择画质:"))
        format_layout.addWidget(self.format_combo)

        # 开始爬取按钮
        self.scrape_button = QPushButton("开始爬取")
        self.scrape_button.clicked.connect(self.start_scrape)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # 结果显示
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)

        # 日志显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #f0f0f0; color: black; font-family: Consolas;")

        # 添加所有布局到主布局
        main_layout.addLayout(url_layout)
        main_layout.addLayout(options_layout)
        main_layout.addLayout(display_layout)
        main_layout.addLayout(path_layout)
        main_layout.addLayout(format_layout)
        main_layout.addWidget(self.scrape_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QLabel("爬取结果:"))
        main_layout.addWidget(self.result_display)
        main_layout.addWidget(QLabel("日志:"))
        main_layout.addWidget(self.log_display)

    def browse_path(self):
        directory = QFileDialog.getExistingDirectory(self, "选择下载路径")
        if directory:
            self.path_display.setText(directory)
            logger.debug(f"选择下载路径: {directory}")
            self.log_display.append(f"选择下载路径: {directory}")

    def start_scrape(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "输入错误", "请输入一个有效的URL。")
            return

        scrape_text = self.text_checkbox.isChecked()
        scrape_images = self.images_checkbox.isChecked()
        scrape_videos = self.videos_checkbox.isChecked()
        scrape_audio = self.audio_checkbox.isChecked()
        download_path = self.path_display.text().strip()
        text_mode = self.text_mode_radio.isChecked()
        selected_format = self.format_combo.currentData()

        if (scrape_images or scrape_videos or scrape_audio) and not download_path:
            QMessageBox.warning(self, "输入错误", "请选择一个下载路径。")
            return

        self.scrape_button.setEnabled(False)
        self.result_display.clear()
        self.log_display.clear()
        self.progress_bar.setValue(0)

        self.thread = ScrapeThread(
            url=url,
            scrape_text=scrape_text,
            scrape_images=scrape_images,
            scrape_videos=scrape_videos,
            scrape_audio=scrape_audio,
            download_path=download_path,
            text_mode=text_mode,
            selected_format=selected_format
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.result.connect(self.display_result)
        self.thread.error.connect(self.display_error)
        self.thread.log.connect(self.display_log)
        self.thread.finished.connect(lambda: self.scrape_button.setEnabled(True))
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_result(self, content):
        self.result_display.append(content)
        self.log_display.append("爬取完成。")
        QMessageBox.information(self, "完成", "爬取完成。")

    def display_error(self, error_message):
        self.result_display.append(f"错误: {error_message}")
        self.log_display.append(f"错误: {error_message}")
        QMessageBox.critical(self, "错误", f"爬取过程中出错: {error_message}")

    def display_log(self, level, message):
        if level.lower() == "debug":
            color = "gray"
        elif level.lower() == "info":
            color = "black"
        elif level.lower() == "warning":
            color = "orange"
        elif level.lower() == "error":
            color = "red"
        else:
            color = "black"
        self.log_display.append(f"<span style='color:{color};'>{level.upper()}: {message}</span>")

    def fetch_formats(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "输入错误", "请输入一个有效的URL。")
            return
        formats = self.get_available_formats(url)
        if formats:
            self.format_combo.clear()
            for fmt_id, fmt_desc in formats:
                self.format_combo.addItem(fmt_desc, fmt_id)
            self.log_display.append("已获取可用画质。")
            QMessageBox.information(self, "成功", "已获取可用画质。")
        else:
            self.log_display.append("未能获取可用画质。")
            QMessageBox.warning(self, "错误", "未能获取可用画质。")

    def get_available_formats(self, url):
        try:
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                format_list = []
                for fmt in formats:
                    if fmt.get('vcodec') != 'none':
                        format_id = fmt['format_id']
                        resolution = fmt.get('resolution') or f"{fmt.get('height', 'unknown')}p"
                        note = fmt.get('format_note', '')
                        fps = fmt.get('fps')
                        if fps:
                            format_desc = f"{format_id} - {resolution} - {note} - {fps}fps"
                        else:
                            format_desc = f"{format_id} - {resolution} - {note}"
                        format_list.append((format_id, format_desc))
                logger.debug(f"可用画质列表: {format_list}")
                return format_list
        except Exception as e:
            logger.error(f"获取格式时出错 {url}: {e}")
            return []


class ScrapeThread(QThread):
    progress = Signal(int)
    result = Signal(str)
    error = Signal(str)
    log = Signal(str, str)

    def __init__(self, url, scrape_text, scrape_images, scrape_videos,
                 scrape_audio, download_path, text_mode, selected_format):
        super().__init__()
        self.url = url
        self.scrape_text = scrape_text
        self.scrape_images = scrape_images
        self.scrape_videos = scrape_videos
        self.scrape_audio = scrape_audio
        self.download_path = download_path
        self.text_mode = text_mode
        self.selected_format = selected_format

    def run(self):
        try:
            self.log.emit("debug", "线程开始运行")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/58.0.3029.110 Safari/537.3"
            }
            self.progress.emit(5)
            self.log.emit("info", "发送网络请求")
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
            self.log.emit("info", "网络请求成功")
            self.progress.emit(15)

            result_text = ""

            if self.scrape_text:
                if self.text_mode:
                    self.log.emit("info", "提取纯文本内容")
                    try:
                        article = Article(self.url)
                        article.download()
                        article.parse()
                        text = article.text
                        if text.strip():
                            result_text += text + "\n\n"
                            self.log.emit("debug", "文本提取成功")
                        else:
                            self.log.emit("warning", "未提取到文本内容")
                    except Exception as e:
                        self.log.emit("error", f"使用 newspaper 提取文本失败: {e}")
                        self.error.emit(f"提取文本失败: {e}")
                self.progress.emit(30)

                # 保存文本内容到TXT文件
                text_filename = os.path.join(self.download_path, "scraped_text.txt")
                text_filename = self.get_unique_filename(text_filename)
                with open(text_filename, "w", encoding="utf-8") as text_file:
                    text_file.write(result_text)
                self.log.emit("info", f"已保存文本到 {text_filename}")

            if self.scrape_images:
                self.log.emit("info", "提取图像链接")
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取 <img> 标签的 src 和 srcset 属性，包括 GIF
                images = set()
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src:
                        images.add(src)
                    srcset = img.get('srcset')
                    if srcset:
                        # srcset 可能包含多个 URL
                        srcs = [s.strip().split(' ')[0] for s in srcset.split(',')]
                        images.update(srcs)

                # 提取 CSS 背景图像，包括 GIF
                for div in soup.find_all(style=True):
                    style = div['style']
                    urls = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
                    images.update(urls)

                images = list(images)
                self.log.emit("debug", f"找到 {len(images)} 个图像链接")

                for idx, img_url in enumerate(images, start=1):
                    if img_url.startswith('data:'):
                        self.log.emit("warning", f"跳过 data URL 图像: {img_url[:30]}...")
                        continue
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = requests.compat.urljoin(self.url, img_url)
                    try:
                        img_response = requests.get(img_url, headers=headers, timeout=15)
                        img_response.raise_for_status()
                        img_name = os.path.join(self.download_path, os.path.basename(img_url.split('?')[0]))
                        # 确保文件名唯一
                        img_name = self.get_unique_filename(img_name)
                        with open(img_name, 'wb') as f:
                            f.write(img_response.content)
                        result_text += f"已下载图像: {img_name}\n"
                        self.log.emit("info", f"已下载图像: {img_name} ({idx}/{len(images)})")
                        # 更新进度，避免超过30-50区间
                        progress_increment = int(15 * idx / len(images))
                        self.progress.emit(30 + progress_increment)
                    except Exception as e:
                        self.log.emit("error", f"下载图像失败 {img_url}: {e}")
                        result_text += f"下载图像失败 {img_url}: {e}\n"
                self.progress.emit(50)

            if self.scrape_videos or self.scrape_audio:
                self.log.emit("info", "处理视频和音频下载")
                ydl_opts = {
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.ydl_hook],
                    'format': self.selected_format or 'best',
                    'quiet': True,
                    'no_warnings': True,
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.url, download=True)
                        if self.scrape_videos:
                            video_title = info.get('title', 'video')
                            video_ext = info.get('ext', 'mp4')
                            video_filename = f"{video_title}.{video_ext}"
                            result_text += f"已下载视频: {video_filename}\n"
                            self.log.emit("info", f"已下载视频: {video_filename}")
                        if self.scrape_audio:
                            audio_title = info.get('title', 'audio')
                            audio_ext = info.get('ext', 'm4a')
                            audio_filename = f"{audio_title}.{audio_ext}"
                            result_text += f"已下载音频: {audio_filename}\n"
                            self.log.emit("info", f"已下载音频: {audio_filename}")
                    self.progress.emit(80)
                except yt_dlp.utils.DownloadError as e:
                    self.log.emit("error", f"下载视频或音频时出错 {self.url}: {e}")
                    self.error.emit(f"下载视频或音频时出错: {e}")
                    return
                except Exception as e:
                    self.log.emit("error", f"未知错误在下载视频或音频时: {e}")
                    self.error.emit(f"下载视频或音频时出错: {e}")
                    return

            if result_text:
                self.result.emit(result_text)

            self.progress.emit(100)
            self.log.emit("debug", "线程运行完成")

        except Exception as e:
            self.log.emit("error", f"爬取过程中发生错误: {e}")
            self.error.emit(f"爬取过程中发生错误: {e}")

    def ydl_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                percentage = int(downloaded / total * 100)
                # 将视频/音频下载进度映射到整体进度
                self.progress.emit(50 + int(30 * percentage / 100))
        elif d['status'] == 'finished':
            self.progress.emit(80)

    def get_unique_filename(self, filepath):
        base, extension = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{extension}"
            counter += 1
        return filepath


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = YuShengJunApp()
    window.show()
    sys.exit(app.exec())
