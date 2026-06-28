# Smoke‑tests PyQt6 UI without rendering anything.
from monai_ui.main_window import MainWindow
from monai_ui.welcome_widget import WelcomeWidget
from monai_ui.image_widget import ImageWidget

def test_main_window_instantiates(qtbot):
    """Smoke test: ensure MainWindow loads without errors."""

    window = MainWindow()        # construct widget
    qtbot.addWidget(window)      # register with Qt test bot

    assert window is not None



def test_welcome_widget_instantiates(qtbot):
    """Smoke test: ensure WelcomeWidget loads without errors."""

    widget = WelcomeWidget()
    qtbot.addWidget(widget)

    assert widget is not None


def test_image_widget_instantiates(qtbot):
    """Smoke test: ensure ImageWidget loads without errors."""

    widget = ImageWidget()
    qtbot.addWidget(widget)

    assert widget is not None
    assert hasattr(widget, "slice_index")

