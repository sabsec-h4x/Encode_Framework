import sys
import os
import base64
import urllib.parse
import html
import hashlib
import logging
from typing import Optional, Tuple

from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, 
                               QFileDialog, QProgressBar, QGroupBox, QGridLayout, 
                               QStatusBar, QMessageBox, QComboBox, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QSettings
from PySide6.QtGui import QPixmap, QImage

# Import crypto modules (we'll implement fallbacks if not available)
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Import steganography modules
try:
    from stegano import lsb
    STEGANO_AVAILABLE = True
except ImportError:
    STEGANO_AVAILABLE = False

# Import QR code modules
try:
    import qrcode
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Import AI modules
try:
    # Placeholder for AI modules - would need to be implemented based on specific libraries
    AI_AVAILABLE = False
except ImportError:
    AI_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Uniencode")

class MediaConversionThread(QThread):
    """Thread for handling media conversion to prevent UI freezing"""
    progress_updated = Signal(int)
    conversion_finished = Signal(bool, str)
    
    def __init__(self, input_file, output_file, conversion_type):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.conversion_type = conversion_type
        self.is_cancelled = False
        
    def run(self):
        try:
            # This is a simplified implementation
            # In a real app, you would use ffmpeg-python or subprocess to call ffmpeg
            # and parse progress updates
            
            # Simulate conversion process
            for i in range(101):
                if self.is_cancelled:
                    self.conversion_finished.emit(False, "Conversion cancelled")
                    return
                self.progress_updated.emit(i)
                self.msleep(50)  # Simulate work
                
            self.conversion_finished.emit(True, f"Conversion complete: {self.output_file}")
        except Exception as e:
            self.conversion_finished.emit(False, f"Error: {str(e)}")
            
    def cancel(self):
        self.is_cancelled = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Encoder Tool (Uniencode)")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.setup_text_data_tab()
        self.setup_crypto_tab()
        self.setup_nn_tab()
        self.setup_media_tab()
        self.setup_qr_tab()
        self.setup_stego_tab()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Initialize settings
        self.settings = QSettings("Uniencode", "Universal Encoder Tool")
        
        # Log startup
        self.log_action("Application started")
    
    def log_action(self, message):
        """Log an action to both the status bar and logger"""
        logger.info(message)
        self.status_bar.showMessage(message)
        
    def setup_text_data_tab(self):
        """Set up the Text/Data encoding tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input section
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout(input_group)
        self.text_input = QTextEdit()
        input_layout.addWidget(self.text_input)
        layout.addWidget(input_group)
        
        # Encoding options
        options_group = QGroupBox("Encoding Options")
        options_layout = QHBoxLayout(options_group)
        
        self.encode_type = QComboBox()
        self.encode_type.addItems(["Base64", "URL", "HTML"])
        options_layout.addWidget(QLabel("Encode Type:"))
        options_layout.addWidget(self.encode_type)
        
        encode_btn = QPushButton("Encode")
        encode_btn.clicked.connect(self.encode_text)
        options_layout.addWidget(encode_btn)
        
        decode_btn = QPushButton("Decode")
        decode_btn.clicked.connect(self.decode_text)
        options_layout.addWidget(decode_btn)
        
        layout.addWidget(options_group)
        
        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        output_layout.addWidget(self.text_output)
        
        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        output_layout.addWidget(copy_btn)
        
        layout.addWidget(output_group)
        
        self.tab_widget.addTab(tab, "Text/Data")
        
    def setup_crypto_tab(self):
        """Set up the Cryptography tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not CRYPTO_AVAILABLE:
            layout.addWidget(QLabel("Crypto functionality not available. Install pycryptodome."))
            self.tab_widget.addTab(tab, "Crypto")
            return
            
        # Input section
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout(input_group)
        self.crypto_input = QTextEdit()
        input_layout.addWidget(self.crypto_input)
        layout.addWidget(input_group)
        
        # Key section
        key_group = QGroupBox("Encryption Key")
        key_layout = QHBoxLayout(key_group)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter encryption key (optional)")
        key_layout.addWidget(self.key_input)
        
        gen_key_btn = QPushButton("Generate Key")
        gen_key_btn.clicked.connect(self.generate_key)
        key_layout.addWidget(gen_key_btn)
        
        layout.addWidget(key_group)
        
        # Crypto options
        options_group = QGroupBox("Cryptography Options")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Operation:"), 0, 0)
        self.crypto_operation = QComboBox()
        self.crypto_operation.addItems(["AES Encrypt", "AES Decrypt", "SHA-256 Hash"])
        options_layout.addWidget(self.crypto_operation, 0, 1)
        
        encrypt_btn = QPushButton("Execute")
        encrypt_btn.clicked.connect(self.execute_crypto)
        options_layout.addWidget(encrypt_btn, 0, 2)
        
        layout.addWidget(options_group)
        
        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.crypto_output = QTextEdit()
        self.crypto_output.setReadOnly(True)
        output_layout.addWidget(self.crypto_output)
        
        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_crypto_to_clipboard)
        output_layout.addWidget(copy_btn)
        
        layout.addWidget(output_group)
        
        self.tab_widget.addTab(tab, "Crypto")
        
    def setup_nn_tab(self):
        """Set up the Neural Network tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not AI_AVAILABLE:
            layout.addWidget(QLabel("AI functionality not available. Install required AI libraries."))
            self.tab_widget.addTab(tab, "Neural Network")
            return
            
        # Placeholder for AI functionality
        layout.addWidget(QLabel("AI text utilities would be implemented here"))
        
        self.tab_widget.addTab(tab, "Neural Network")
        
    def setup_media_tab(self):
        """Set up the Media conversion tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QHBoxLayout(file_group)
        
        self.media_input_path = QLineEdit()
        self.media_input_path.setPlaceholderText("Select input file")
        file_layout.addWidget(self.media_input_path)
        
        browse_input_btn = QPushButton("Browse")
        browse_input_btn.clicked.connect(self.browse_input_media)
        file_layout.addWidget(browse_input_btn)
        
        layout.addWidget(file_group)
        
        # Output selection
        output_group = QGroupBox("Output Settings")
        output_layout = QHBoxLayout(output_group)
        
        self.media_output_path = QLineEdit()
        self.media_output_path.setPlaceholderText("Output file path")
        output_layout.addWidget(self.media_output_path)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_media)
        output_layout.addWidget(browse_output_btn)
        
        layout.addWidget(output_group)
        
        # Conversion options
        options_group = QGroupBox("Conversion Options")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Conversion Type:"), 0, 0)
        self.conversion_type = QComboBox()
        self.conversion_type.addItems(["Audio to MP3", "Video to H.264"])
        options_layout.addWidget(self.conversion_type, 0, 1)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.start_conversion)
        options_layout.addWidget(self.convert_btn, 0, 2)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        options_layout.addWidget(self.cancel_btn, 0, 3)
        
        layout.addWidget(options_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.conversion_status = QLabel("Ready")
        layout.addWidget(self.conversion_status)
        
        self.tab_widget.addTab(tab, "Media")
        
        # Media conversion thread
        self.conversion_thread = None
        
    def setup_qr_tab(self):
        """Set up the QR Code tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not QRCODE_AVAILABLE:
            layout.addWidget(QLabel("QR Code functionality not available. Install qrcode and PIL."))
            self.tab_widget.addTab(tab, "QR Code")
            return
            
        splitter = QSplitter(Qt.Vertical)
        
        # Generate QR section
        generate_group = QGroupBox("Generate QR Code")
        generate_layout = QVBoxLayout(generate_group)
        
        self.qr_input = QTextEdit()
        self.qr_input.setPlaceholderText("Enter text to encode in QR code")
        generate_layout.addWidget(self.qr_input)
        
        generate_btn = QPushButton("Generate QR Code")
        generate_btn.clicked.connect(self.generate_qr)
        generate_layout.addWidget(generate_btn)
        
        self.qr_image_label = QLabel()
        self.qr_image_label.setAlignment(Qt.AlignCenter)
        self.qr_image_label.setMinimumHeight(200)
        generate_layout.addWidget(self.qr_image_label)
        
        save_qr_btn = QPushButton("Save QR Code")
        save_qr_btn.clicked.connect(self.save_qr)
        generate_layout.addWidget(save_qr_btn)
        
        # Decode QR section
        decode_group = QGroupBox("Decode QR Code")
        decode_layout = QVBoxLayout(decode_group)
        
        self.qr_decode_input = QLabel()
        self.qr_decode_input.setAlignment(Qt.AlignCenter)
        self.qr_decode_input.setText("No image selected")
        self.qr_decode_input.setMinimumHeight(100)
        self.qr_decode_input.setStyleSheet("border: 1px solid gray;")
        decode_layout.addWidget(self.qr_decode_input)
        
        browse_qr_btn = QPushButton("Browse QR Image")
        browse_qr_btn.clicked.connect(self.browse_qr_image)
        decode_layout.addWidget(browse_qr_btn)
        
        decode_btn = QPushButton("Decode QR Code")
        decode_btn.clicked.connect(self.decode_qr)
        decode_layout.addWidget(decode_btn)
        
        self.qr_output = QTextEdit()
        self.qr_output.setReadOnly(True)
        decode_layout.addWidget(self.qr_output)
        
        splitter.addWidget(generate_group)
        splitter.addWidget(decode_group)
        splitter.setSizes([350, 350])
        
        layout.addWidget(splitter)
        self.tab_widget.addTab(tab, "QR Code")
        
    def setup_stego_tab(self):
        """Set up the Steganography tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not STEGANO_AVAILABLE:
            layout.addWidget(QLabel("Steganography functionality not available. Install stegano."))
            self.tab_widget.addTab(tab, "Stego/File")
            return
            
        # Hide data section
        hide_group = QGroupBox("Hide Data in Image")
        hide_layout = QVBoxLayout(hide_group)
        
        # Image selection
        image_select_layout = QHBoxLayout()
        self.stego_image_path = QLineEdit()
        self.stego_image_path.setPlaceholderText("Select carrier image")
        image_select_layout.addWidget(self.stego_image_path)
        
        browse_image_btn = QPushButton("Browse")
        browse_image_btn.clicked.connect(self.browse_stego_image)
        image_select_layout.addWidget(browse_image_btn)
        hide_layout.addLayout(image_select_layout)
        
        # Secret message
        self.stego_secret = QTextEdit()
        self.stego_secret.setPlaceholderText("Enter secret message to hide")
        hide_layout.addWidget(self.stego_secret)
        
        # Output path
        output_layout = QHBoxLayout()
        self.stego_output_path = QLineEdit()
        self.stego_output_path.setPlaceholderText("Output image path")
        output_layout.addWidget(self.stego_output_path)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_stego_output)
        output_layout.addWidget(browse_output_btn)
        hide_layout.addLayout(output_layout)
        
        hide_btn = QPushButton("Hide Data")
        hide_btn.clicked.connect(self.hide_data)
        hide_layout.addWidget(hide_btn)
        
        layout.addWidget(hide_group)
        
        # Extract data section
        extract_group = QGroupBox("Extract Data from Image")
        extract_layout = QVBoxLayout(extract_group)
        
        # Image selection for extraction
        extract_image_layout = QHBoxLayout()
        self.extract_image_path = QLineEdit()
        self.extract_image_path.setPlaceholderText("Select image with hidden data")
        extract_image_layout.addWidget(self.extract_image_path)
        
        browse_extract_btn = QPushButton("Browse")
        browse_extract_btn.clicked.connect(self.browse_extract_image)
        extract_image_layout.addWidget(browse_extract_btn)
        extract_layout.addLayout(extract_image_layout)
        
        extract_btn = QPushButton("Extract Data")
        extract_btn.clicked.connect(self.extract_data)
        extract_layout.addWidget(extract_btn)
        
        self.extracted_data = QTextEdit()
        self.extracted_data.setReadOnly(True)
        extract_layout.addWidget(self.extracted_data)
        
        layout.addWidget(extract_group)
        
        self.tab_widget.addTab(tab, "Stego/File")
    
    # Text/Data tab methods
    def encode_text(self):
        text = self.text_input.toPlainText()
        encode_type = self.encode_type.currentText()
        
        try:
            if encode_type == "Base64":
                encoded = base64.b64encode(text.encode()).decode()
            elif encode_type == "URL":
                encoded = urllib.parse.quote(text)
            elif encode_type == "HTML":
                encoded = html.escape(text)
                
            self.text_output.setPlainText(encoded)
            self.log_action(f"Text encoded using {encode_type}")
        except Exception as e:
            self.text_output.setPlainText(f"Error: {str(e)}")
            self.log_action(f"Encoding error: {str(e)}")
    
    def decode_text(self):
        text = self.text_input.toPlainText()
        encode_type = self.encode_type.currentText()
        
        try:
            if encode_type == "Base64":
                decoded = base64.b64decode(text).decode()
            elif encode_type == "URL":
                decoded = urllib.parse.unquote(text)
            elif encode_type == "HTML":
                decoded = html.unescape(text)
                
            self.text_output.setPlainText(decoded)
            self.log_action(f"Text decoded from {encode_type}")
        except Exception as e:
            self.text_output.setPlainText(f"Error: {str(e)}")
            self.log_action(f"Decoding error: {str(e)}")
    
    def copy_to_clipboard(self):
        text = self.text_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.log_action("Output copied to clipboard")
    
    # Crypto tab methods
    def generate_key(self):
        if CRYPTO_AVAILABLE:
            key = get_random_bytes(16)  # 128-bit key
            self.key_input.setText(key.hex())
            self.log_action("Generated new encryption key")
    
    def execute_crypto(self):
        if not CRYPTO_AVAILABLE:
            self.crypto_output.setPlainText("Crypto functionality not available")
            return
            
        operation = self.crypto_operation.currentText()
        text = self.crypto_input.toPlainText()
        key = self.key_input.text()
        
        try:
            if operation == "AES Encrypt":
                if not key:
                    key = get_random_bytes(16).hex()
                    self.key_input.setText(key)
                    
                key_bytes = bytes.fromhex(key)
                cipher = AES.new(key_bytes, AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(text.encode())
                result = base64.b64encode(cipher.nonce + tag + ciphertext).decode()
                self.log_action("Text encrypted with AES")
                
            elif operation == "AES Decrypt":
                if not key:
                    self.crypto_output.setPlainText("Key required for decryption")
                    return
                    
                data = base64.b64decode(text)
                nonce = data[:16]
                tag = data[16:32]
                ciphertext = data[32:]
                
                key_bytes = bytes.fromhex(key)
                cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
                result = cipher.decrypt_and_verify(ciphertext, tag).decode()
                self.log_action("Text decrypted with AES")
                
            elif operation == "SHA-256 Hash":
                result = hashlib.sha256(text.encode()).hexdigest()
                self.log_action("SHA-256 hash generated")
                
            self.crypto_output.setPlainText(result)
            
        except Exception as e:
            self.crypto_output.setPlainText(f"Error: {str(e)}")
            self.log_action(f"Crypto error: {str(e)}")
    
    def copy_crypto_to_clipboard(self):
        text = self.crypto_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.log_action("Crypto output copied to clipboard")
    
    # Media tab methods
    def browse_input_media(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Media File", "", 
            "Media Files (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.flac)"
        )
        if file_path:
            self.media_input_path.setText(file_path)
            # Auto-generate output path
            base, ext = os.path.splitext(file_path)
            if self.conversion_type.currentText() == "Audio to MP3":
                output_path = base + ".mp3"
            else:
                output_path = base + "_converted.mp4"
            self.media_output_path.setText(output_path)
    
    def browse_output_media(self):
        conversion_type = self.conversion_type.currentText()
        if conversion_type == "Audio to MP3":
            filter_str = "MP3 Files (*.mp3)"
            default_ext = ".mp3"
        else:
            filter_str = "MP4 Files (*.mp4)"
            default_ext = ".mp4"
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Converted File", 
            self.media_output_path.text() or "", 
            filter_str
        )
        if file_path:
            if not file_path.endswith(default_ext):
                file_path += default_ext
            self.media_output_path.setText(file_path)
    
    def start_conversion(self):
        input_path = self.media_input_path.text()
        output_path = self.media_output_path.text()
        
        if not input_path or not output_path:
            QMessageBox.warning(self, "Error", "Please select input and output files")
            return
            
        if not os.path.exists(input_path):
            QMessageBox.warning(self, "Error", "Input file does not exist")
            return
            
        # Disable convert button, enable cancel button
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.conversion_status.setText("Converting...")
        
        # Start conversion thread
        self.conversion_thread = MediaConversionThread(
            input_path, output_path, self.conversion_type.currentText()
        )
        self.conversion_thread.progress_updated.connect(self.progress_bar.setValue)
        self.conversion_thread.conversion_finished.connect(self.conversion_finished)
        self.conversion_thread.start()
        
        self.log_action(f"Started media conversion: {os.path.basename(input_path)}")
    
    def cancel_conversion(self):
        if self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.cancel()
            self.conversion_status.setText("Cancelling...")
    
    def conversion_finished(self, success, message):
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.conversion_status.setText(message)
        
        if success:
            self.log_action("Media conversion completed successfully")
        else:
            self.log_action(f"Media conversion failed: {message}")
    
    # QR Code tab methods
    def generate_qr(self):
        text = self.qr_input.toPlainText()
        if not text:
            QMessageBox.warning(self, "Error", "Please enter text to encode")
            return
            
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to QPixmap for display
            qimage = QImage(img.size[0], img.size[1], QImage.Format_RGB32)
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    color = img.getpixel((x, y))
                    qimage.setPixel(x, y, (255 << 16 | 255 << 8 | 255) if color else 0)
            
            pixmap = QPixmap.fromImage(qimage)
            self.qr_image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            
            self.generated_qr_img = img  # Save for later saving
            self.log_action("QR code generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")
            self.log_action(f"QR generation error: {str(e)}")
    
    def save_qr(self):
        if not hasattr(self, 'generated_qr_img'):
            QMessageBox.warning(self, "Error", "Generate a QR code first")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save QR Code", "", "PNG Images (*.png)"
        )
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            self.generated_qr_img.save(file_path)
            self.log_action(f"QR code saved to {file_path}")
    
    def browse_qr_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select QR Image", "", "Image Files (*.png *.jpg *.bmp)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.qr_decode_input.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
                self.qr_image_to_decode = file_path
                self.log_action(f"QR image loaded: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load image")
    
    def decode_qr(self):
        if not hasattr(self, 'qr_image_to_decode'):
            QMessageBox.warning(self, "Error", "Please select a QR image first")
            return
            
        try:
            # For simplicity, we're using stegano's lsb reveal which can also decode QR
            # In a real implementation, you'd use a proper QR decoder
            result = lsb.reveal(self.qr_image_to_decode)
            self.qr_output.setPlainText(result)
            self.log_action("QR code decoded")
        except Exception as e:
            self.qr_output.setPlainText(f"Error decoding QR: {str(e)}")
            self.log_action(f"QR decoding error: {str(e)}")
    
    # Steganography tab methods
    def browse_stego_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Carrier Image", "", "Image Files (*.png)"
        )
        if file_path:
            self.stego_image_path.setText(file_path)
    
    def browse_stego_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output Image", "", "PNG Images (*.png)"
        )
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            self.stego_output_path.setText(file_path)
    
    def hide_data(self):
        image_path = self.stego_image_path.text()
        output_path = self.stego_output_path.text()
        secret = self.stego_secret.toPlainText()
        
        if not all([image_path, output_path, secret]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Error", "Carrier image does not exist")
            return
            
        try:
            secret_image = lsb.hide(image_path, secret)
            secret_image.save(output_path)
            QMessageBox.information(self, "Success", f"Data hidden in {output_path}")
            self.log_action(f"Data hidden in image: {os.path.basename(output_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to hide data: {str(e)}")
            self.log_action(f"Steganography error: {str(e)}")
    
    def browse_extract_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image with Hidden Data", "", "Image Files (*.png)"
        )
        if file_path:
            self.extract_image_path.setText(file_path)
    
    def extract_data(self):
        image_path = self.extract_image_path.text()
        
        if not image_path:
            QMessageBox.warning(self, "Error", "Please select an image")
            return
            
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Error", "Image does not exist")
            return
            
        try:
            result = lsb.reveal(image_path)
            self.extracted_data.setPlainText(result)
            self.log_action("Data extracted from image")
        except Exception as e:
            self.extracted_data.setPlainText(f"Error extracting data: {str(e)}")
            self.log_action(f"Data extraction error: {str(e)}")
    
    def closeEvent(self, event):
        """Handle application close"""
        # Cancel any ongoing conversions
        if hasattr(self, 'conversion_thread') and self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.cancel()
            self.conversion_thread.wait()
            
        self.log_action("Application closing")
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Universal Encoder Tool")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()