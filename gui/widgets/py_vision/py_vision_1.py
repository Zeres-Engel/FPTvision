import os
import cv2
from PySide6.QtCore import Qt, QRect, QEvent, QPoint
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFileDialog, QMessageBox
from PIL import Image
import FPTvision

import numpy as np
from PySide6.QtWidgets import QPushButton, QLabel, QGraphicsDropShadowEffect, QLineEdit, QApplication, QWidget
from PySide6.QtGui import Qt, QPainter, QBrush, QColor, QPixmap,QImage, QPen, QTransform


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

class ModelFunction1(QWidget):
    def __init__(self):
        super().__init__()

        # Khởi tạo model nhận diện
        self.model = FPTvision.app.FaceAnalysis()
        self.model.prepare(ctx_id=0, det_size=(640, 640))

        # Thiết lập giao diện
        self.setWindowTitle("Face Detection")
        self.setGeometry(100, 100, 800, 600)

        self.btn_open = PyIconButton(
            icon_path=set_svg_icon("icon_search.svg"),
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
        self.btn_open.clicked.connect(self.open_image)

        self.btn_save = PyIconButton(
            icon_path=set_svg_icon("icon_save.svg"),
            parent=self,
            app_parent=self,
            tooltip_text="Save",
            width=40,
            height=40,
            radius=20,
            dark_one="#1b1e23",
            icon_color="#c3ccdf",
            icon_color_hover="#dce1ec",
            icon_color_pressed="#f5f6f9",
            icon_color_active="#f5f6f9",
            bg_color="#1b1e23",
            bg_color_hover="#21252d",
            bg_color_pressed="#ff007f",
        )
        self.btn_save.clicked.connect(self.save_face)

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

        self.canvas_image = QLabel()
        self.canvas_image.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.text_name)
        layout.addWidget(self.canvas_image)

        self.setLayout(layout)

        # Khởi tạo biến
        self.image_path = None
        self.image_pixmap = None

    def open_image(self):
        # Chọn ảnh từ máy tính
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image Files (*.jpg)")
        if file_dialog.exec():
            self.image_path = file_dialog.selectedFiles()[0]

            # Hiển thị ảnh lên giao diện
            image = Image.open(self.image_path)

            # Chuyển đổi PIL.Image sang QImage
            image_data = image.convert("RGBA").tobytes("raw", "RGBA")
            q_image = QImage(
                image_data, image.size[0], image.size[1], QImage.Format_RGBA8888
            )
            self.image_pixmap = QPixmap.fromImage(q_image)

            # Thay đổi kích thước hình ảnh
            max_width = self.canvas_image.width()
            max_height = self.canvas_image.height()
            resized_pixmap = self.image_pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio)

            self.canvas_image.setPixmap(resized_pixmap)

    def save_face(self):
        if self.image_path is not None:
            if self.image_pixmap is not None:
                # Load the image
                image = cv2.imread(self.image_path)
                try:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    # Detect faces using the InsightFace model
                    faces = self.model.get(image_rgb)
                    if len(faces) == 1:
                        # Get the first detected face
                        bbox = faces[0].bbox.astype(int)
                        face_image = image_rgb[bbox[1]:bbox[3], bbox[0]:bbox[2]]

                        # Process the face size
                        desired_size = 112

                        # Resize and pad the face if necessary
                        face_image = self.process_face(face_image, desired_size)

                        # Save the face
                        name = self.text_name.text()
                        if name != "":
                            face_path = os.path.join("./gui/aligned", f"{name}.jpg")
                            cv2.imwrite(
                                face_path, cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
                            )
                            QMessageBox.information(
                                self, "Information", "Face saved successfully"
                            )
                            self.text_name.setText("")  # Reset PyLineEdit
                        else:
                            QMessageBox.warning(self, "Warning", "Please enter a name")
                    elif len(faces) == 0:
                        QMessageBox.warning(
                            self, "Warning", "No face found in the image"
                        )
                    else:
                        QMessageBox.warning(
                            self, "Warning", "Multiple faces found in the image"
                        )
                except:
                    QMessageBox.warning(
                        self, "Error", "Your image does not follow the standard color format, so accurate detection cannot be performed!"
                    )
            else:
                QMessageBox.warning(
                    self, "Warning", "Please select an image before saving"
                )
        else:
            QMessageBox.warning(
                self, "Warning", "Please select an image before saving"
            )

    def process_face(self, face_image, desired_size):
        # Face size
        h, w, _ = face_image.shape

        # Calculate the maximum side of the square bounding box
        max_size = max(w, h)

        # Calculate padding values
        delta_w = max_size - w
        delta_h = max_size - h

        # Calculate the starting point to transform the bounding box into a square
        start_x = delta_w // 2
        start_y = delta_h // 2

        # Create a centered square
        padded_image = np.zeros((max_size, max_size, 3), dtype=np.uint8)
        padded_image[start_y: start_y + h, start_x: start_x + w, :] = face_image

        # Resize the image
        resized_image = cv2.resize(padded_image, (desired_size, desired_size))

        return resized_image


if __name__ == "__main__":
    app = QApplication([])
    model_operation = ModelFunction1()
    model_operation.show()
    app.exec()