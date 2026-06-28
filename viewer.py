# Runs the PyQt6 app and loads the main window.
import sys
from PyQt6.QtWidgets import QApplication
from monai_ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()