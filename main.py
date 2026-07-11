import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.search_dialog import SearchDialog

from db.controller import fetch_all_books, insert_book, fetch_book_details, update_book_status, fetch_filtered_books
from db.create_db import create_db
from api.api_connector import get_book, get_cover
from gui.book_details_dialogue import BookDetailsDialog

class ReadingTrackerApp(MainWindow):
    def __init__(self):
        super().__init__()
        create_db()
        self.refresh_library()
        
        self.search_bar.textChanged.connect(self.apply_filters)
        self.author_search.textChanged.connect(self.apply_filters)
        self.year_search.textChanged.connect(self.apply_filters)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.rating_filter.currentTextChanged.connect(self.apply_filters)
        
    def refresh_library(self):
        books = fetch_all_books()
        self.populate_library(books, get_cover)
        
    def open_search_dialog(self):
        dialog = SearchDialog(
            search_func=get_book, 
            cover_func=get_cover, 
            insert_func=insert_book
        )
        dialog.exec()
        self.refresh_library()
    
    def open_book_details(self, book_data):
        dialog = BookDetailsDialog(
            b_id=book_data['b_id'],
            fetch_func=fetch_book_details,
            update_func=update_book_status,
            cover_func=get_cover
        )
        
        # If the user clicks "Save Changes", dialog.exec() returns True
        if dialog.exec(): 
            self.refresh_library()
            
    def apply_filters(self):
        # Extract all values
        search_text = self.search_bar.text().strip()
        author = self.author_search.text().strip()
        year = self.year_search.text().strip()
        status = self.status_filter.currentText()
        rating = self.rating_filter.currentText()
        
        # Pass all 5 parameters to the DB function
        books = fetch_filtered_books(search_text, status, author, year, rating)
        self.populate_library(books, get_cover)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = ReadingTrackerApp()
    window.show()
    
    sys.exit(app.exec())