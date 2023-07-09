from . functions_main_window import *

from gui.widgets import PyIconButton, ModelFunction1, ModelFunction2, ModelFunction3
from gui.core.json_settings import Settings
from gui.core.json_themes import Themes
from gui.widgets import PyGrips
from gui.core.functions import Functions

from PySide6.QtGui import Qt 
from PySide6.QtSvgWidgets import QSvgWidget

import FPTvision

class SetupMainWindow:
    def __init__(self):
        super().__init__()
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)
        
    add_left_menus = [
        {
            "btn_icon" : "icon_home.svg",
            "btn_id" : "btn_0",
            "btn_text" : "Home",
            "btn_tooltip" : "Home",
            "show_top" : True,
            "is_active" : True,
        }, 
        {
            "btn_icon" : "icon_add_user.svg",
            "btn_id" : "btn_1",
            "btn_text" : "Extract Face From An Image",
            "btn_tooltip" : "Extract Face",
            "show_top" : True,
            "is_active" : False,
        },
        {
            "btn_icon" : "icon_add_user.svg",
            "btn_id" : "btn_2",
            "btn_text" : "Extract Face From Camera",
            "btn_tooltip" : "Extract Face",
            "show_top" : True,
            "is_active" : False
        },
        {
            "btn_icon" : "icon_search.svg",
            "btn_id" : "btn_3",
            "btn_text" : "Recognize Faces", 
            "btn_tooltip" : "Recognition",
            "show_top" : True,
            "is_active" : False
        }
    ]
    
    def setup_btns(self):
        if self.ui.title_bar.sender() != None:
            return self.ui.title_bar.sender()
        elif self.ui.left_menu.sender() != None:
            return self.ui.left_menu.sender()
        elif self.ui.left_column.sender() != None:
            return self.ui.left_column.sender()
        
    def setup_gui(self):
        self.setWindowTitle(self.settings["app_name"])
        
        if self.settings["custom_title_bar"]:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
        if self.settings["custom_title_bar"]:
            self.left_grip = PyGrips(self, "left", self.hide_grips)
            self.right_grip = PyGrips(self, "right", self.hide_grips)
            self.top_grip = PyGrips(self, "top", self.hide_grips)
            self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
            self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
            self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
            self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
            self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)
        self.ui.left_menu.add_menus(SetupMainWindow.add_left_menus)
        self.ui.left_menu.clicked.connect(self.btn_clicked)
        self.ui.left_menu.released.connect(self.btn_released)
        self.ui.title_bar.clicked.connect(self.btn_clicked)
        self.ui.title_bar.released.connect(self.btn_released)
        
        if self.settings["custom_title_bar"]:
            self.ui.title_bar.set_title(self.settings["app_name"])
        else:
            self.ui.title_bar.set_title("")
        self.ui.left_column.clicked.connect(self.btn_clicked)
        self.ui.left_column.released.connect(self.btn_released)
        
        MainFunctions.set_page(self, self.ui.load_pages.page_1)
        MainFunctions.set_left_column_menu(
            self,
            menu = self.ui.left_column.menus.menu_1,
            title = "Settings Left Column",
            icon_path = Functions.set_svg_icon("icon_settings.svg")
        )
         
        settings = Settings()
        self.settings = settings.items
        
        themes = Themes()
        self.themes = themes.items
    
        
        #Home page
        self.Home_logo = QSvgWidget(Functions.set_svg_image("Home.svg"))
        self.Home_logo.setFixedSize(700, 700)
        self.ui.load_pages.row_1_1layout.addWidget(self.Home_logo, Qt.AlignCenter | Qt.AlignCenter)
        
        self.btn_search = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_search.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "Search",
            width = 40,
            height = 40,
            radius = 20,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["dark_four"],
            icon_color_pressed = self.themes["app_color"]["icon_active"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["pink"]
        )
        
        self.btn_save_1 = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_save.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "Save",
            width = 40,
            height = 40,
            radius = 8,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["dark_four"],
            icon_color_pressed = self.themes["app_color"]["icon_active"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["green"]
        )
        
        self.btn_capture = PyIconButton(
            icon_path = Functions.set_svg_icon("icon_save.svg"),
            parent = self,
            app_parent = self.ui.central_widget,
            tooltip_text = "Save",
            width = 40,
            height = 40,
            radius = 8,
            dark_one = self.themes["app_color"]["dark_one"],
            icon_color = self.themes["app_color"]["icon_color"],
            icon_color_hover = self.themes["app_color"]["dark_four"],
            icon_color_pressed = self.themes["app_color"]["icon_active"],
            icon_color_active = self.themes["app_color"]["icon_active"],
            bg_color = self.themes["app_color"]["dark_one"],
            bg_color_hover = self.themes["app_color"]["dark_three"],
            bg_color_pressed = self.themes["app_color"]["green"]
        )
        
        self.Detector = FPTvision.app.FaceAnalysis()
        self.Detector.prepare(ctx_id=0, det_size=(640, 640))
        
        self.Recognition = FPTvision.model_zoo.arcface_onnx.ArcFaceONNX(model_file='./gui/models/Recognition/model.onnx')
        self.Recognition.prepare(ctx_id=0)

        # page 2 (3 tính năng: text bar, 2 button)
        self.Function1 = ModelFunction1(self.Detector)
        self.ui.load_pages.row_1_2layout.addWidget(self.Function1.canvas_image)
        self.ui.load_pages.row_2_2layout.addWidget(self.Function1.text_name)
        
        self.ui.load_pages.row_2_2layout.addWidget(self.btn_search)
        self.btn_search.clicked.connect(self.Function1.open_image)
        
        self.ui.load_pages.row_2_2layout.addWidget(self.btn_save_1)
        self.btn_save_1.clicked.connect(self.Function1.save_face)
        
        # page 3 (1 tính năng: 1 button)
        self.Function2 = ModelFunction2(self.Detector)
        self.ui.load_pages.row_1_3layout.addWidget(self.Function2.canvas_image)
        self.ui.load_pages.row_2_3layout.addWidget(self.Function2.text_name)
        
        self.ui.load_pages.row_2_3layout.addWidget(self.btn_capture)
        self.btn_capture.clicked.connect(self.Function2.capture_face)
        
        # page 4 (chỉ  cần show camera)
        self.Function3 = ModelFunction3(self.Detector, self.Recognition)
        self.ui.load_pages.row_1_4layout.addWidget(self.Function3.video_label)
        
    def resize_grips(self):
        if self.settings["custom_title_bar"]:
            self.left_grip.setGeometry(5, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
            self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
            self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
            self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
            self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)