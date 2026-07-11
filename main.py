import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.search_dialog import SearchDialog

class ReadingTrackerApp(MainWindow):
    def __init__(self):
        super().__init__()
        
    def open_search_dialog(self):
        # This overrides the dummy method we wrote in main_window.py
        dialog = SearchDialog()
        dialog.exec() # .exec() pauses the main window while the dialog is open

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize and show our customized main window
    window = ReadingTrackerApp()
    window.show()
    
    sys.exit(app.exec())