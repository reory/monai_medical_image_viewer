# displays slices, handles scaling

import os
import numpy as np
import nibabel as nib
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSlider, QCheckBox, QGroupBox, QFormLayout
)
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime
from monai_utils.loaders import (
    load_with_monai, 
    load_dicom_series, 
    find_matching_mask
)

class ImageWidget(QWidget):

    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.volume = None
        self.mask = None
        self.slice_index = 0

        # Main vertical layout for the entire widget view
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Top navigation bar
        nav_layout = QHBoxLayout()

        # Clickable back button
        self.btn_back = QPushButton("🔙Back To Dashboard")
        self.btn_back.setFont(QFont("Arial", 10))
        self.btn_back.setFixedWidth(180)
        self.btn_back.clicked.connect(self.back_requested.emit)
        nav_layout.addWidget(self.btn_back)

        # Dynamic text tracking
        self.slice_label = QLabel("Slice: 0 / 0")
        self.slice_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.slice_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        nav_layout.addWidget(self.slice_label)
        main_layout.addLayout(nav_layout)

        # Live datetime widget
        self.lbl_datetime = QLabel()
        self.lbl_datetime.setFont(QFont("Consolas", 10))
        self.lbl_datetime.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        nav_layout.addWidget(self.lbl_datetime)

        # Timer to update datetime
        timer = QTimer(self)
        timer.timeout.connect(self._update_datetime)
        timer.start(1000)

        self._update_datetime()

        # Split screen - Image left, Controls Right
        workspace_layout = QHBoxLayout()
        workspace_layout.setSpacing(15)

        # Left side - Image Canvas View
        self.label = QLabel(
            "No image loaded", 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.label.setStyleSheet("background-color: #111; border-radius: 4px;")
        self.label.setMouseTracking(True)
        self.setMouseTracking(True)
        workspace_layout.addWidget(self.label, stretch=3)

        # Right Side: Control Sidebar Panel
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(15)

        # Scan Metadata Card
        meta_group = QGroupBox("🔬 Scan Metadata")
        meta_form = QFormLayout(meta_group)
        self.lbl_filename = QLabel("None")
        self.lbl_dims = QLabel("None")
        self.lbl_spacing = QLabel("None")
        meta_form.addRow("File:", self.lbl_filename)
        meta_form.addRow("Dimensions:", self.lbl_dims)
        meta_form.addRow("Voxel Spacing:", self.lbl_spacing)
        sidebar_layout.addWidget(meta_group)

        # Contrast & Windowing (HU Controls)
        contrast_group = QGroupBox("🎛️ Contrast & Windowing")
        contrast_layout = QVBoxLayout(contrast_group)
        
        contrast_layout.addWidget(QLabel("Window Width (Contrast):"))
        self.sld_width = QSlider(Qt.Orientation.Horizontal)
        self.sld_width.setRange(1, 100)
        self.sld_width.setValue(100)
        self.sld_width.valueChanged.connect(self.update_slice)
        contrast_layout.addWidget(self.sld_width)

        contrast_layout.addWidget(QLabel("Window Level (Brightness):"))
        self.sld_level = QSlider(Qt.Orientation.Horizontal)
        self.sld_level.setRange(0, 100)
        self.sld_level.setValue(50)
        self.sld_level.valueChanged.connect(self.update_slice)
        contrast_layout.addWidget(self.sld_level)

        # Preset Buttons Row
        preset_layout = QHBoxLayout()
        btn_full = QPushButton("Full")
        btn_soft = QPushButton("Soft Tissue")
        btn_bone = QPushButton("Bone")
        
        btn_full.clicked.connect(self._set_preset_full)
        btn_soft.clicked.connect(self._set_preset_soft)
        btn_bone.clicked.connect(self._set_preset_bone)
        
        preset_layout.addWidget(btn_full)
        preset_layout.addWidget(btn_soft)
        preset_layout.addWidget(btn_bone)
        contrast_layout.addLayout(preset_layout)
        sidebar_layout.addWidget(contrast_group)

        # Mask & Overlay Controls
        mask_group = QGroupBox("🩸 Mask & Overlay")
        mask_layout = QVBoxLayout(mask_group)
        
        self.chk_mask_visible = QCheckBox("Show Spleen Segmentation")
        self.chk_mask_visible.setChecked(True)
        self.chk_mask_visible.toggled.connect(self.update_slice)
        mask_layout.addWidget(self.chk_mask_visible)

        mask_layout.addWidget(QLabel("Mask Opacity:"))
        self.sld_opacity = QSlider(Qt.Orientation.Horizontal)
        self.sld_opacity.setRange(0, 100)
        self.sld_opacity.setValue(60) # Default to a nice 60% translucent blend
        self.sld_opacity.valueChanged.connect(self.update_slice)
        self.chk_mask_visible.toggled.connect(self.sld_opacity.setEnabled)
        mask_layout.addWidget(self.sld_opacity)
        sidebar_layout.addWidget(mask_group)

        # Dynamic Slice Navigation Slider
        nav_group = QGroupBox("🎞️ Navigation Slider")
        nav_box = QVBoxLayout(nav_group)
        self.lbl_slice_counter = QLabel(
            "Slice: 0 / 0", 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.lbl_slice_counter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        nav_box.addWidget(self.lbl_slice_counter)
        
        self.sld_nav = QSlider(Qt.Orientation.Horizontal)
        self.sld_nav.setRange(0, 0)
        self.sld_nav.valueChanged.connect(self._on_slider_nav_changed)
        nav_box.addWidget(self.sld_nav)
        sidebar_layout.addWidget(nav_group)

        sidebar_layout.addStretch()
        workspace_layout.addWidget(sidebar)

        # Bottom status bar
        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet(
            "background-color: #222; color: #ddd; padding: 6px; border-radius: 4px;"
        )
        self.status_bar.setFont(QFont("Consolas", 10))
        main_layout.addLayout(workspace_layout, stretch=1)
        main_layout.addWidget(self.status_bar)


    def load_image(self, path):

        # Read out metadata strings immediately
        self.lbl_filename.setText(os.path.basename(path))

        try:
            img_tensor= load_with_monai(path)
            self.volume = img_tensor.numpy() if hasattr(img_tensor, "numpy") else img_tensor
        except Exception as e:
            print(f"MONAI loader fallback triggered: {e}")
            # Fallback to nibabel
            img = nib.load(path)
            self.volume = img.get_fdata()
        
        # Populate shape metrics safely
        if self.volume is not None:
            self.lbl_dims.setText(
                f"{self.volume.shape[0]} x " 
                f"{self.volume.shape[1]} x "
                f"{self.volume.shape[2]}"
            )
        
        # Parse physical spacing scales safely via nibabel headers
        try:
            nib_img = nib.load(path)
            zooms = nib_img.header.get_zooms()
            self.lbl_spacing.setText(
                f"{zooms[0]:.2f}, {zooms[1]:.2f}, {zooms[2]:.2f} mm"
            )
        except Exception:
            self.lbl_spacing.setText("Unknown")
        
        # Clear out any stale masks from previous views
        self.mask = None

        # Automatically look for and layer a matching label file
        mask_path = find_matching_mask(path)
        if mask_path:
            try:
                mask_tensor = load_with_monai(mask_path)
                mask_data = mask_tensor.numpy() if hasattr(mask_tensor, 'numpy') else mask_tensor
                self.mask = mask_data.astype(bool)
                print(f"Successfully linked segmentation mask: {mask_path}")
            except Exception:
                try:
                    self.mask = nib.load(mask_path).get_fdata().astype(bool)
                except Exception:
                    self.mask = None

        if self.volume is not None:
            # Snap view to the middle slice of the 3D stack by default
            total_slices = self.volume.shape[2]
            self.slice_index = total_slices // 2
            
            # Synchronise navigation slider capacities
            self.sld_nav.blockSignals(True)
            self.sld_nav.setRange(0, total_slices - 1)
            self.sld_nav.setValue(self.slice_index)
            self.sld_nav.blockSignals(False)

            # Restore baseline contrast distributions
            self._set_preset_full()

    def load_dicom(self, folder):
        self.volume = load_dicom_series(folder)
        self.mask = None
        self.lbl_filename.setText("DICOM Series")
        
        if self.volume is not None:
            self.lbl_dims.setText(
                f"{self.volume.shape[0]} x "
                f"{self.volume.shape[1]} x "
                f"{self.volume.shape[2]}"
            )
            self.lbl_spacing.setText("From DICOM metadata")
            
            total_slices = self.volume.shape[2]
            self.slice_index = total_slices // 2
            
            self.sld_nav.blockSignals(True)
            self.sld_nav.setRange(0, total_slices - 1)
            self.sld_nav.setValue(self.slice_index)
            self.sld_nav.blockSignals(False)
            
            self._set_preset_full()

    def _on_slider_nav_changed(self, value):
        """Fires when the manual horizontal navigation tracker moves."""

        self.slice_index = value
        self.update_slice()

    def wheelEvent(self, event):
        """
        Propagates scroll inputs directly to the navigation slider to 
        prevent duplicate drawing loops.
        """
        if self.volume is None:
            return

        delta = event.angleDelta().y()
        current = self.sld_nav.value()
        if delta > 0:
            self.sld_nav.setValue(min(current + 1, self.sld_nav.maximum()))
        else:
            self.sld_nav.setValue(max(current - 1, self.sld_nav.minimum()))

    def mouseMoveEvent(self, event):
        if self.volume is None:
            return

        # Convert widget coordinates → image coordinates
        pos = event.position().toPoint()
        x = pos.x()
        y = pos.y()

        # Get the displayed pixmap geometry
        pixmap = self.label.pixmap()
        if pixmap is None:
            return

        label_w = self.label.width()
        label_h = self.label.height()
        pix_w = pixmap.width()
        pix_h = pixmap.height()

        # Compute scaling offsets (centered image)
        offset_x = (label_w - pix_w) // 2
        offset_y = (label_h - pix_h) // 2

        # Convert mouse → image coordinates
        img_x = x - offset_x
        img_y = y - offset_y

        if not (0 <= img_x < pix_w and 0 <= img_y < pix_h):
            return  # outside image

        # Map to volume coordinates
        vol_x = int(img_x * (self.volume.shape[0] / pix_w))
        vol_y = int(img_y * (self.volume.shape[1] / pix_h))
        vol_z = self.slice_index

        # Safety check
        if (
            0 <= vol_x < self.volume.shape[0] and
            0 <= vol_y < self.volume.shape[1]
        ):
            intensity = self.volume[vol_x, vol_y, vol_z]
            self.status_bar.setText(
            f"Voxel: ({vol_x}, {vol_y}, {vol_z})   Intensity: {intensity:.2f}"
        )

    def _set_preset_full(self):
        self.sld_width.setValue(100)
        self.sld_level.setValue(50)

    def _set_preset_soft(self):
        self.sld_width.setValue(30)
        self.sld_level.setValue(55)

    def _set_preset_bone(self):
        self.sld_width.setValue(80)
        self.sld_level.setValue(25)

    def _update_datetime(self):
        now = datetime.now()
        self.lbl_datetime.setText(now.strftime("%d %b %Y  %H:%M:%S"))

    def update_slice(self):
        if self.volume is None:
            self.lbl_slice_counter.setText("Slice: 0 / 0")
            return

        total_slices = self.volume.shape[2]
        self.lbl_slice_counter.setText(
            f"Slice: {self.slice_index + 1} / {total_slices}"
        )

        slice_2d = self.volume[:, :, self.slice_index]
        
        # Read window width and level sliders 
        # (mapped to a normalized 0.0 - 1.0 landscape)
        width = self.sld_width.value() / 100.0
        level = 1.0 -  (self.sld_level.value() / 100.0)
        
        # Compute Hounsfield simulation bounding coordinates
        lower = level - (width / 2.0)
        upper = level + (width / 2.0)
        
        # Clip data intensities into window bounds and scale to monitor pixels (0-255)
        clipped = np.clip(slice_2d, lower, upper)
        if upper > lower:
            normalized = (clipped - lower) / (upper - lower) * 255
        else:
            normalized = np.zeros_like(slice_2d)
            
        slice_2d_bytes = np.clip(normalized, 0, 255).astype(np.uint8)
        rgb = np.stack([slice_2d_bytes] * 3, axis=-1)

        # Alpha-blend the segmentation layer onto the background matrix
        if self.mask is not None and self.chk_mask_visible.isChecked():
            mask_slice = self.mask[:, :, self.slice_index]
            if mask_slice.shape == slice_2d.shape:
                alpha = self.sld_opacity.value() / 100.0
                
                # Draw pixel clusters under the mask boundary
                pixels_under_mask = rgb[mask_slice].astype(float)
                red_overlay = np.array([255, 0, 0], dtype=float)
                
                # Compute floating linear interpolations
                blended_pixels = (1.0 - alpha) * pixels_under_mask + alpha * red_overlay
                rgb[mask_slice] = blended_pixels.astype(np.uint8)

        h, w, _ = rgb.shape
        bytes_per_line = w * 3
        
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.label.setPixmap(pixmap)


    def resizeEvent(self, event):
        """
        Forces the medical frame to scale dynamically 
        if you expand the OS window.
        """

        super().resizeEvent(event)
        self.update_slice()