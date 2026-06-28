# 💬 Welcome
Thanks for your interest in contributing to the MONAI Medical Image Viewer!
This project is built to be simple, educational, and fun — and contributions of all sizes are welcome.

Whether you want to fix a bug, improve the UI, add new imaging features, or help with documentation, this guide will help you get started.

---

## 📦 Project Structure Overview
The project is organized into three main areas:

```python
monai_ui/        # PyQt6 UI components (main window, viewer, dashboard)
monai_utils/     # Loaders, transforms, helper utilities
data/            # Local datasets (ignored by Git)
viewer.py        # Application entry point
```
If you're adding new UI features, you’ll likely work inside monai_ui/.
If you're adding new loaders or processing logic, you’ll work inside monai_utils/.

---

## 🛠️ How to Contribute
### 1. Fork the repository
Create your own fork on GitHub so you can work independently.

### 2. Create a feature branch
Use a descriptive name:

```bash
git checkout -b feature/neon-slider-theme
git checkout -b fix/dicom-loader-crash
```

### 3. Make your changes
Follow the existing style:

- PyQt6 widgets go in monai_ui/

- Loaders and transforms go in monai_utils/

- Keep UI code readable and modular

- Avoid committing large medical datasets

### 4. Test your changes
Run the viewer locally:

```bash
python viewer.py
```
Make sure:

- NIfTI loading works

- UI elements behave correctly

- No crashes occur when switching screens

### 5. Submit a Pull Request
Include:

- A clear description of the change

- Screenshots if it’s a UI update

- Notes on any new dependencies

- Small PRs are easier to review than large ones.

---

## 📐 Coding Style Guidelines

- Follow PEP‑8 where practical

- Use meaningful variable names

- Keep functions short and focused

- Avoid deeply nested logic

- Prefer clarity over cleverness

### PyQt6
- Group related widgets into layouts

- Keep styling consistent with the Neon Tech theme

- Avoid hard‑coding large blocks of CSS in multiple places

- Use signals/slots for communication between widgets

### MONAI / NiBabel
- Use MONAI loaders when possible

- Fall back to NiBabel for simple NIfTI reads

- Keep DICOM handling inside monai_utils.loaders

---

## 🧪 Adding New Features
If you want to add a new feature, please:

- Open an issue describing the feature

- Explain why it’s useful

- Provide a rough plan or UI sketch

- This helps keep the project organized and avoids duplicate work.

---

## 🐛 Reporting Bugs
If you find a bug, please include:

- Steps to reproduce

- Expected behavior

- Actual behavior

- Screenshot (if UI‑related)

- OS + Python version

- Clear bug reports help fix issues faster.

---

## 📄 Documentation
Documentation improvements are always welcome:

- README updates

- Code comments

- Docstrings

- Tutorials

- Example screenshots

---

## 🤝 Code of Conduct
Be respectful, constructive, and collaborative.
This project is meant to be welcoming to beginners and experts alike.

---

## 💡 Thank You
Your contributions help make this viewer better for everyone — whether you're fixing a typo or adding a major feature.
Thanks 😊