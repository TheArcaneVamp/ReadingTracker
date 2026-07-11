from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QWidget, QScrollArea, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

# --- 1. The Background Workers ---
class SearchWorker(QThread):
    search_finished = pyqtSignal(list)
    
    def __init__(self, query, search_func):
        super().__init__()
        self.query = query
        self.search_func = search_func 
        
    def run(self):
        results = self.search_func(self.query) 
        self.search_finished.emit(results)
        
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

# --- 2. The Custom Result Card Widget ---
class ResultCard(QWidget):
    def __init__(self, book_data, add_callback, cover_func):
        super().__init__()
        self.book_data = book_data
        self.add_callback = add_callback
        self.cover_func = cover_func # Store it here
        self.image_worker = None
        
        self.setup_ui()
        self.load_thumbnail()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # 1. Thumbnail Container (Fixed Size)
        self.cover_label = QLabel("Loading...")
        self.cover_label.setFixedSize(60, 90)
        self.cover_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; font-size: 10px;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setScaledContents(True) # Stretches image to fit label perfectly
        
        # 2. Text Info
        info_text = f"<b>{self.book_data['title']}</b><br>By: {self.book_data['author']}<br>Year: {self.book_data['year_published']}"
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        
        # 3. Add Button
        add_btn = QPushButton("Add to Library")
        add_btn.setFixedSize(100, 30)
        add_btn.clicked.connect(lambda: self.add_callback(self.book_data))
        
        layout.addWidget(self.cover_label)
        layout.addWidget(info_label)
        layout.addStretch()
        layout.addWidget(add_btn)

    def load_thumbnail(self):
        url = self.book_data.get("cover_url")
        if not url:
            self.cover_label.setText("No Cover")
            return
            
        # Pass the stored cover_func into the worker
        self.image_worker = ImageWorker(url, self.cover_func) 
        self.image_worker.image_finished.connect(self.set_image)
        self.image_worker.start()

    def set_image(self, image_bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        self.cover_label.setPixmap(pixmap)

# --- 3. The Search Dialog ---
class SearchDialog(QDialog):
    def __init__(self, search_func, cover_func, insert_func):
        super().__init__()
        self.search_func = search_func
        self.cover_func = cover_func
        self.insert_func = insert_func
        
        self.setWindowTitle("Search Open Library")
        self.resize(600, 500)
        self.setup_ui()
    
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter book title...")
        self.search_btn = QPushButton("Search")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.results_container)
        
        layout.addWidget(self.scroll_area)
        
        self.search_btn.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query: return
            
        self.search_btn.setEnabled(False)
        self.status_label.setText("Searching Open Library...")
        self.clear_results()
        
        # Pass the injected search_func here
        self.worker = SearchWorker(query, self.search_func) 
        self.worker.search_finished.connect(self.display_results)
        self.worker.start()

    def display_results(self, books):
        self.search_btn.setEnabled(True)
        
        if not books:
            self.status_label.setText("No books found.")
            return
            
        self.status_label.setText(f"Found {len(books)} results:")
        
        for item in books:
            book_data = item['book_entry']
            # Pass the cover_func down to the ResultCard
            card = ResultCard(book_data, self.add_book_to_db, self.cover_func) 
            self.results_layout.addWidget(card)

    def add_book_to_db(self, book_data):
        # Execute the injected database function
        success, message = self.insert_func(book_data)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Notice", message)

    def clear_results(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()