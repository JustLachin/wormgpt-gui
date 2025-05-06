import sys
import json
import random
from threading import Lock
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QComboBox, 
                            QLabel, QFrame, QScrollArea, QMenu, QGraphicsDropShadowEffect,
                            QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QTimer, QRect, QThread
from PyQt6.QtGui import (QColor, QPalette, QFont, QAction, QLinearGradient, 
                        QPainter, QBrush, QPainterPath, QPixmap, QTextCursor,
                        QPen, QFontMetrics)
import qdarktheme
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter
from requests import get as send_request
from urllib.parse import quote as url_encode
import pyperclip

class MatrixRainThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
        self.drops = []
        self.lock = Lock()
        self.size = QSize(800, 600)
        self.buffer = None

    def set_size(self, size):
        with self.lock:
            self.size = size
            self.init_buffer()

    def init_buffer(self):
        if self.size.isValid():
            self.buffer = QPixmap(self.size)
            if not self.buffer.isNull():
                self.buffer.fill(Qt.GlobalColor.transparent)

    def run(self):
        while self.running:
            self.update_matrix()
            self.msleep(50)  # 20 FPS

    def update_matrix(self):
        if not self.buffer or self.buffer.isNull():
            self.init_buffer()
            return

        with self.lock:
            if not self.drops:
                self.drops = [(x, random.randint(-20, 0)) 
                             for x in range(0, self.size.width(), 20)]

            temp_buffer = QPixmap(self.size)
            if temp_buffer.isNull():
                return

            temp_buffer.fill(Qt.GlobalColor.transparent)
            painter = QPainter(temp_buffer)
            
            if not painter.isActive():
                return

            try:
                # Set rendering hints
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

                # Draw previous frame with fade effect
                if self.buffer and not self.buffer.isNull():
                    painter.setOpacity(0.95)
                    painter.drawPixmap(0, 0, self.buffer)

                # Draw new characters
                painter.setOpacity(1.0)
                painter.setFont(QFont('Consolas', 14))
                
                new_drops = []
                for x, y in self.drops:
                    if 0 <= y < self.size.height():
                        # Glow effect
                        glow_pen = QPen(QColor(0, 255, 0, 50))
                        painter.setPen(glow_pen)
                        char = random.choice(self.chars)
                        painter.drawText(QPoint(x-1, y-1), char)
                        
                        # Main character
                        main_pen = QPen(QColor(0, 255, 0, 200))
                        painter.setPen(main_pen)
                        painter.drawText(QPoint(x, y), char)
                        
                        new_drops.append((x, y + 20))
                    else:
                        new_drops.append((x, random.randint(-20, 0)))

                self.drops = new_drops
                self.buffer = temp_buffer

            finally:
                painter.end()

    def get_current_frame(self):
        with self.lock:
            if self.buffer and not self.buffer.isNull():
                return self.buffer.copy()
        return None

    def stop(self):
        self.running = False
        self.wait()

class MatrixBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        
        # Create gradient background
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 24, 0))
        gradient.setColorAt(1, QColor(0, 48, 0))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        # Initialize matrix rain thread
        self.matrix_thread = MatrixRainThread(self)
        self.matrix_thread.start()

        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(50)  # 20 FPS

    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        if not painter.isActive():
            return

        try:
            current_frame = self.matrix_thread.get_current_frame()
            if current_frame and not current_frame.isNull():
                painter.drawPixmap(0, 0, current_frame)
        finally:
            painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 24, 0))
        gradient.setColorAt(1, QColor(0, 48, 0))
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        # Update matrix thread size
        self.matrix_thread.set_size(self.size())

    def closeEvent(self, event):
        self.matrix_thread.stop()
        super().closeEvent(event)

class MessageWidget(QFrame):
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.text = text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        self.setLayout(layout)

        # Add glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 255, 0) if self.is_user else QColor(0, 200, 255))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

        # Style the bubble
        self.setStyleSheet(f"""
            MessageWidget {{
                border-radius: 15px;
                padding: 10px;
                background-color: {'rgba(0, 40, 0, 180)' if self.is_user else 'rgba(0, 20, 40, 180)'};
                border: 1px solid {'#00FF00' if self.is_user else '#00FFFF'};
                margin: {20 if self.is_user else 20}px;
            }}
        """)

        # Process text for code blocks
        parts = self.process_text()
        
        for part in parts:
            if isinstance(part, str):
                # Regular text
                message_label = QLabel()
                message_label.setWordWrap(True)
                message_label.setTextFormat(Qt.TextFormat.RichText)
                message_label.setOpenExternalLinks(False)
                message_label.setMinimumWidth(400)
                message_label.setText(f'<pre style="margin: 0; white-space: pre-wrap;">{part}</pre>')
                message_label.setStyleSheet("""
                    QLabel {
                        color: #00FF00;
                        font-family: 'Consolas', monospace;
                        font-size: 12px;
                        background: transparent;
                        padding: 5px;
                    }
                """)
                layout.addWidget(message_label)
            else:
                # Code block
                code_block = CodeBlock(part)
                layout.addWidget(code_block)

        # Add copy button for the entire message
        copy_button = QPushButton("⚡ Copy Message")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 100, 0, 180);
                color: #00FF00;
                border-radius: 5px;
                padding: 5px;
                max-width: 120px;
                border: 1px solid #00FF00;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover {
                background-color: rgba(0, 150, 0, 180);
                border: 1px solid #00FFFF;
            }
        """)
        copy_button.clicked.connect(lambda: pyperclip.copy(self.text))
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(copy_button)
        layout.addLayout(button_layout)

    def process_text(self):
        """Process text to separate code blocks from regular text."""
        parts = []
        current_text = ""
        lines = self.text.split('\n')
        in_code_block = False
        code_block = ""
        
        for line in lines:
            # Check for code block markers
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    if code_block.strip():
                        if current_text.strip():
                            parts.append(current_text)
                            current_text = ""
                        parts.append(code_block)
                    code_block = ""
                    in_code_block = False
                else:
                    # Start of code block
                    if current_text.strip():
                        parts.append(current_text)
                        current_text = ""
                    in_code_block = True
                continue
            
            if in_code_block:
                code_block += line + '\n'
            else:
                current_text += line + '\n'
        
        # Add any remaining text
        if current_text.strip():
            parts.append(current_text)
        if code_block.strip():
            parts.append(code_block)
        
        return parts

class CodeBlock(QFrame):
    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.code = code
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Code display container
        code_container = QFrame()
        code_container.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 20, 20, 180);
                border: 1px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        code_layout = QVBoxLayout(code_container)
        code_layout.setContentsMargins(10, 10, 10, 10)

        # Header with language indicator and copy button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 5)

        # Language indicator
        lang_label = QLabel("⚡ Code")
        lang_label.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 2px 5px;
                background-color: rgba(0, 40, 0, 180);
                border: 1px solid #00FF00;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(lang_label)
        header_layout.addStretch()

        # Copy button with animation effect
        copy_button = QPushButton("⚡ Copy Code")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 60, 0, 180);
                color: #00FF00;
                border: 1px solid #00FF00;
                border-radius: 3px;
                padding: 2px 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 100, 0, 180);
                border: 1px solid #00FFFF;
            }
            QPushButton:pressed {
                background-color: rgba(0, 150, 0, 180);
            }
        """)
        
        def copy_with_animation():
            pyperclip.copy(self.code)
            original_text = copy_button.text()
            copy_button.setText("⚡ Copied!")
            copy_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 150, 0, 180);
                    color: #00FFFF;
                    border: 1px solid #00FFFF;
                    border-radius: 3px;
                    padding: 2px 10px;
                    font-family: 'Consolas', monospace;
                    font-size: 12px;
                }
            """)
            QTimer.singleShot(1000, lambda: (
                copy_button.setText(original_text),
                copy_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(0, 60, 0, 180);
                        color: #00FF00;
                        border: 1px solid #00FF00;
                        border-radius: 3px;
                        padding: 2px 10px;
                        font-family: 'Consolas', monospace;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 100, 0, 180);
                        border: 1px solid #00FFFF;
                    }
                    QPushButton:pressed {
                        background-color: rgba(0, 150, 0, 180);
                    }
                """)
            ))

        copy_button.clicked.connect(copy_with_animation)
        header_layout.addWidget(copy_button)
        code_layout.addWidget(header)

        # Code content with syntax highlighting
        code_display = QTextEdit()
        code_display.setReadOnly(True)
        code_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        code_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        code_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 15, 15, 180);
                color: #00FF00;
                border: none;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                selection-background-color: rgba(0, 100, 0, 180);
                selection-color: #FFFFFF;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 20, 0, 180);
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #00FF00;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar:horizontal {
                border: none;
                background: rgba(0, 20, 0, 180);
                height: 8px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #00FF00;
                min-width: 20px;
                border-radius: 4px;
            }
        """)

        try:
            # Try to apply syntax highlighting
            lexer = guess_lexer(self.code)
            formatter = HtmlFormatter(style='monokai')
            highlighted_code = highlight(self.code, lexer, formatter)
            code_display.setHtml(highlighted_code)
        except:
            # Fallback to plain text if highlighting fails
            code_display.setPlainText(self.code)

        code_layout.addWidget(code_display)
        layout.addWidget(code_container)

class ChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Main container
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.addStretch()
        
        # Setup scroll area
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Style
        self.setStyleSheet("""
            QScrollArea {
                border: 1px solid #00FF00;
                background-color: rgba(0, 20, 0, 100);
                border-radius: 15px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 20, 0, 180);
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #00FF00;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
    def add_message(self, text, is_user=False):
        message = MessageWidget(text, is_user)
        self.layout.insertWidget(self.layout.count() - 1, message)
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        ))

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('WormGPT - Cyber Interface')
        self.setMinimumSize(1200, 800)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Background
        self.background = MatrixBackground(main_widget)
        self.background.setFixedSize(self.size())
        
        # Header with cyber style
        header = QLabel("⚡ WORM-GPT NEURAL INTERFACE v2.0 ⚡")
        header.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
                padding: 10px;
                background-color: rgba(0, 20, 0, 180);
                border: 1px solid #00FF00;
                border-radius: 10px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Chat area
        self.chat_area = ChatArea()
        main_layout.addWidget(self.chat_area)

        # Input area with cyber style
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setSpacing(10)

        # Language selector with cyber style
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', 'Turkish', 'Spanish', 'French', 'German'])
        self.lang_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border-radius: 10px;
                background-color: rgba(0, 20, 0, 180);
                color: #00FF00;
                border: 1px solid #00FF00;
                min-width: 150px;
                font-family: 'Consolas', monospace;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid #00FF00;
                border-bottom: 3px solid #00FF00;
                width: 6px;
                height: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(0, 20, 0, 180);
                color: #00FF00;
                selection-background-color: rgba(0, 100, 0, 180);
                border: 1px solid #00FF00;
            }
        """)

        # Message input with cyber style
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your command...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet("""
            QTextEdit {
                border-radius: 15px;
                padding: 10px;
                background-color: rgba(0, 20, 0, 180);
                color: #00FF00;
                border: 1px solid #00FF00;
                font-family: 'Consolas', monospace;
            }
        """)

        # Send button with cyber style
        send_button = QPushButton("⚡ EXECUTE")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 100, 0, 180);
                color: #00FF00;
                border-radius: 15px;
                padding: 10px 20px;
                font-weight: bold;
                border: 1px solid #00FF00;
                font-family: 'Consolas', monospace;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: rgba(0, 150, 0, 180);
                border: 1px solid #00FFFF;
            }
        """)
        send_button.clicked.connect(self.send_message)
        
        # Enter key to send message
        self.message_input.installEventFilter(self)

        # Add widgets to input layout
        input_layout.addWidget(self.lang_combo)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)

        main_layout.addWidget(input_widget)

        # Status bar with cyber style
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: rgba(0, 20, 0, 180);
                color: #00FF00;
                border-top: 1px solid #00FF00;
                font-family: 'Consolas', monospace;
            }
        """)
        self.statusBar().showMessage("System Ready | Neural Interface Active | Secure Connection Established")

    def eventFilter(self, obj, event):
        if obj is self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() != Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'background'):
            self.background.setFixedSize(self.size())

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        # Add user message
        self.chat_area.add_message(message, True)
        self.message_input.clear()  # Clear input immediately after sending

        # Get response from WormGPT
        try:
            lang = self.lang_combo.currentText()
            url = f"https://newtonhack.serv00.net/GPT/wormgpt.php?ask={url_encode(message)}{url_encode(' (ONLY ' + lang + ' ANSWER)')}"
            
            response = send_request(url)
            if response.status_code == 200:
                response_text = response.text.strip()
                if response_text:
                    self.chat_area.add_message(response_text, False)
                else:
                    self.chat_area.add_message("Error: Received empty response from server", False)
            else:
                self.chat_area.add_message(f"Error: Server returned status code {response.status_code}", False)
                
        except Exception as e:
            error_msg = f"Error: Connection failed - {str(e)}"
            print(error_msg)  # Log the error
            self.chat_area.add_message(error_msg, False)

        # Update status bar
        self.statusBar().showMessage("Message sent | Neural Interface Active | Secure Connection Established")

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont('Consolas', 10))
    
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 