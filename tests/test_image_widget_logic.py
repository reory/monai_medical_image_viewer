import numpy as np
from monai_ui.image_widget import ImageWidget
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtCore import QSize

def test_slice_navigation(qtbot):
    """Ensure slider navigation updates slice_index."""

    widget = ImageWidget()
    qtbot.addWidget(widget)

    widget.volume = np.zeros((64, 64, 10))
    widget.sld_nav.setRange(0, 9)

    widget.sld_nav.setValue(5)
    assert widget.slice_index == 5

    widget.sld_nav.setValue(0)
    assert widget.slice_index == 0

def test_mask_visibility_flag(qtbot):
    """Ensure mask visibility checkbox toggles correctly."""

    widget = ImageWidget()
    qtbot.addWidget(widget)

    assert widget.chk_mask_visible.isChecked() is True
    widget.chk_mask_visible.setChecked(False)
    assert widget.chk_mask_visible.isChecked() is False

def test_presets(qtbot):
    """Ensure preset buttons adjust sliders correctly."""

    widget = ImageWidget()
    qtbot.addWidget(widget)

    widget._set_preset_full()
    assert widget.sld_width.value() == 100
    assert widget.sld_level.value() == 50

    widget._set_preset_soft()
    assert widget.sld_width.value() == 30
    assert widget.sld_level.value() == 55

    widget._set_preset_bone()
    assert widget.sld_width.value() == 80
    assert widget.sld_level.value() == 25

def test_update_slice(qtbot):
    """Ensure update_slice runs without crashing."""

    widget = ImageWidget()
    qtbot.addWidget(widget)

    widget.volume = np.zeros((32, 32, 5))
    widget.slice_index = 2

    widget.update_slice()  # should not crash
    assert widget.lbl_slice_counter.text().startswith("Slice:")


def test_resize_event_triggers_update(qtbot):
    """Ensure resizeEvent calls update_slice without crashing."""

    widget = ImageWidget()
    qtbot.addWidget(widget)

    widget.volume = np.zeros((32, 32, 5))
    widget.slice_index = 2

    # Proper Qt resize event
    event = QResizeEvent(QSize(800, 600), QSize(640, 480))
    widget.resizeEvent(event)

    assert widget.lbl_slice_counter.text().startswith("Slice:")



def test_slider_navigation_updates_slice(qtbot):
    """Ensure slider navigation updates slice_index."""
    widget = ImageWidget()
    qtbot.addWidget(widget)

    widget.volume = np.zeros((64, 64, 10))
    widget.sld_nav.setRange(0, 9)

    widget.sld_nav.setValue(7)
    assert widget.slice_index == 7

    widget.sld_nav.setValue(0)
    assert widget.slice_index == 0


def test_update_slice_runs(qtbot):
    """Ensure update_slice runs safely with a valid volume."""
    widget = ImageWidget()
    qtbot.addWidget(widget)

    widget.volume = np.zeros((32, 32, 5))
    widget.slice_index = 1

    widget.update_slice()  # should not crash

    assert widget.lbl_slice_counter.text().startswith("Slice:")





