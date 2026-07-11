from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QScrollArea, QGridLayout, QLabel, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QMouseEvent

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
                
class LibraryBookCard(QWidget):
    # This signal broadcasts the book's data when the card is clicked
    card_clicked = pyqtSignal(dict) 

    def __init__(self, book_data, cover_func):
        super().__init__()
        self.book_data = book_data
        self.cover_func = cover_func
        self.image_worker = None
        
        self.setup_ui()
        self.load_cover()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) # Internal padding
        
        # Bug 3 Fix: Make it look like a physical card
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            LibraryBookCard {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
            }
            LibraryBookCard:hover {
                background-color: #f5f5f5;
                border: 1px solid #909090;
            }
        """)
        self.setFixedSize(150, 240) 
        self.setCursor(Qt.CursorShape.PointingHandCursor) # Changes mouse to a hand on hover
        
        # Cover Image
        self.cover_label = QLabel("Loading...")
        self.cover_label.setFixedSize(110, 160)
        self.cover_label.setStyleSheet("background-color: #e0e0e0; border: none;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setScaledContents(True)
        
        # Bug 1 Fix: Strict text sizing
        self.title_label = QLabel(self.book_data['title'])
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFixedHeight(40) # Forces text to stop expanding
        self.title_label.setStyleSheet("border: none; background: transparent; font-size: 11px;")
        
        layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

    # Bug 4 Fix: Catch the mouse click and emit the signal
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.card_clicked.emit(self.book_data)

    def load_cover(self):
        url = self.book_data.get("cover_url")
        if not url:
            self.cover_label.setText("No Cover")
            return
            
        self.image_worker = ImageWorker(url, self.cover_func)
        self.image_worker.image_finished.connect(self.set_image)
        self.image_worker.start()

    def set_image(self, image_bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(image_bytes)
        self.cover_label.setPixmap(pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reading Tracker Library")
        self.resize(1000, 700)
        
        self.setup_ui()
        self.apply_modern_styling()
        
        self.all_cards = []
        self.current_columns = 0
        
    def setup_ui(self):
        # 1. The Central Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 2. The Top Control Bar
        top_bar_layout = QHBoxLayout()
        
        title_label = QLabel("My Library")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.add_book_btn = QPushButton("Add Book")
        self.add_book_btn.setFixedSize(120, 40)
        
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch() # Pushes the label left and button right
        top_bar_layout.addWidget(self.add_book_btn)
        
        main_layout.addLayout(top_bar_layout)
        
        filter_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Title...")
        
        self.author_search = QLineEdit()
        self.author_search.setPlaceholderText("Author...")
        
        self.year_search = QLineEdit()
        self.year_search.setPlaceholderText("Year...")
        self.year_search.setFixedWidth(60)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "TBR", "CR", "Finished", "DNF"])
        
        self.rating_filter = QComboBox()
        self.rating_filter.addItems(["All", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        
        filter_layout.addWidget(QLabel("Title:"))
        filter_layout.addWidget(self.search_bar)
        filter_layout.addWidget(QLabel("Author:"))
        filter_layout.addWidget(self.author_search)
        filter_layout.addWidget(QLabel("Year:"))
        filter_layout.addWidget(self.year_search)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(QLabel("Rating:"))
        filter_layout.addWidget(self.rating_filter)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # 3. The Scrollable Library Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Allows grid to expand
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        # Aligns books to the top left so they don't float weirdly in the center
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 
        
        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area)
        
        # 4. Connect the Signals
        self.add_book_btn.clicked.connect(self.open_search_dialog)

    def open_search_dialog(self):
        print("Search dialog will open here.")
        # We will instantiate your SearchDialog class here in the next step
        
    def clear_grid(self):
        # Destroys all existing widgets in the layout so we start fresh
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                
                # If the widget is a book card with an active download thread, kill the thread
                if hasattr(widget, 'image_worker') and widget.image_worker and widget.image_worker.isRunning():
                    widget.image_worker.terminate() 
                    widget.image_worker.wait()      
                    
                widget.deleteLater()
                
        self.all_cards.clear()     
        self.current_columns = 0

    def populate_library(self, books_data, cover_func):
        self.clear_grid()
        
        for book in books_data:
            card = LibraryBookCard(book, cover_func)
            card.card_clicked.connect(self.open_book_details)
            self.all_cards.append(card)
            
        # 2. Draw them on the grid based on the current window size
        self.re_layout_grid()
         
    def open_book_details(self, book_data):
        # We will build the actual Book Details dialog here next.
        print(f"User clicked on: {book_data['title']} (ID: {book_data['b_id']})")   
    
    def re_layout_grid(self):
        if not self.all_cards: return
        
        # Calculate how many cards fit based on the scroll area's current width
        available_width = self.scroll_area.viewport().width()
        card_width = 170 # 150px card width + 20px padding/spacing
        columns = max(1, available_width // card_width)
        
        # Prevent unnecessary layout recalculations if the column count hasn't changed
        if columns == self.current_columns: return
        self.current_columns = columns
        
        # Remove widgets from the grid layout (but DO NOT delete them from memory)
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.takeAt(i)
            
        # Re-insert the existing cards at their new responsive coordinates
        for index, card in enumerate(self.all_cards):
            row = index // columns
            col = index % columns
            self.grid_layout.addWidget(card, row, col)
            
    def resizeEvent(self, event):
        # Let the standard PyQt window resize happen first
        super().resizeEvent(event)
        # Then forcefully shuffle our book cards to fit the new width
        self.re_layout_grid()
            
    def apply_modern_styling(self):
        self.setStyleSheet("""
            /* 1. Main Background */
            QMainWindow, QWidget {
                background-color: #f3f4f6;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }

            /* 2. Scroll Area (Remove the ugly indented border) */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }

            /* 3. Inputs & Dropdowns */
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                color: #374151;
            }
            
            /* Highlight the border blue when the user clicks inside */
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3b82f6;
                padding: 5px 11px; /* Adjust padding to offset the thicker border */
            }

            /* 4. Modern Mac-Style Scrollbar */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #d1d5db;
                min-height: 40px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9ca3af;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px; /* Completely hides the clunky top/bottom arrows */
            }
        """)