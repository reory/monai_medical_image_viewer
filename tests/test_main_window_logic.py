import nibabel as nib
import numpy as np
from monai_ui.main_window import MainWindow

def test_switch_pages(qtbot):
    """Ensure show_welcome_screen switches to index 0."""

    window = MainWindow()
    qtbot.addWidget(window)

    # Simulate switching to viewer first
    window.stacked_widget.setCurrentIndex(1)
    assert window.stacked_widget.currentIndex() == 1

    # Now switch back to welcome
    window.show_welcome_screen()
    assert window.stacked_widget.currentIndex() == 0


def test_menu_actions_exist(qtbot):
    """Ensure the File menu contains the expected actions."""

    window = MainWindow()
    qtbot.addWidget(window)

    file_menu = window.menuBar().actions()[0].menu()

    action_texts = [a.text() for a in file_menu.actions()]

    assert " 🔙 Go to Welcome Screen" in action_texts
    assert "Open NIfTI Image" in action_texts
    assert "Open DICOM Folder" in action_texts


def test_load_and_switch_to_image(qtbot, tmp_path):
    """Ensure loading an image switches to viewer."""
    # Create fake NIfTI file
    vol = np.zeros((10, 10, 10))
    nifti_path = tmp_path / "fake.nii.gz"
    nib.Nifti1Image(vol, np.eye(4)).to_filename(nifti_path)

    window = MainWindow()
    qtbot.addWidget(window)

    window.load_and_switch_to_image(str(nifti_path))

    assert window.stacked_widget.currentIndex() == 1


def test_open_nifti_file(qtbot, tmp_path, monkeypatch):
    """Ensure open_nifti_file loads a volume."""
    vol = np.zeros((10, 10, 10))
    nifti_path = tmp_path / "fake.nii.gz"
    nib.Nifti1Image(vol, np.eye(4)).to_filename(nifti_path)

    # Monkeypatch file dialog
    monkeypatch.setattr(
        "monai_ui.main_window.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(nifti_path), "")
    )

    window = MainWindow()
    qtbot.addWidget(window)

    window.open_nifti_file()

    assert window.image_widget.volume is not None


def test_open_dicom_folder(qtbot, tmp_path, monkeypatch):
    """Ensure open_dicom_folder loads a DICOM series."""
    import SimpleITK as sitk

    folder = tmp_path / "dicom"
    folder.mkdir()

    # Create synthetic DICOM slices
    for i in range(3):
        img = sitk.Image(10, 10, sitk.sitkInt16)
        sitk.WriteImage(img, str(folder / f"slice_{i}.dcm"))

    monkeypatch.setattr(
        "monai_ui.main_window.QFileDialog.getExistingDirectory",
        lambda *args, **kwargs: str(folder)
    )

    window = MainWindow()
    qtbot.addWidget(window)

    window.open_dicom_folder()

    assert window.image_widget.volume is not None
    assert window.stacked_widget.currentIndex() == 1
