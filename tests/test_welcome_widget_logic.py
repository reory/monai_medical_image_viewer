from monai_ui.welcome_widget import WelcomeWidget

def test_buttons_exist(qtbot):
    """Ensure the two dashboard buttons exist."""

    widget = WelcomeWidget()
    qtbot.addWidget(widget)

    assert hasattr(widget, "btn_nifti")
    assert hasattr(widget, "btn_dicom")


def test_scan_local_dataset_populates_list(qtbot, tmp_path, monkeypatch):
    """Ensure scan_local_dataset populates the list when files exist."""

    # Create fake dataset structure
    target = tmp_path / "data" / "spleen" / "Task09_Spleen" / "imagesTr"
    target.mkdir(parents=True)

    # Add fake NIfTI files
    (target / "spleen_01.nii.gz").write_text("dummy")
    (target / "spleen_02.nii.gz").write_text("dummy")

    # Monkeypatch the path inside the widget
    monkeypatch.setattr(
        "monai_ui.welcome_widget.os.path.join",
        lambda *args: str(target)
    )

    widget = WelcomeWidget()
    qtbot.addWidget(widget)

    assert widget.file_list.count() == 2


def test_double_click_emits_signal(qtbot, tmp_path, monkeypatch):
    """Ensure double-clicking an item emits file_selected with full path."""

    # Create fake dataset structure
    target_dir = tmp_path / "data" / "spleen" / "Task09_Spleen" / "imagesTr"
    target_dir.mkdir(parents=True)

    file_name = "spleen_01.nii.gz"
    full_path = target_dir / file_name
    full_path.write_text("dummy")

    # Monkeypatch the path inside the widget
    monkeypatch.setattr(
        "monai_ui.welcome_widget.os.path.join",
        lambda *args: str(target_dir)
    )
    monkeypatch.setattr(
        "monai_ui.welcome_widget.os.path.exists",
        lambda p: True
    )

    widget = WelcomeWidget()
    qtbot.addWidget(widget)

    # Add item manually
    widget.file_list.clear()
    widget.file_list.addItem(file_name)

    captured = []

    def on_selected(path):
        captured.append(path)

    widget.file_selected.connect(on_selected)

    # Simulate double-click
    item = widget.file_list.item(0)
    widget._on_item_double_clicked(item)

    assert captured[0] == str(target_dir)

