# # rs_trainer_gui.py
# import os
# import sys
# import platform
# import shutil
# import subprocess
# import threading
# import requests
# import webbrowser
#
# from pathlib import Path
# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
#     QPushButton, QFileDialog, QTextEdit, QLineEdit, QMessageBox
# )
# from PySide6.QtGui import QIcon
#
# APP_NAME = "Azulyn"
# CURRENT_VERSION = "1.0.0"
# VERSION_URL = "https://raw.githubusercontent.com/blueboy4g/RS_Trainer/main/version_mac.json" if platform.system() != "Windows" else "https://raw.githubusercontent.com/blueboy4g/RS_Trainer/main/version.json"
# APPDATA_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME) if platform.system() != "Windows" else os.path.join(os.environ["APPDATA"], APP_NAME)
# os.makedirs(APPDATA_DIR, exist_ok=True)
#
# KEYBINDS_FILE = os.path.join(APPDATA_DIR, "keybinds.json")
# BUILD_ROTATION_FILE = os.path.join(APPDATA_DIR, "build_rotation.txt")
# DEFAULT_BUILD_ROTATION_FILE = os.path.join("config", "build_rotation.txt")
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("RuneScape Trainer")
#         self.setGeometry(100, 100, 650, 450)
#
#         self.last_boss_file = QLineEdit()
#         self.last_rotation_file = QLineEdit()
#         self.log_output = QTextEdit()
#         self.log_output.setReadOnly(True)
#
#         self.init_ui()
#         self.ensure_files()
#
#     def ensure_files(self):
#         if not os.path.exists(BUILD_ROTATION_FILE) and os.path.exists(DEFAULT_BUILD_ROTATION_FILE):
#             shutil.copy(DEFAULT_BUILD_ROTATION_FILE, BUILD_ROTATION_FILE)
#
#     def init_ui(self):
#         main_layout = QVBoxLayout()
#
#         self.last_boss_file.setText("Select boss file...")
#         self.last_rotation_file.setText("Select rotation file...")
#
#         main_layout.addWidget(QLabel("Current Boss:"))
#         main_layout.addWidget(self.last_boss_file)
#
#         browse_btn = QPushButton("Browse Boss File")
#         browse_btn.clicked.connect(self.browse_boss_file)
#         main_layout.addWidget(browse_btn)
#
#         main_layout.addWidget(QLabel("Rotation File:"))
#         main_layout.addWidget(self.last_rotation_file)
#
#         browse_rot_btn = QPushButton("Browse Rotation File")
#         browse_rot_btn.clicked.connect(self.browse_rotation_file)
#         main_layout.addWidget(browse_rot_btn)
#
#         start_btn = QPushButton("Start RS Overlay")
#         start_btn.clicked.connect(lambda: self.run_script("../Resources/scripts/rs_overlay.py"))
#         main_layout.addWidget(start_btn)
#
#         rot_btn = QPushButton("Build Rotation")
#         rot_btn.clicked.connect(lambda: self.run_script("../Resources/scripts/rotation_creation.py", log_output=True))
#         main_layout.addWidget(rot_btn)
#
#         update_btn = QPushButton("Check for Updates")
#         update_btn.clicked.connect(self.check_for_update)
#         main_layout.addWidget(update_btn)
#
#         donation_btn = QPushButton("Donate / YouTube")
#         donation_btn.clicked.connect(lambda: webbrowser.open("https://www.youtube.com/@Azulyn1"))
#         main_layout.addWidget(donation_btn)
#
#         main_layout.addWidget(QLabel("Log Output:"))
#         main_layout.addWidget(self.log_output)
#
#         container = QWidget()
#         container.setLayout(main_layout)
#         self.setCentralWidget(container)
#
#     def browse_boss_file(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Select Boss JSON", APPDATA_DIR, "JSON Files (*.json)")
#         if file_path:
#             self.last_boss_file.setText(file_path)
#
#     def browse_rotation_file(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Select Rotation File", APPDATA_DIR, "Text Files (*.txt)")
#         if file_path:
#             self.last_rotation_file.setText(file_path)
#
#
#     def run_script(self, script_name):
#         if getattr(sys, 'frozen', False):
#             # Running from bundled .app
#             #TODO
#             #base_dir = sys._MEIPASS  # temp unpacked dir
#             python_exe = sys.executable
#             script_path = os.path.join(os.path.dirname(sys.executable), script_name)
#         else:
#             # Running from source
#             python_exe = sys.executable
#             script_path = script_name
#
#         print(f"Launching: {script_path}")
#         subprocess.Popen([python_exe, script_path])
#
#     def check_for_update(self):
#         try:
#             response = requests.get(VERSION_URL, timeout=5)
#             data = response.json()
#             latest_version = data.get("version")
#             notes = data.get("notes", "")
#             download_url = data.get("download_url")
#             if latest_version != CURRENT_VERSION:
#                 reply = QMessageBox.question(self, "Update Available",
#                                              f"New version {latest_version} is available:\n\n{notes}\n\nDownload now?",
#                                              QMessageBox.Yes | QMessageBox.No)
#                 if reply == QMessageBox.Yes:
#                     webbrowser.open(download_url)
#             else:
#                 QMessageBox.information(self, "Up to Date", f"You're running version {CURRENT_VERSION}")
#         except Exception as e:
#             QMessageBox.critical(self, "Update Check Failed", str(e))
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())
