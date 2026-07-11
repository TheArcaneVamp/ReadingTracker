# gui/book_details_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

class ImageWorker(QThread):
    image_finished = pyqtSignal(bytes)
    def __init__(self, url, cover_func):
        super().__init__()
        self.url = url
        self.cover_func = cover_func
    def run(self):
        if self.url:
            data = self.cover_func(self.url)
            if data:
                self.image_finished.emit(data)

class BookDetailsDialog(QDialog):
    def __init__(self, b_id, fetch_func, update_func, cover_func):
        super().__init__()
        self.b_id = b_id
        self.update_func = update_func
        self.cover_func = cover_func
        self.image_worker = None
        
        # Fetch the deep data immediately
        self.book_data = fetch_func(self.b_id)
        
        self.setWindowTitle(self.book_data.get('title', 'Book Details'))
        self.resize(600, 400)
        self.setup_ui()
        self.load_cover()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # --- Left Column: Cover ---
        left_layout = QVBoxLayout()
        self.cover_label = QLabel("Loading...")
        self.cover_label.setFixedSize(150, 220)
        self.cover_label.setStyleSheet("background-color: #e0e0e0; border: 1px solid #aaa;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setScaledContents(True)
        left_layout.addWidget(self.cover_label)
        left_layout.addStretch()
        main_layout.addLayout(left_layout)
        
        # --- Right Column: Details & Edits ---
        right_layout = QVBoxLayout()
        
        title_lbl = QLabel(f"<h2>{self.book_data['title']}</h2>")
        author_lbl = QLabel(f"<b>Authors:</b> {self.book_data.get('author_string', 'Unknown')}")
        year_lbl = QLabel(f"<b>Published:</b> {self.book_data['year_published']}")
        
        # Scrollable Description
        desc_box = QTextEdit()
        desc_box.setReadOnly(True)
        desc_box.setText(self.book_data.get('description') or "No description available.")
        
        # Editable Controls Layout
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("<b>Status:</b>"))
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(['TBR', 'CR', 'Finished', 'DNF'])
        self.status_dropdown.setCurrentText(self.book_data['status'])
        controls_layout.addWidget(self.status_dropdown)
        
        controls_layout.addWidget(QLabel("<b>Rating (0-10):</b>"))
        self.rating_spinbox = QSpinBox()
        self.rating_spinbox.setRange(0, 10) # 0 means unrated
        self.rating_spinbox.setValue(self.book_data.get('rating') or 0)
        controls_layout.addWidget(self.rating_spinbox)
        
        controls_layout.addStretch()
        
        # Save Button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        
        right_layout.addWidget(title_lbl)
        right_layout.addWidget(author_lbl)
        right_layout.addWidget(year_lbl)
        right_layout.addWidget(desc_box)
        right_layout.addLayout(controls_layout)
        right_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(right_layout)

    def load_cover(self):
        url = self.book_data.get("cover_url")
        if url:
            self.image_worker = ImageWorker(url, self.cover_func)
            self.image_worker.image_finished.connect(self.set_image)
            self.image_worker.start()
        else:
            self.cover_label.setText("No Cover")

    def set_image(self, image_bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        self.cover_label.setPixmap(pixmap)
        
    def save_changes(self):
        status = self.status_dropdown.currentText()
        rating = self.rating_spinbox.value()
        
        success = self.update_func(self.b_id, status, rating)
        if success:
            QMessageBox.information(self, "Saved", "Book details updated successfully.")
            self.accept() # Closes dialog and returns "Accepted" signal
        else:
            QMessageBox.warning(self, "Error", "Failed to save changes.")

    def cleanup_thread(self):
        # Forcefully kill the high-res image download if it is still running
        if self.image_worker and self.image_worker.isRunning():
            self.image_worker.terminate()
            self.image_worker.wait()

    def closeEvent(self, event):
        # Triggered when the user clicks the 'X' button
        self.cleanup_thread()
        super().closeEvent(event)
        
    def reject(self):
        # Triggered when the user presses the 'Escape' key
        self.cleanup_thread()
        super().reject()