# Provides a shared Qt application fixture + temporary directory helpers.

import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app():
    """Global QApplication instance for UI smoke tests."""

    return QApplication([])