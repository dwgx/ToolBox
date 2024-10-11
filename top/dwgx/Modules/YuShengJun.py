import logging
import os
import re
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QCheckBox, QProgressBar,
    QFileDialog, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
from newspaper import Article
import yt_dlp


logger = logging.getLogger("YuShengJunApp")
logging.basicConfig(level=logging.DEBUG)

class YuShengJunApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YuShengJun 爬虫工具")
        self.resize(800, 600)

        main_layout = QVBoxLayout(self)


        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入要爬取的URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)


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


        display_layout = QHBoxLayout()
        self.text_mode_radio = QCheckBox("提取纯文本")
        self.text_mode_radio.setChecked(True)
        self.webview_mode_radio = QCheckBox("显示网页内容")
        display_layout.addWidget(QLabel("选择文本获取方式:"))
        display_layout.addWidget(self.text_mode_radio)
        display_layout.addWidget(self.webview_mode_radio)


        path_layout = QHBoxLayout()
        self.path_label = QLabel("下载路径:")
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_display)
        path_layout.addWidget(self.browse_button)


        format_layout = QHBoxLayout()
        self.format_button = QPushButton("获取可用画质")
        self.format_button.clicked.connect(self.fetch_formats)
        self.format_combo = QComboBox()
        format_layout.addWidget(self.format_button)
        format_layout.addWidget(QLabel("选择画质:"))
        format_layout.addWidget(self.format_combo)


        self.scrape_button = QPushButton("开始爬取")
        self.scrape_button.clicked.connect(self.start_scrape)


        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)


        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)


        extract_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.extract_button = QPushButton("提取链接")
        self.extract_button.clicked.connect(self.extract_links)
        extract_layout.addWidget(QLabel("输入文本以提取链接:"))
        extract_layout.addWidget(self.text_input)
        extract_layout.addWidget(self.extract_button)


        main_layout.addLayout(url_layout)
        main_layout.addLayout(options_layout)
        main_layout.addLayout(display_layout)
        main_layout.addLayout(path_layout)
        main_layout.addLayout(format_layout)
        main_layout.addWidget(self.scrape_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_display)
        main_layout.addLayout(extract_layout)

    def browse_path(self):
        directory = QFileDialog.getExistingDirectory(self, "选择下载路径")
        if directory:
            self.path_display.setText(directory)

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
        webview_mode = self.webview_mode_radio.isChecked()
        selected_format = self.format_combo.currentData()

        if (scrape_images or scrape_videos or scrape_audio) and not download_path:
            QMessageBox.warning(self, "输入错误", "请选择一个下载路径。")
            return

        self.scrape_button.setEnabled(False)
        self.result_display.clear()
        self.progress_bar.setValue(0)

        self.thread = ScrapeThread(
            url=url,
            scrape_text=scrape_text,
            scrape_images=scrape_images,
            scrape_videos=scrape_videos,
            scrape_audio=scrape_audio,
            download_path=download_path,
            text_mode=text_mode,
            webview_mode=webview_mode,
            selected_format=selected_format
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.result.connect(self.display_result)
        self.thread.error.connect(self.display_error)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_result(self, content):
        if self.webview_mode_radio.isChecked():

            self.webview = QWebEngineView()
            self.webview.setHtml(content)
            self.result_display.hide()
            self.layout().addWidget(self.webview)
        else:
            self.result_display.append(content)
        self.scrape_button.setEnabled(True)
        QMessageBox.information(self, "完成", "爬取完成。")

    def display_error(self, error_message):
        self.result_display.append(f"错误: {error_message}")
        self.scrape_button.setEnabled(True)
        QMessageBox.critical(self, "错误", f"爬取过程中出错: {error_message}")

    def extract_links(self):
        text = self.text_input.toPlainText()
        urls = self.extract_urls(text)
        if urls:
            self.result_display.clear()
            for url in urls:
                self.result_display.append(url)
        else:
            QMessageBox.information(self, "结果", "未找到任何链接。")

    def extract_urls(self, text):
        url_regex = re.compile(
            r'(?i)\b((?:https?://|www\d{0,3}[.]|'
            r'[a-z0-9.\-]+[.][a-z]{2,4}/)'
            r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'
            r'(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|'
            r'[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
        )
        urls = re.findall(url_regex, text)
        return [url[0] for url in urls]

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
            QMessageBox.information(self, "成功", "已获取可用画质。")
        else:
            QMessageBox.warning(self, "错误", "未能获取可用画质。")

    def get_available_formats(self, url):
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                formats = info_dict.get('formats', [])
                format_list = []
                for fmt in formats:
                    if fmt.get('vcodec') != 'none':
                        format_id = fmt['format_id']
                        resolution = fmt.get('resolution') or f"{fmt.get('height', 'unknown')}p"
                        note = fmt.get('format_note', '')
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
                 scrape_audio, download_path, text_mode, webview_mode, selected_format):
        super().__init__()
        self.url = url
        self.scrape_text = scrape_text
        self.scrape_images = scrape_images
        self.scrape_videos = scrape_videos
        self.scrape_audio = scrape_audio
        self.download_path = download_path
        self.text_mode = text_mode
        self.webview_mode = webview_mode
        self.selected_format = selected_format

    def run(self):
        try:
            logger.debug("线程开始运行")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/58.0.3029.110 Safari/537.3"
            }
            self.progress.emit(10)
            logger.debug("发送网络请求")
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.debug("网络请求成功")
            self.progress.emit(30)

            result_text = ""

            if self.scrape_text:
                if self.text_mode:
                    logger.info("提取纯文本内容")
                    try:
                        article = Article(self.url)
                        article.download()
                        article.parse()
                        text = article.text
                        if text.strip():
                            self.result.emit(text + "\n\n")
                            logger.debug("文本提取成功")
                        else:
                            logger.warning("未提取到文本内容")
                    except Exception as e:
                        logger.error(f"使用 newspaper3k 提取文本失败: {e}")
                        self.error.emit(f"提取文本失败: {e}")
                elif self.webview_mode:
                    logger.info("获取网页内容")

                    self.result.emit(response.text)
                self.progress.emit(50)

            if self.scrape_images:
                logger.info("提取图像链接")
                soup = BeautifulSoup(response.text, 'html.parser')
                images = [img['src'] for img in soup.find_all('img') if img.get('src')]
                logger.debug(f"找到 {len(images)} 个图像链接")
                for img_url in images:
                    if img_url.startswith('data:'):
                        logger.warning(f"跳过 data URL 图像: {img_url[:30]}...")
                        continue
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = requests.compat.urljoin(self.url, img_url)
                    try:
                        img_response = requests.get(img_url, headers=headers, timeout=10)
                        img_response.raise_for_status()
                        img_name = os.path.join(self.download_path, os.path.basename(img_url))
                        with open(img_name, 'wb') as f:
                            f.write(img_response.content)
                        result_text += f"已下载图像: {img_name}\n"
                        logger.info(f"已下载图像: {img_name}")
                    except Exception as e:
                        logger.error(f"下载图像失败 {img_url}: {e}")
                self.progress.emit(70)

            if self.scrape_videos or self.scrape_audio:
                logger.info("处理视频和音频下载")
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
                            logger.info(f"已下载视频: {video_filename}")
                        if self.scrape_audio:
                            audio_title = info.get('title', 'audio')
                            audio_ext = info.get('ext', 'm4a')
                            audio_filename = f"{audio_title}.{audio_ext}"
                            result_text += f"已下载音频: {audio_filename}\n"
                            logger.info(f"已下载音频: {audio_filename}")
                    self.progress.emit(90)
                except yt_dlp.utils.DownloadError as e:
                    logger.error(f"下载视频或音频时出错 {self.url}: {e}")
                    self.error.emit(f"下载视频或音频时出错: {e}")
                    return
                except Exception as e:
                    logger.error(f"未知错误在下载视频或音频时: {e}")
                    self.error.emit(f"下载视频或音频时出错: {e}")
                    return

            if result_text:
                self.result.emit(result_text)

            self.progress.emit(100)
            logger.debug("线程运行完成")

        except requests.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            self.error.emit(f"网络请求失败: {e}")
        except Exception as e:
            logger.error(f"爬取过程中出错: {e}")
            self.error.emit(str(e))

    def ydl_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                percentage = int(downloaded / total * 100)
                self.progress.emit(percentage)
        elif d['status'] == 'finished':
            self.progress.emit(100)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = YuShengJunApp()
    window.show()
    sys.exit(app.exec())
