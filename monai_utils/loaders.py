# MONAI LoadImage, spacing, normalization

import SimpleITK as sitk
import numpy as np
import os


from monai.transforms import (
    LoadImage, 
    EnsureChannelFirst, 
    ScaleIntensity,
    Compose
)

def load_dicom_series(folder):
    """Create Dicom series reader."""
    reader = sitk.ImageSeriesReader()
    series = reader.GetGDCMSeriesFileNames(folder)
    reader.SetFileNames(series)
    image = reader.Execute()
    array = sitk.GetArrayFromImage(image)  # shape: [slices, H, W]
    return np.transpose(array, (1, 2, 0))  # convert to [H, W, slices]


def load_with_monai(path):
    transforms = Compose([
        LoadImage(image_only=True),
        EnsureChannelFirst(),
        ScaleIntensity()
    ])

    img = transforms(path)
    return img[0]

def find_matching_mask(image_path: str) -> str | None:
    base = os.path.basename(image_path)  # spleen_10.nii.gz
    task_dir = os.path.dirname(os.path.dirname(image_path))  # .../Task09_Spleen
    mask_path = os.path.join(task_dir, "labelsTr", base)
    return mask_path if os.path.exists(mask_path) else None
