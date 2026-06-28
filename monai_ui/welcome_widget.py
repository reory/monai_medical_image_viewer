import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QListWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class WelcomeWidget(QWidget):
    file_selected = pyqtSignal(str)
    dicom_clicked = pyqtSignal()
    browse_nifti_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left panel - Load browser
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel.setFixedWidth(280)

        left_layout = QVBoxLayout(left_panel)

        sidebar_title = QLabel("Local Spleen Dataset")
        sidebar_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        sidebar_title.setStyleSheet(
            "background-color: #00C6FF;"
            "color: black;"
            "padding: 6px 10px;"
            "border-radius: 6px;"
            "font-weight: 600;"
        )
        left_layout.addWidget(sidebar_title)


        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        left_layout.addWidget(self.file_list)

        main_layout.addWidget(left_panel)

        # Right panel - Dashboard buttons
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.setSpacing(30)

        # Welcome header text
        welcome_header = QLabel("MONAI Medical Image Viewer")
        welcome_header.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        welcome_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(welcome_header)

        subheader = QLabel("Select a quick-load file on the left "
                            "or browse external directories below."
                    )
        subheader.setFont(QFont("Arial", 11))
        subheader.setStyleSheet("color: #666;")
        subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(subheader)

        # Quick action Button Grid wrapper
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Button - Open External NIFTI file
        self.btn_nifti = QPushButton("🗒️ \nOpen NIFTI Scan\n(.nii.gz)")
        self.btn_nifti.setFont(QFont("Arial", 12))
        self.btn_nifti.setFixedSize(180, 120)
        self.btn_nifti.triggered = self.browse_nifti_clicked.emit
        self.btn_nifti.clicked.connect(self.browse_nifti_clicked.emit)

        # Button - Open Dicom Folder Series
        self.btn_dicom = QPushButton("📁 \nOpen DICOM\nFolder")
        self.btn_dicom.setFont(QFont("Arial", 12))
        self.btn_dicom.setFixedSize(180, 120)
        self.btn_dicom.clicked.connect(self.dicom_clicked.emit)

        button_layout.addWidget(self.btn_nifti)
        button_layout.addWidget(self.btn_dicom)
        right_layout.addLayout(button_layout)

        main_layout.addLayout(right_layout, stretch=1)

        # Trigger automatic dataset check on initialisation
        self.scan_local_dataset()

    def scan_local_dataset(self):
        """Scans the local repo directory specifically for training volumes."""

        self.file_list.clear()

        target_dir = os.path.join("data", "spleen", "Task09_Spleen", "imagesTr")

        if os.path.exists(target_dir):
            # Gather valid medical scan volumes, filtering out hidden
            # operating system metadata layers
            files = [
                f for f in os.listdir(target_dir) if f.endswith(".nii.gz") 
                and not f.startswith("._")
            ]
            files.sort()

            for file_name in files:
                self.file_list.addItem(file_name)

        if self.file_list.count() == 0:
            self.file_list.addItem("No local images found.")
            self.file_list.setEnabled(False)

    def _on_item_double_clicked(self, item):
        """
        Resolves the shorthand name back into a 
        full machine path when double clicked.
        """

        file_name = item.text()
        full_path = os.path.abspath(os.path.join(
            "data", "spleen", "Task09_Spleen", "imagesTr", file_name)
        )
        if os.path.exists(full_path):
            self.file_selected.emit(full_path)