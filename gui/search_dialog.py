from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QWidget, QScrollArea, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from api.api_connector import get_book  

# --- 1. The Background Worker ---
class SearchWorker(QThread):
    # This signal will broadcast the list of dictionaries back to the GUI
    search_finished = pyqtSignal(list)
    
    def __init__(self, query):
        super().__init__()
        self.query = query
        
    def run(self):
        # This runs entirely in the background
        results = get_book(self.query)
        self.search_finished.emit(results)

# --- 2. The Search Dialog ---
class SearchDialog(QDialog):
    def __init__(self, db_controller=None):
        super().__init__()
        self.db_controller = db_controller # We will pass the DB logic here later
        self.setWindowTitle("Search Open Library")
        self.resize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Top Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter book title...")
        self.search_btn = QPushButton("Search")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)
        
        # Status Label (to show "Searching...")
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Scroll Area for Results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.results_container)
        
        layout.addWidget(self.scroll_area)
        
        # Connect the search button
        self.search_btn.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
            
        self.search_btn.setEnabled(False)
        self.status_label.setText("Searching Open Library...")
        self.clear_results()
        
        # Spin up the background thread
        self.worker = SearchWorker(query)
        self.worker.search_finished.connect(self.display_results)
        self.worker.start()

    def display_results(self, books):
        self.search_btn.setEnabled(True)
        
        if not books:
            self.status_label.setText("No books found.")
            return
            
        self.status_label.setText(f"Found top {len(books)} results:")
        
        for item in books:
            book_data = item['book_entry']
            card = self.create_result_card(book_data)
            self.results_layout.addWidget(card)

    def create_result_card(self, book_data):
        # A miniature layout for each individual book result
        card_widget = QWidget()
        card_layout = QHBoxLayout(card_widget)
        
        # Basic text info (Title, Author, Year)
        info_text = f"<b>{book_data['title']}</b><br>By: {book_data['author']}<br>Year: {book_data['year_published']}"
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        
        # Add button
        add_btn = QPushButton("Add to Library")
        add_btn.setFixedSize(100, 30)
        # Use a lambda to capture the specific book_data for this button
        add_btn.clicked.connect(lambda checked, b=book_data: self.add_book_to_db(b))
        
        card_layout.addWidget(info_label)
        card_layout.addStretch()
        card_layout.addWidget(add_btn)
        
        return card_widget

    def add_book_to_db(self, book_data):
        print(f"Ready to insert: {book_data['title']} into the database.")
        # We will connect your db.controller.insert_book() function here next.
        QMessageBox.information(self, "Success", f"'{book_data['title']}' selected!")

    def clear_results(self):
        # Safely remove old results before showing new ones
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()