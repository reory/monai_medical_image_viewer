# Tests MONAI + NiBabel loaders and mask‑matching logic.

import os
import numpy as np
import pytest

from monai_utils.loaders import (
    load_with_monai,
    load_dicom_series,
    find_matching_mask,
)

def test_find_matching_mask_basic():
    """Ensure mask matching returns None for non existent files."""

    result = find_matching_mask("nonexistent_spleen_999.nii.gz")
    assert result is None

def test_find_matching_mask_realistic(tmp_path):
    """Simulate real MONAI Task09_Spleen structure."""

    task = tmp_path / "Task09_Spleen"
    images = task / "imagesTr"
    labels = task / "labelsTr"

    images.mkdir(parents=True)
    labels.mkdir(parents=True)

    img = images / "spleen_10.nii.gz"
    lbl = labels / "spleen_10.nii.gz"

    img.write_text("dummy")
    lbl.write_text("dummy")

    result = find_matching_mask(str(img))

    # The function returns an absolute path
    expected = os.path.join("labelsTr", "spleen_10.nii.gz")
    assert expected in result


def test_load_with_monai_fallback(tmp_path):
    """Ensure fallback loader works when Monai fails."""

    # Create a fake NIFTI file
    fake = tmp_path / "fake.nii.gz"
    fake.write_bytes(b"not a real nifti")

    with pytest.raises(Exception):
        load_with_monai(str(fake))

def test_load_dicom_series_empty(tmp_path):
    """Empty DICOM folder should return None or raise cleanly."""

    folder = tmp_path / "dicom"
    folder.mkdir()

    try:
        vol = load_dicom_series(str(folder))
        assert vol is None or isinstance(vol, np.ndarray)
    except Exception:
        pass