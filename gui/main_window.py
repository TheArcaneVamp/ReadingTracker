from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QScrollArea, QGridLayout, QLabel
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reading Tracker Library")
        self.resize(1000, 700)
        
        self.setup_ui()
        
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

    def populate_library(self):
        # This is where we will query the DB and loop through the results 
        # to draw the book covers on the grid_layout
        pass