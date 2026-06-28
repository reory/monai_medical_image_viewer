# menus, file open, layout

import os
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QStackedWidget, QPushButton,
    QVBoxLayout, QWidget, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from monai_ui.image_widget import ImageWidget
from monai_ui.welcome_widget import WelcomeWidget

# Vibrant Neon Tech UI Style
NEON_STYLE = """
QPushButton {
    background-color: #00C6FF;
    color: black;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #0094CC;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MONAI Medical Image Viewer")
        self.resize(1024, 768)
        
        # Stacked widget handles switching layouts seamlessly
        self.stacked_widget = QStackedWidget()
        
        # Footer wrapper layout
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add stacked widget (Main UI)
        layout.addWidget(self.stacked_widget)

        # Footer credit bar
        footer = QLabel("Powered by Monai @ Built By Roy Peters @ Neon Tech UI")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "background-color: #00C6FF;"
            "color: black;"
            "padding: 6px;"
            "font-weight: 600;"
            "border-top: 2px solid #0094CC;"
        )
        layout.addWidget(footer)

        # Set wrapper as central widget
        self.setCentralWidget(central)

        # Instantiate UI views
        self.welcome_widget = WelcomeWidget()
        self.image_widget = ImageWidget()

        # Apply Neon Tech UI to all buttons inside both widgets
        self._apply_neon_style(self.welcome_widget)
        self._apply_neon_style(self.image_widget)

        # Index 0 = Welcome Dashboard
        # Index 1 = Medical Image Viewer Canvas
        self.stacked_widget.addWidget(self.welcome_widget)
        self.stacked_widget.addWidget(self.image_widget)

        # Connect custom signals from the dashboard to MainWindow handlers
        self.welcome_widget.file_selected.connect(self.load_and_switch_to_image)
        self.welcome_widget.browse_nifti_clicked.connect(self.open_nifti_file)
        self.welcome_widget.dicom_clicked.connect(self.open_dicom_folder)
        self.image_widget.back_requested.connect(self.show_welcome_screen)

        self._create_menu()

    def _apply_neon_style(self, widget):
        """
        Apply Neon Tech stylesheet to all QPushButtons inside the widget.
        Works for both WelcomeWidget and ImageWidget.
        """
        for btn in widget.findChildren(QPushButton):
            btn.setStyleSheet(NEON_STYLE)

    def _create_menu(self):

        menu = self.menuBar().addMenu("File")

        # Return Home shortcut option
        home_action = QAction(" 🔙 Go to Welcome Screen", self)
        home_action.triggered.connect(self.show_welcome_screen)
        menu.addAction(home_action)

        menu.addSeparator()
        
        # Specific path loop for NIfTI volumes
        open_nifti_action = QAction("Open NIfTI Image", self)
        open_nifti_action.triggered.connect(self.open_nifti_file)
        menu.addAction(open_nifti_action)

        # Specific path loop for DICOM folder series
        open_dicom_action = QAction("Open DICOM Folder", self)
        open_dicom_action.triggered.connect(self.open_dicom_folder)
        menu.addAction(open_dicom_action)

    def show_welcome_screen(self):
        """Switches the view back to the welcome landing page."""

        self.welcome_widget.scan_local_dataset()
        self.stacked_widget.setCurrentIndex(0)

    def load_and_switch_to_image(self, file_path):
        """
        Loads a target file into the image processor and flips the active screen.
        """

        if file_path:
            self.image_widget.load_image(file_path)
            self.stacked_widget.setCurrentIndex(1)

    def open_nifti_file(self):
        """Fallback manual explorer to open an external NIfTI volume file."""

        # Accelerate navigation by defaulting directly into your active spleen subset
        default_dir = os.path.join("data", "spleen", "Task09_Spleen", "imagesTr")
        if not os.path.exists(default_dir):
            default_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open NIfTI File",
            default_dir,
            "NIfTI Volumes (*.nii *.nii.gz)"
        )

        if file_path:
            self.image_widget.load_image(file_path)

    def open_dicom_folder(self):
        """Opens a local directory containing a raw DICOM sequence slice map."""

        folder = QFileDialog.getExistingDirectory(self, "Open DICOM Folder")
        if folder:
            self.image_widget.load_dicom(folder)
            self.stacked_widget.setCurrentIndex(1)
