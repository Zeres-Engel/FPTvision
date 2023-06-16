import cv2
import os
from PySide6 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageQt
import FPTvision
import os
import numpy as np
from PySide6.QtWidgets import QPushButton, QLabel, QGraphicsDropShadowEffect, QLineEdit, QApplication, QWidget, QMessageBox
from PySide6.QtGui import Qt, QPainter, QBrush, QColor, QPixmap,QImage, QPen, QTransform
from PySide6.QtCore import QRect, QEvent, QPoint

def set_svg_icon(icon_name):
    app_path = os.path.abspath(os.getcwd())
    folder = "./gui/images/svg_icons/"
    path = os.path.join(app_path, folder)
    icon = os.path.normpath(os.path.join(path, icon_name))
    return icon
style = '''
QLineEdit {{
	background-color: {_bg_color}; 
	border-radius: {_radius}px;
	border: {_border_size}px solid transparent;
	padding-left: 10px;
    padding-right: 10px;
	selection-color: {_selection_color};
	selection-background-color: {_context_color};
    color: {_color};
}}
QLineEdit:focus {{
	border: {_border_size}px solid {_context_color};
    background-color: {_bg_color_active};
}}
'''
class PyLineEdit(QLineEdit):
    def __init__(
        self, 
        text = "",
        place_holder_text = "",
        radius = 8,
        border_size = 2,
        color = "#FFF",
        selection_color = "#FFF",
        bg_color = "#333",
        bg_color_active = "#222",
        context_color = "#00ABE8"
    ):
        super().__init__()
        if text:
            self.setText(text)
        if place_holder_text:
            self.setPlaceholderText(place_holder_text)
        self.set_stylesheet(
            radius,
            border_size,
            color,
            selection_color,
            bg_color,
            bg_color_active,
            context_color
        )
    def set_stylesheet(
        self,
        radius,
        border_size,
        color,
        selection_color,
        bg_color,
        bg_color_active,
        context_color
    ):
        style_format = style.format(
            _radius = radius,
            _border_size = border_size,           
            _color = color,
            _selection_color = selection_color,
            _bg_color = bg_color,
            _bg_color_active = bg_color_active,
            _context_color = context_color
        )
        self.setStyleSheet(style_format)

class PyIconButton(QPushButton):
    def __init__(
        self,
        icon_path = None,
        parent = None,
        app_parent = None,
        tooltip_text = "",
        btn_id = None,
        width = 30,
        height = 30,
        radius = 8,
        bg_color = "#343b48",
        bg_color_hover = "#3c4454",
        bg_color_pressed = "#2c313c",
        icon_color = "#c3ccdf",
        icon_color_hover = "#dce1ec",
        icon_color_pressed = "#edf0f5",
        icon_color_active = "#f5f6f9",
        dark_one = "#1b1e23",
        text_foreground = "#8a95aa",
        context_color = "#568af2",
        top_margin = 40,
        is_active = False
    ):
        super().__init__()
        self.setFixedSize(width, height)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName(btn_id)
        self._bg_color = bg_color
        self._bg_color_hover = bg_color_hover
        self._bg_color_pressed = bg_color_pressed        
        self._icon_color = icon_color
        self._icon_color_hover = icon_color_hover
        self._icon_color_pressed = icon_color_pressed
        self._icon_color_active = icon_color_active
        self._context_color = context_color
        self._top_margin = top_margin
        self._is_active = is_active
        self._set_bg_color = bg_color
        self._set_icon_path = icon_path
        self._set_icon_color = icon_color
        self._set_border_radius = radius
        self._parent = parent
        self._app_parent = app_parent
        self._tooltip_text = tooltip_text
        self._tooltip = _ToolTip(
            app_parent,
            tooltip_text,
            dark_one,
            text_foreground
        )
        self._tooltip.hide()
    def clicked(self):
        self.clicked.emit()
    def set_active(self, is_active):
        self._is_active = is_active
        self.repaint()
    def is_active(self):
        return self._is_active
    def paintEvent(self, event):
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._is_active:
            brush = QBrush(QColor(self._context_color))
        else:
            brush = QBrush(QColor(self._set_bg_color))
        rect = QRect(0, 0, self.width(), self.height())
        paint.setPen(Qt.NoPen)
        paint.setBrush(brush)
        paint.drawRoundedRect(
            rect, 
            self._set_border_radius, 
            self._set_border_radius
        )
        self.icon_paint(paint, self._set_icon_path, rect)
        paint.end()
    def change_style(self, event):
        if event == QEvent.Enter:
            self._set_bg_color = self._bg_color_hover
            self._set_icon_color = self._icon_color_hover
            self.repaint()         
        elif event == QEvent.Leave:
            self._set_bg_color = self._bg_color
            self._set_icon_color = self._icon_color
            self.repaint()
        elif event == QEvent.MouseButtonPress:            
            self._set_bg_color = self._bg_color_pressed
            self._set_icon_color = self._icon_color_pressed
            self.repaint()
        elif event == QEvent.MouseButtonRelease:
            self._set_bg_color = self._bg_color_hover
            self._set_icon_color = self._icon_color_hover
            self.repaint()
    def enterEvent(self, event):
        self.change_style(QEvent.Enter)
        self.move_tooltip()
        self._tooltip.show()
    def leaveEvent(self, event):
        self.change_style(QEvent.Leave)
        self.move_tooltip()
        self._tooltip.hide()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.change_style(QEvent.MouseButtonPress)
            self.setFocus()
            return self.clicked.emit()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            
            self.change_style(QEvent.MouseButtonRelease)
            return self.released.emit()
    def icon_paint(self, qp, image, rect):
        icon = QPixmap(image)
        painter = QPainter(icon)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        if self._is_active:
            painter.fillRect(icon.rect(), self._icon_color_active)
        else:
            painter.fillRect(icon.rect(), self._set_icon_color)
        qp.drawPixmap(
            (rect.width() - icon.width()) / 2, 
            (rect.height() - icon.height()) / 2,
            icon
        )        
        painter.end()
    def set_icon(self, icon_path):
        self._set_icon_path = icon_path
        self.repaint()
    def move_tooltip(self):
        gp = self.mapToGlobal(QPoint(0, 0))
        pos = self._parent.mapFromGlobal(gp)
        pos_x = (pos.x() - (self._tooltip.width() // 2)) + (self.width() // 2)
        pos_y = pos.y() - self._top_margin
        self._tooltip.move(pos_x, pos_y)
        
class _ToolTip(QLabel):
    style_tooltip = """ 
    QLabel {{		
        background-color: {_dark_one};	
        color: {_text_foreground};
        padding-left: 5px;
        padding-right: 5px;
        border-radius: 10px;
        border: 0px solid transparent;
        font: 800 9pt "Segoe UI";
    }}
    """
    def __init__(
        self,
        parent, 
        tooltip,
        dark_one,
        text_foreground
    ):
        QLabel.__init__(self)
        style = self.style_tooltip.format(
            _dark_one = dark_one,
            _text_foreground = text_foreground
        )
        self.setObjectName(u"label_tooltip")
        self.setStyleSheet(style)
        self.setMinimumHeight(20)
        self.setParent(parent)
        self.setText(tooltip)
        self.adjustSize()
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)

class ModelFunction2(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detection")

        # Create widgets
        self.btn_capture = PyIconButton(
            icon_path=set_svg_icon("icon_add_user.svg"),
            parent=self,
            app_parent=self,
            tooltip_text="Open",
            width=40,
            height=40,
            radius=8,
            dark_one="#1b1e23",
            icon_color="#c3ccdf",
            icon_color_hover="#dce1ec",
            icon_color_pressed="#f5f6f9",
            icon_color_active="#f5f6f9",
            bg_color="#1b1e23",
            bg_color_hover="#21252d",
            bg_color_pressed="#00ff7f",
        )

        self.text_name = PyLineEdit(
            text="",
            place_holder_text="Enter name",
            radius=8,
            border_size=2,
            color="#8a95aa",
            selection_color="#f5f6f9",
            bg_color="#1b1e23",
            bg_color_active="#21252d",
            context_color="#568af2",
        )
        self.text_name.setMinimumHeight(30)

        self.canvas_widget = QtWidgets.QWidget(self)
        self.canvas_widget.setMinimumSize(640, 480)  # Set minimum size for the webcam screen
        self.canvas_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas_layout = QtWidgets.QVBoxLayout(self.canvas_widget)
        self.canvas_image = QtWidgets.QLabel(self.canvas_widget)
        self.canvas_image.setAlignment(QtCore.Qt.AlignCenter)
        self.canvas_layout.addWidget(self.canvas_image)

        #! Set layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.btn_capture)
        layout.addWidget(self.text_name)
        layout.addWidget(self.canvas_widget)
        
        # Đường dẫn đến file trạng thái
        self.status_file = './gui/status.txt'
        self.status = 0

        # Initialize variables
        self.cap = None  # VideoCapture instance
        self.model = None  # Model instance

        # Connect signals
        self.btn_capture.clicked.connect(self.capture_face)

        # Initialize model detection
        self.init_model()
        
        self.check_status()

        # Open webcam
        self.open_webcam()
        
        # Start frame update
        self.update_frame()
        
        self.close_webcam()

    def init_model(self):
        self.model = FPTvision.app.FaceAnalysis(allowed_modules=['detection'])
        self.model.prepare(ctx_id=0, det_size=(640, 640))
        
    def check_status(self):
        with open(self.status_file, 'r') as file:
            self.status = file.read().strip()

    def update_frame(self):
        # Kiểm tra nội dung file trạng thái
        with open(self.status_file, 'r') as file:
            self.status = file.read().strip()

        if self.status == '3':
            if self.cap is None:
                # Mở camera khi trạng thái là "3"
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width to 1280
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height to 720
        else:
            self.close_webcam()

        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Flip the frame horizontally

                # Detect face using InsightFace model
                faces = self.model.get(frame)
                for face in faces:
                    bbox = face.bbox.astype(int)
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)

                # Calculate the scaled size for the image to fit the canvas
                canvas_width = self.canvas_widget.width()
                canvas_height = self.canvas_widget.height()
                image_ratio = image.width / image.height
                canvas_ratio = canvas_width / canvas_height
                if image_ratio > canvas_ratio:
                    new_width = canvas_width
                    new_height = int(canvas_width / image_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * image_ratio)
                image = image.resize((new_width, new_height))

                qt_image = ImageQt.ImageQt(image)
                pixmap = QtGui.QPixmap.fromImage(qt_image)
                self.canvas_image.setPixmap(pixmap.scaled(canvas_width, canvas_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.canvas_image.clear()
            self.close_webcam()

        QtCore.QTimer.singleShot(15, self.update_frame)


    def open_webcam(self):
        if self.cap is None and self.status == '3': 
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set frame width to 1280
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set frame height to 720
        else:
            self.close_webcam()

    def close_webcam(self):
        if self.cap is not None and self.status != '3':
            self.cap.release()
            self.cap = None

    def capture_face(self):
        ret, frame = self.cap.read()
        if ret:
            # Detect face using InsightFace model
            faces = self.model.get(frame)
            if len(faces) > 0:
                # Get first face detected
                bbox = faces[0].bbox.astype(int)
                face_image = frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]

                # Resize face image to 112x112 and center it
                h, w, _ = face_image.shape
                size = max(h, w)
                pad_h = (size - h) // 2
                pad_w = (size - w) // 2
                face_image = cv2.copyMakeBorder(face_image, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, value=(0, 0, 0))
                face_image = cv2.resize(face_image, (112, 112))

                # Save face image
                name = self.text_name.text()
                if name != "":
                    filename = os.path.join("./gui/aligned", f"{name}.jpg")
                    cv2.imwrite(filename, face_image)
                    QMessageBox.information(self, "Status", f"Face detected and saved successfully")
                else:
                    QMessageBox.warning(self, "Status", "Please enter a name for the face image")
            else:
                QMessageBox.warning(self, "Status", "No face detected")

if __name__ == "__main__":
    # Initialize GUI
    app_instance = QtWidgets.QApplication([])
    model_operation = ModelFunction2()
    model_operation.show()
    app_instance.exec_()
