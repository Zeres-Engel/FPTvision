import os
import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication
from gui.core.json_settings import Settings
from gui.uis.windows.main_window import *
from gui.widgets import *
from gui.uis.windows.main_window.functions_main_window import *

os.environ["QT_FONT_DPI"] = "96"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create UI
        self.ui = UI_MainWindow()

        # Setup UI
        self.ui.setup_ui(self)

        # Create setting
        settings = Settings()
        self.settings = settings.items

        # Hide grips
        self.hide_grips = True

        # Create and write to status file
        self.update_status_file(0)
        
        # Setup UI on window
        SetupMainWindow.setup_gui(self)

        # Show
        self.show()

    def closeEvent(self, event):
        # Delete status file before closing the application
        self.delete_status_file()
        event.accept()

    def btn_clicked(self):
        btn = SetupMainWindow.setup_btns(self)

        if btn.objectName() == "btn_0":
            self.ui.left_menu.select_only_one(btn.objectName())
            self.update_status_file(1)
            MainFunctions.set_page(self, self.ui.load_pages.page_1)

        if btn.objectName() == "btn_1":
            self.ui.left_menu.select_only_one(btn.objectName())
            self.update_status_file(2)
            MainFunctions.set_page(self, self.ui.load_pages.page_2)

        if btn.objectName() == "btn_2":
            self.ui.left_menu.select_only_one(btn.objectName())
            self.update_status_file(3)
            MainFunctions.set_page(self, self.ui.load_pages.page_3)

        if btn.objectName() == "btn_3":
            self.ui.left_menu.select_only_one(btn.objectName())
            self.update_status_file(4)
            MainFunctions.set_page(self, self.ui.load_pages.page_4)

    def btn_released(self):
        btn = SetupMainWindow.setup_btns(self)

    def resizeEvent(self, event):
        SetupMainWindow.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition()

    def update_status_file(self, status):
        file_path = "./gui/status.txt"
        with open(file_path, "w") as file:
            file.write(str(status))

    def delete_status_file(self):
        file_path = "./gui/status.txt"
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())