import sys
import re
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtGui import QFont

class CodeCleaner(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Code Cleaner')
        self.resize(800, 600)

        main_layout = QVBoxLayout()


        input_label = QLabel("输入代码:")
        main_layout.addWidget(input_label)


        self.input_text_edit = QTextEdit(self)
        self.input_text_edit.setPlaceholderText("在这里输入代码...")
        main_layout.addWidget(self.input_text_edit)


        self.clean_button = QPushButton("去除 Python 注释", self)
        self.clean_button.clicked.connect(self.remove_comments)
        main_layout.addWidget(self.clean_button)


        output_label = QLabel("去除注释后的代码:")
        main_layout.addWidget(output_label)


        self.output_text_edit = QTextEdit(self)
        self.output_text_edit.setPlaceholderText("去除注释后的代码将在这里显示...")
        self.output_text_edit.setReadOnly(True)
        main_layout.addWidget(self.output_text_edit)

        self.setLayout(main_layout)

    def remove_comments(self):
        input_code = self.input_text_edit.toPlainText()
        cleaned_code = self.strip_python_comments(input_code)
        self.output_text_edit.setText(cleaned_code)

    def strip_python_comments(self, code):

        try:

            pattern_multiline_single = re.compile(r"", re.DOTALL)
            pattern_multiline_double = re.compile(r'', re.DOTALL)
            code = re.sub(pattern_multiline_single, '', code)
            code = re.sub(pattern_multiline_double, '', code)



            def remove_single_line_comments(line):
                in_single_quote = False
                in_double_quote = False
                for i, char in enumerate(line):
                    if char == "'" and not in_double_quote:
                        in_single_quote = not in_single_quote
                    elif char == '"' and not in_single_quote:
                        in_double_quote = not in_double_quote
                    elif char == '#' and not in_single_quote and not in_double_quote:
                        return line[:i].rstrip()
                return line

            code_lines = code.split('\n')
            cleaned_lines = [remove_single_line_comments(line).rstrip() for line in code_lines]
            return "\n".join(cleaned_lines)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"去除注释时发生错误: {e}")
            return code

def main():
    app = QApplication(sys.argv)
    window = CodeCleaner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
